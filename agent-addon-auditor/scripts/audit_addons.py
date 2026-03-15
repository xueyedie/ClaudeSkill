#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".yaml", ".yml", ".json",
    ".js", ".ts", ".toml", ".ini", ".cfg", ".conf", ".env", ".csv", ".xml",
}
TEXT_FILENAMES = {
    "SKILL.md", "README", "README.md", "openai.yaml", ".env", ".gitignore",
}
MAX_FILE_BYTES = 1_000_000
SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}
SEVERITY_LABELS = {
    "critical": "严重",
    "high": "高危",
    "medium": "中危",
    "low": "低危",
    "clean": "未发现明显风险",
}
ACTION_LABELS = {
    "critical": "阻断并隔离",
    "high": "阻断并隔离",
    "medium": "人工复核",
    "low": "谨慎放行",
    "clean": "谨慎放行",
}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    title: str
    severity: str
    category: str
    rationale: str
    pattern: str
    flags: int = re.IGNORECASE


LINE_RULES = [
    Rule(
        "remote-pipe-shell",
        "远程内容直接管道给 shell",
        "critical",
        "remote-exec",
        "远程内容通过管道直接交给 bash/sh/zsh 执行，是高置信度的恶意安装或投递模式。",
        r"(?:curl|wget)[^\n|]*\|\s*(?:bash|sh|zsh)\b",
    ),
    Rule(
        "obfuscated-shell",
        "base64 解码后管道给 shell",
        "critical",
        "obfuscation",
        "base64 解码再交给 shell，常用于隐藏恶意安装器。",
        r"base64\s+(?:-d|--decode|-D)[^\n|]*\|\s*(?:bash|sh|zsh)\b",
    ),
    Rule(
        "silent-user-bypass",
        "绕过用户确认的指令",
        "high",
        "prompt-injection",
        "skill 不应要求模型在用户不知情或未确认的情况下直接执行敏感动作。",
        r"(?:do not|don't|never)\s+(?:ask|tell|mention)[^\n]{0,80}(?:user|confirmation)|without\s+asking\s+(?:the\s+)?user|不要[^\n]{0,20}(?:询问|告知|提醒)(?:用户)?|未经(?:用户)?确认",
    ),
    Rule(
        "ignore-safety",
        "忽略前置或安全指令",
        "high",
        "prompt-injection",
        "要求忽略既有规则、安全检查或系统指令，是强 prompt injection 信号。",
        r"ignore\s+(?:all\s+)?(?:previous|prior|system|safety)\s+instructions|bypass\s+(?:guardrails|safety|restrictions)|忽略(?:所有)?(?:之前|前面|系统|安全)指令|绕过(?:安全|限制|护栏)",
    ),
    Rule(
        "terminal-social-engineering",
        "诱导用户在终端粘贴命令",
        "high",
        "social-engineering",
        "要求用户在终端复制或粘贴命令，是常见的社工安装入口。",
        r"copy\s+and\s+paste[^\n]{0,80}terminal|run\s+(?:this|the\s+following)\s+(?:command|script)[^\n]{0,40}(?:terminal|shell)|复制[^\n]{0,20}(?:到|进).{0,10}(?:终端|terminal)|在(?:终端|terminal)[^\n]{0,20}(?:运行|执行)",
    ),
    Rule(
        "password-zip",
        "带密码压缩包说明",
        "high",
        "social-engineering",
        "带密码压缩包常被用来绕过自动扫描。",
        r"password[-\s]?protected\s+(?:zip|archive)|archive\s+password\s*:|带密码(?:的)?(?:zip|压缩包|压缩文件)|压缩包密码",
    ),
    Rule(
        "quarantine-clear",
        "清除隔离属性",
        "high",
        "execution-evasion",
        "清除 macOS 隔离属性可能用于绕过安全提示后再执行。",
        r"xattr\s+-c\b",
    ),
    Rule(
        "tmp-exec",
        "临时目录执行",
        "medium",
        "execution-evasion",
        "将可执行内容放到临时目录再运行，是常见落地执行手法。",
        r"\$(?:TMPDIR|TEMP)|/tmp/|mktemp\b",
    ),
    Rule(
        "chmod-exec",
        "赋予执行权限",
        "medium",
        "execution-evasion",
        "对文件执行 chmod +x 需要结合上下文复核。",
        r"chmod\s+\+x\b",
    ),
    Rule(
        "suspicious-webhook",
        "可疑 webhook 或原始 IP 目标",
        "high",
        "exfiltration",
        "webhook 收集器、临时站点和原始 IP 经常出现在数据外传链中。",
        r"https?://(?:webhook\.site|pastebin\.com|glot\.io|gist\.githubusercontent\.com|\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?(?:/|\b)",
    ),
    Rule(
        "env-secret-access",
        "敏感环境文件访问",
        "high",
        "secret-access",
        "读取 .env 等环境文件可能暴露 API key、token 等敏感信息。",
        r"(?:^|[\s'\"/])(?:\.env|\.clawdbot/\.env|\.claude/\.env)(?:$|[\s'\"/])",
    ),
    Rule(
        "ssh-key-access",
        "SSH 私钥访问",
        "high",
        "secret-access",
        "SSH 私钥和 agent 凭据不应被 skill 读取或传输。",
        r"id_(?:rsa|dsa|ecdsa|ed25519)|\.ssh/",
    ),
    Rule(
        "browser-cookie-access",
        "浏览器数据访问",
        "high",
        "secret-access",
        "浏览器 Cookie、配置和本地数据都属于高敏感信息。",
        r"Cookies\b|Login Data\b|Web Data\b|BraveSoftware|Chrome/User Data|Firefox/Profiles|浏览器.{0,10}(?:Cookie|配置|资料|用户数据)",
    ),
    Rule(
        "wallet-access",
        "钱包或密钥库访问",
        "high",
        "secret-access",
        "钱包目录、助记词和 keystore 是常见窃取目标。",
        r"metamask|keystore|solana/id\.json|wallet|seed\s+phrase|助记词|钱包目录|密钥库",
    ),
    Rule(
        "dangerous-python-shell",
        "Python shell 执行入口",
        "medium",
        "code-exec",
        "当输入不可信或来自网络时，这类 shell 执行入口需要重点复核。",
        r"subprocess\.(?:run|Popen|call)\([^\n]{0,160}shell\s*=\s*True|os\.system\(|eval\(|exec\(",
    ),
    Rule(
        "curl-download",
        "远程下载命令",
        "medium",
        "remote-exec",
        "远程下载不一定恶意，但出现在第三方 skill 中值得复核。",
        r"\bcurl\b[^\n]{0,160}\s(?:-O|-o|--output|--remote-name|-fsSL|-sSL)|\bwget\b",
    ),
    Rule(
        "data-post",
        "POST 或上传命令",
        "medium",
        "exfiltration",
        "上传本地数据到远程目标可能意味着数据外传。",
        r"\bcurl\b[^\n]{0,160}\s(?:-d|--data|--data-binary|--upload-file)\b|requests\.post\(|fetch\([^\n]{0,100}method\s*:\s*['\"]POST['\"]",
    ),
]


