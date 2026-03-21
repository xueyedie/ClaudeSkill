#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"
JOBS_DIR = OUTPUT_DIR / "jobs"
DOWNLOAD_SCRIPT = SKILL_DIR / "scripts" / "download_video_and_subtitles.py"
DEFAULT_POLL_INTERVAL = 5
SUMMARY_PROMPT = """请基于这份视频字幕，用简洁中文输出一份结构清晰的总结。

输出格式请尽量保持如下结构：

一句话概览：
<1-2 句，概括视频主旨>

核心要点：
- <要点 1>
- <要点 2>
- <要点 3>
- <要点 4>

关键论据或例子：
- <例子/论据 1>
- <例子/论据 2>

对我的启发：
- <可执行建议 1>
- <可执行建议 2>

要求：
- 只基于字幕内容总结，不要编造画面信息
- 如果字幕里有明显识别噪声，请忽略噪声后按语义归纳
- 保持紧凑、清晰、适合直接发到 IM
- 不要输出多余前言
"""

MAX_DINGTALK_MEDIA_BYTES = 20 * 1024 * 1024


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_json_from_mixed_output(text: str) -> dict[str, Any] | None:
    candidate = (text or "").strip()
    if not candidate:
        return None
    decoder = json.JSONDecoder()
    starts = [idx for idx, ch in enumerate(candidate) if ch == "{"] + [
        idx for idx, ch in enumerate(candidate) if ch == "["
    ]
    for start in reversed(starts):
        try:
            parsed, end = decoder.raw_decode(candidate[start:])
        except json.JSONDecodeError:
            continue
        if candidate[start + end :].strip():
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def sanitize_id(value: str) -> str:
    return "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"}) or "unknown"


def build_job_id() -> str:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    token = secrets.token_hex(3)
    return f"sgp-{stamp}-{token}"


def job_dir_for(job_id: str) -> Path:
    return JOBS_DIR / job_id


def state_path_for(job_id: str) -> Path:
    return job_dir_for(job_id) / "state.json"


def load_state(job_id: str) -> dict[str, Any]:
    return read_json(state_path_for(job_id))


