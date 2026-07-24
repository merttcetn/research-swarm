---
name: parallel-research-synthesis
description: Split large research and analysis tasks across read-only Claude Code subagents, keep raw sources and detailed worker notes out of the main conversation context, and return one evidence-backed synthesis without losing material findings. Use when the user asks to research, inspect, compare, summarize, or extract findings from many files, reports, URLs, repository areas, or from one large source through multiple independent analytical lenses; especially when the user asks for subagents, parallel research, or context-efficient synthesis. Do not use for simple single-source questions, tightly sequential investigations, or parallel implementation work.
---

# Parallel Research Synthesis

Coordinate a map-reduce research workflow from the main Claude Code conversation. Do not set `context: fork`: Claude Code subagents cannot spawn other subagents, so the coordinator must remain in the main thread and use the `Agent` tool itself.

## Core guarantees

- Keep every source read-only.
- Keep detailed worker findings in per-worker report files rather than worker chat responses.
- Treat compact receipts as routing and integrity metadata, never as research summaries.
- Preserve every material finding in worker reports and the full synthesis artifact.
- Require evidence pointers for material claims.
- Separate source-backed facts, inference, and recommendations.
- Do not treat agreement between agents as independent source corroboration.

## Decide whether to delegate

Use this workflow when:

- The source set is too large for the main context.
- Independent analytical lenses materially improve the answer.
- The user explicitly requests subagents or parallel research.
- The task needs comparison, contradiction checking, or cross-source synthesis.

Work directly for one short source and one narrow question. Keep implementation outside this skill; finish the research synthesis before starting any separately authorized changes.

## Stage 1: Frame without reading the corpus

1. Fix the research question, decision to support, output shape, and constraints.
2. Inventory source names, paths, URLs, sizes, headings, or directory structure without reading full bodies.
3. Choose:
   - **Source shards** for disjoint files, URLs, or repository areas.
   - **Analytical lenses** for distinct questions over a shared source.
   - **Hybrid** for a large corpus with a shared evidence contract.
4. Default to 2–3 workers and never exceed available parallel capacity.
5. Freeze each lane's scope and exclusions before dispatch.

## Stage 2: Create isolated report paths

Create one narrowly named temporary task directory with:

```text
<task-dir>/
  worker-01.md
  worker-02.md
  worker-03.md
  synthesis.md
```

Give each worker exactly one report path. Workers may write only their report artifact and must not modify sources or project files.

If workers cannot share a filesystem, disclose that perfect context isolation and lossless handoff cannot both be guaranteed. Reduce worker count and prefer complete material findings over arbitrary response limits.

## Stage 3: Dispatch workers with Agent

Read [references/worker-contract.md](references/worker-contract.md) before dispatching.

Use separate parallel `Agent` calls for independent lanes. Prefer read-only research/explore agents when available. Include:

- The exact research question.
- The worker's owned sources or analytical lens.
- Read-only boundaries and unique report path.
- One-line static sibling scopes.
- The worker report and receipt contracts.

Tell workers not to spawn more agents. Claude Code subagents cannot delegate further anyway. In filesystem mode, require only the compact JSON receipt as the worker's final chat response.

## Stage 4: Dispatch a fresh synthesis agent

After workers finish, read [references/synthesis-contract.md](references/synthesis-contract.md).

Start one fresh synthesis `Agent` with:

- The original question and requested answer shape.
- Worker report paths, not raw worker chat.
- Failed or partial lane receipts.
- The `synthesis.md` output path.

Require it to read worker reports first. It may open raw sources only to verify decisive evidence, resolve contradictions, or fill a critical gap. It must not redo the whole investigation.

## Stage 5: Answer without reopening reports

Use the synthesis agent's decision-complete response for the user-facing answer. Do not read every worker report back into the main context.

Include:

- The direct conclusion.
- Priority findings and evidence pointers.
- Material disagreement, uncertainty, and missing coverage.
- A link or path to `synthesis.md` whenever the inline answer omits material detail.
- A brief note that parallel read-only research was used.

Retain `synthesis.md` if it carries material detail not present inline. Clean up only the exact temporary task directory and only after no retained report depends on it.

## Failure handling

- Continue past a non-critical worker failure and disclose the gap.
- Retry a critical lane once with narrower scope.
- Preserve conflicting claims instead of majority-voting them away.
- Do not count overlapping worker claims as stronger evidence.
- If a worker returns prose instead of a receipt but wrote its report, use the report; do not echo the prose.
- Stop using stale worker results when the user redirects the task.

## Quality gate

Before answering, ensure:

- Every major claim has evidence.
- Every material worker finding is represented, deliberately merged, or explicitly excluded.
- Fact, inference, and recommendation remain distinguishable.
- Duplicate findings are merged without hiding disagreement.
- No source or project file was modified.
