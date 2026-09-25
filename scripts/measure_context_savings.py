#!/usr/bin/env python3
"""Measure worker-to-main intermediate handoff size from run-directory fixtures."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re


class MeasurementError(ValueError):
    """A run-directory fixture cannot produce a trustworthy measurement."""


WORKER_NAME = re.compile(r"^worker-(?P<identifier>.+)\.md$")
RECEIPT_NAME = re.compile(r"^receipt-(?P<identifier>.+)\.json$")


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


def artifacts_by_id(paths: list[Path], pattern: re.Pattern[str], label: str) -> dict[str, Path]:
    artifacts: dict[str, Path] = {}
    for path in paths:
        match = pattern.fullmatch(path.name)
        if match is None:
            raise MeasurementError(f"{path}: invalid {label} filename")
        artifacts[match.group("identifier")] = path
    return artifacts


def read_nonempty_report(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise MeasurementError(f"{path}: cannot read nonempty UTF-8 worker report: {exc}") from exc
    if not text.strip():
        raise MeasurementError(f"{path}: worker report is empty or whitespace-only")
    return text


def parse_receipt(path: Path) -> dict:
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MeasurementError(f"{path}: malformed receipt JSON: {exc}") from exc
    if not isinstance(receipt, dict):
        raise MeasurementError(f"{path}: receipt JSON must be an object")
    return receipt


def validate_receipt(receipt: dict, path: Path, worker: Path) -> None:
    integer_fields = ("sources_reviewed", "finding_count", "evidence_count", "report_bytes")
    required = ("status", "report_path", "coverage_complete", "gaps", *integer_fields)
    missing = [field for field in required if field not in receipt]
    if missing:
        raise MeasurementError(f"{path}: receipt is missing required fields: {missing}")
    if not isinstance(receipt["status"], str) or receipt["status"] not in {
        "done", "partial", "failed"
    }:
        raise MeasurementError(f"{path}: status must be done, partial, or failed")
    if not isinstance(receipt["report_path"], str) or not receipt["report_path"].strip():
        raise MeasurementError(f"{path}: report_path must be a nonempty string")
    if type(receipt["coverage_complete"]) is not bool:
        raise MeasurementError(f"{path}: coverage_complete must be a boolean")
    if not isinstance(receipt["gaps"], list) or not all(
        isinstance(gap, str) for gap in receipt["gaps"]
    ):
        raise MeasurementError(f"{path}: gaps must be an array of strings")
    invalid_integers = [
        field for field in integer_fields
        if type(receipt[field]) is not int or receipt[field] < 0
    ]
    if invalid_integers:
        raise MeasurementError(f"{path}: counts must be nonnegative integers: {invalid_integers}")

    recorded_path = Path(receipt["report_path"])
    if not recorded_path.is_absolute() or recorded_path.resolve() != worker.resolve():
        raise MeasurementError(
            f"{path}: report_path does not identify paired worker {worker.resolve()}"
        )
    actual_bytes = worker.stat().st_size
    if receipt["report_bytes"] != actual_bytes:
        raise MeasurementError(
            f"{path}: report_bytes is {receipt['report_bytes']}; actual size is {actual_bytes}"
        )


def validate_run(run_dir: Path) -> tuple[list[Path], list[Path], list[str], list[str]]:
    if not run_dir.is_dir():
        raise MeasurementError(f"{run_dir}: measurement input is not an existing directory")

    workers = artifacts_by_id(sorted(run_dir.glob("worker-*.md")), WORKER_NAME, "worker report")
    receipts = artifacts_by_id(sorted(run_dir.glob("receipt-*.json")), RECEIPT_NAME, "receipt")
    if not workers:
        raise MeasurementError(f"{run_dir}: no worker-*.md measurement inputs found")
    if not receipts:
        raise MeasurementError(f"{run_dir}: no receipt-*.json measurement inputs found")

    worker_only = sorted(workers.keys() - receipts.keys())
    receipt_only = sorted(receipts.keys() - workers.keys())
    if worker_only or receipt_only:
        raise MeasurementError(
            "Unmatched worker/receipt identifiers "
            f"(workers without receipts: {worker_only}; receipts without workers: {receipt_only})"
        )

    worker_text: list[str] = []
    receipt_text: list[str] = []
    for identifier in sorted(workers):
        worker = workers[identifier]
        receipt_path = receipts[identifier]
        report = read_nonempty_report(worker)
        receipt = parse_receipt(receipt_path)
        validate_receipt(receipt, receipt_path, worker)
        worker_text.append(report)
        receipt_text.append(receipt_path.read_text(encoding="utf-8"))
    return (list(workers.values()), list(receipts.values()), worker_text, receipt_text)


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


def calculate(run_dir: Path, encoding_name: str) -> dict:
    worker_paths, receipt_paths, worker_reports, receipt_strings = validate_run(run_dir)
    worker_text = "\n".join(worker_reports)
    receipt_text = "\n".join(receipt_strings)
    count_tokens, method = token_counter(encoding_name)

    worker_tokens = count_tokens(worker_text)
    receipt_tokens = count_tokens(receipt_text)
    worker_chars = len(worker_text)
    receipt_chars = len(receipt_text)

    result = {
        "method": method,
        "scope": "worker-to-main intermediate handoff only",
        "cost_scope": (
            "not total API usage, billing, quota, or aggregate worker compute"
        ),
        "input_scope": {
            "kind": "explicit run-directory measurement fixture",
            "runtime_lifecycle_verified": False,
            "persistent_workflow_artifacts_authorized": False,
        },
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
    return result


def main() -> None:
    args = parse_args()
    try:
        result = calculate(args.run_dir.resolve(), args.encoding)
    except MeasurementError as exc:
        raise SystemExit(f"measurement error: {exc}") from exc
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
