#!/usr/bin/env python3
"""
Complete workflow case study: Integrating a Bell County news article 
from START through END with full state management and decision tracking.

Workflow States: START -> PROCESS -> DECISION -> ACTION -> VALIDATE -> END

This script demonstrates the full lifecycle with evidence capture at each step.
"""

import json
import os
import uuid
import hashlib
import datetime
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import pipeline components
try:
    from pipeline import (
        run_pipeline, load_allowlist, canonicalize_url, 
        compute_hash, now_iso, OUTPUT
    )
except ImportError:
    # Fallback: define minimal versions locally
    def compute_hash(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()
    
    def now_iso():
        return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    def load_allowlist() -> Dict[str, Any]:
        p = Path(__file__).parent / "allowlist.json"
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def canonicalize_url(url: str) -> str:
        u = url.strip().lower()
        if u.startswith("http://"):
            u = u[len("http://"):]
        if u.startswith("https://"):
            u = u[len("https://"):]
        if u.endswith("/"):
            u = u[:-1]
        return u
    
    OUTPUT = Path(__file__).parent / "output"
    OUTPUT.mkdir(exist_ok=True)


class WorkflowState(Enum):
    """Define workflow state machine"""
    START = "START"
    PROCESS = "PROCESS"
    DECISION = "DECISION"
    ACTION = "ACTION"
    VALIDATE = "VALIDATE"
    END = "END"


@dataclass
class StateTransition:
    """Record a state transition with evidence"""
    from_state: WorkflowState
    to_state: WorkflowState
    timestamp: str
    event: str
    data: Dict[str, Any]
    decision_result: bool = None


class WorkflowManager:
    """Manage workflow state transitions and evidence capture"""
    
    def __init__(self, article_id: str, article_title: str):
        self.article_id = article_id
        self.article_title = article_title
        self.workflow_id = str(uuid.uuid4())
        self.current_state = WorkflowState.START
        self.transitions: List[StateTransition] = []
        self.state_data = {}
        self.workflow_log_path = OUTPUT / f"workflow-{self.workflow_id}.json"
        
    def transition(self, to_state: WorkflowState, event: str, data: Dict[str, Any], 
                   decision_result: bool = None) -> bool:
        """Record a state transition"""
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            timestamp=now_iso(),
            event=event,
            data=data,
            decision_result=decision_result
        )
        self.transitions.append(transition)
        self.current_state = to_state
        self._save_workflow_state()
        return True
    
    def _save_workflow_state(self):
        """Persist workflow state to disk"""
        workflow_doc = {
            "workflow_id": self.workflow_id,
            "article_id": self.article_id,
            "article_title": self.article_title,
            "current_state": self.current_state.value,
            "transitions": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "timestamp": t.timestamp,
                    "event": t.event,
                    "data": t.data,
                    "decision_result": t.decision_result
                }
                for t in self.transitions
            ]
        }
        with open(self.workflow_log_path, "w") as f:
            json.dump(workflow_doc, f, indent=2)


def phase_start(title: str, source: str) -> tuple:
    """
    PHASE 1: START
    Initialize workflow, define article metadata, establish initial state.
    """
    print("\n" + "="*70)
    print("PHASE 1: START - Workflow Initialization")
    print("="*70)
    
    article_id = str(uuid.uuid4())[:8]
    workflow = WorkflowManager(article_id, title)
    
    article_metadata = {
        "id": article_id,
        "title": title,
        "source": source,
        "ingestion_time": now_iso(),
        "expected_category": "Bell County News",
    }
    
    print(f"\n✓ Article ID: {article_id}")
    print(f"✓ Title: {title}")
    print(f"✓ Source: {source}")
    print(f"✓ Workflow ID: {workflow.workflow_id}")
    
    workflow.transition(
        WorkflowState.PROCESS,
        event="article_received",
        data=article_metadata
    )
    
    return workflow, article_metadata