@dataclass
class Finding:
    addon: str
    source: str
    rule_id: str
    title: str
    severity: str
    category: str
    rationale: str
    line: int | None
    excerpt: str

    def dedupe_key(self) -> tuple:
        return (self.addon, self.source, self.rule_id, self.line, self.excerpt)


@dataclass
class AddonReport:
    name: str
    root: str
    files_scanned: int
    findings: list[Finding]
    unsupported_files: int
    notes: list[str]

    @property
    def severity(self) -> str:
        if not self.findings:
            return "clean"
        max_weight = max(SEVERITY_ORDER[f.severity] for f in self.findings)
        if max_weight >= SEVERITY_ORDER["critical"]:
            return "critical"
        if max_weight >= SEVERITY_ORDER["high"]:
            return "high"
        if max_weight >= SEVERITY_ORDER["medium"]:
            return "medium"
        return "low"

    @property
    def summary(self) -> dict[str, int]:
        return dict(Counter(f.severity for f in self.findings))


def is_text_candidate(path: Path) -> bool:
    if path.name in TEXT_FILENAMES:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def safe_read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def discover_addons(root: Path) -> list[Path]:
    if root.is_file() and root.name.lower().endswith(".zip"):
        raise ValueError("ZIP discovery must happen after extraction")
    if (root / "SKILL.md").exists():
        return [root]
    addons = sorted({path.parent for path in root.rglob("SKILL.md")})
    return addons or [root]


