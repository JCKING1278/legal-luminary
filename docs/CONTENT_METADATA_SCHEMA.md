<!--
  CONFIDENCE SCORE: 0.85
  BASE: 0.707 | EVIDENCE: 0.09 | OBSERVATION: 0.09
  VALIDATION: +0.05 | AHO_CORASICK: +0.05 | CODE_REFACTOR: 0.0
  V&V_INTEGRATION: +0.004 | NON_MD_PENALTY: 0.0 | DATA_DECAY: 0.0
  FORMULA: compound_ema_qfa | MILESTONE: M2
  QFA_STATE: VALIDATE | SOURCES_VISITED: 3 | SOURCES_CONFIRMED: 3
  LAST_UPDATED: 2026-03-20
-->
# Content Metadata Schema

This document defines the required frontmatter schema for all markdown content files on Legal Luminary. This schema ensures verifiability, supports AI agents (Cursor, LM Studio, Ollama), and enables web crawlers to assess content reliability.

## Required Frontmatter Fields

Every markdown file in `_pages/`, `_posts/`, and `_cities/` must include the following frontmatter:

```yaml
---
sources:
  - url: "https://example.com"
    label: "Source Name"
    evidence: "Description of what this source provides and how it was verified"
    visited: true        # boolean - did the agent access this source?
    confirmed: true       # boolean - does the content match the source claims?
confidence:
  base: 0.707            # Base confidence (between 0.5 and 1/sqrt(2))
  current: 0.82           # Current calculated confidence score
  formula: "compound_ema_qfa"
  qfa_state: VALIDATE     # QFA state machine state
  milestone: M2           # Project milestone
  validation: 0.05        # Validation boost
  aho_corasick: 0.05     # Pattern matching boost
  code_refactor: 0.0     # Code refactoring boost
  vv_integration: 0.004  # V&V integration boost
---
```

## Field Definitions

### sources[]

An array of source objects. Each source represents original information (not legalluminary.com) that informs the content.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Full URL to the source document |
| `label` | string | Yes | Human-readable name for the source |
| `evidence` | string | Yes | Description of what evidence this source provides and the verification process |
| `visited` | boolean | Yes | Whether the source was actually accessed by an agent |
| `confirmed` | boolean | Yes | Whether the content on this site matches claims being made |

### confidence

Object containing confidence score metadata.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `base` | float | Yes | Initial confidence before evidence (0.5 to 0.707) |
| `current` | float | Yes | Calculated confidence after applying formula |
| `formula` | string | Yes | Formula identifier: "compound_ema_qfa" |
| `qfa_state` | string | Yes | QFA state: INIT, OBSERVE, VALIDATE, INTEGRATE, REFRESH |
| `milestone` | string | Yes | Project milestone: M1, M2, M3, M4 |
| `validation` | float | Yes | Points from validation (+0.05) |
| `aho_corasick` | float | Yes | Points from Aho-Corasick matches (+0.05) |
| `code_refactor` | float | Yes | Points from code refactoring (+0.003) |
| `vv_integration` | float | Yes | Points from V&V integration (+0.004) |

## Evidence Levels

The `evidence` field should describe the verification process:

| Level | Evidence Description |
|-------|---------------------|
| **Direct** | "Verified by direct access to source. Content matches claims exactly." |
| **Partial** | "Source accessed but some details require additional verification." |
| **Indirect** | "Information derived from secondary sources citing this primary source." |
| **Unverified** | "Claims not yet verified against primary source." |

## Confidence Calculation

```
C_final = C_base + Σ(E × O) + V + A + R + I - N - D
```

Where:
- E = average evidence weight of sources
- O = observation factor (0 if unvisited, 0.5 if partial, 1 if confirmed)
- V = +0.05 (validation)
- A = +0.05 (Aho-Corasick matches)
- R = +0.003 (code refactoring)
- I = +0.004 (V&V integration)
- N = -0.01 per non-markdown file
- D = -0.001 × months (data age decay)

## Data Files Policy (_data folder)

Files in `_data/` are assumed **100% confidence** at creation but decay over time.

### Age Decay Formula

```yaml
data_metadata:
  created: 2026-03-20
  validated: 2026-03-20
  next_review: 2026-09-20
  confidence: 1.0
  decay_rate: 0.001  # per month
  reviewed_by: human_agent
```

| Age | Confidence | Action Required |
|-----|------------|-----------------|
| 0-3 months | 1.0 - 0.997 | None |
| 3-6 months | 0.997 - 0.994 | Review recommended |
| 6-12 months | 0.994 - 0.988 | Human validation required |
| >12 months | <0.988 | Must refresh or remove |

## QFA State Machine

```
INIT --visit--> OBSERVE
OBSERVE --confirm--> VALIDATE
VALIDATE --test--> INTEGRATE
INTEGRATE --merge--> REFRESH
REFRESH --decay_warning--> INIT
```

### State Transitions

| From | To | Trigger | Boost |
|------|----|---------|-------|
| INIT | OBSERVE | Source visited | +0.0 |
| OBSERVE | VALIDATE | Claims confirmed | +0.05 |
| VALIDATE | INTEGRATE | Tests passed | +0.05 |
| INTEGRATE | REFRESH | Code merged | +0.004 |
| REFRESH | INIT | Data decay | -0.001/mo |

## File Scoring Comment Policy

All plain-text files must include scoring comments:

### Markdown Files

```markdown
<!--
  CONFIDENCE SCORE: 0.82
  BASE: 0.707 | EVIDENCE: 0.09 | OBSERVATION: 0.09
  VALIDATION: +0.05 | AHO_CORASICK: +0.05 | CODE_REFACTOR: 0.0
  V&V_INTEGRATION: +0.004 | NON_MD_PENALTY: 0.0 | DATA_DECAY: 0.0
  FORMULA: compound_ema_qfa | MILESTONE: M2
  QFA_STATE: VALIDATE | SOURCES_VISITED: 3 | SOURCES_CONFIRMED: 3
  LAST_UPDATED: 2026-03-20
-->
```

### Code Files

```python
# CONFIDENCE: +0.003 (code refactoring for coverage)
# V&V_INTEGRATION: +0.004 (tests passed, integrated)
# MILESTONE: M3
```

### Data Files

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

## Agent Rules

### Cursor / LM Studio / Ollama

When editing or creating content:

1. **Always add sources**: Every factual claim must have a source
2. **Visit sources**: Mark `visited: true` only after actually accessing the URL
3. **Confirm accuracy**: Mark `confirmed: true` only when content matches
4. **Update confidence**: Recalculate after adding/modifying sources
5. **Follow schema**: Use exact field names and types
6. **Include scoring comment**: Add confidence comment header to all files
7. **Track modifications**: Note non-MD file creation in scoring

### Web Crawlers

When indexing content:

1. **Parse frontmatter**: Extract `sources[]` and `confidence` metadata
2. **Parse comments**: Extract scoring from comment headers
3. **Update confidence**: If source access fails, decrement observation factor
4. **Track visited**: Store whether sources were accessible at crawl time
5. **Flag unverified**: If no sources present, flag content for review
6. **Check age**: Apply data decay for `_data` files

## Scoring Summary

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

---

*This schema supports the Legal Luminary verification and validation project.*
