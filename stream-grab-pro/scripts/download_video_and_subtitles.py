#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

import yt_dlp

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"
COOKIE_FILE = SKILL_DIR / "cookies.txt"
MANAGED_BROWSER_ROOT = Path.home() / ".openclaw" / "browser"
DEFAULT_BROWSER_PROFILE = "openclaw"
DEFAULT_BROWSER_ENGINE = "chrome"
DEFAULT_WHISPER_MODEL = "small"
DEFAULT_WHISPER_MODEL_DIR = Path("/tmp/whisper-models")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
AUTH_MODES = {"auto", "cookies", "managed_browser", "none"}
SUBTITLE_SOURCE_PREFERENCES = {"best", "manual", "automatic"}
PREFERRED_LANGUAGES = ["zh-Hans", "zh-CN", "zh", "zh-TW", "en"]
RAW_SUBTITLE_EXTENSIONS = {
    ".vtt",
    ".srt",
    ".ttml",
    ".xml",
    ".json",
    ".json3",
    ".srv1",
    ".srv2",
    ".srv3",
    ".ass",
    ".ssa",
}
PLATFORMS = {
    "youtube": ["youtube.com", "youtu.be"],
    "tiktok": ["tiktok.com"],
    "douyin": ["douyin.com"],
    "bilibili": ["bilibili.com", "b23.tv"],
    "tencent": ["v.qq.com"],
    "youku": ["youku.com"],
    "iqiyi": ["iqiyi.com"],
    "mango": ["mgtv.com"],
    "kuaishou": ["kuaishou.com", "kwai.com"],
    "xiaohongshu": ["xiaohongshu.com", "xhslink.com"],
    "xigua": ["ixigua.com"],
}


def detect_platform(url: str) -> str:
    for name, domains in PLATFORMS.items():
        for domain in domains:
            if domain in url:
                return name
    return "unknown"


def normalize_auth_mode(value: str | None) -> str:
    mode = (value or "auto").strip().lower().replace("-", "_")
    return mode if mode in AUTH_MODES else "auto"


def normalize_source_preference(value: str | None) -> str:
    source = (value or "best").strip().lower()
    return source if source in SUBTITLE_SOURCE_PREFERENCES else "best"


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]+', "-", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.strip(".")
    return value or "untitled-video"


def make_error_hint(message: str) -> str:
    lowered = message.lower()
    if "operation not permitted" in lowered or "permission denied" in lowered:
        return "当前环境没有写入目标目录的权限。请在可写环境中重试。"
    if "412" in message:
        return "平台返回 412 错误。请先登录托管浏览器或提供 cookies.txt。"
    if "403" in message or "not a bot" in lowered or "confirm you're not a bot" in lowered:
        return "平台可能需要登录态。请先登录托管浏览器或提供 cookies.txt。"
    if "429" in message:
        return "请求过于频繁，请稍后再试。"
    if "login" in lowered or "sign in" in lowered:
        return "此视频需要登录才能访问。请先登录托管浏览器或提供 cookies.txt。"
    if "geo" in lowered or "region" in lowered or "not available" in lowered:
        return "此视频可能有地区限制。"
    if "cookie" in lowered:
        return "鉴权可能有问题。请检查 cookies.txt 或托管浏览器登录态。"
    return ""


def auth_required_from_message(message: str) -> bool:
    lowered = message.lower()
    markers = [
        "login",
        "sign in",
        "cookie",
        "cookies",
        "not a bot",
        "confirm you're not a bot",
        "412",
        "403",
    ]
    return any(marker in lowered for marker in markers)


def get_managed_browser_profile_dir(profile_name: str | None) -> Path:
    profile = (profile_name or DEFAULT_BROWSER_PROFILE).strip() or DEFAULT_BROWSER_PROFILE
    return MANAGED_BROWSER_ROOT / profile / "user-data"


