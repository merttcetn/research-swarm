# Synthesis Contract

Use this contract for the final synthesis subagent.

## Required prompt sections

```markdown
## User question
<original question and requested output shape>

## Inputs
- <worker report path>
- <worker report path>

## Known gaps
- <failed, partial, or inaccessible lane>

## Boundaries
- Read worker reports before opening raw sources.
- Open raw sources only to verify critical evidence, resolve contradictions, or fill a decisive gap.
- Do not redo every worker's research.
- Do not modify source files or implement recommendations.
- Write the full synthesis only to: <synthesis path>
```

## Synthesis procedure

1. Confirm which lanes and sources were covered.
2. Normalize semantically equivalent findings.
3. Rank findings by relevance to the user question, not by repetition count.
4. Preserve meaningful disagreement.
5. Distinguish:
   - **Established:** directly supported by evidence.
   - **Inferred:** reasoned from evidence but not explicitly established.
   - **Recommended:** proposed next action.
6. Verify only the small number of evidence pointers necessary to support decisive claims.
7. Check that every material worker finding is represented, deliberately merged, or explicitly excluded with a reason.
8. Write the detailed synthesis report.
9. Return a decision-complete, user-ready answer without exposing internal coordination details.

## Detailed synthesis format

```markdown
# <Research title>

## Executive synthesis
<direct answer>

## Priority findings
1. <finding + evidence>

## Agreements and contradictions
- <what aligns, what conflicts, and why>

## Gaps and confidence
- <coverage limitation>

## Recommended next actions
1. <action tied to evidence>

## Source map
- <source pointer and what it supported>
```

## Final response contract

Return:

- A direct answer first.
- A concise inline synthesis, normally 500–800 words, without omitting information needed for the user's decision.
- Up to seven priority findings.
- Material uncertainty or missing coverage.
- Evidence pointers usable by the main agent.
- The synthesis report path.
- The total worker finding count, merged finding count, and any deliberately excluded items.

If all material findings cannot fit inline, keep them in `synthesis.md` and make the report path prominent. Do not include raw worker reports, worker prompts, or lengthy process narration.