def match_line_rules(addon_name: str, rel_path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    for line_num, line in enumerate(lines, start=1):
        for rule in LINE_RULES:
            if re.search(rule.pattern, line, flags=rule.flags):
                findings.append(
                    Finding(
                        addon=addon_name,
                        source=rel_path,
                        rule_id=rule.rule_id,
                        title=rule.title,
                        severity=rule.severity,
                        category=rule.category,
                        rationale=rule.rationale,
                        line=line_num,
                        excerpt=line.strip()[:240],
                    )
                )
    return findings


def find_window(lines: list[str], patterns: list[str], window_size: int = 6) -> tuple[int | None, str]:
    compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for start in range(len(lines)):
        end = min(len(lines), start + window_size)
        window = lines[start:end]
        if all(any(pattern.search(line) for line in window) for pattern in compiled):
            excerpt = " ".join(line.strip() for line in window if line.strip())[:240]
            return start + 1, excerpt or "文件级启发式命中"
    return None, "文件级启发式命中"


def match_file_heuristics(addon_name: str, rel_path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    lower = text.lower()
    lines = text.splitlines()
    exec_hint = re.search(r"(?:\./\S+|bash\s+\S+|sh\s+\S+|zsh\s+\S+)", text)

    if ("curl" in lower or "wget" in lower) and ("chmod +x" in lower) and exec_hint:
        line, excerpt = find_window(
            lines,
            [
                r"\b(?:curl|wget)\b",
                r"chmod\s+\+x\b",
                r"(?:\./\S+|bash\s+\S+|sh\s+\S+|zsh\s+\S+)",
            ],
        )
        if line is not None:
            findings.append(
                Finding(
                    addon=addon_name,
                    source=rel_path,
                    rule_id="download-execute-chain",
                    title="下载后赋权并执行",
                    severity="critical",
                    category="remote-exec",
                    rationale="联网下载后 chmod +x 并直接执行，是常见恶意安装链。",
                    line=line,
                    excerpt=excerpt,
                )
            )

    if ("base64" in lower) and ("curl" in lower or "wget" in lower) and ("bash" in lower or "sh" in lower or "zsh" in lower):
        line, excerpt = find_window(
            lines,
            [
                r"base64\s+(?:-d|--decode|-D)\b",
                r"\b(?:curl|wget)\b",
                r"\b(?:bash|sh|zsh)\b",
            ],
        )
        if line is not None:
            findings.append(
                Finding(
                    addon=addon_name,
                    source=rel_path,
                    rule_id="obfuscated-network-exec-chain",
                    title="混淆后的联网执行链",
                    severity="critical",
                    category="obfuscation",
                    rationale="混淆、联网获取和 shell 执行同时出现，是高置信度恶意信号。",
                    line=line,
                    excerpt=excerpt,
                )
            )

    if (("prereq" in lower) or ("prerequisites" in lower) or ("前置" in text) or ("先决条件" in text)) and (("terminal" in lower) or ("shell" in lower) or ("终端" in text)) and (("curl" in lower) or ("wget" in lower)):
        line, excerpt = find_window(
            lines,
            [
                r"\b(?:prereq|prerequisites)\b|前置|先决条件",
                r"\b(?:terminal|shell)\b|终端",
                r"\b(?:curl|wget)\b",
            ],
        )
        if line is not None:
            findings.append(
                Finding(
                    addon=addon_name,
                    source=rel_path,
                    rule_id="prereq-terminal-fetch",
                    title="前置步骤要求用户在终端下载远程内容",
                    severity="high",
                    category="social-engineering",
                    rationale="将远程获取命令伪装成 prerequisite，是已知社工安装手法。",
                    line=line,
                    excerpt=excerpt,
                )
            )

    if ((".env" in lower) or (".ssh" in lower) or ("id_rsa" in lower) or ("cookie" in lower) or ("钱包" in text)) and (("curl" in lower) or ("requests.post" in lower) or ("webhook.site" in lower) or ("--data" in lower)):
        line, excerpt = find_window(
            lines,
            [
                r"(?:^|[\s'\"/])(?:\.env|\.clawdbot/\.env|\.claude/\.env)(?:$|[\s'\"/])|\.ssh/|id_(?:rsa|dsa|ecdsa|ed25519)|cookie|钱包",
                r"requests\.post\(|webhook\.site|--data(?:-binary)?\b|\bcurl\b[^\n]{0,120}\s(?:-d|--data|--data-binary|--upload-file)\b",
            ],
        )
        if line is not None:
            findings.append(
                Finding(
                    addon=addon_name,
                    source=rel_path,
                    rule_id="secret-exfil-chain",
                    title="疑似敏感数据收集并外传",
                    severity="critical",
                    category="exfiltration",
                    rationale="访问敏感文件再发起外联上传，强烈指向数据外传。",
                    line=line,
                    excerpt=excerpt,
                )
            )

    return findings


def analyze_addon(addon_root: Path, display_root: Path) -> AddonReport:
    findings: list[Finding] = []
    unsupported_files = 0
    files_scanned = 0
    notes: list[str] = []

    for path in sorted(p for p in addon_root.rglob("*") if p.is_file()):
        rel_path = str(path.relative_to(addon_root))
        if not is_text_candidate(path):
            unsupported_files += 1
            continue
        text = safe_read_text(path)
        if text is None:
            unsupported_files += 1
            continue
        files_scanned += 1
        findings.extend(match_line_rules(addon_root.name, rel_path, text))
        findings.extend(match_file_heuristics(addon_root.name, rel_path, text))

    if not (addon_root / "SKILL.md").exists():
        notes.append("根目录未发现 SKILL.md；结果可能对应的是松散目录而不是标准打包 skill。")

    deduped: dict[tuple, Finding] = {}
    for finding in findings:
        deduped.setdefault(finding.dedupe_key(), finding)

    return AddonReport(
        name=addon_root.name,
        root=str(addon_root.relative_to(display_root.parent if display_root.parent != display_root else display_root)),
        files_scanned=files_scanned,
        findings=sorted(deduped.values(), key=lambda f: (-SEVERITY_ORDER[f.severity], f.source, f.line or 0, f.rule_id)),
        unsupported_files=unsupported_files,
        notes=notes,
    )


def analyze_target(target: Path) -> tuple[list[AddonReport], list[tempfile.TemporaryDirectory[str]]]:
    temp_dirs: list[tempfile.TemporaryDirectory[str]] = []
    target = target.resolve()

    if not target.exists():
        raise FileNotFoundError(f"Target not found: {target}")

    if target.is_file() and target.suffix.lower() == ".zip":
        temp_dir = tempfile.TemporaryDirectory(prefix="addon_audit_")
        temp_dirs.append(temp_dir)
        with zipfile.ZipFile(target) as zf:
            zf.extractall(temp_dir.name)
        extracted_root = Path(temp_dir.name)
        addons = discover_addons(extracted_root)
        return [analyze_addon(addon, extracted_root) for addon in addons], temp_dirs

    if target.is_dir():
        addons = discover_addons(target)
        return [analyze_addon(addon, target) for addon in addons], temp_dirs

    raise ValueError(f"Unsupported target type: {target}")


def overall_severity(reports: Iterable[AddonReport]) -> str:
    reports = list(reports)
    if not reports:
        return "clean"
    ranking = {"clean": 0, **SEVERITY_ORDER}
    return max((r.severity for r in reports), key=lambda value: ranking[value])


def reports_to_json(targets: list[str], reports: list[AddonReport]) -> str:
    payload = {
        "targets": targets,
        "summary": {
            "addons": len(reports),
            "findings": sum(len(r.findings) for r in reports),
            "by_severity": dict(Counter(f.severity for r in reports for f in r.findings)),
            "overall": overall_severity(reports),
        },
        "reports": [
            {
                "name": r.name,
                "root": r.root,
                "severity": r.severity,
                "severity_zh": SEVERITY_LABELS[r.severity],
                "recommended_action_zh": ACTION_LABELS[r.severity],
                "files_scanned": r.files_scanned,
                "unsupported_files": r.unsupported_files,
                "summary": r.summary,
                "notes": r.notes,
                "findings": [asdict(f) for f in r.findings],
            }
            for r in reports
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def top_findings(report: AddonReport, limit: int = 8) -> list[Finding]:
    ordered = sorted(report.findings, key=lambda f: (-SEVERITY_ORDER[f.severity], f.source, f.line or 0, f.rule_id))
    return ordered[:limit]


def reports_to_markdown(targets: list[str], reports: list[AddonReport]) -> str:
    overall = overall_severity(reports)
    total_findings = sum(len(r.findings) for r in reports)
    lines = [
        "# 中文技能审计报告",
        "",
        "## 审计结论",
        f"- 扫描目标：{', '.join(targets)}",
        f"- 分析的 skill 数量：{len(reports)}",
        f"- 总命中数：{total_findings}",
        f"- 最高风险级别：**{SEVERITY_LABELS[overall]}**",
        f"- 建议动作：**{ACTION_LABELS[overall]}**",
        "",
    ]

    for report in reports:
        lines.extend([
            f"## Skill：{report.name}",
            f"- 风险级别：**{SEVERITY_LABELS[report.severity]}**",
            f"- 建议动作：**{ACTION_LABELS[report.severity]}**",
            f"- 已扫描文本文件：{report.files_scanned}",
            f"- 跳过或不支持的文件：{report.unsupported_files}",
        ])
        if report.summary:
            summary_text = "，".join(
                f"{SEVERITY_LABELS[k]} {v} 条"
                for k, v in sorted(report.summary.items(), key=lambda item: -SEVERITY_ORDER[item[0]])
            )
            lines.append(f"- 命中分布：{summary_text}")
        for note in report.notes:
            lines.append(f"- 备注：{note}")
        lines.append("")
        lines.append("### 关键发现")
        if not report.findings:
            lines.append("- 未发现与当前规则集直接匹配的明显风险模式。")
        else:
            for finding in top_findings(report):
                loc = f"{finding.source}:{finding.line}" if finding.line else finding.source
                lines.append(f"- [{SEVERITY_LABELS[finding.severity]}] {finding.title}（规则：{finding.rule_id}）")
                lines.append(f"  - 位置：{loc}")
                lines.append(f"  - 证据：`{finding.excerpt}`")
                lines.append(f"  - 原因：{finding.rationale}")
        lines.append("")
        lines.append("### 修复建议")
        if report.severity in {"critical", "high"}:
            lines.extend([
                "- 删除所有让用户复制到终端执行的安装步骤，禁止远程脚本直连执行。",
                "- 移除读取 `.env`、SSH key、浏览器数据、钱包目录等敏感路径的逻辑。",
                "- 删除任何要求模型忽略安全规则、跳过确认或绕过限制的指令。",
                "- 把所有依赖改为可审计的本地打包文件，不要在运行时临时下载执行。",
            ])
        elif report.severity == "medium":
            lines.extend([
                "- 结合上下文人工检查相关命令是否真的必要，尤其是下载、临时目录和 shell 执行入口。",
                "- 对涉及联网和执行权限的步骤增加明确注释与用户确认。",
            ])
        else:
            lines.extend([
                "- 当前未见明显高风险模式，但仍建议在沙箱中试运行并做一次人工复核。",
                "- 新增依赖、脚本或安装文档后重新审计。",
            ])
        lines.append("")

    lines.extend([
        "## 处置建议",
        f"- 本次整体建议：**{ACTION_LABELS[overall]}**",
        "- 严重 / 高危：不要安装，不要执行，并对命中文件逐项人工复核。",
        "- 中危：结合上下文继续检查，再决定是否允许。",
        "- 未发现明显风险：不代表绝对安全，仍建议沙箱运行。",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit third-party agent add-ons and skills for prompt injection and malware-like patterns.")
    parser.add_argument("targets", nargs="+", help="One or more skill folders, zip files, or directories containing multiple skills")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_reports: list[AddonReport] = []
    temp_dirs: list[tempfile.TemporaryDirectory[str]] = []
    try:
        for raw_target in args.targets:
            reports, temps = analyze_target(Path(raw_target))
            all_reports.extend(reports)
            temp_dirs.extend(temps)
        if args.format == "json":
            print(reports_to_json(args.targets, all_reports))
        else:
            print(reports_to_markdown(args.targets, all_reports))
        return 0
    finally:
        for temp_dir in temp_dirs:
            temp_dir.cleanup()


if __name__ == "__main__":
    sys.exit(main())
