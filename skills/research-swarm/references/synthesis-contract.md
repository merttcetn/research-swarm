# Synthesis Contract

Use this contract for the one fresh synthesis subagent. Its final response becomes the main agent's sole detailed research state after the temp worker reports are deleted.

## Required prompt sections

```markdown
## User question
<original question and requested output shape>

## Worker reports
- <absolute worker report path>
- <absolute worker report path>

## Receipt totals
- expected_reports: <count>
- completed_reports: <count>
- worker_findings: <sum>
- worker_evidence_pointers: <sum>

## Known gaps
- <failed, partial, or inaccessible lane>

## Boundaries
- Read every available worker report before synthesizing.
- Open raw sources only for targeted verification of decisive evidence, unresolved contradictions, or a critical gap.
- Do not redo the workers' full research.
- Do not modify sources or project files.
- Do not write a synthesis file or any other artifact.
- Return the complete synthesis directly as your final response.
```

## Synthesis procedure

1. Confirm expected, available, and partial worker reports.
2. Read every available report.
3. Normalize semantically equivalent findings without treating repetition as corroboration.
4. Rank findings by relevance to the user question.
5. Preserve meaningful disagreement and identify what would resolve it.
6. Distinguish:
   - **Established:** directly supported by evidence.
   - **Inferred:** reasoned from evidence but not explicitly established.
   - **Recommended:** a proposed next action.
7. Verify only the evidence necessary for decisive claims or unresolved contradictions.
8. Account for every material worker finding as represented, deliberately merged, or deliberately excluded with a reason.
9. Produce a decision-complete response that can replace the temporary reports as the sole research state.
10. Return that response directly. Write no files.

## Final response shape

```markdown
# <Research title>

## Direct answer
<decision-complete answer to the user question>

## Findings
1. <material finding + evidence pointer + confidence/type when useful>

## Agreements and contradictions
- <what aligns, what conflicts, and what would resolve it>

## Gaps and confidence
- <coverage limitation and impact>

## Recommended next actions
1. <action tied to evidence>

## Evidence map
- <source pointer and what it supported>

## Coverage audit
- worker_reports_expected: <count>
- worker_reports_read: <count>
- worker_findings_received: <count>
- synthesized_findings: <count>
- deliberately_excluded_findings: <count and reasons>
- unresolved_gaps: <count and short labels>
```

## Completeness rules

- Include every material detail needed for the user's decision. Expand the final response rather than writing an artifact or silently omitting findings.
- Merge duplicates, but preserve unique evidence, disagreement, uncertainty, and material caveats.
- Keep evidence pointers usable after the ephemeral worker reports are deleted. Cite original paths, URLs, commits, or other stable source locations rather than worker report paths.
- Do not include worker prompts, raw worker reports, reasoning traces, tool logs, receipt JSON, or temporary paths.
- Do not return a synthesis path. No synthesis file exists.
- End only after the coverage audit proves that all material worker findings were handled.
