---
name: research-swarm
description: "Orchestrate large research and analysis tasks through parallel read-only subagents without loading raw sources or detailed worker output into the main agent context. Workers write lossless reports only to an ephemeral OS temp workspace and return compact receipts; a fresh synthesis subagent reads those reports and returns one decision-complete result directly to the main agent, which then deletes the workspace. Use for multi-file, multi-URL, repository, report, transcript, comparison, evidence-mapping, or multi-lens research when subagents and context isolation materially help. Supports Codex and Claude Code. Do not use for simple single-source questions, tightly sequential investigations, parallel implementation, or runtimes that merge subagent history into the main context."
---

# Research Swarm

Run an ephemeral map-reduce research workflow. Keep the main agent as an orchestrator, never a researcher: frame the task, partition the scope from metadata, create an OS temp workspace, dispatch workers, wait, dispatch one fresh synthesizer, receive its complete final response, delete the workspace, and continue using only that merged result.

## Non-negotiable guarantees

- Keep source files and external systems read-only.
- Do not let the main agent open raw source bodies, worker reports, or subagent tool output.
- Store detailed worker findings only in uniquely named `worker-*.md` files under one exact OS temp directory.
- Return only compact path/count receipts from workers to the main agent.
- Return the complete synthesis directly from the synthesis subagent to the main agent.
- Never create `synthesis.md` or another synthesis artifact inside the research workflow.
- Delete the exact temp workspace after a complete synthesis is received or after the workflow is abandoned.
- Do not reuse completed research or synthesis subagents. Their internal contexts must not become main-agent context.
- Preserve every material finding through the synthesis coverage audit before deleting worker reports.
- Do not treat agreement between agents as independent source corroboration.

## Confirm runtime support

Use this workflow only when the runtime:

1. isolates subagent context and tool output from the main agent;
2. lets workers and the synthesizer share files through an OS temp directory; and
3. returns only each subagent's final response to its parent.

If any condition is unavailable, stop and explain that lossless context isolation cannot be guaranteed. Do not fall back to returning detailed worker reports through the main conversation unless the user explicitly accepts the extra context cost.

Adapt dispatch to the runtime:

- **Codex:** coordinate from the primary agent and use the available collaboration/subagent tools. Respect the runtime's concurrency limit.
- **Claude Code:** coordinate from the main conversation and use the `Agent` tool. Do not put the coordinator in `context: fork`; Claude Code subagents cannot spawn nested subagents.
- **Other compatible agents:** use their native subagent mechanism only after confirming the three isolation conditions above.

In every runtime, prohibit workers and the synthesizer from delegating further.

## Decide whether to swarm

Use this workflow when at least one condition holds:

- The source set is too large to inspect comfortably in the main context.
- Two or more independent analytical lenses materially improve the answer.
- The user explicitly requests subagents, parallel research, or context isolation.
- The task needs comparison, evidence mapping, contradiction checking, or cross-source synthesis.

Work directly when one short source and one narrow question are faster without delegation. Keep implementation outside this skill. Complete the synthesis first; implement only when the user separately authorizes it.

## Stage 1: Frame from metadata only

1. Restate the research question, decision to support, expected output, and constraints.
2. Inventory only source metadata such as paths, URLs, filenames, sizes, headings already provided by the user, or directory structure. Do not open source bodies.
3. Select a partition strategy:
   - **Source shards:** assign disjoint files, URLs, or repository areas.
   - **Analytical lenses:** assign distinct questions over a shared source.
   - **Hybrid:** shard a large corpus and give each shard the same evidence contract.
4. Default to 2–3 workers. Increase only for clean independent lanes and never exceed available concurrency.
5. Freeze each lane's owned scope, sibling summaries, and exclusions before dispatch.

If partitioning requires content inspection, delegate that inspection as a worker lane rather than performing it in the main agent.

## Stage 2: Create the ephemeral workspace

