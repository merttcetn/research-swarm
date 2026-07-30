<div align="center">

# Research Swarm

### Parallelize information intake without flooding the main agent's context

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=flat-square)](./skills/research-swarm/SKILL.md)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-D97757?style=flat-square)](./skills/research-swarm/SKILL.md)
[![Validated saving](https://img.shields.io/badge/main--context_saving-97.66%25-16A34A?style=flat-square)](./benchmarks/validated-run/metrics.json)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mert_Çetin-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/mertcetin20/)

[How it works](#how-it-works) · [Measured impact](#measured-main-context-impact) · [Install](#installation) · [Use](#usage)

</div>

---

`research-swarm` is a reusable Codex and Claude Code skill for large research tasks. It divides independent reading across read-only subagents, stores complete worker findings only in an ephemeral OS temp workspace, and gives the main agent compact integrity receipts plus one decision-ready synthesis before deleting every temporary report.

The goal is deliberately narrow:

> **Make research faster through parallel intake while keeping raw sources and verbose intermediate analysis out of the main agent's context window.**

## Why this exists

A naive multi-agent research workflow still bloats the coordinator:

1. Every worker reads a different source.
2. Every worker pastes its full report back into the main conversation.
3. The main agent spends thousands of tokens carrying intermediate detail merely to synthesize it.

This skill changes the handoff boundary. Workers write complete reports to isolated temp files and return only small receipts containing the report path, coverage state, and finding/evidence counts. A fresh synthesis agent reads those reports and returns the complete final answer directly to the coordinator. The coordinator never opens the sources or reports; after accepting the synthesis, it deletes the exact temp workspace and continues from the merged result.

## How it works

<p align="center">
  <img src="./assets/research-swarm-flow.svg" alt="Research Swarm routes a research request through a main coordinator, three read-only workers with isolated report files, and a fresh synthesis agent. Only compact receipts return to the main context." width="100%">
</p>

### The context boundary

| Component | Reads raw sources? | Reads worker reports? | Returns to main context |
|---|---:|---:|---|
| Main coordinator | No — metadata only | No | Orchestration + final synthesis |
| Read-only workers | Yes, scoped lane only | No | Receipt under 700 characters |
| Synthesis agent | Only for targeted verification | Yes, all reports | Decision-complete synthesis |

The small JSON receipt is **not** a lossy summary. It is routing and integrity metadata:

```json
{
  "status": "done",
  "report_path": "/tmp/run/worker-01.md",
  "sources_reviewed": 4,
  "finding_count": 12,
  "evidence_count": 27,
  "coverage_complete": true,
  "report_bytes": 14820,
  "gaps": []
}
```

During the run, all material findings remain in worker reports outside the main context. Before cleanup, the synthesis contract requires every finding to be represented, deliberately merged, or explicitly excluded with a reason. The direct synthesis response then becomes the only detailed research state carried forward.

The main context receives only:

```text
original request
+ minimal orchestration state
+ compact worker receipts
+ decision-complete synthesis
```

Raw sources, worker reasoning, detailed reports, subagent tool output, and duplicate findings never enter the main context.

## Measured main-context impact

A validated run used two parallel workers to compare three large skill artifacts. The workers produced **31 findings** backed by **94 evidence pointers**.

Without report isolation, the two detailed worker reports would have added **7,255 tokens** to the main context. With compact receipts, the intermediate handoff added only **170 tokens**.

<p align="center">
  <img src="./assets/context-impact.svg" alt="Research Swarm reduces intermediate main-context usage from 7,255 tokens of full worker reports to 170 tokens of compact receipts, a 97.66 percent reduction." width="100%">
</p>

| Metric | Full worker reports | Compact receipts | Reduction |
|---|---:|---:|---:|
| Characters | 27,123 | 641 | **97.64%** |
| Estimated tokens (`o200k_base`) | 7,255 | 170 | **97.66%** |
| Tokens kept out of main context | — | — | **7,085** |

The direct final synthesis represented the result as **10 merged findings with 0 deliberately excluded findings**.

> [!IMPORTANT]
> This is a measurement of **main-context pressure**, not total API usage or billing. Parallel workers may consume more aggregate compute. The required final synthesis is intentionally excluded because both the baseline and optimized design must deliver it.

Token counts use OpenAI's `o200k_base` tokenizer as a reproducible estimate. Different models tokenize text differently; the **97.64% character reduction** is tokenizer-independent.

Raw benchmark data: [`benchmarks/validated-run/metrics.json`](./benchmarks/validated-run/metrics.json)

Re-run the measurement on any compatible research run:

```bash
uv run --with tiktoken \
  python scripts/measure_context_savings.py /path/to/run-directory
```

The run directory must contain `worker-*.md` and `receipt-*.json` files.

## Features

- **Parallel read-only research** using source shards, analytical lenses, or a hybrid partition.
- **Context-isolated worker reports** stored outside the main conversation.
- **Ephemeral OS-temp lifecycle** with verified cleanup after synthesis.
- **Lossless handoff contracts** with finding, evidence, coverage, and gap accounting.
- **Dedicated synthesis pass** that reads worker reports while the main agent waits.
- **No synthesis artifact**: the complete result returns directly to the main agent.
- **Evidence-first output** with paths, lines, URLs, commits, and explicit confidence.
- **Contradiction preservation** rather than majority-voting conflicting claims away.
- **Bounded concurrency**: normally 2–3 workers, increased only for clean independent lanes.
- **Graceful partial failure** with explicit coverage gaps.
- **One universal skill** that adapts its subagent dispatch to Codex or Claude Code.

## Repository layout

```text
research-swarm/
├── assets/
│   ├── context-impact.svg
│   └── research-swarm-flow.svg
├── skills/
│   └── research-swarm/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
├── benchmarks/
│   └── validated-run/metrics.json
├── scripts/
│   ├── measure_context_savings.py
│   └── validate_ephemeral_contract.py
└── README.md
```

## Installation

### Skills CLI

Install from GitHub with automatic agent detection:

```bash
npx skills add merttcetn/research-swarm -g
```

Or select the target explicitly:

```bash
npx skills add merttcetn/research-swarm -g --agent codex
npx skills add merttcetn/research-swarm -g --agent claude-code
```

### Manual installation

Codex:

```bash
mkdir -p ~/.codex/skills/research-swarm
rsync -a skills/research-swarm/ ~/.codex/skills/research-swarm/
```

Invoke explicitly with:

```text
$research-swarm
```

Claude Code:

```bash
mkdir -p ~/.claude/skills/research-swarm
rsync -a skills/research-swarm/ ~/.claude/skills/research-swarm/
```

Invoke explicitly with:

```text
/research-swarm
```

The universal skill adapts to the active runtime. In Claude Code it coordinates from the main thread because Claude Code subagents cannot spawn nested subagents. Detailed worker activity remains isolated; only compact receipts return to the coordinator.

## Usage

### Analyze one large source through independent lenses

```text
$research-swarm

Analyze this transcript with separate subagents for:
1. recurring workflows,
2. technical feasibility and risks,
3. reusable skill candidates.

Return one evidence-backed synthesis without loading the full transcript
into the main context.
```

### Compare many reports

```text
/research-swarm

Split the reports in ./research across read-only workers. Identify consensus,
contradictions, unresolved questions, and the five most important decisions.
Return one decision-complete synthesis directly and remove all temporary reports.
```

### Inspect independent repository areas

```text
$research-swarm

Research authentication, data persistence, and API boundaries in parallel.
Do not edit files. Return a source-linked architecture assessment.
```

## When to use it

Use the skill when:

- the source set is too large for one context window;
- multiple independent analytical lenses improve the answer;
- research can be partitioned without cross-worker dependencies;
- evidence mapping and contradiction analysis matter;
- the user explicitly requests parallel subagents.

Work directly when one short source and one narrow question can be answered faster without delegation.

## Safety and limitations

- Sources and project files remain read-only throughout the research workflow.
- Workers may write only their assigned temporary report artifact.
- The main agent opens neither raw sources nor worker reports while the swarm runs.
- The synthesis agent writes no file; its complete final response returns directly to the main agent.
- The exact OS temp workspace is deleted and confirmed absent after synthesis or cancellation.
- Completed worker and synthesis tasks are never reused; their internal contexts do not merge into the main conversation.
- Without shared temp storage and isolated subagent contexts, the workflow stops rather than silently inflating main context.
- The skill reduces main-agent context pressure; it does not promise lower total compute usage.
- Speedup depends on source independence, available concurrency, tool latency, and model limits.
- Model agreement is not treated as independent source corroboration.
- Research and implementation stay separate; this skill does not silently apply findings.

## Author

Created by **Mert Çetin**.

- [LinkedIn](https://www.linkedin.com/in/mertcetin20/)
- [GitHub repository](https://github.com/merttcetn/research-swarm)

---

<div align="center">

Built for faster research, smaller coordinator contexts, and evidence that survives the handoff.

</div>
