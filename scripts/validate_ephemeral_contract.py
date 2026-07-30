#!/usr/bin/env python3
"""Validate Research Swarm's ephemeral context-isolation contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/research-swarm/SKILL.md"
WORKER = ROOT / "skills/research-swarm/references/worker-contract.md"
SYNTHESIS = ROOT / "skills/research-swarm/references/synthesis-contract.md"
OPENAI_YAML = ROOT / "skills/research-swarm/agents/openai.yaml"
README = ROOT / "README.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(path: Path, text: str, fragments: list[str]) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise AssertionError(f"{path}: missing required contract text: {missing}")


def forbid(path: Path, text: str, fragments: list[str]) -> None:
    present = [fragment for fragment in fragments if fragment in text]
    if present:
        raise AssertionError(f"{path}: forbidden legacy behavior remains: {present}")


def main() -> None:
    skill = read(SKILL)
    worker = read(WORKER)
    synthesis = read(SYNTHESIS)
    openai_yaml = read(OPENAI_YAML)
    readme = read(README)

    require(
        SKILL,
        skill,
        [
            "main agent as an orchestrator, never a researcher",
            "Do not let the main agent open raw source bodies",
            "After dispatch, the main agent must wait.",
            "Do not give it a synthesis output path.",
            "Delete that exact directory and all worker reports.",
            "Confirm the directory no longer exists.",
            "never reuse or message the completed workers or synthesizer.",
            "Never create `synthesis.md`",
        ],
    )
    require(
        WORKER,
        worker,
        [
            "return a single JSON object and nothing else",
            "under 700 characters",
            "Never return the detailed report through chat.",
        ],
    )
    require(
        SYNTHESIS,
        synthesis,
        [
            "Do not write a synthesis file or any other artifact.",
            "Return the complete synthesis directly",
            "## Coverage audit",
            "Do not return a synthesis path.",
        ],
    )
    require(
        OPENAI_YAML,
        openai_yaml,
        [
            'display_name: "Research Swarm"',
            "$research-swarm",
            "clean up all temporary reports",
        ],
    )
    require(
        README,
        readme,
        [
            "ephemeral OS temp workspace",
            "never opens the sources or reports",
            "**No synthesis artifact**",
            "deleted and confirmed absent",
        ],
    )

    forbid(
        SKILL,
        skill,
        [
            "  synthesis.md",
            "The full `synthesis.md`",
            "preserve or copy `synthesis.md`",
            "Use compact-return mode",
        ],
    )
    forbid(
        SYNTHESIS,
        synthesis,
        [
            "<synthesis path>",
            "Write the full synthesis",
            "keep them in `synthesis.md`",
            "The synthesis report path",
        ],
    )
    forbid(README, readme, ["Preserve a full synthesis artifact."])

    result = {
        "status": "passed",
        "invariants": {
            "main_agent_researches": False,
            "worker_chat_contains_findings": False,
            "synthesis_file_created": False,
            "synthesis_returns_directly": True,
            "temp_cleanup_required": True,
            "completed_agents_reused": False,
        },
        "files_checked": 5,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