def apply_auth_to_opts(opts: dict, auth_mode: str, browser_profile: str | None) -> list[str]:
    sources: list[str] = []
    profile_dir = get_managed_browser_profile_dir(browser_profile)

    if auth_mode == "cookies":
        if not COOKIE_FILE.exists():
            raise FileNotFoundError(f"cookies.txt 不存在：{COOKIE_FILE}")
        opts["cookiefile"] = str(COOKIE_FILE)
        sources.append("cookies.txt")
        return sources

    if auth_mode == "managed_browser":
        if not profile_dir.exists():
            raise FileNotFoundError(
                f"托管浏览器 profile 不存在：{profile_dir}。请先让用户登录托管浏览器。"
            )
        opts["cookiesfrombrowser"] = (DEFAULT_BROWSER_ENGINE, str(profile_dir), None, None)
        sources.append(f"managed-browser:{profile_dir.parent.name}")
        return sources

    if auth_mode == "auto":
        if COOKIE_FILE.exists():
            opts["cookiefile"] = str(COOKIE_FILE)
            sources.append("cookies.txt")
        if profile_dir.exists():
            opts["cookiesfrombrowser"] = (DEFAULT_BROWSER_ENGINE, str(profile_dir), None, None)
            sources.append(f"managed-browser:{profile_dir.parent.name}")

    return sources


proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or None


def get_platform_headers(platform: str) -> dict:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    referer_map = {
        "bilibili": "https://www.bilibili.com/",
        "youtube": "https://www.youtube.com/",
        "douyin": "https://www.douyin.com/",
        "tiktok": "https://www.tiktok.com/",
        "tencent": "https://v.qq.com/",
        "youku": "https://www.youku.com/",
        "iqiyi": "https://www.iqiyi.com/",
        "mango": "https://www.mgtv.com/",
        "kuaishou": "https://www.kuaishou.com/",
        "xiaohongshu": "https://www.xiaohongshu.com/",
        "xigua": "https://www.ixigua.com/",
    }
    if platform in referer_map:
        headers["Referer"] = referer_map[platform]
        headers["Origin"] = referer_map[platform].rstrip("/")
    return headers


def get_base_opts(
    platform: str,
    *,
    auth_mode: str,
    browser_profile: str,
) -> tuple[dict, list[str]]:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "user_agent": USER_AGENT,
        "socket_timeout": 30,
        "retries": 5,
        "extractor_retries": 5,
        "nocheckcertificate": True,
        "http_headers": get_platform_headers(platform),
    }
    if proxy:
        opts["proxy"] = proxy
    auth_sources = apply_auth_to_opts(opts, auth_mode, browser_profile)
    return opts, auth_sources


def build_format_selector() -> str:
    return (
        "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/"
        "bestvideo[vcodec^=avc]+bestaudio/"
        "bestvideo+bestaudio/"
        "best"
    )


def prettify_language(code: str, track_formats: list[dict] | None = None) -> str:
    if track_formats:
        for item in track_formats:
            if item.get("name"):
                return f"{code} ({item['name']})"
    return code


def extract_subtitle_tracks(info: dict) -> list[dict]:
    manual = info.get("subtitles") or {}
    automatic = info.get("automatic_captions") or {}
    merged: dict[str, dict] = {}

    def add_tracks(source_name: str, mapping: dict):
        for language, formats in mapping.items():
            entry = merged.setdefault(
                language,
                {
                    "language": language,
                    "label": language,
                    "manual_available": False,
                    "automatic_available": False,
                    "formats": set(),
                },
            )
            entry["label"] = prettify_language(language, formats)
            entry["formats"].update(item.get("ext") for item in formats if item.get("ext"))
            if source_name == "manual":
                entry["manual_available"] = True
            else:
                entry["automatic_available"] = True

    add_tracks("manual", manual)
    add_tracks("automatic", automatic)

    tracks = []
    for entry in merged.values():
        if entry["manual_available"] and entry["automatic_available"]:
            source = "manual+automatic"
        elif entry["manual_available"]:
            source = "manual"
        else:
            source = "automatic"
        tracks.append({
            "language": entry["language"],
            "label": entry["label"],
            "source": source,
            "formats": sorted(entry["formats"]),
        })
    tracks.sort(key=lambda item: (0 if item["source"].startswith("manual") else 1, item["language"]))
    return tracks


def choose_subtitle_track(tracks: list[dict], requested_language: str | None) -> dict:
    if not tracks:
        raise RuntimeError("当前视频没有可用字幕。")
    if requested_language:
        for track in tracks:
            if track["language"] == requested_language:
                return track
        raise RuntimeError(
            "未找到指定字幕语言。可用语言：" + ", ".join(track["language"] for track in tracks)
        )

    for preferred in PREFERRED_LANGUAGES:
        for track in tracks:
            if track["language"] == preferred and "manual" in track["source"]:
                return track
    for preferred in PREFERRED_LANGUAGES:
        for track in tracks:
            if track["language"] == preferred:
                return track
    return tracks[0]