def save_state(job_id: str, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    atomic_write_json(state_path_for(job_id), state)


def update_state(job_id: str, **fields: Any) -> dict[str, Any]:
    state = load_state(job_id)
    state.update(fields)
    save_state(job_id, state)
    return state


def update_nested_state(job_id: str, section: str, **fields: Any) -> dict[str, Any]:
    state = load_state(job_id)
    node = dict(state.get(section) or {})
    node.update(fields)
    state[section] = node
    save_state(job_id, state)
    return state


def ensure_binary(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"当前环境没有可用的 {name} 命令。")
    return resolved


def spawn_background(command: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
            close_fds=True,
        )
    return proc.pid


def load_download_module():
    spec = importlib.util.spec_from_file_location("streamgrab_download", DOWNLOAD_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError(f"无法加载下载脚本：{DOWNLOAD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def send_im_message(
    *,
    channel: str,
    target: str,
    message: str | None = None,
    media: str | None = None,
    reply_to: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    openclaw_bin = ensure_binary("openclaw")
    command = [openclaw_bin, "message", "send", "--json", "--channel", channel, "--target", target]
    if message:
        command.extend(["--message", message])
    if media:
        command.extend(["--media", media])
    if reply_to:
        command.extend(["--reply-to", reply_to])
    if dry_run:
        command.append("--dry-run")
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "openclaw message send failed"
        raise RuntimeError(detail)
    stdout = (proc.stdout or "").strip()
    return json.loads(stdout) if stdout.startswith("{") else {"raw": stdout}


def build_no_subtitle_message(state: dict[str, Any]) -> str:
    title = state.get("title") or "这个视频"
    job_id = state["job_id"]
    return (
        f"《{title}》的视频我已经发给你了，但这次没有抓到平台字幕。\n"
        "如果你需要我继续用 Whisper 转录字幕，直接回复“需要”即可。"
        f"\n如果当前会话里同时有多个待转录任务，也可以回复：需要 {job_id}"
    )


def build_auth_required_message(state: dict[str, Any], result: dict[str, Any]) -> str:
    hint = result.get("hint") or "平台可能需要登录态。"
    return (
        f"这个视频暂时没能下载成功。\n原因：{result.get('error', 'unknown error')}\n"
        f"建议：{hint}\n"
        "你可以让我继续时选择两种方式之一：登录托管浏览器，或提供 cookies.txt。"
    )


def build_failure_message(prefix: str, detail: str) -> str:
    return f"{prefix}\n原因：{detail}"


def choose_subtitle_attachment(subtitles: dict[str, Any] | None) -> str | None:
    if not subtitles:
        return None
    for key in ("srt_file", "raw_file", "txt_file"):
        value = subtitles.get(key)
        if value:
            return value
    return None


def format_size(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f}MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f}KB"
    return f"{num_bytes}B"


def build_media_path_message(label: str, media_path: str, reason: str | None = None) -> str:
    if reason:
        return f"{label}没有作为附件发送成功。\n原因：{reason}\n本地路径：{media_path}"
    return f"{label}没有作为附件发送，改为提供本地路径。\n本地路径：{media_path}"


def send_media_or_path(
    *,
    state: dict[str, Any],
    media_path: str,
    attachment_message: str,
    path_label: str,
) -> None:
    path_obj = Path(media_path)
    try:
        media_size = path_obj.stat().st_size
    except FileNotFoundError:
        send_im_message(
            channel=state["channel"],
            target=state["target"],
            message=build_media_path_message(path_label, media_path, "本地文件不存在"),
            reply_to=state.get("reply_to"),
            dry_run=bool(state.get("message_dry_run")),
        )
        return

    if media_size > MAX_DINGTALK_MEDIA_BYTES:
        send_im_message(
            channel=state["channel"],
            target=state["target"],
            message=build_media_path_message(
                path_label,
                media_path,
                f"文件大小 {format_size(media_size)}，超过机器人媒体上传 20MB 限制",
            ),
            reply_to=state.get("reply_to"),
            dry_run=bool(state.get("message_dry_run")),
        )
        return

    try:
        send_im_message(
            channel=state["channel"],
            target=state["target"],
            media=media_path,
            message=attachment_message,
            reply_to=state.get("reply_to"),
            dry_run=bool(state.get("message_dry_run")),
        )
    except Exception as exc:
        send_im_message(
            channel=state["channel"],
            target=state["target"],
            message=build_media_path_message(path_label, media_path, str(exc)),
            reply_to=state.get("reply_to"),
            dry_run=bool(state.get("message_dry_run")),
        )


def summarize_transcript(transcript_path: Path, model: str | None) -> str:
    summarize_bin = ensure_binary("summarize")
    command = [
        summarize_bin,
        str(transcript_path),
        "--length",
        "short",
        "--max-output-tokens",
        "700",
        "--prompt",
        SUMMARY_PROMPT,
    ]
    if model:
        command.extend(["--model", model])
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    detail = proc.stderr.strip() or proc.stdout.strip() or "summarize failed"
    raise RuntimeError(detail)


def fallback_summary(state: dict[str, Any], transcript_path: Path, summary_error: str) -> str:
    lines = [
        line.strip()
        for line in transcript_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip()
    ]
    preview = "\n".join(f"- {line}" for line in lines[:6]) if lines else "- 字幕内容为空或不可读。"
    title = state.get("title") or "这个视频"
    return (
        f"一句话概览：\n《{title}》的字幕已经提取完成，但自动总结这次没有成功生成。\n\n"
        f"核心片段预览：\n{preview}\n\n"
        f"说明：\n- 自动总结失败原因：{summary_error}\n- 你可以直接查看我刚发给你的字幕文件。"
    )


def create_initial_state(args: argparse.Namespace, job_id: str) -> dict[str, Any]:
    job_dir = job_dir_for(job_id)
    logs_dir = job_dir / "logs"
    run = {
        "job_id": job_id,
        "job_dir": str(job_dir),
        "status": "download_queued",
        "url": args.url,
        "channel": args.channel,
        "target": args.target,
        "reply_to": args.reply_to,
        "auth": args.auth,
        "browser_profile": args.browser_profile,
        "lang": args.lang,
        "subtitle_source": args.subtitle_source,
        "summary_model": args.summary_model,
        "message_dry_run": bool(args.message_dry_run),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "title": None,
        "platform": None,
        "video_file": None,
        "subtitles": None,
        "download": {
            "worker_pid": None,
            "watcher_pid": None,
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
        },
        "whisper": {
            "requested": False,
            "model": args.whisper_model,
            "language": args.whisper_language,
            "model_dir": args.whisper_model_dir,
            "worker_pid": None,
            "watcher_pid": None,
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
        },
        "delivery": {
            "video_sent": False,
            "subtitle_sent": False,
            "summary_sent": False,
            "whisper_prompt_sent": False,
            "auth_message_sent": False,
            "failure_message_sent": False,
        },
        "logs": {
            "download_worker": str(logs_dir / "download-worker.log"),
            "download_watcher": str(logs_dir / "download-watcher.log"),
            "whisper_worker": str(logs_dir / "whisper-worker.log"),
            "whisper_watcher": str(logs_dir / "whisper-watcher.log"),
        },
    }
    save_state(job_id, run)
    return run


def start_download(args: argparse.Namespace) -> int:
    job_id = build_job_id()
    state = create_initial_state(args, job_id)
    script = Path(__file__).resolve()
    worker_pid = spawn_background(
        [sys.executable, str(script), "worker-download", "--job-id", job_id],
        Path(state["logs"]["download_worker"]),
    )
    watcher_pid = spawn_background(
        [sys.executable, str(script), "watch-download", "--job-id", job_id],
        Path(state["logs"]["download_watcher"]),
    )
    state["download"]["worker_pid"] = worker_pid
    state["download"]["watcher_pid"] = watcher_pid
    save_state(job_id, state)
    print(
        json.dumps(
            {
                "success": True,
                "job_id": job_id,
                "status": state["status"],
                "job_dir": state["job_dir"],
                "worker_pid": worker_pid,
                "watcher_pid": watcher_pid,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def worker_download(args: argparse.Namespace) -> int:
    state = update_state(args.job_id, status="download_running")
    update_nested_state(args.job_id, "download", started_at=now_iso())
    command = [
        sys.executable,
        str(DOWNLOAD_SCRIPT),
        state["url"],
        "--format",
        "json",
        "--disable-whisper-fallback",
        "--auth",
        state.get("auth") or "auto",
        "--browser-profile",
        state.get("browser_profile") or "openclaw",
        "--subtitle-source",
        state.get("subtitle_source") or "best",
    ]
    if state.get("lang"):
        command.extend(["--lang", state["lang"]])
    proc = subprocess.run(command, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    result_path = job_dir_for(args.job_id) / "download-result.json"
    parsed: dict[str, Any]
    parsed_json = parse_json_from_mixed_output(stdout)
    if parsed_json is not None:
        parsed = parsed_json
    else:
        parsed = {
            "success": False,
            "error": stderr or stdout or "下载脚本没有返回可解析 JSON。",
            "raw_stdout": stdout,
            "raw_stderr": stderr,
        }
    atomic_write_json(result_path, parsed)
    fields: dict[str, Any] = {
        "title": parsed.get("title"),
        "platform": parsed.get("platform"),
        "video_file": parsed.get("video_file"),
        "subtitles": parsed.get("subtitles"),
        "download_result_path": str(result_path),
    }
    state = update_state(args.job_id, **fields)
    update_nested_state(
        args.job_id,
        "download",
        finished_at=now_iso(),
        result=parsed,
        error=None if parsed.get("success") else parsed.get("error"),
    )
    if parsed.get("success"):
        if parsed.get("subtitles"):
            update_state(args.job_id, status="download_completed")
        else:
            update_state(args.job_id, status="awaiting_whisper_confirm")
        return 0
    if parsed.get("auth_required"):
        update_state(args.job_id, status="auth_required")
        return 1
    update_state(args.job_id, status="download_failed")
    return 1


def wait_for_status(job_id: str, active_statuses: set[str], poll_interval: int) -> dict[str, Any]:
    while True:
        state = load_state(job_id)
        status = state.get("status") or ""
        if status not in active_statuses:
            return state
        time.sleep(poll_interval)


def send_summary_for_state(state: dict[str, Any], subtitles: dict[str, Any]) -> None:
    transcript_file = subtitles.get("txt_file")
    if not transcript_file:
        return
    transcript_path = Path(transcript_file)
    if not transcript_path.exists():
        return
    try:
        summary_text = summarize_transcript(transcript_path, state.get("summary_model"))
    except Exception as exc:
        summary_text = fallback_summary(state, transcript_path, str(exc))
    send_im_message(
        channel=state["channel"],
        target=state["target"],
        message=summary_text,
        reply_to=state.get("reply_to"),
        dry_run=bool(state.get("message_dry_run")),
    )
    update_nested_state(state["job_id"], "delivery", summary_sent=True)


def deliver_download_completion(job_id: str, state: dict[str, Any]) -> None:
    delivery = state.get("delivery") or {}
    if not delivery.get("video_sent") and state.get("video_file"):
        send_media_or_path(
            state=state,
            media_path=state["video_file"],
            attachment_message=f"视频文件：{state.get('title') or '下载结果'}",
            path_label="视频文件",
        )
        state = update_nested_state(job_id, "delivery", video_sent=True)
        delivery = state["delivery"]

    subtitles = state.get("subtitles")
    if subtitles:
        subtitle_file = choose_subtitle_attachment(subtitles)
        if subtitle_file and not delivery.get("subtitle_sent"):
            source = subtitles.get("source") or "platform"
            send_media_or_path(
                state=state,
                media_path=subtitle_file,
                attachment_message=f"字幕文件（来源：{source}）",
                path_label="字幕文件",
            )
            state = update_nested_state(job_id, "delivery", subtitle_sent=True)
        send_summary_for_state(state, subtitles)
        update_state(job_id, status="completed")
        return

    if not delivery.get("whisper_prompt_sent"):
        send_im_message(
            channel=state["channel"],
            target=state["target"],
            message=build_no_subtitle_message(state),
            reply_to=state.get("reply_to"),
            dry_run=bool(state.get("message_dry_run")),
        )
        update_nested_state(job_id, "delivery", whisper_prompt_sent=True)


def watch_download(args: argparse.Namespace) -> int:
    state = wait_for_status(args.job_id, {"download_queued", "download_running"}, args.poll_interval)
    status = state.get("status")
    if status == "download_completed":
        deliver_download_completion(args.job_id, state)
        return 0
    if status == "awaiting_whisper_confirm":
        deliver_download_completion(args.job_id, state)
        return 0
    if status == "auth_required":
        delivery = state.get("delivery") or {}
        if not delivery.get("auth_message_sent"):
            result = (state.get("download") or {}).get("result") or {}
            send_im_message(
                channel=state["channel"],
                target=state["target"],
                message=build_auth_required_message(state, result),
                reply_to=state.get("reply_to"),
                dry_run=bool(state.get("message_dry_run")),
            )
            update_nested_state(args.job_id, "delivery", auth_message_sent=True)
        return 0
    if status == "download_failed":
        delivery = state.get("delivery") or {}
        if not delivery.get("failure_message_sent"):
            error = ((state.get("download") or {}).get("result") or {}).get("error") or "下载失败"
            send_im_message(
                channel=state["channel"],
                target=state["target"],
                message=build_failure_message("视频下载失败。", error),
                reply_to=state.get("reply_to"),
                dry_run=bool(state.get("message_dry_run")),
            )
            update_nested_state(args.job_id, "delivery", failure_message_sent=True)
        return 0
    return 0


def find_waiting_job(channel: str, target: str, job_id: str | None = None) -> dict[str, Any]:
    if job_id:
        state = load_state(job_id)
        if state.get("status") != "awaiting_whisper_confirm":
            raise RuntimeError(f"job {job_id} 当前不在等待 Whisper 确认状态。")
        return state
    candidates: list[dict[str, Any]] = []
    if not JOBS_DIR.exists():
        raise RuntimeError("当前没有可恢复的 StreamGrabPro 后台任务。")
    for child in JOBS_DIR.iterdir():
        state_file = child / "state.json"
        if not state_file.exists():
            continue
        state = read_json(state_file)
        if state.get("channel") != channel or state.get("target") != target:
            continue
        if state.get("status") != "awaiting_whisper_confirm":
            continue
        candidates.append(state)
    if not candidates:
        raise RuntimeError("没有找到等待 Whisper 确认的后台任务。")
    if len(candidates) > 1:
        candidates.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
        latest = candidates[0]
        latest["warning"] = "找到多个待转录任务，已默认选择最新的一条。"
        return latest
    return candidates[0]


def start_whisper(args: argparse.Namespace) -> int:
    state = find_waiting_job(args.channel, args.target, args.job_id)
    job_id = state["job_id"]
    script = Path(__file__).resolve()
    update_state(
        job_id,
        status="whisper_queued",
        subtitles=None,
    )
    update_nested_state(
        job_id,
        "whisper",
        requested=True,
        model=args.whisper_model or state.get("whisper", {}).get("model") or "small",
        language=args.whisper_language,
        model_dir=args.whisper_model_dir or state.get("whisper", {}).get("model_dir") or "/tmp/whisper-models",
    )
    updated = load_state(job_id)
    worker_pid = spawn_background(
        [sys.executable, str(script), "worker-whisper", "--job-id", job_id],
        Path(updated["logs"]["whisper_worker"]),
    )
    watcher_pid = spawn_background(
        [sys.executable, str(script), "watch-whisper", "--job-id", job_id],
        Path(updated["logs"]["whisper_watcher"]),
    )
    update_nested_state(job_id, "whisper", worker_pid=worker_pid, watcher_pid=watcher_pid)
    print(
        json.dumps(
            {
                "success": True,
                "job_id": job_id,
                "status": "whisper_queued",
                "worker_pid": worker_pid,
                "watcher_pid": watcher_pid,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def worker_whisper(args: argparse.Namespace) -> int:
    state = update_state(args.job_id, status="whisper_running")
    update_nested_state(args.job_id, "whisper", started_at=now_iso())
    if not state.get("video_file"):
        update_nested_state(args.job_id, "whisper", finished_at=now_iso(), error="缺少 video_file")
        update_state(args.job_id, status="whisper_failed")
        return 1
    run_dir = Path((state.get("download") or {}).get("result", {}).get("output_dir") or state.get("job_dir"))
    subtitle_dir = run_dir / "subtitles"
    subtitle_dir.mkdir(parents=True, exist_ok=True)
    whisper_cfg = state.get("whisper") or {}
    module = load_download_module()
    try:
        result = module.run_whisper_fallback(
            video_file=Path(state["video_file"]),
            subtitle_dir=subtitle_dir,
            model=whisper_cfg.get("model") or "small",
            model_dir=Path(whisper_cfg.get("model_dir") or "/tmp/whisper-models"),
            language=whisper_cfg.get("language"),
        )
    except Exception as exc:
        update_nested_state(args.job_id, "whisper", finished_at=now_iso(), error=str(exc))
        update_state(args.job_id, status="whisper_failed")
        return 1
    result_path = job_dir_for(args.job_id) / "whisper-result.json"
    atomic_write_json(result_path, result)
    update_nested_state(
        args.job_id,
        "whisper",
        finished_at=now_iso(),
        result=result,
        error=None,
        result_path=str(result_path),
    )
    update_state(args.job_id, status="whisper_completed", subtitles=result)
    return 0


def watch_whisper(args: argparse.Namespace) -> int:
    state = wait_for_status(args.job_id, {"whisper_queued", "whisper_running"}, args.poll_interval)
    status = state.get("status")
    if status == "whisper_completed":
        subtitles = state.get("subtitles") or (state.get("whisper") or {}).get("result")
        if subtitles:
            subtitle_file = choose_subtitle_attachment(subtitles)
            delivery = state.get("delivery") or {}
            if subtitle_file and not delivery.get("subtitle_sent"):
                send_media_or_path(
                    state=state,
                    media_path=subtitle_file,
                    attachment_message=f"Whisper 字幕文件（模型：{(state.get('whisper') or {}).get('model') or 'small'}）",
                    path_label="Whisper 字幕文件",
                )
                state = update_nested_state(args.job_id, "delivery", subtitle_sent=True)
            send_summary_for_state(state, subtitles)
            update_state(args.job_id, status="completed")
        return 0
    if status == "whisper_failed":
        delivery = state.get("delivery") or {}
        if not delivery.get("failure_message_sent"):
            error = (state.get("whisper") or {}).get("error") or "Whisper 转录失败"
            send_im_message(
                channel=state["channel"],
                target=state["target"],
                message=build_failure_message("Whisper 转录没有成功完成。", error),
                reply_to=state.get("reply_to"),
                dry_run=bool(state.get("message_dry_run")),
            )
            update_nested_state(args.job_id, "delivery", failure_message_sent=True)
        return 0
    return 0


def show_status(args: argparse.Namespace) -> int:
    if args.job_id:
        state = load_state(args.job_id)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    if not JOBS_DIR.exists():
        print("[]")
        return 0
    items = []
    for child in sorted(JOBS_DIR.iterdir()):
        state_file = child / "state.json"
        if not state_file.exists():
            continue
        state = read_json(state_file)
        items.append(
            {
                "job_id": state.get("job_id"),
                "status": state.get("status"),
                "title": state.get("title"),
                "url": state.get("url"),
                "channel": state.get("channel"),
                "target": state.get("target"),
                "updated_at": state.get("updated_at"),
            }
        )
    print(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistent background jobs for StreamGrabPro")
    sub = parser.add_subparsers(dest="command", required=True)

    start_download_parser = sub.add_parser("start-download")
    start_download_parser.add_argument("url")
    start_download_parser.add_argument("--channel", required=True)
    start_download_parser.add_argument("--target", required=True)
    start_download_parser.add_argument("--reply-to", default=None)
    start_download_parser.add_argument("--auth", default="auto")
    start_download_parser.add_argument("--browser-profile", default="openclaw")
    start_download_parser.add_argument("--lang", default=None)
    start_download_parser.add_argument("--subtitle-source", default="best")
    start_download_parser.add_argument("--whisper-model", default="small")
    start_download_parser.add_argument("--whisper-model-dir", default="/tmp/whisper-models")
    start_download_parser.add_argument("--whisper-language", default=None)
    start_download_parser.add_argument("--summary-model", default=None)
    start_download_parser.add_argument("--message-dry-run", action="store_true")
    start_download_parser.set_defaults(func=start_download)

    worker_download_parser = sub.add_parser("worker-download")
    worker_download_parser.add_argument("--job-id", required=True)
    worker_download_parser.set_defaults(func=worker_download)

    watch_download_parser = sub.add_parser("watch-download")
    watch_download_parser.add_argument("--job-id", required=True)
    watch_download_parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL)
    watch_download_parser.set_defaults(func=watch_download)

    start_whisper_parser = sub.add_parser("start-whisper")
    start_whisper_parser.add_argument("--channel", required=True)
    start_whisper_parser.add_argument("--target", required=True)
    start_whisper_parser.add_argument("--job-id", default=None)
    start_whisper_parser.add_argument("--whisper-model", default="small")
    start_whisper_parser.add_argument("--whisper-model-dir", default="/tmp/whisper-models")
    start_whisper_parser.add_argument("--whisper-language", default=None)
    start_whisper_parser.set_defaults(func=start_whisper)

    worker_whisper_parser = sub.add_parser("worker-whisper")
    worker_whisper_parser.add_argument("--job-id", required=True)
    worker_whisper_parser.set_defaults(func=worker_whisper)

    watch_whisper_parser = sub.add_parser("watch-whisper")
    watch_whisper_parser.add_argument("--job-id", required=True)
    watch_whisper_parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL)
    watch_whisper_parser.set_defaults(func=watch_whisper)

    status_parser = sub.add_parser("status")
    status_parser.add_argument("--job-id", default=None)
    status_parser.set_defaults(func=show_status)

    return parser


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
