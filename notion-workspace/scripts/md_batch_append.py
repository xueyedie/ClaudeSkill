#!/usr/bin/env python3
"""Append a Markdown file to a Notion page in line batches.

Never ends a batch inside an unclosed ``` fenced block — otherwise the next
batch starts mid-fence and Notion/notion_cli will mis-parse (orphan code
blocks, \"正在加载 Plain Text\" placeholders, raw | lines as paragraphs).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def _ends_inside_fence(lines: list[str]) -> bool:
    """True if, after these lines, a ``` fence is still open."""
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
    return in_fence


def chunk_by_lines(lines: list[str], max_lines: int) -> list[list[str]]:
    chunks: list[list[str]] = []
    i = 0
    n = len(lines)
    while i < n:
        start = i
        end = min(i + max_lines, n)
        while _ends_inside_fence(lines[start:end]) and end < n:
            end += 1
        chunks.append(lines[start:end])
        i = end
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page_id", help="Notion page id to append to")
    parser.add_argument("md_file", type=Path, help="Path to Markdown file")
    parser.add_argument("--batch-lines", type=int, default=80, help="Target max lines per batch")
    parser.add_argument(
        "--cli",
        type=Path,
        default=Path(__file__).resolve().parent / "notion_cli.py",
        help="Path to notion_cli.py",
    )
    parser.add_argument("--sleep", type=float, default=0.5, help="Seconds between API calls")
    args = parser.parse_args()

    text = args.md_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines and text:
        lines = [text]
    if not lines:
        print("Empty file, nothing to append.", file=sys.stderr)
        return

    chunks = chunk_by_lines(lines, args.batch_lines)
    print(f"File: {args.md_file} ({len(lines)} lines) -> {len(chunks)} batch(es)", file=sys.stderr)

    for idx, chunk in enumerate(chunks, 1):
        content = "".join(chunk)
        if not content.strip():
            continue
        print(f"Appending batch {idx}/{len(chunks)} ({len(chunk)} lines)...", file=sys.stderr)
        r = subprocess.run(
            [sys.executable, str(args.cli), "append-text", args.page_id, "--content", content],
            capture_output=True,
            text=True,
        )
        if r.stdout:
            print(r.stdout, end="")
        if r.stderr:
            print(r.stderr, end="", file=sys.stderr)
        if r.returncode != 0:
            print(f"ERROR: batch {idx} failed with exit {r.returncode}", file=sys.stderr)
            sys.exit(r.returncode)
        if args.sleep and idx < len(chunks):
            time.sleep(args.sleep)

    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
