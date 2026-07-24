#!/usr/bin/env python3
"""Measure worker-to-main context savings for a research run directory."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare detailed worker reports with compact receipts. "
            "Use --encoding for tokenizer-based counts when tiktoken is installed."
        )
    )
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--encoding", default="o200k_base")
    return parser.parse_args()


def load_text(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def token_counter(encoding_name: str):
    try:
        import tiktoken
    except ImportError:
        return (
            lambda text: math.ceil(len(text) / 4),
            "four-characters-per-token estimate",
        )

    encoding = tiktoken.get_encoding(encoding_name)
    return lambda text: len(encoding.encode(text)), f"tiktoken:{encoding_name}"


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    worker_paths = sorted(run_dir.glob("worker-*.md"))
    receipt_paths = sorted(run_dir.glob("receipt-*.json"))

    if not worker_paths or not receipt_paths:
        raise SystemExit(
            "Expected at least one worker-*.md and one receipt-*.json file."
        )

    worker_text = load_text(worker_paths)
    receipt_text = load_text(receipt_paths)
    count_tokens, method = token_counter(args.encoding)

    worker_tokens = count_tokens(worker_text)
    receipt_tokens = count_tokens(receipt_text)
    worker_chars = len(worker_text)
    receipt_chars = len(receipt_text)

    result = {
        "method": method,
        "scope": "worker-to-main intermediate handoff only",
        "worker_reports": len(worker_paths),
        "worker_report_chars": worker_chars,
        "receipt_chars": receipt_chars,
        "character_savings_percent": round(
            (1 - receipt_chars / worker_chars) * 100, 2
        ),
        "worker_report_tokens": worker_tokens,
        "receipt_tokens": receipt_tokens,
        "token_savings": worker_tokens - receipt_tokens,
        "token_savings_percent": round(
            (1 - receipt_tokens / worker_tokens) * 100, 2
        ),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