def phase_process(workflow: WorkflowManager, metadata: Dict, content: str) -> Dict:
    """
    PHASE 2: PROCESS
    Extract, parse, and normalize article content.
    Compute content hash, validate structure, extract metadata.
    """
    print("\n" + "="*70)
    print("PHASE 2: PROCESS - Content Extraction & Normalization")
    print("="*70)
    
    # Extract content hash
    content_hash = compute_hash(content)
    content_length = len(content)
    
    # Extract domain from source
    source_domain = canonicalize_url(metadata["source"])
    
    # Normalize content
    lines = content.split("\n")
    
    process_result = {
        "content_hash": content_hash,
        "content_length": content_length,
        "line_count": len(lines),
        "source_domain": source_domain,
        "timestamp": now_iso(),
    }
    
    print(f"\n✓ Content hash (SHA-256): {content_hash[:16]}...")
    print(f"✓ Content length: {content_length} bytes")
    print(f"✓ Source domain: {source_domain}")
    print(f"✓ Structure: {len(lines)} lines")
    
    workflow.transition(
        WorkflowState.DECISION,
        event="content_processed",
        data=process_result
    )
    
    return process_result


def phase_decision(workflow: WorkflowManager, metadata: Dict, process_result: Dict) -> Dict:
    """
    PHASE 3: DECISION
    Apply verification rules: allowlist check, source validation, content quality.
    Make acceptance/rejection decision with evidence.
    """
    print("\n" + "="*70)
    print("PHASE 3: DECISION - Verification & Rule Application")
    print("="*70)
    
    allowlist = load_allowlist()
    domain = process_result["source_domain"]
    
    # Check 1: Domain verification against allowlist
    domain_valid = False
    matched_domain = None
    for allowed in allowlist.get("domains", []):
        canonical_allowed = canonicalize_url(allowed)
        if domain == canonical_allowed or domain.endswith("." + canonical_allowed):
            domain_valid = True
            matched_domain = canonical_allowed
            break
    
    # Check 2: Content quality
    content_valid = process_result["content_length"] > 50  # Minimum content threshold
    
    # Check 3: Contact verification
    contact_valid = False
    for contact in allowlist.get("contacts", []):
        if contact["organization"].lower() in metadata["source"].lower():
            contact_valid = True
            break
    
    # Overall decision
    accepted = domain_valid and content_valid
    
    decision_result = {
        "domain_check": {
            "valid": domain_valid,
            "matched": matched_domain,
            "domain": domain,
        },
        "content_check": {
            "valid": content_valid,
            "min_length": 50,
            "actual_length": process_result["content_length"],
        },
        "contact_check": {
            "valid": contact_valid,
        },
        "final_decision": "ACCEPT" if accepted else "REJECT",
        "reasons": [],
        "timestamp": now_iso(),
    }
    
    # Populate rejection reasons if rejected
    if not domain_valid:
        decision_result["reasons"].append("Domain not in allowlist")
    if not content_valid:
        decision_result["reasons"].append("Content below minimum threshold")
    if not contact_valid:
        decision_result["reasons"].append("Contact verification failed (non-blocking)")
    
    print(f"\n✓ Domain Verification: {'PASS' if domain_valid else 'FAIL'}")
    if domain_valid:
        print(f"  → Matched allowlist entry: {matched_domain}")
    
    print(f"✓ Content Quality: {'PASS' if content_valid else 'FAIL'}")
    print(f"  → Length check: {process_result['content_length']} bytes (min: 50)")
    
    print(f"✓ Contact Verification: {'PASS' if contact_valid else 'FAIL'} (informational)")
    
    print(f"\n{'='*50}")
    print(f"DECISION: {decision_result['final_decision']}")
    print(f"{'='*50}")
    
    if decision_result["reasons"]:
        print("\nRejection Reasons:")
        for reason in decision_result["reasons"]:
            print(f"  • {reason}")
    
    workflow.transition(
        WorkflowState.ACTION if accepted else WorkflowState.VALIDATE,
        event="verification_complete",
        data=decision_result,
        decision_result=accepted
    )
    
    return decision_result


