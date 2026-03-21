# Confidence Score Mathematical Definition

This document defines the reinforcing confidence score formula used by Legal Luminary for evaluating AI agent outputs, web crawler findings, and content verification.

## Overview

Confidence scores are calculated using a **compounding summation formula** that:
1. Starts with a base confidence between 0.5 and 1/√2
2. Iteratively incorporates evidence (E) and observation (O) factors
3. Each calculation depends on the previous confidence state (reinforcing)
4. Converges toward maximum confidence as evidence accumulates
5. Penalizes non-content file creation
6. Rewards validated code contributions

## Base Parameters

| Parameter | Symbol | Value/Range | Description |
|-----------|--------|-------------|-------------|
| Minimum base | C_min | 0.5 | Floor confidence for unverified claims |
| Maximum base | C_max | 1/√2 ≈ 0.707 | Upper confidence before evidence |
| Learning rate | α | 0.1 - 0.3 | How much new evidence affects confidence |
| Decay factor | δ | 0.05 - 0.15 | Prevents overconfidence, promotes convergence |

## Reinforcement Modifiers

| Modifier | Symbol | Delta | Description |
|----------|--------|-------|-------------|
| Validation | V | +0.05 | When verification has been validated |
| Aho-Corasick Match | A | +0.05 | When Aho-Corasick automaton finds matches |
| Code Refactoring | R | +0.003 | Updating/refactoring code for coverage |
| V&V Integration | I | +0.004 | After V&V testing and integration |
| Non-MD File Creation | N | -0.01 | Creating non-markdown files |
| Data Age Decay | D | -0.001/mo | _data files lose confidence over time |

## Primary Formula: Compounding Confidence

```
C_n = C_{n-1} + α × E_n × O_n × (C_max - C_{n-1}) - δ × (C_{n-1} - C_min) + V + A + R + I - N - D
```

### Simplified Form (without modifiers)

When δ = α/2 and E_n × O_n = 1:

```
C_n = C_{n-1} × (1 - α/2) + α/2 × C_max
```

## Full Reinforcement Formula

```
C_final = C_base + Σ(evidence_observations) + V + A + R + I - N - D
```

### Components

| Component | Formula | Range |
|-----------|---------|-------|
| Base | C_base ∈ [0.5, 0.707] | Initial confidence |
| Evidence Sum | Σ(E × O) | Compounding evidence |
| Validation | V = 0.05 if validated | +0.05 |
| Aho-Corasick | A = 0.05 if matches | +0.05 |
| Code Refactor | R = 0.003 per file | +0.003 |
| V&V Integration | I = 0.004 after test | +0.004 |
| Non-MD Penalty | N = 0.01 per file | -0.01 |
| Data Decay | D = 0.001 × months | -0.001/mo |

## Quantum Finite Automata (QFA) Integration

QFA generates reinforcement rules based on project milestones and objectives. Rules are defined as:

```
Rule = (State, Symbol) → (NewState, ConfidenceModifier)
```

### QFA States

| State | Description | Exit Confidence |
|-------|-------------|----------------|
| INIT | Initial verification | +0.0 |
| OBSERVE | Source observed | +0.05 |
| VALIDATE | Validation passed | +0.05 |
| INTEGRATE | V&V complete | +0.004 |
| REFRESH | Data refreshed | +0.01 |

### QFA Transitions

```
INIT --visit--> OBSERVE
OBSERVE --confirm--> VALIDATE
VALIDATE --test--> INTEGRATE
INTEGRATE --merge--> REFRESH
REFRESH --decay_warning--> INIT
```

## Aho-Corasick Pattern Matching Integration

The Aho-Corasick automaton provides **reinforcing confidence through pattern detection**. When the automaton finds milestone-aligned patterns in files, it increases confidence based on:

1. **Unique pattern matches** (each pattern contributes once per file)
2. **Milestone alignment** (patterns contribute to specific project milestones)
3. **Category coverage** (multiple categories found increase confidence)

### Pattern Categories

| Category | Milestone | Example Patterns |
|----------|-----------|------------------|
| structure | M1_INIT | `---`, `layout:`, `permalink:` |
| metadata | M1_INIT | `title:`, `description:` |
| format | M1_INIT | `# `, `| `, table rows |
| verification | M2_VERIFY | `sources:`, `evidence:`, `visited:` |
| source | M2_VERIFY | `bellcountytx.com`, `capitol.texas.gov` |
| qfa | M2_VERIFY | `QFA_STATE:`, `AHO_CORASICK:` |
| content | M2_VERIFY | `Fort Cavazos`, `Fort Hood` |
| code | M3_COVERAGE | `def `, `class `, `import ` |
| testing | M3_COVERAGE | `test`, `pytest`, `assert ` |
| coverage | M3_COVERAGE | `coverage`, `_test.py` |
| quality | M3_COVERAGE | `validate` |
| tracking | M4_VV | `MILESTONE:`, `LAST_UPDATED:` |
| process | M4_VV | `next_review:`, `decay_rate:` |

### Aho-Corasick Confidence Formula

```
A_boost = Σ(unique_pattern_matches × pattern_weight)
```

