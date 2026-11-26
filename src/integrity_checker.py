#!/usr/bin/env python3
"""Local file-integrity checker using SHA-256 hashes.

Use this utility only with files you own or are authorized to monitor.
It operates locally and does not access the network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
HASH_ALGORITHM = "sha256"
CHUNK_SIZE = 1024 * 1024


def utc_timestamp() -> str:
    """Return a timezone-aware UTC timestamp for generated records."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(file_path: Path) -> str:
    """Calculate a file's SHA-256 digest without loading it all into memory."""
    digest = hashlib.sha256()
    with file_path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(target_dir: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Build a sorted inventory of regular files; symbolic links are skipped."""
    inventory: dict[str, dict[str, Any]] = {}
    skipped: list[str] = []
    for path in sorted(target_dir.rglob("*")):
        relative_path = path.relative_to(target_dir).as_posix()
        if path.is_symlink():
            skipped.append(relative_path)
            continue
        if not path.is_file():
            continue
        stat = path.stat()
        inventory[relative_path] = {
            "sha256": sha256_file(path),
            "size_bytes": stat.st_size,
        }
    return inventory, skipped


def validate_target(target: Path) -> Path:
    target = target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        raise ValueError(f"Target directory does not exist or is not a directory: {target}")
    return target


def load_baseline(baseline_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Baseline file not found: {baseline_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Baseline file is not valid JSON: {baseline_path}") from exc
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported or missing baseline schema_version.")
    if data.get("algorithm") != HASH_ALGORITHM:
        raise ValueError("Baseline hash algorithm does not match this tool.")
    if not isinstance(data.get("files"), dict):
        raise ValueError("Baseline is missing a valid 'files' inventory.")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def initialize_baseline(target: Path, baseline_path: Path) -> dict[str, Any]:
    target = validate_target(target)
    baseline_path = baseline_path.expanduser().resolve()
    if baseline_path.is_relative_to(target):
        raise ValueError("Store the baseline outside the monitored target directory.")
    inventory, skipped = build_inventory(target)
    baseline = {
        "schema_version": SCHEMA_VERSION,
        "algorithm": HASH_ALGORITHM,
        "created_at_utc": utc_timestamp(),
        "target_label": target.name,
        "files": inventory,
        "skipped_symlinks": skipped,
    }
    write_json(baseline_path, baseline)
    return baseline


def compare_inventory(
    baseline_files: dict[str, dict[str, Any]],
    current_files: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    entries: list[dict[str, Any]] = []
    old_names, new_names = set(baseline_files), set(current_files)
    for name in sorted(old_names | new_names):
        if name not in baseline_files:
            status, before, after = "ADDED", None, current_files[name]
        elif name not in current_files:
            status, before, after = "DELETED", baseline_files[name], None
        elif baseline_files[name]["sha256"] != current_files[name]["sha256"]:
            status, before, after = "MODIFIED", baseline_files[name], current_files[name]
        else:
            status, before, after = "UNCHANGED", baseline_files[name], current_files[name]
        entries.append({"path": name, "status": status, "baseline": before, "current": after})
    summary = {
        status: sum(1 for item in entries if item["status"] == status)
        for status in ("UNCHANGED", "MODIFIED", "ADDED", "DELETED")
    }
    summary["total_compared"] = len(entries)
    summary["changes_detected"] = summary["MODIFIED"] + summary["ADDED"] + summary["DELETED"]
    return entries, summary


def verify_target(target: Path, baseline_path: Path, report_path: Path) -> dict[str, Any]:
    target = validate_target(target)
    baseline_path = baseline_path.expanduser().resolve()
    report_path = report_path.expanduser().resolve()
    if baseline_path.is_relative_to(target):
        raise ValueError("Baseline must be stored outside the monitored target directory.")
    if report_path.is_relative_to(target):
        raise ValueError("Report must be stored outside the monitored target directory.")
    baseline = load_baseline(baseline_path)
    current_inventory, skipped = build_inventory(target)
    entries, summary = compare_inventory(baseline["files"], current_inventory)
    report = {
        "generated_at_utc": utc_timestamp(),
        "target_label": target.name,
        "baseline_file": baseline_path.name,
        "algorithm": HASH_ALGORITHM,
        "summary": summary,
        "entries": entries,
        "skipped_symlinks": skipped,
        "interpretation": (
            "No differences were detected against the saved baseline."
            if summary["changes_detected"] == 0
            else "Differences were detected. Review each changed path and confirm whether it was expected."
        ),
    }
    write_json(report_path, report)
    return report


def print_summary(summary: dict[str, int], report_path: Path) -> None:
    print("\nFILE INTEGRITY VERIFICATION")
    print("-" * 32)
    print(f"Files compared : {summary['total_compared']}")
    print(f"Unchanged      : {summary['UNCHANGED']}")
    print(f"Modified       : {summary['MODIFIED']}")
    print(f"Added          : {summary['ADDED']}")
    print(f"Deleted        : {summary['DELETED']}")
    print(f"Changes found  : {summary['changes_detected']}")
    print(f"Report saved   : {report_path}")
    print("-" * 32)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and verify SHA-256 file-integrity baselines for authorized local folders."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="Create a SHA-256 baseline inventory.")
    init_parser.add_argument("--target", required=True, type=Path, help="Folder to monitor.")
    init_parser.add_argument("--baseline", required=True, type=Path, help="JSON baseline output path (outside target).")
    verify_parser = subparsers.add_parser("verify", help="Compare a folder against a saved baseline.")
    verify_parser.add_argument("--target", required=True, type=Path, help="Folder to monitor.")
    verify_parser.add_argument("--baseline", required=True, type=Path, help="Existing JSON baseline.")
    verify_parser.add_argument("--report", required=True, type=Path, help="JSON verification report output path (outside target).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            baseline = initialize_baseline(args.target, args.baseline)
            print("Baseline created successfully.")
            print(f"Files recorded : {len(baseline['files'])}")
            print(f"Algorithm      : {HASH_ALGORITHM.upper()}")
            print(f"Saved to       : {args.baseline.expanduser().resolve()}")
            if baseline["skipped_symlinks"]:
                print(f"Symlinks skipped: {len(baseline['skipped_symlinks'])}")
            return 0
        report = verify_target(args.target, args.baseline, args.report)
        print_summary(report["summary"], args.report.expanduser().resolve())
        if report["skipped_symlinks"]:
            print(f"Symbolic links skipped: {len(report['skipped_symlinks'])}")
        return 0 if report["summary"]["changes_detected"] == 0 else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
