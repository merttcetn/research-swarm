# Synthesis Contract

## Prompt

```markdown
## User question
<original question and output shape>

## Worker reports
- <absolute report path>

## Known gaps
- <failed or partial lane>

## Boundaries
- Read worker reports before opening raw sources.
- Open raw sources only for targeted verification or a decisive gap.
- Do not redo all worker research.
- Do not modify source or project files.
- Write the full synthesis to: <synthesis path>
```

## Procedure

1. Confirm lane and source coverage.
2. Normalize equivalent findings.
3. Rank by relevance, not repetition count.
4. Preserve meaningful disagreement.
5. Mark claims as established, inferred, or recommended.
6. Verify only decisive evidence pointers.
7. Ensure every material worker finding is represented, deliberately merged, or excluded with a stated reason.
8. Write the full synthesis.

## Full synthesis

```markdown
# <Title>

## Executive synthesis
<direct answer>

## Priority findings
1. <finding + evidence>

## Agreements and contradictions
- <alignment and conflicts>

## Gaps and confidence
- <coverage limitation>

## Recommended next actions
1. <evidence-linked action>

## Source map
- <source and supported claim>
```

## Final response

Return a decision-complete inline synthesis, normally 500–800 words, with evidence pointers, material uncertainty, the synthesis path, total worker finding count, merged finding count, and deliberately excluded item count. If all material detail does not fit inline, keep it in `synthesis.md` and make that path prominent.