### Milestone Bonus Thresholds

When milestone contributions exceed thresholds, additional bonuses apply:

| Milestone | Threshold | Bonus |
|-----------|-----------|-------|
| M2_VERIFY | ≥0.10 | +0.05 |
| M4_VV | ≥0.05 | +0.04 |

### Final Aho-Corasick Enhanced Confidence

```
C_final = min(1.0, C_base + A_boost + milestone_bonus)
```

## Data Files Policy (_data folder)

Files in `_data/` are assumed **100% confidence** at creation.

### Age Decay Formula

```
C_data = 1.0 - (0.001 × months_since_validation)
```

| Age | Confidence | Action Required |
|-----|------------|-----------------|
| 0-3 months | 1.0 - 0.997 | None |
| 3-6 months | 0.997 - 0.994 | Review recommended |
| 6-12 months | 0.994 - 0.988 | Human validation required |
| >12 months | <0.988 | Must refresh or remove |

### Data Refresh Trigger

```yaml
# Required frontmatter for _data files
data_metadata:
  created: 2026-03-20
  validated: 2026-03-20
  next_review: 2026-09-20
  confidence: 1.0
  reviewed_by: human_agent
```

## File Type Scoring Policy

### Plain-Text MIME Types (.md, .txt, .yml, .yaml, .json, .csv)

Include scoring comment header:

```markdown
<!--
  CONFIDENCE SCORE: 0.82
  BASE: 0.707 | EVIDENCE: 0.08 | OBSERVATION: 0.05
  VALIDATION: +0.05 | AHO_CORASICK: +0.05 | CODE_REFACTOR: 0.0
  V&V_INTEGRATION: +0.004 | NON_MD_PENALTY: 0.0 | DATA_DECAY: 0.0
  FORMULA: compound_ema_qfa | MILESTONE: M2
  LAST_UPDATED: 2026-03-20
-->
```

### Code Files (.py, .js, .ts, .rb, .sh)

Include scoring comment:

```python
# CONFIDENCE: +0.003 (code refactoring for coverage)
# V&V_INTEGRATION: +0.004 (tests passed)
# MILESTONE: M3
```

### Data Files (.json, .csv in _data/)

Include scoring comment:

```json
{
  "_confidence": {
    "score": 0.997,
    "created": "2026-03-20",
    "next_review": "2026-09-20",
    "decay_rate": 0.001,
    "human_validated": true
  }
}
```

## Milestone Integration

| Milestone | QFA State | Confidence Boost |
|-----------|-----------|-----------------|
| M1: Project Init | INIT | +0.10 |
| M2: Source Verification | VALIDATE | +0.15 |
| M3: Code Coverage | INTEGRATE | +0.18 |
| M4: V&V Testing | REFRESH | +0.20 |

## Implementation Example

```python
class ConfidenceScorer:
    C_MIN = 0.5
    C_MAX = 1 / 2**0.5  # ~0.707
    
    def __init__(self, base: float = None):
        self.confidence = base or self.C_MIN
    
    def add_evidence(self, evidence: float, observation: float, 
                     alpha: float = 0.2, delta: float = 0.1):
        increase = alpha * evidence * observation * (self.C_MAX - self.confidence)
        decrease = delta * (self.confidence - self.C_MIN)
        self.confidence += increase - decrease
    
    def apply_modifiers(self, validation: bool = False,
                       aho_corasick: bool = False,
                       code_refactor: float = 0.0,
                       vv_integration: bool = False,
                       non_md_penalty: float = 0.0,
                       data_decay: float = 0.0):
        self.confidence += 0.05 if validation else 0.0
        self.confidence += 0.05 if aho_corasick else 0.0
        self.confidence += code_refactor
        self.confidence += 0.004 if vv_integration else 0.0
        self.confidence -= non_md_penalty
        self.confidence -= data_decay
        return max(0.0, min(1.0, self.confidence))
    
    def qfa_transition(self, state: str, symbol: str) -> tuple:
        transitions = {
            ('INIT', 'visit'): ('OBSERVE', 0.05),
            ('OBSERVE', 'confirm'): ('VALIDATE', 0.05),
            ('VALIDATE', 'test'): ('INTEGRATE', 0.004),
            ('INTEGRATE', 'merge'): ('REFRESH', 0.0),
        }
        return transitions.get((state, symbol), (state, 0.0))
```

## Scoring Summary Table

| Action | Points | Applies To |
|--------|--------|------------|
| Base confidence | 0.5 - 0.707 | All files |
| Evidence observation | +0.01 - 0.05 | Per source |
| Validation passed | +0.05 | Verified content |
| Aho-Corasick match | +0.05 | Pattern matching |
| Code refactoring | +0.003 | Per file |
| V&V integration | +0.004 | After testing |
| Non-MD creation | -0.01 | New files |
| Data age decay | -0.001/mo | _data files |

## Project Milestones

- **M1**: Project initialization and structure
- **M2**: Source verification and content validation  
- **M3**: Code coverage and testing infrastructure
- **M4**: Full V&V and deployment

---

*This schema supports the Legal Luminary verification and validation project.*