def choose_subtitle_source(track: dict, preference: str) -> str:
    preference = normalize_source_preference(preference)
    if preference == "automatic" and "automatic" in track["source"]:
        return "automatic"
    if preference == "manual" and "manual" in track["source"]:
        return "manual"
    if "manual" in track["source"]:
        return "manual"
    return "automatic"


def parse_vtt_timestamp(value: str) -> float:
    value = value.replace(",", ".")
    parts = value.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = "0"
        m, s = parts
    else:
        raise ValueError(value)
    return int(h) * 3600 + int(m) * 60 + float(s)


def clean_subtitle_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{[^}]+\}", "", text)
    text = text.replace("&nbsp;", " ")
    return unescape(text).strip()


def dedupe_entries(entries: list[dict]) -> list[dict]:
    deduped = []
    for entry in entries:
        text = clean_subtitle_text(entry.get("text", ""))
        if not text:
            continue
        normalized = {
            "start": entry.get("start"),
            "end": entry.get("end"),
            "text": text,
        }
        if deduped and deduped[-1]["text"] == text:
            continue
        deduped.append(normalized)
    return deduped


def parse_vtt_file(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    for block in re.split(r"\n\s*\n", content):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        for index, line in enumerate(lines):
            match = re.match(
                r"(\d{2}:\d{2}:\d{2}[.,]\d{3}|\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3}|\d{2}:\d{2}[.,]\d{3})",
                line,
            )
            if not match:
                continue
            text = "\n".join(lines[index + 1 :]).strip()
            entries.append({
                "start": parse_vtt_timestamp(match.group(1)),
                "end": parse_vtt_timestamp(match.group(2)),
                "text": text,
            })
            break
    return dedupe_entries(entries)


def parse_srt_file(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    for block in re.split(r"\n\s*\n", content):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        time_line_index = 1 if re.fullmatch(r"\d+", lines[0]) else 0
        if time_line_index >= len(lines):
            continue
        match = re.match(
            r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})",
            lines[time_line_index],
        )
        if not match:
            continue
        entries.append({
            "start": parse_vtt_timestamp(match.group(1)),
            "end": parse_vtt_timestamp(match.group(2)),
            "text": "\n".join(lines[time_line_index + 1 :]).strip(),
        })
    return dedupe_entries(entries)


def parse_json_subtitle_payload(payload: dict | list) -> list[dict]:
    entries = []
    if isinstance(payload, dict) and isinstance(payload.get("body"), list):
        for item in payload["body"]:
            entries.append({
                "start": float(item.get("from", 0)),
                "end": float(item.get("to", item.get("from", 0))),
                "text": item.get("content", ""),
            })
    elif isinstance(payload, dict) and isinstance(payload.get("events"), list):
        for item in payload["events"]:
            segments = item.get("segs") or []
            text = "".join(segment.get("utf8", "") for segment in segments)
            entries.append({
                "start": float(item.get("tStartMs", 0)) / 1000,
                "end": float(item.get("tStartMs", 0) + item.get("dDurationMs", 0)) / 1000,
                "text": text,
            })
    elif isinstance(payload, dict) and isinstance(payload.get("segments"), list):
        for item in payload["segments"]:
            entries.append({
                "start": float(item.get("start", 0)),
                "end": float(item.get("end", item.get("start", 0))),
                "text": item.get("text", ""),
            })
    elif isinstance(payload, list):
        for item in payload:
            entries.append({
                "start": float(item.get("from", 0)),
                "end": float(item.get("to", item.get("from", 0))),
                "text": item.get("content", item.get("text", "")),
            })
    return dedupe_entries(entries)


def parse_json_subtitle_file(path: Path) -> list[dict]:
    return parse_json_subtitle_payload(json.loads(path.read_text(encoding="utf-8", errors="ignore")))


