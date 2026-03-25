# Candidate Headshot Integrity Incident (P0)

## Severity
- Priority: P0 (highest)
- Scope: Cross-project
- Status: Open

## Problem
- Candidate cards can display incorrect headshots (including incumbent photos reused for challengers/non-incumbents).
- This causes identity misrepresentation and data-provenance failures.

## Required Resolution Criteria
- Every candidate headshot must map to the correct person.
- No non-incumbent may share the same `headshot_url` as the incumbent in the same office group.
- Every headshot must include source provenance: URL, retrieval timestamp, and usage locations.
- Placeholder/mocked images must be removed or explicitly documented as unresolved blockers.

## Agent Policy
- All agents treat this incident as highest-priority tasking until closed.