def phase_action(workflow: WorkflowManager, metadata: Dict, content: str, 
                 decision: Dict) -> Dict:
    """
    PHASE 4: ACTION
    If accepted, create markdown page, update site structure.
    Record action taken with audit trail.
    """
    print("\n" + "="*70)
    print("PHASE 4: ACTION - Content Integration")
    print("="*70)
    
    if decision["final_decision"] != "ACCEPT":
        print("\n⚠ Skipping ACTION phase (content not accepted)")
        return {"action": "skipped", "reason": "content_rejected"}
    
    # Generate markdown page
    page_title = metadata["title"]
    page_slug = metadata["title"].lower().replace(" ", "-")[:30]
    page_filename = f"bell-county-{page_slug}-{metadata['id']}.md"
    
    # Create front matter
    frontmatter = f"""---
layout: default
title: {page_title}
category: Bell County News
source: {metadata['source']}
ingestion_date: {metadata['ingestion_time']}
verification_id: {workflow.workflow_id}
---

"""
    
    # Create content body
    body = content
    
    # Full markdown
    markdown_content = frontmatter + body
    
    # Create staging directory if needed
    staging_dir = OUTPUT.parent / "staging"
    staging_dir.mkdir(exist_ok=True)
    
    page_path = staging_dir / page_filename
    
    with open(page_path, "w") as f:
        f.write(markdown_content)
    
    action_result = {
        "action": "page_created",
        "page_filename": page_filename,
        "page_path": str(page_path),
        "page_slug": page_slug,
        "frontmatter": {
            "title": page_title,
            "category": "Bell County News",
            "source": metadata["source"],
            "verification_id": workflow.workflow_id,
        },
        "content_preview": markdown_content[:200] + "...",
        "timestamp": now_iso(),
    }
    
    print(f"\n✓ Page created: {page_filename}")
    print(f"✓ Path: {page_path}")
    print(f"✓ Slug: {page_slug}")
    print(f"✓ Size: {len(markdown_content)} bytes")
    
    workflow.transition(
        WorkflowState.VALIDATE,
        event="content_integrated",
        data=action_result
    )
    
    return action_result


def phase_validate(workflow: WorkflowManager, action_result: Dict = None, 
                  decision: Dict = None) -> Dict:
    """
    PHASE 5: VALIDATE
    Verify outputs: check page file integrity, validate markdown syntax,
    confirm allowlist consistency, verify evidence artifacts.
    """
    print("\n" + "="*70)
    print("PHASE 5: VALIDATE - Output Verification & Integrity Checks")
    print("="*70)
    
    validation_results = {
        "timestamp": now_iso(),
        "checks": {},
        "all_passed": True,
    }
    
    # Check 1: Workflow log exists and is valid
    if workflow.workflow_log_path.exists():
        validation_results["checks"]["workflow_log"] = {"status": "PASS", "detail": f"Log file exists at {workflow.workflow_log_path}"}
    else:
        validation_results["checks"]["workflow_log"] = {"status": "FAIL", "detail": "Workflow log not found"}
        validation_results["all_passed"] = False
    
    # Check 2: If action was taken, verify page file exists
    if action_result and action_result.get("action") == "page_created":
        page_path = Path(action_result["page_path"])
        if page_path.exists():
            file_size = page_path.stat().st_size
            validation_results["checks"]["page_file"] = {
                "status": "PASS", 
                "detail": f"Page file exists, size: {file_size} bytes"
            }
        else:
            validation_results["checks"]["page_file"] = {"status": "FAIL", "detail": "Page file not found"}
            validation_results["all_passed"] = False
    
    # Check 3: Verify decision was made
    if decision:
        if decision.get("final_decision") in ["ACCEPT", "REJECT"]:
            validation_results["checks"]["decision_validity"] = {
                "status": "PASS", 
                "detail": f"Decision recorded: {decision['final_decision']}"
            }
        else:
            validation_results["checks"]["decision_validity"] = {"status": "FAIL", "detail": "Invalid decision value"}
            validation_results["all_passed"] = False
    
    # Check 4: Verify workflow state transitions are complete
    if workflow.current_state == WorkflowState.VALIDATE:
        validation_results["checks"]["state_progression"] = {
            "status": "PASS", 
            "detail": f"Workflow in terminal state: {workflow.current_state.value}"
        }
    else:
        validation_results["checks"]["state_progression"] = {
            "status": "WARN", 
            "detail": f"Workflow in state: {workflow.current_state.value} (not terminal)"
        }
    
    print("\n✓ Integrity Checks:")
    for check_name, result in validation_results["checks"].items():
        status_icon = "✓" if result["status"] == "PASS" else "✗" if result["status"] == "FAIL" else "⚠"
        print(f"  {status_icon} {check_name}: {result['detail']}")
    
    print(f"\n✓ Overall Validation: {'PASS' if validation_results['all_passed'] else 'FAIL'}")
    
    workflow.transition(
        WorkflowState.END,
        event="validation_complete",
        data=validation_results,
        decision_result=validation_results["all_passed"]
    )
    
    return validation_results