def parse_ttml_time(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.endswith("s"):
        try:
            return float(value[:-1])
        except ValueError:
            return None
    try:
        return parse_vtt_timestamp(value)
    except Exception:
        return None


def parse_ttml_file(path: Path) -> list[dict]:
    tree = ET.parse(path)
    entries = []
    for node in tree.iter():
        if node.tag.split("}")[-1] != "p":
            continue
        entries.append({
            "start": parse_ttml_time(node.attrib.get("begin")),
            "end": parse_ttml_time(node.attrib.get("end")),
            "text": "".join(node.itertext()),
        })
    return dedupe_entries(entries)


def parse_subtitle_file(path: Path) -> list[dict]:
    suffixes = "".join(path.suffixes).lower()
    if suffixes.endswith(".vtt"):
        return parse_vtt_file(path)
    if suffixes.endswith(".srt"):
        return parse_srt_file(path)
    if suffixes.endswith(".ttml") or suffixes.endswith(".xml"):
        return parse_ttml_file(path)
    if any(suffixes.endswith(ext) for ext in (".json3", ".json", ".srv1", ".srv2", ".srv3")):
        return parse_json_subtitle_file(path)
    return []


def format_short_timestamp(seconds: float | None) -> str:
    if seconds is None:
        return "--:--"
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def format_srt_timestamp(seconds: float | None) -> str:
    total_ms = int(round((seconds or 0) * 1000))
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_subtitle_outputs(
    subtitle_dir: Path,
    *,
    title: str,
    platform: str,
    url: str,
    language: str,
    source: str,
    entries: list[dict],
    raw_file: Path,
) -> dict:
    safe_language = sanitize_filename(language)
    txt_path = subtitle_dir / f"subtitle-{safe_language}.txt"
    srt_path = subtitle_dir / f"subtitle-{safe_language}.srt"

    txt_lines = [
        f"视频标题：{title}",
        f"平台：{platform}",
        f"原始链接：{url}",
        f"字幕语言：{language}",
        f"字幕来源：{source}",
        "",
        "字幕内容：",
        "",
    ]
    for entry in entries:
        txt_lines.append(f"[{format_short_timestamp(entry.get('start'))}] {entry['text']}")
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    blocks = []
    for index, entry in enumerate(entries, start=1):
        blocks.extend([
            str(index),
            f"{format_srt_timestamp(entry.get('start'))} --> {format_srt_timestamp(entry.get('end'))}",
            entry["text"],
            "",
        ])
    srt_path.write_text("\n".join(blocks), encoding="utf-8")
    return {
        "raw_file": str(raw_file),
        "txt_file": str(txt_path),
        "srt_file": str(srt_path),
        "language": language,
        "source": source,
        "count": len(entries),
    }


def find_subtitle_file(subtitle_dir: Path, language: str) -> Path | None:
    candidates = []
    normalized = language.lower()
    for path in subtitle_dir.iterdir():
        if not path.is_file():
            continue
        suffixes = "".join(path.suffixes).lower()
        if not any(suffixes.endswith(ext) for ext in RAW_SUBTITLE_EXTENSIONS):
            continue
        filename = path.name.lower()
        score = 1 if f".{normalized}." in filename else 0
        candidates.append((score, path.stat().st_mtime, path))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][2]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://www.bilibili.com/",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def extract_bvid(url: str) -> str:
    match = re.search(r"(BV[0-9A-Za-z]+)", url)
    if not match:
        raise RuntimeError("无法从 Bilibili 链接中提取 BV 号。")
    return match.group(1)


def run_browser_command(profile: str, args: list[str]) -> str:
    cmd = ["openclaw", "browser", "--browser-profile", profile] + args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "browser command failed")
    return proc.stdout.strip()


def parse_browser_subtitle_output(stdout: str) -> dict:
    text = stdout.strip()
    if not text:
        return {}
    lines = [
        line for line in text.splitlines()
        if not line.startswith("Config warnings:")
        and "duplicate plugin id detected" not in line
    ]
    text = "\n".join(lines).strip()
    for candidate in (text, text.strip('"'), text.replace('\\"', '"')):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue
    return {}


def get_browser_assisted_bilibili_subtitle_meta(bvid: str, cid: int, browser_profile: str) -> dict:
    video_url = f"https://www.bilibili.com/video/{bvid}/"
    run_browser_command(browser_profile, ["start"])
    run_browser_command(browser_profile, ["open", video_url])
    run_browser_command(browser_profile, ["wait", "--time", "4000"])
    fn = (
        "async () => {"
        f" const r = await fetch('https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}', "
        "{ credentials: 'include', headers: { Referer: 'https://www.bilibili.com/' } });"
        " const j = await r.json();"
        " return JSON.stringify((j.data && j.data.subtitle) || {});"
        "}"
    )
    stdout = run_browser_command(browser_profile, ["evaluate", "--fn", fn])
    return parse_browser_subtitle_output(stdout)