Create one narrowly named directory with the operating system's secure temp-directory mechanism, such as `mktemp -d`. Resolve and record its exact absolute path. Never use a repository, workspace root, home directory, or broad user-owned directory as disposable storage.

Use only this runtime layout:

```text
<os-temp-task-dir>/
  worker-01.md
  worker-02.md
  worker-03.md
```

Do not create receipt files or a synthesis file. Receipts travel as compact subagent final responses. The synthesizer returns its result directly.

## Stage 3: Dispatch workers and wait

Read [references/worker-contract.md](references/worker-contract.md) before dispatching.

Give every worker:

- the exact research question;
- one owned source shard or analytical lens;
- read-only source boundaries;
- one unique absolute `worker-*.md` path;
- static one-line sibling scopes; and
- the worker report and receipt contracts.

Dispatch independent workers concurrently. A worker may write only its assigned report file. Require its final response to contain only the compact receipt.

After dispatch, the main agent must wait. Do not use the waiting period to open sources, inspect worker files, reproduce research, or perform adjacent investigation. Accept only receipts and minimal orchestration status.

## Stage 4: Dispatch one fresh synthesizer and wait

After all critical workers finish, read [references/synthesis-contract.md](references/synthesis-contract.md).

Start one fresh synthesis subagent with:

- the original user question and requested output shape;
- the absolute worker report paths;
- receipt counts and coverage state;
- failed or partial lane information; and
- the synthesis response contract.

Do not give it a synthesis output path. Require it to write no files and return the decision-complete synthesis directly as its final response.

The synthesizer must read worker reports first. It may open raw sources only for targeted verification of decisive evidence, unresolved contradictions, or a critical gap. It must not redo the full research.

While synthesis runs, the main agent must wait and must not open sources or worker reports.

## Stage 5: Validate the handoff, clean up, and continue

Use receipt metadata and the synthesis response's coverage audit to verify:

- every expected worker report was read;
- every worker finding was represented, deliberately merged, or explicitly excluded with a reason;
- material contradictions and gaps remain visible; and
- the response is complete enough to be the sole research state carried forward.

If the coverage audit is incomplete, send one corrective follow-up to the same synthesizer while the temp reports still exist. Do not make the main agent inspect the reports.

After accepting the synthesis:

1. Treat the synthesizer's final response as the only detailed research content added to main context.
2. Resolve the recorded temp path again and confirm it is the exact task directory under the OS temp area.
3. Delete that exact directory and all worker reports.
4. Confirm the directory no longer exists.
5. Close or release completed subagent tasks when the runtime supports explicit closure; never reuse or message the completed workers or synthesizer.
6. Return or continue from the merged synthesis without reopening sources.

Research Swarm never creates a durable synthesis artifact. If the user separately requested a durable document, create it only after cleanup as a separate authorized task using the returned synthesis.

## Failure and interruption handling

- Continue past a non-critical worker failure and disclose the gap to the synthesizer.
- Retry a critical worker once with narrower scope before synthesis.
- Preserve conflicting claims instead of majority-voting them away.
- If a worker returns prose instead of a receipt, request a compact correction only when its report exists; never ask it to repeat detailed findings.
- If synthesis fails, retry once while the worker reports still exist.
- If the user redirects or cancels the task, stop using pending results, end the subagent tasks when supported, and delete the exact temp workspace.
- If cleanup fails, retry only against the validated exact temp path. Report the remaining path and do not claim the workflow completed until it is removed.

## Quality gate

Before returning control, ensure:

- The main agent opened no raw source body and no worker report.
- Worker final responses contained receipts rather than findings.
- The synthesis subagent wrote no files and returned a decision-complete result directly.
- Every material worker finding was accounted for in the coverage audit.
- Fact, inference, recommendation, contradiction, and missing access remain distinguishable.
- No `synthesis.md` or durable research artifact was created.
- The exact temp workspace was deleted and confirmed absent.
- Completed subagents were not reused.
- No source was modified and no implementation occurred under this research-only workflow.