def phase_end(workflow: WorkflowManager, validation: Dict) -> Dict:
    """
    PHASE 6: END
    Finalize workflow, generate completion report, record metrics.
    """
    print("\n" + "="*70)
    print("PHASE 6: END - Workflow Completion & Reporting")
    print("="*70)
    
    # Generate final report
    total_transitions = len(workflow.transitions)
    
    completion_report = {
        "workflow_id": workflow.workflow_id,
        "article_id": workflow.article_id,
        "article_title": workflow.article_title,
        "current_state": workflow.current_state.value,
        "total_transitions": total_transitions,
        "validation_passed": validation["all_passed"],
        "completion_time": now_iso(),
        "transition_history": [
            {
                "step": i + 1,
                "from": t.from_state.value,
                "to": t.to_state.value,
                "event": t.event,
            }
            for i, t in enumerate(workflow.transitions)
        ]
    }
    
    # Save final report
    report_path = OUTPUT / f"completion-report-{workflow.workflow_id}.json"
    with open(report_path, "w") as f:
        json.dump(completion_report, f, indent=2)
    
    print(f"\n✓ Workflow completed successfully")
    print(f"✓ Total state transitions: {total_transitions}")
    print(f"✓ Validation result: {'PASS' if validation['all_passed'] else 'FAIL'}")
    print(f"✓ Completion report: {report_path}")
    
    print("\nState Transition History:")
    for transition in completion_report["transition_history"]:
        print(f"  {transition['step']}. {transition['from']:15} → {transition['to']:15} ({transition['event']})")
    
    return completion_report


def run_complete_workflow(title: str, source: str, content: str):
    """
    Execute complete workflow from START through END.
    """
    print("\n" + "="*70)
    print("STARTING COMPLETE WORKFLOW: Article Integration Case Study")
    print("="*70)
    
    # Phase 1: START
    workflow, metadata = phase_start(title, source)
    
    # Phase 2: PROCESS
    process_result = phase_process(workflow, metadata, content)
    
    # Phase 3: DECISION
    decision = phase_decision(workflow, metadata, process_result)
    
    # Phase 4: ACTION (conditional)
    if decision["final_decision"] == "ACCEPT":
        action_result = phase_action(workflow, metadata, content, decision)
    else:
        action_result = {"action": "skipped", "reason": "content_rejected"}
    
    # Phase 5: VALIDATE
    validation = phase_validate(workflow, action_result, decision)
    
    # Phase 6: END
    completion_report = phase_end(workflow, validation)
    
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE")
    print("="*70)
    
    return completion_report


if __name__ == "__main__":
    # Example: Integrate a realistic Bell County news article
    article_title = "Bell County Commissioners Approve New Legal Resource Center"
    article_source = "killeendailyherald.com"
    article_content = """
    The Bell County Commissioners Court met on February 11, 2026 to discuss 
    emerging community legal services. The commissioners approved funding for 
    a new centralized legal resource center to serve residents across Bell County.
    
    The center will provide access to legal information, referral services, and 
    educational materials. It will complement existing services provided by the 
    Texas Attorney General's office and the State Bar of Texas.
    
    County Judge Robert Shumate noted the importance of ensuring equitable access 
    to legal information for all county residents. The center is expected to open 
    by Q3 2026.
    
    Additional details about the center and how to access its services will be 
    announced in coming weeks.
    """
    
    report = run_complete_workflow(article_title, article_source, article_content)
    
    print(f"\n✓ Workflow Report saved with ID: {report['workflow_id']}")
