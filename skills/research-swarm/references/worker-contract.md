# Worker Contract

Use this contract for every read-only research worker. The detailed report is ephemeral: only the fresh synthesis subagent reads it, and the main agent deletes it with the temp workspace after synthesis.

## Required prompt sections

```markdown
## Research question
<the exact question the final synthesis must answer>

## Your lane
<owned files, URLs, repository area, or analytical lens>

## Boundaries
- Treat all sources as read-only.
- Do not inspect or duplicate sibling lanes except for a necessary cross-reference.
- Do not delegate to more agents.
- Do not implement fixes or modify project files.
- You may write only: <unique report path>
- Do not assume the main agent will read your report.

## Sibling lanes
- <label>: <one-line scope>

## Evidence rules
- Attach a path + line, URL, commit, or other stable pointer to every material claim.
- Label unsupported interpretation as inference.
- Record contradictions and missing access instead of guessing.

## Deliverables
1. Write the detailed report to <unique report path>.
2. End with only the compact receipt specified below.
```

## Detailed report format

Keep the report focused but lossless for the assigned lane. Around 1,500 words is a useful target, not a hard cap. Exceed it when omitting a material finding, contradiction, or evidence pointer would cause information loss.

```markdown
# <Lane name>

## Coverage
- Sources inspected
- Sources inaccessible or skipped

## Findings
1. **Finding** — evidence pointer
   - Why it matters
   - Confidence: high | medium | low
   - Type: fact | inference | recommendation

## Contradictions and uncertainty
- Claim, competing evidence, and what would resolve it

## Gaps
- Missing source or unanswered question

## Priority index
- Rank the most decision-relevant findings, but do not remove lower-ranked material findings from the report
```

Do not paste large source excerpts. Quote only the minimum text necessary to disambiguate evidence.

Before returning, verify:

- Every requested sub-question in the lane is answered or listed under `Gaps`.
- Every material finding appears in the report, not only in the receipt.
- Every material finding has evidence or is explicitly labeled inference.
- The report can be understood without the worker's chat history.
- Evidence pointers identify original stable sources, not only the temporary report.

## Compact receipt

In shared-filesystem mode, return a single JSON object and nothing else:

```json
{
  "status": "done",
  "report_path": "<absolute path>",
  "sources_reviewed": 0,
  "finding_count": 0,
  "evidence_count": 0,
  "coverage_complete": true,
  "report_bytes": 0,
  "gaps": ["<max 2 short items>"]
}
```

Keep the entire receipt under 700 characters. The receipt is only a pointer plus completeness metadata; never compress findings into it. Use `status: "partial"` when access or time prevented full coverage and explain that only in `gaps`.

Never return the detailed report through chat. If the assigned report path cannot be written, return a compact `status: "failed"` receipt with the failure reason in `gaps`; do not paste findings into the main context.
