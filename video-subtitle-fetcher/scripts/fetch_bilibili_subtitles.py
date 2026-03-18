#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 B 站字幕并输出为纯文本或 JSON。

用法：
    python fetch_bilibili_subtitles.py <bilibili_url> [--format text|json]

说明：
    - 优先直接请求 B 站 API 获取字幕元数据
    - 若直连结果没有字幕，则尝试使用 OpenClaw 浏览器登录态做一次补充查询
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SKILL_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = SKILL_DIR.parent.parent
OUTPUT_DIR = WORKSPACE_DIR / "output"
SUBTITLES_DIR = SKILL_DIR / "subtitles"
DEFAULT_BROWSER_PROFILE = "openclaw"


def extract_bvid(url: str) -> str:
    match = re.search(r'(BV[0-9A-Za-z]+)', url)
    if match:
        return match.group(1)
    raise ValueError("Unable to extract BV id from URL")


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]+', '-', value)
    value = re.sub(r'\s+', ' ', value).strip()
    value = value.strip('.')
    return value or "untitled-video"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.bilibili.com/',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def get_view_data(bvid: str) -> dict:
    payload = fetch_json(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
    data = payload.get('data') or {}
    if not data:
        raise RuntimeError("Bilibili view API returned no data")
    return data


def get_player_subtitle_meta(bvid: str, cid: int) -> dict:
    payload = fetch_json(f'https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}')
    return (payload.get('data') or {}).get('subtitle') or {}


def run_browser_command(args: list[str]) -> str:
    cmd = ['openclaw', 'browser', '--browser-profile', DEFAULT_BROWSER_PROFILE] + args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or 'browser command failed')
    return proc.stdout.strip()


def parse_browser_subtitle_output(stdout: str) -> dict:
    text = stdout.strip()
    if not text:
        return {}

    lines = [line for line in text.splitlines() if not line.startswith('Config warnings:') and 'duplicate plugin id detected' not in line]
    text = '\n'.join(lines).strip()
    if not text:
        return {}

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


def get_browser_assisted_subtitle_meta(bvid: str, cid: int) -> dict:
    video_url = f'https://www.bilibili.com/video/{bvid}/'
    run_browser_command(['start'])
    run_browser_command(['open', video_url])
    run_browser_command(['wait', '--time', '4000'])
    fn = (
        "async () => {"
        f" const r = await fetch('https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}', "
        "{ credentials: 'include', headers: { Referer: 'https://www.bilibili.com/' } });"
        " const j = await r.json();"
        " return JSON.stringify((j.data && j.data.subtitle) || {});"
        "}"
    )
    stdout = run_browser_command(['evaluate', '--fn', fn])
    return parse_browser_subtitle_output(stdout)


def resolve_subtitle_url(meta: dict) -> str:
    subtitles = meta.get('subtitles') or []
    if not subtitles:
        raise RuntimeError("No subtitles found for this Bilibili video")
    subtitle_url = subtitles[0].get('subtitle_url')
    if not subtitle_url:
        raise RuntimeError("Subtitle metadata did not include subtitle_url")
    if subtitle_url.startswith('//'):
        return f'https:{subtitle_url}'
    if subtitle_url.startswith('/'):
        return f'https://{subtitle_url.lstrip("/")}'
    return subtitle_url


def fetch_subtitle_body(subtitle_url: str) -> dict:
    req = urllib.request.Request(
        subtitle_url,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.bilibili.com/',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def format_clock(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3600000
    minutes = (total_ms % 3600000) // 60000
    secs = (total_ms % 60000) // 1000
    millis = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def write_outputs(title: str, fetch_date: str, url: str, entries: list[dict], bvid: str) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(title)

    delivery_txt = OUTPUT_DIR / f"bilibili-{safe_title}-{fetch_date}.txt"
    delivery_srt = OUTPUT_DIR / f"bilibili-{safe_title}-{fetch_date}.srt"
    raw_json = SUBTITLES_DIR / f"{bvid}-subtitle.json"

    txt_lines = [
        f"视频标题：{title}",
        f"抓取日期：{fetch_date}",
        f"原始链接：{url}",
        "",
        "字幕内容：",
        "",
    ]
    for entry in entries:
        txt_lines.append(f"[{format_timestamp(entry['from'])}] {entry['content']}")
    delivery_txt.write_text('\n'.join(txt_lines) + '\n', encoding='utf-8')

    srt_blocks = []
    for idx, entry in enumerate(entries, start=1):
        srt_blocks.extend([
            str(idx),
            f"{format_clock(entry['from'])} --> {format_clock(entry['to'])}",
            entry['content'],
            "",
        ])
    delivery_srt.write_text('\n'.join(srt_blocks), encoding='utf-8')

    raw_json.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    return delivery_txt, delivery_srt, raw_json


def main():
    parser = argparse.ArgumentParser(description='Fetch Bilibili subtitles')
    parser.add_argument('url', help='Bilibili video URL')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    try:
        bvid = extract_bvid(args.url)
        view = get_view_data(bvid)
        title = view.get('title') or bvid
        cid = view.get('cid')
        if not cid:
            raise RuntimeError('Bilibili API did not return cid')

        subtitle_meta = get_player_subtitle_meta(bvid, cid)
        source = 'direct-api'
        if not (subtitle_meta.get('subtitles') or []):
            subtitle_meta = get_browser_assisted_subtitle_meta(bvid, cid)
            source = 'browser-fallback'

        subtitle_url = resolve_subtitle_url(subtitle_meta)
        subtitle_payload = fetch_subtitle_body(subtitle_url)
        entries = subtitle_payload.get('body') or []
        if not entries:
            raise RuntimeError('Subtitle payload body is empty')

        fetch_date = datetime.now().strftime('%Y%m%d')
        txt_path, srt_path, raw_json_path = write_outputs(title, fetch_date, args.url, entries, bvid)
        result = {
            'success': True,
            'title': title,
            'bvid': bvid,
            'cid': cid,
            'fetch_date': fetch_date,
            'subtitle_source': source,
            'subtitle_url': subtitle_url,
            'count': len(entries),
            'delivery_file': str(txt_path),
            'srt_file': str(srt_path),
            'raw_json_file': str(raw_json_path),
        }
    except Exception as exc:
        result = {
            'success': False,
            'error': str(exc),
            'url': args.url,
        }

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"标题: {result['title']}")
    print(f"条目数: {result['count']}")
    print(f"交付文件: {result['delivery_file']}")
    print(f"SRT 文件: {result['srt_file']}")


if __name__ == '__main__':
    main()
