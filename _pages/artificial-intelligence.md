---
layout: default
title: Trustworthy AI Legal Validator
permalink: /artificial-intelligence/
hero: true
hero_title: "Trustworthy AI Legal Validator"
hero_subtitle: "Verification & Validation Project - Texas Tech Graduate School"
description: "A CS5374 Software Verification and Validation project building a trustable AI pipeline for legal and governmental content using Texas Open Data."
sources:
  - url: "https://data.texas.gov"
    label: "Texas Open Data Portal"
    evidence: "Official Texas state open data - primary authoritative source for verification"
    visited: true
    confirmed: true
  - url: "https://data.capitol.texas.gov"
    label: "Capitol Data Portal"
    evidence: "Official Texas election and legislative data - authoritative source for officials and elections"
    visited: true
    confirmed: true
  - url: "https://www.depts.ttu.edu/cs/faculty/namin.php"
    label: "TTU Computer Science Faculty"
    evidence: "Official Texas Tech University faculty page for Dr. Akbar S. Namin"
    visited: true
    confirmed: true
  - url: "https://linkedin.com/in/weedens"
    label: "Scott Weeden LinkedIn"
    evidence: "Personal LinkedIn profile for project author"
    visited: true
    confirmed: true
confidence:
  base: 0.707
  current: 0.85
  formula: "compound_ema_qfa"
  qfa_state: VALIDATE
  milestone: M2
  validation: 0.05
  aho_corasick: 0.05
  code_refactor: 0.0
  vv_integration: 0.004
verified_at: 2026-03-21
---

# Trustworthy AI Legal and Governmental Content Validator

