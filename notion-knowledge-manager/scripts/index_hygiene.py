#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

EXPECTED_DOMAINS = {"AI", "游戏"}
MANAGEMENT_TITLES = {"Knowledge Hub", "Knowledge Index", "Inbox", "Index Archive"}
DEFAULT_REQUIRED_FIELDS = ["Title", "Domain", "Parent Topic", "Type", "URL"]
REVIEW_CYCLE_DAYS = {
    "weekly": 7,
    "monthly": 31,
    "quarterly": 92,
}
DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]


@dataclass
class Finding:
    severity: str
    kind: str
    title: str
    row_number: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="检查 Notion Knowledge Index 的 CSV 导出，发现缺失字段、重复项、误分类和过期复查项。"
    )
    parser.add_argument("csv_path", help="Knowledge Index 的 CSV 导出文件路径")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式，默认 text",
    )
    parser.add_argument(
        "--required-fields",
        nargs="*",
        default=DEFAULT_REQUIRED_FIELDS,
        help="需要检查的必填字段列表，默认: Title Domain Parent Topic Type URL",
    )
    parser.add_argument(
        "--skip-stale-review",
        action="store_true",
        help="跳过 Review Cycle / Last Reviewed 的过期检查",
    )
    return parser.parse_args()


def normalize(value: Optional[str]) -> str:
    return (value or "").strip()


def parse_date(raw: str) -> Optional[date]:
    text = normalize(raw)
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def load_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def add_finding(findings: List[Finding], severity: str, kind: str, title: str, row_number: int, message: str) -> None:
    findings.append(Finding(severity=severity, kind=kind, title=title or "<空标题>", row_number=row_number, message=message))


def check_missing_fields(rows: List[Dict[str, str]], required_fields: List[str], findings: List[Finding]) -> None:
    for index, row in enumerate(rows, start=2):
        title = normalize(row.get("Title"))
        for field in required_fields:
            if not normalize(row.get(field)):
                add_finding(findings, "medium", "missing_field", title, index, f"缺少字段: {field}")


def check_domain(rows: List[Dict[str, str]], findings: List[Finding]) -> None:
    for index, row in enumerate(rows, start=2):
        title = normalize(row.get("Title"))
        domain = normalize(row.get("Domain"))
        if domain and domain not in EXPECTED_DOMAINS:
            add_finding(findings, "high", "invalid_domain", title, index, f"Domain 不在允许值内: {domain}")


def check_management_titles(rows: List[Dict[str, str]], findings: List[Finding]) -> None:
    for index, row in enumerate(rows, start=2):
        title = normalize(row.get("Title"))
        if title in MANAGEMENT_TITLES:
            add_finding(findings, "high", "management_entry", title, index, "管理层对象不应作为普通内容条目长期留在索引表")


def check_duplicates(rows: List[Dict[str, str]], findings: List[Finding]) -> None:
    titles: Dict[str, List[int]] = defaultdict(list)
    urls: Dict[str, List[int]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        title = normalize(row.get("Title"))
        url = normalize(row.get("URL"))
        if title:
            titles[title].append(index)
        if url:
            urls[url].append(index)

    for title, indexes in titles.items():
        if len(indexes) > 1:
            for idx in indexes:
                add_finding(findings, "medium", "duplicate_title", title, idx, f"标题重复，涉及行: {indexes}")

    for url, indexes in urls.items():
        if len(indexes) > 1:
            for idx in indexes:
                add_finding(findings, "high", "duplicate_url", rows[idx - 2].get("Title", ""), idx, f"URL 重复，涉及行: {indexes}")


def check_stale_review(rows: List[Dict[str, str]], findings: List[Finding]) -> None:
    today = date.today()
    for index, row in enumerate(rows, start=2):
        title = normalize(row.get("Title"))
        cycle = normalize(row.get("Review Cycle")).lower()
        last_reviewed = parse_date(row.get("Last Reviewed", ""))

        if cycle in REVIEW_CYCLE_DAYS and not last_reviewed:
            add_finding(findings, "medium", "missing_last_reviewed", title, index, f"Review Cycle={cycle}，但 Last Reviewed 为空")
            continue

        if cycle not in REVIEW_CYCLE_DAYS or not last_reviewed:
            continue

        if (today - last_reviewed).days > REVIEW_CYCLE_DAYS[cycle]:
            add_finding(
                findings,
                "low",
                "stale_review",
                title,
                index,
                f"已超过复查周期，Review Cycle={cycle}，Last Reviewed={last_reviewed.isoformat()}",
            )


def build_summary(findings: List[Finding], rows_count: int) -> Dict[str, object]:
    severity_counts: Dict[str, int] = defaultdict(int)
    kind_counts: Dict[str, int] = defaultdict(int)
    for finding in findings:
        severity_counts[finding.severity] += 1
        kind_counts[finding.kind] += 1
    return {
        "rows_count": rows_count,
        "findings_count": len(findings),
        "severity_counts": dict(sorted(severity_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
    }


def render_text(summary: Dict[str, object], findings: List[Finding]) -> str:
    lines = [
        "Knowledge Index 体检结果",
        f"- 行数: {summary['rows_count']}",
        f"- 问题数: {summary['findings_count']}",
        f"- 严重度统计: {json.dumps(summary['severity_counts'], ensure_ascii=False)}",
        f"- 类型统计: {json.dumps(summary['kind_counts'], ensure_ascii=False)}",
        "",
    ]
    for finding in findings:
        lines.append(
            f"[{finding.severity}] 行 {finding.row_number} | {finding.title} | {finding.kind} | {finding.message}"
        )
    if not findings:
        lines.append("未发现问题。")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise SystemExit(f"找不到文件: {csv_path}")

    rows = load_rows(csv_path)
    findings: List[Finding] = []

    check_missing_fields(rows, args.required_fields, findings)
    check_domain(rows, findings)
    check_management_titles(rows, findings)
    check_duplicates(rows, findings)
    if not args.skip_stale_review:
        check_stale_review(rows, findings)

    findings.sort(key=lambda item: (item.severity, item.kind, item.row_number, item.title))
    summary = build_summary(findings, len(rows))

    if args.format == "json":
        print(json.dumps({"summary": summary, "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2))
    else:
        print(render_text(summary, findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
