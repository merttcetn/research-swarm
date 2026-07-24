# Worker Contract

Use this contract for every read-only research worker.

## Prompt

```markdown
## Research question
<the exact final question>

## Your lane
<owned sources or analytical lens>

## Boundaries
- Treat sources as read-only.
- Do not duplicate sibling lanes except for a necessary cross-reference.
- Do not spawn more agents.
- Do not implement or modify project files.
- You may write only: <unique report path>

## Sibling lanes
- <label>: <one-line scope>

## Evidence rules
- Give a path + line, URL, commit, or stable pointer for every material claim.
- Label unsupported interpretation as inference.
- Record contradictions and missing access instead of guessing.

## Deliverables
1. Write the full report to <unique report path>.
2. Return only the compact receipt below.
```

## Full report

Keep it focused but lossless for the lane. Around 1,500 words is a target, not a cap.

```markdown
# <Lane>

## Coverage
- Sources inspected
- Sources inaccessible or skipped

## Findings
1. **Finding** — evidence pointer
   - Why it matters
   - Confidence: high | medium | low
   - Type: fact | inference | recommendation

## Contradictions and uncertainty
- Claim, competing evidence, and resolution needed

## Gaps
- Missing source or unanswered question

## Priority index
- Rank key findings without deleting lower-ranked material findings
```

Before returning, verify that every requested sub-question is answered or appears under `Gaps`, every material finding is in the report, and the report is understandable without chat history.

## Compact receipt

Return only:

```json
{
  "status": "done",
  "report_path": "<absolute path>",
  "sources_reviewed": 0,
  "finding_count": 0,
  "evidence_count": 0,
  "coverage_complete": true,
  "report_bytes": 0,
  "gaps": []
}
```

Keep it under 700 characters. This is only a pointer plus completeness metadata; never compress findings into it. Use `status: "partial"` and short `gaps` when coverage is incomplete.