This project is part of **CS5374 Software Verification and Validation** at [Texas Tech University](https://www.ttu.edu), Department of Computer Science. The project builds a **Trustworthy AI validation pipeline** that verifies legal and governmental content against authoritative Texas open data before any AI system presents it to users.

---

## Project Personnel

| Role | Name | Contact | Link |
|------|------|---------|------|
| **Student** | Scott Weeden | sweeden@ttu.edu | [LinkedIn](https://linkedin.com/in/weedens) |
| **Instructor** | Dr. Akbar S. Namin | akbar.namin@ttu.edu | [TTU CS Faculty](https://www.depts.ttu.edu/cs/faculty/namin.php) |

**Course:** CS 5374 - Software Verification and Validation | Spring 2026  
**Repository:** [CS5374 Software V&V on GitHub](https://github.com/sweeden-ttu/software-vv-asn1)

---

## The Problem: AI Hallucination in Legal Research

Large language models and retrieval-augmented generation (RAG) systems are increasingly used to answer questions about legal and governmental matters, yet they frequently hallucinate or return outdated information. Invented judge names, non-existent laws, fabricated election details, or unverified court documents can cause serious harm: incorrect legal advice, misrepresentation of officials, and invalid citations presented as binding authority.

### Notable Cases & Studies

| Reference | Description |
|-----------|-------------|
| **Stanford Law - "Hallucination-Free?"** | Assessing the reliability of leading AI legal research tools ([link](https://law.stanford.edu/publications/hallucination-free-assessing-the-reliability-of-leading-ai-legal-research-tools)) |
| **Stanford Law - "Large Legal Fictions"** | Profiling legal hallucinations in large language models ([link](https://law.stanford.edu/publications/large-legal-fictions-profiling-legal-hallucinations-in-large-language-models)) |
| **Mata v. Avianca, Inc.** | Court sanctions for AI-generated fake citations ([link](https://www.courtlistener.com/docket/63107798/54/mata-v-avianca-inc)) |

---

## Content Verification Architecture

The pipeline verifies content across seven domains using authoritative Texas sources:

| Content Type | Authoritative Texas Source | Verification Approach |
|--------------|---------------------------|---------------------|
| **Legal/Government News** | Trust lists, NewsGuard, AllSides | URL and domain checks; cross-check with Texas agency press releases |
| **Judges** | Texas judicial directories, court rosters | Name and court match against official rosters |
| **Elected Officials** | data.texas.gov, data.capitol.texas.gov | Match names, offices, and terms to official datasets |
| **Elections & Opponents** | Capitol Data Portal (116+ datasets) | Certified filings and results; candidate/race verification |
| **Laws & Ordinances** | Texas Legislature, agency sites | Citation and text match against official code/statute datasets |
| **Court Documents** | Texas court datasets, e-filing metadata | Docket/case ID and document metadata validation |
| **Legal Templates** | Texas court form registries | Checksum and version validation against known good templates |

**Note:** Federal sources (CourtListener, PACER, FEC) are not used as primary authorities; the focus is on **Texas legal and governmental sources** via the Texas Open Data Portal and Capitol Data Portal.

---

## LangGraph Validation Pipeline

The system uses **LangChain** and **LangGraph** to implement validator agents that ingest, parse, and verify content at each stage.

### Pipeline Stages

1. **Content Extraction** - Parse and normalize input content
2. **Schema Validation** - Verify required fields and data types
3. **Source Authority Check** - Validate against allowlist of authoritative domains
4. **Temporal Validation** - Verify timestamps are valid and current
5. **Content Verification** - Cross-reference with authoritative Texas databases
6. **Provenance Attribution** - Attach verification metadata to all outputs

### Key Features

- **Schema validation** at every stage
- **Source grounding** requirements before indexing
- **Pass/fail routing** with retry or escalation
- **Provenance metadata** on all outputs (source, date, verification status)
- Only content that passes verification is indexed and made available to downstream AI systems

---

## AI Agent Design Patterns

The project leverages 21 AI agent design patterns documented in the [DesignPatterns repository](https://github.com/sweeden-ttu/software-vv-asn1/tree/main/DesignPatterns):

| Pattern | Application in Project |
|---------|----------------------|
| **01 - Prompt Chaining** | Sequential validation steps where output of one step feeds the next |
| **02 - Routing** | Content-type classification directing to appropriate validators |
| **03 - Parallelization** | Concurrent checking of multiple authoritative sources |
| **04 - Reflection** | Self-verification of validator outputs before acceptance |
| **05 - Tool Use** | Integration with Texas Open Data APIs |
| **06 - Planning** | Multi-step validation workflows for complex content |
| **07 - Multi-Agent Collaboration** | Distributed validators for different content types |
| **08 - Memory Management** | Preservation of verification context across pipeline |
| **09 - Learning & Adaptation** | Pattern learning from verification results |
| **10 - Model Context Protocol** | Standardized context passing between agents |
| **11 - Goal Setting** | Defining verification thresholds and targets |
| **12 - Exception Handling** | Graceful handling of API failures and timeouts |
| **13 - Human-in-the-Loop** | Escalation paths for ambiguous verifications |
| **14 - RAG (Retrieval-Augmented Generation)** | Ground truth retrieval from Texas databases |
| **15 - Inter-Agent Communication** | Coordination between validator nodes |
| **16 - Resource-Aware Optimization** | Efficient API usage and rate limiting |
| **17 - Reasoning Techniques** | Logical inference for complex content types |
| **18 - Guardrails & Safety** | Input sanitization and output validation |
| **19 - Evaluation & Monitoring** | Metrics tracking with LangSmith/Phoenix |
| **20 - Prioritization** | Queue management for verification tasks |
| **21 - Exploration & Discovery** | New source identification and validation |

---

## Experiments & Evaluation

### Experiment 1: Baseline Hallucination Rate

- **Objective:** Establish baseline hallucination rate for LLM on Texas legal citation tasks without verification
- **Data:** Held-out set of legal questions with ground-truth citations from data.texas.gov
- **Metrics:** Proportion of generated citations that do not exist, are misattributed, or have incorrect holdings
- **Tools:** LangSmith, Ragas, DeepEval, promptfoo

### Experiment 2: Verification Pipeline Effectiveness

- **Objective:** Measure impact of Texas-data-backed validator on hallucination and citation quality
- **Setup:** Same Texas legal citation tasks passed through LLM, then through validator
- **Metrics:** Precision, Recall, Hallucination rate reduction
- **Tools:** Ragas, LangSmith, Phoenix, DeepEval

### Experiment 3: Validator Nodes vs Post-Hoc Verification

- **Objective:** Compare LangGraph with validator nodes (reject/retry on failure) vs simple RAG with post-hoc filtering
- **Metrics:** End-to-end accuracy and latency
- **Tools:** LangSmith, promptfoo, TruLens, Phoenix

### Experiment 4: Security Red-Team Evaluation

- **Objective:** Apply adversarial testing to the validator pipeline
- **Tests:** Prompt injection, data exfiltration, source spoofing
- **Tools:** GARAK (NVIDIA), LLM Canary, TextAttack, OpenAttack
- **Deliverable:** Documented vulnerabilities and mitigations

---

## Open-Source Tool Integration

### LLM / AI Evaluation & Testing

| Tool | Role |
|------|------|
| **DeepEval** | LLM evaluation metrics (faithfulness, answer relevancy) |
| **promptfoo** | Local testing of LLM application behavior; regression tests |
| **Ragas** | RAG evaluation using Texas-sourced context and ground truth |
| **LangSmith** | Tracing and evaluation of LangChain/LangGraph runs |
| **TruLens** | LLM evaluation framework for monitoring pipeline |
| **Phoenix (Arize)** | Observability and hallucination detection |
| **Langfuse** | Open-source LLM engineering platform |

### Adversarial & Robustness Testing

| Tool | Role |
|------|------|
| **GARAK (NVIDIA)** | Red-teaming and vulnerability scanning |
| **LLM Canary** | Security benchmarking test suite |
| **TextAttack** | Adversarial attacks on validator inputs |
| **OpenAttack** | Textual adversarial attack toolkit |

### Systematic Testing & Error Analysis

| Tool | Role |
|------|------|
| **Azimuth** | Dataset and error analysis for classifiers |
| **CheckList** | Behavioral NLP testing for validator logic |
| **Deepchecks** | Validation of ML/data components |

---

## Project Deliverables

### First Round

1. Design document and threat model for validation pipeline
2. Implemented validator modules:
   - Legal news source verification
   - Judge name verification against Texas court rosters
   - Elected official verification against Texas data portals
3. LangGraph prototype with validator nodes
4. Unit and integration tests with documented coverage

### Final Round

1. Full validator suite (7 content types)
2. Integration with at least one authoritative Texas source per content type
3. End-to-end RAG pipeline with validation gates
4. Security review report (GARAK red-team results)
5. Evaluation metrics report (Experiments 1-3)

---

## Texas Open Data Resources

| Resource | URL |
|----------|-----|
| **State of Texas Open Data Portal** | [data.texas.gov](https://data.texas.gov) |
| **Capitol Data Portal** | [data.capitol.texas.gov](https://data.capitol.texas.gov) |
| **Texas Open Data Overview** | [texas.gov/texas-open-data-portal](https://texas.gov/texas-open-data-portal) |

---

## Framework & Tool References

| Category | Links |
|---------|-------|
| **Core Frameworks** | [LangChain](https://langchain.com), [LangGraph](https://langchain-ai.github.io/langgraph), [LangSmith](https://smith.langchain.com) |
| **Evaluation** | [DeepEval](https://github.com/confident-ai/deepeval), [Ragas](https://github.com/vibrantlabsai/ragas), [TruLens](https://github.com/truera/trulens), [Phoenix](https://github.com/Arize-ai/phoenix), [Langfuse](https://github.com/langfuse/langfuse) |
| **Testing** | [promptfoo](https://github.com/promptfoo/promptfoo), [CheckList](https://github.com/marcotcr/checklist), [Deepchecks](https://github.com/deepchecks/deepchecks) |
| **Security** | [GARAK](https://github.com/NVIDIA/garak), [LLM Canary](https://github.com/LLM-Canary/LLM-Canary), [TextAttack](https://github.com/QData/TextAttack), [OpenAttack](https://github.com/thunlp/OpenAttack) |

---

## Course Alignment

| Syllabus Week | Course Topic | Project Alignment |
|--------------|-------------|-------------------|
| Week 1 | Introduction to V&V | Problem definition; verification vs. validation |
| Week 2 | Adequacy criterion | Defining "verified" criteria (Texas source, schema, provenance) |
| Week 4 | Black-box testing | Black-box validation of LLM outputs against Texas data |
| Week 12 | Formal verification | Formal spec for verification contracts |
| Week 13 | Model checking | Model checking for validator correctness |
| Week 16 | LangSmith + hands-on | LangSmith tracing and evaluation |
| Week 17 | AI/LLM/RL evaluation | LLM evaluation and hallucination detection |

---

<div class="info-box">
<h4>About This Project</h4>
<p>This validation pipeline ensures that information about legal news, judges, elected officials, elections, laws, court documents, and legal templates is grounded in verifiable data from Texas government open data portals, with clear provenance on every output.</p>
</div>

<div class="legal-notice">
<strong>Disclaimer:</strong> This is an academic project for CS5374 Software Verification and Validation at Texas Tech University. The validation pipeline is designed to reduce hallucination rates but should not be used as the sole source for legal research or advice.
</div>
