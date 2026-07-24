---
name: research-swarm
description: "Split large research and analysis tasks across read-only subagents, keep raw sources and detailed worker notes out of the main agent context, and return one compact evidence-backed synthesis. Use when the user asks to research, inspect, compare, summarize, or extract findings from many files, reports, URLs, repository areas, or from one large source through multiple independent analytical lenses; especially when the user explicitly requests subagents, parallel research, a research swarm, or context-efficient synthesis. Supports Codex and Claude Code. Do not use for simple single-source questions, tightly sequential investigations, or parallel implementation work."
---

# Research Swarm

Use a map-reduce research workflow: the main agent coordinates, worker subagents inspect sources, and a fresh synthesis subagent combines their reports. Keep implementation and source mutation outside this skill.

## Core guarantees

- Keep every source read-only.
- Keep detailed worker findings outside the main context whenever a shared filesystem is available.
- Treat compact receipts as routing and integrity metadata, never as substitutes for research findings.
- Preserve every material finding in worker reports and in the full synthesis artifact.
- Give workers disjoint source batches, distinct analytical lenses, or both.
- Require evidence pointers for material claims.
- Separate source-backed findings from inference and recommendation.
- Bound agent count and output size; more agents are not automatically better.
- Do not treat agreement between agents as independent source corroboration.

## Adapt to the active runtime

- **Codex:** coordinate from the primary agent and dispatch independent workers with the available collaboration/subagent tools. Respect the runtime's concurrency limit.
- **Claude Code:** coordinate from the main conversation and dispatch workers with the `Agent` tool. Do not set `context: fork` for the coordinator because Claude Code subagents cannot spawn nested subagents.
- **Other compatible agents:** use their native subagent mechanism only when it can isolate worker activity and return compact receipts. If it cannot share report artifacts, use the compact-return fallback described below.

In every runtime, workers must not delegate further.

## Decide whether to use the workflow

Use this workflow when at least one condition holds:

- The source set is too large to inspect comfortably in the main context.
- Two or more independent analytical lenses materially improve the answer.
- The user explicitly requests subagents or parallel research.
- The task needs a comparison, evidence map, contradiction check, or cross-source synthesis.

Work directly when one short source and one narrow question can be handled faster without delegation. If the task mixes research and implementation, complete and present the research synthesis first; implement only when the user separately authorized that work.

## Stage 1: Frame without consuming the corpus

1. Restate the research question, decision to support, expected output, and important constraints.
2. Inventory sources using names, paths, URLs, file sizes, headings, or directory structure. Do not read full source bodies merely to create the inventory.
3. Select a partition strategy:
   - **Source shards:** assign disjoint files, URLs, or repository areas.
   - **Analytical lenses:** assign distinct questions over a shared source, such as facts, risks, workflows, or feasibility.
   - **Hybrid:** shard a large corpus and give each shard the same evidence contract.
4. Default to 2–3 workers. Increase only when the source set has clean independent lanes and capacity is available. Never exceed the available concurrent subagent slots.
5. Define what is out of scope so workers do not duplicate adjacent research.

## Stage 2: Create a context-isolated workspace

When workers share a filesystem, create one narrowly named temporary task directory. Give every worker a unique report path within it. Do not use a broad or user-owned directory as disposable storage.

Use this layout:

```text
<task-dir>/
  worker-01.md
  worker-02.md
  worker-03.md
  synthesis.md
```

If no shared filesystem exists, disclose that perfect context isolation and lossless handoff cannot both be guaranteed. Use compact-return mode, reduce worker count, and require complete material findings rather than imposing a word limit that drops evidence.

## Stage 3: Dispatch read-only workers

Read [references/worker-contract.md](references/worker-contract.md) before dispatching.

Give each worker:

- The exact research question.
- Its owned sources or analytical lens.
- Read-only source boundaries.
- Its unique report path, when available.
- A static one-line description of sibling scopes.
- The required report and receipt formats.

Dispatch independent workers concurrently using the active runtime's native subagent mechanism. Instruct workers not to delegate further and not to modify source files. A worker may write only its assigned report artifact.

In filesystem mode, require the final worker response to contain only the compact receipt. The receipt confirms that the full report exists and passed coverage checks; it does not summarize or replace that report. Never ask workers to paste their detailed report into chat.

## Stage 4: Run a separate synthesis subagent

After all critical workers finish, read [references/synthesis-contract.md](references/synthesis-contract.md).

Start one fresh synthesis subagent using the same runtime mechanism. Give it:

- The original user question and desired answer shape.
- Only the worker report paths, not the raw worker chat output.
- The synthesis report path.
- Any failed-worker receipts or known coverage gaps.

Tell the synthesizer to read worker reports first and open raw sources only for targeted evidence verification, unresolved contradictions, or critical missing context. It must not redo the full research.

## Stage 5: Return the result

Use the synthesizer's decision-complete final response as the basis of the user-facing answer. Do not reopen all worker reports in the main context. The full `synthesis.md` must retain material details that do not fit the inline answer.

Include:

- The direct answer or executive synthesis.
- The most important findings in priority order.
- Meaningful disagreements, uncertainty, and missing access.
- Evidence links or local file pointers.
- A brief note that parallel read-only research was used.

If the user requested a durable report, preserve or copy `synthesis.md` to the requested location and link it. If the inline answer omits any material detail, retain and link `synthesis.md` even when the user did not explicitly request a file. Clean up only the exact temporary task directory, and only after no retained report depends on it.

## Failure handling

- If a non-critical worker fails, continue and disclose the coverage gap.
- If a critical lane fails, retry once with a narrower scope or replace that worker.
- If workers overlap heavily, do not count repeated claims as stronger evidence.
- If reports conflict, preserve both claims and ask the synthesizer to resolve them from primary evidence when possible.
- If a worker violates the compact receipt contract, do not echo its long response to the user; request a compact correction only if its report artifact is missing.
- If the user redirects the task, stop using stale worker results.

## Quality gate

Before answering, ensure:

- Every major claim has at least one evidence pointer.
- Coverage and inaccessible sources are explicit.
- Fact, inference, and recommendation are distinguishable.
- Duplicate findings are merged without hiding disagreement.
- Worker receipts report complete finding and evidence counts instead of carrying a lossy mini-summary.
- The full synthesis preserves material findings even when the inline answer is shorter.
- The answer fits the user's requested depth.
- No source was modified and no implementation was performed under this research-only workflow.