def fetch_bilibili_subtitles_fallback(
    *,
    url: str,
    browser_profile: str,
    subtitle_dir: Path,
) -> dict:
    bvid = extract_bvid(url)
    view = fetch_json(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}")
    data = view.get("data") or {}
    cid = data.get("cid")
    title = data.get("title") or bvid
    if not cid:
        raise RuntimeError("Bilibili API 没有返回 cid。")

    subtitle_meta = (fetch_json(f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}").get("data") or {}).get("subtitle") or {}
    source = "direct-api"
    if not (subtitle_meta.get("subtitles") or []):
        subtitle_meta = get_browser_assisted_bilibili_subtitle_meta(bvid, cid, browser_profile)
        source = "browser-fallback"

    subtitles = subtitle_meta.get("subtitles") or []
    if not subtitles:
        raise RuntimeError("Bilibili 当前没有可用字幕。")
    subtitle_info = subtitles[0]
    subtitle_url = subtitle_info.get("subtitle_url")
    if not subtitle_url:
        raise RuntimeError("Bilibili 字幕元数据中没有 subtitle_url。")
    if subtitle_url.startswith("//"):
        subtitle_url = f"https:{subtitle_url}"
    elif subtitle_url.startswith("/"):
        subtitle_url = f"https://{subtitle_url.lstrip('/')}"

    payload = fetch_json(subtitle_url)
    entries = parse_json_subtitle_payload(payload)
    if not entries:
        raise RuntimeError("Bilibili 字幕内容为空。")

    raw_file = subtitle_dir / f"subtitle-{subtitle_info.get('lan', 'raw')}.json"
    raw_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    language = subtitle_info.get("lan_doc") or subtitle_info.get("lan") or "unknown"
    outputs = write_subtitle_outputs(
        subtitle_dir,
        title=title,
        platform="bilibili",
        url=url,
        language=language,
        source=source,
        entries=entries,
        raw_file=raw_file,
    )
    outputs["title"] = title
    return outputs


def download_video(
    *,
    url: str,
    platform: str,
    auth_mode: str,
    browser_profile: str,
    video_dir: Path,
) -> tuple[dict, list[str], Path]:
    opts, auth_sources = get_base_opts(platform, auth_mode=auth_mode, browser_profile=browser_profile)
    opts["skip_download"] = True
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    download_opts, _ = get_base_opts(platform, auth_mode=auth_mode, browser_profile=browser_profile)
    download_opts.update({
        "format": build_format_selector(),
        "outtmpl": str(video_dir / "video.%(ext)s"),
        "merge_output_format": "mp4",
        "prefer_ffmpeg": True,
        "keepvideo": False,
        "postprocessors": [{"key": "FFmpegFixupM3u8"}],
    })
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        ydl.download([url])

    video_file = None
    preferred = video_dir / "video.mp4"
    if preferred.exists():
        video_file = preferred
    else:
        for path in sorted(video_dir.glob("video.*"), key=lambda item: item.stat().st_mtime, reverse=True):
            video_file = path
            break
    if video_file is None:
        raise RuntimeError("视频下载已执行，但没有找到输出文件。")

    return info, auth_sources, video_file


def download_subtitles(
    *,
    info: dict,
    url: str,
    platform: str,
    auth_mode: str,
    browser_profile: str,
    subtitle_dir: Path,
    requested_language: str | None,
    subtitle_source: str,
) -> dict | None:
    tracks = extract_subtitle_tracks(info)
    if not tracks:
        if platform == "bilibili" and auth_mode in {"auto", "managed_browser"}:
            return fetch_bilibili_subtitles_fallback(
                url=url,
                browser_profile=browser_profile,
                subtitle_dir=subtitle_dir,
            )
        return None

    track = choose_subtitle_track(tracks, requested_language)
    selected_source = choose_subtitle_source(track, subtitle_source)
    download_opts, _ = get_base_opts(platform, auth_mode=auth_mode, browser_profile=browser_profile)
    download_opts.update({
        "skip_download": True,
        "writesubtitles": selected_source == "manual",
        "writeautomaticsub": selected_source == "automatic",
        "subtitleslangs": [track["language"]],
        "subtitlesformat": "vtt/best",
        "outtmpl": str(subtitle_dir / "%(id)s.%(ext)s"),
    })
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        ydl.download([url])

    raw_file = find_subtitle_file(subtitle_dir, track["language"])
    if raw_file is None:
        if platform == "bilibili" and auth_mode in {"auto", "managed_browser"}:
            return fetch_bilibili_subtitles_fallback(
                url=url,
                browser_profile=browser_profile,
                subtitle_dir=subtitle_dir,
            )
        return None

    entries = parse_subtitle_file(raw_file)
    if not entries:
        raise RuntimeError("字幕文件已下载，但解析结果为空。")

    outputs = write_subtitle_outputs(
        subtitle_dir,
        title=info.get("title") or "Unknown",
        platform=platform,
        url=url,
        language=track["language"],
        source=selected_source,
        entries=entries,
        raw_file=raw_file,
    )
    outputs["title"] = info.get("title") or "Unknown"
    return outputs


def build_result_text(result: dict) -> str:
    lines = [
        f"成功: {result['success']}",
        f"标题: {result.get('title', '')}",
        f"平台: {result.get('platform', '')}",
        f"输出目录: {result.get('output_dir', '')}",
        f"视频文件: {result.get('video_file', '')}",
        f"授权来源: {', '.join(result.get('auth_sources', [])) or 'none'}",
    ]
    subtitles = result.get("subtitles")
    if subtitles:
        lines.extend([
            f"字幕语言: {subtitles.get('language', '')}",
            f"字幕来源: {subtitles.get('source', '')}",
            f"原始字幕: {subtitles.get('raw_file', '')}",
            f"SRT: {subtitles.get('srt_file', '')}",
            f"TXT: {subtitles.get('txt_file', '')}",
        ])
    else:
        lines.append("字幕: 当前未找到可用字幕")
    if result.get("warning"):
        lines.append(f"警告: {result['warning']}")
    return "\n".join(lines)


def pick_existing_file(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def run_whisper_fallback(
    *,
    video_file: Path,
    subtitle_dir: Path,
    model: str,
    model_dir: Path,
    language: str | None,
) -> dict:
    whisper_bin = shutil.which("whisper")
    if not whisper_bin:
        raise RuntimeError("当前环境没有安装 whisper 命令，无法执行回退转写。")

    whisper_dir = subtitle_dir / f"whisper-{sanitize_filename(model)}"
    whisper_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        whisper_bin,
        str(video_file),
        "--model",
        model,
        "--model_dir",
        str(model_dir),
        "--output_dir",
        str(whisper_dir),
        "--output_format",
        "all",
        "--verbose",
        "False",
    ]
    if language:
        cmd.extend(["--language", language])

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=7200,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "whisper command failed"
        raise RuntimeError(f"Whisper 转写失败：{detail}")

    stem = video_file.stem
    txt_file = whisper_dir / f"{stem}.txt"
    srt_file = whisper_dir / f"{stem}.srt"
    vtt_file = whisper_dir / f"{stem}.vtt"
    json_file = whisper_dir / f"{stem}.json"
    raw_file = pick_existing_file(json_file, srt_file, vtt_file, txt_file)
    if raw_file is None or not txt_file.exists():
        raise RuntimeError("Whisper 已执行，但没有生成可用字幕文件。")

    parsed_source = pick_existing_file(srt_file, vtt_file, json_file)
    entries = parse_subtitle_file(parsed_source) if parsed_source else []
    return {
        "raw_file": str(raw_file),
        "txt_file": str(txt_file),
        "srt_file": str(srt_file if srt_file.exists() else raw_file),
        "language": language or "auto",
        "source": f"whisper:{model}",
        "count": len(entries),
        "engine": "whisper",
        "whisper_model": model,
        "generated_dir": str(whisper_dir),
    }


def main():
    parser = argparse.ArgumentParser(description="Download best video and subtitles with StreamGrabPro skill")
    parser.add_argument("url", help="Video URL")
    parser.add_argument("--auth", default="auto", choices=sorted(AUTH_MODES))
    parser.add_argument("--browser-profile", default=DEFAULT_BROWSER_PROFILE)
    parser.add_argument("--lang", default=None, help="Preferred subtitle language")
    parser.add_argument("--subtitle-source", default="best", choices=sorted(SUBTITLE_SOURCE_PREFERENCES))
    parser.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL, help="Whisper fallback model")
    parser.add_argument("--whisper-model-dir", default=str(DEFAULT_WHISPER_MODEL_DIR), help="Whisper model cache directory")
    parser.add_argument("--whisper-language", default=None, help="Optional Whisper language override")
    parser.add_argument("--disable-whisper-fallback", action="store_true", help="Disable Whisper fallback when platform subtitles are unavailable")
    parser.add_argument("--format", default="text", choices=["text", "json"])
    args = parser.parse_args()

    auth_mode = normalize_auth_mode(args.auth)
    subtitle_source = normalize_source_preference(args.subtitle_source)
    platform = detect_platform(args.url)
    started_at = time.strftime("%Y%m%d-%H%M%S")

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        temp_opts, _ = get_base_opts(platform, auth_mode=auth_mode, browser_profile=args.browser_profile)
        temp_opts["skip_download"] = True
        with yt_dlp.YoutubeDL(temp_opts) as ydl:
            preview_info = ydl.extract_info(args.url, download=False)

        title = preview_info.get("title") or preview_info.get("id") or "untitled-video"
        safe_title = sanitize_filename(title)
        run_dir = OUTPUT_DIR / f"{platform}-{safe_title}-{started_at}"
        video_dir = run_dir / "video"
        subtitle_dir = run_dir / "subtitles"
        video_dir.mkdir(parents=True, exist_ok=True)
        subtitle_dir.mkdir(parents=True, exist_ok=True)

        info, auth_sources, video_file = download_video(
            url=args.url,
            platform=platform,
            auth_mode=auth_mode,
            browser_profile=args.browser_profile,
            video_dir=video_dir,
        )
        subtitle_outputs = None
        subtitle_error = None
        whisper_error = None
        whisper_used = False
        warning_messages: list[str] = []

        try:
            subtitle_outputs = download_subtitles(
                info=info,
                url=args.url,
                platform=platform,
                auth_mode=auth_mode,
                browser_profile=args.browser_profile,
                subtitle_dir=subtitle_dir,
                requested_language=args.lang,
                subtitle_source=subtitle_source,
            )
            if subtitle_outputs is None:
                subtitle_error = "当前视频没有可用平台字幕。"
        except Exception as exc:
            subtitle_error = str(exc)

        if subtitle_error:
            warning_messages.append(f"平台字幕抓取失败：{subtitle_error}")

        if subtitle_outputs is None and not args.disable_whisper_fallback:
            try:
                subtitle_outputs = run_whisper_fallback(
                    video_file=video_file,
                    subtitle_dir=subtitle_dir,
                    model=args.whisper_model,
                    model_dir=Path(args.whisper_model_dir),
                    language=args.whisper_language,
                )
                whisper_used = True
                warning_messages.append(f"已回退到 Whisper {args.whisper_model} 生成字幕。")
            except Exception as exc:
                whisper_error = str(exc)
                warning_messages.append(f"Whisper 回退失败：{whisper_error}")

        metadata = {
            "title": info.get("title") or title,
            "url": args.url,
            "platform": platform,
            "video_file": str(video_file),
            "auth_sources": auth_sources,
            "subtitles": subtitle_outputs,
            "subtitle_error": subtitle_error,
            "whisper_fallback_used": whisper_used,
            "whisper_model": args.whisper_model,
            "whisper_error": whisper_error,
            "created_at": started_at,
        }
        (run_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        result = {
            "success": True,
            "title": metadata["title"],
            "platform": platform,
            "url": args.url,
            "output_dir": str(run_dir),
            "video_file": str(video_file),
            "auth_sources": auth_sources,
            "subtitles": subtitle_outputs,
        }
        if warning_messages:
            result["warning"] = " ".join(warning_messages)
    except Exception as exc:
        message = str(exc)
        result = {
            "success": False,
            "url": args.url,
            "platform": platform,
            "error": message,
            "hint": make_error_hint(message),
            "auth_required": auth_required_from_message(message),
            "auth_choices": ["managed_browser", "cookies"],
            "cookie_file": str(COOKIE_FILE),
            "managed_browser_profile": args.browser_profile,
        }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not result["success"]:
        print(result["error"], file=sys.stderr)
        if result.get("hint"):
            print(result["hint"], file=sys.stderr)
        sys.exit(1)

    print(build_result_text(result))


if __name__ == "__main__":
    main()
