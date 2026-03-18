#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 YouTube 字幕并输出为纯文本或 JSON。

用法：
    python fetch_youtube_subtitles.py <youtube_url> [--lang en,zh-Hans]
    python fetch_youtube_subtitles.py <youtube_url> [--lang en] [--browser chrome] [--format text|json]

环境变量：
    YT_COOKIES_BROWSER   默认浏览器 cookie 来源
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_BROWSER = "chrome:/Users/bot/.openclaw/browser/openclaw/user-data"
SKILL_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = SKILL_DIR.parent.parent
SUBTITLES_DIR = SKILL_DIR / "subtitles"
OUTPUT_DIR = WORKSPACE_DIR / "output"


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url


def normalize_youtube_url(url: str) -> str:
    video_id = extract_video_id(url)
    return f"https://www.youtube.com/watch?v={video_id}"


def parse_vtt(vtt_path: Path) -> list[dict]:
    try:
        content = vtt_path.read_text(encoding='utf-8')
    except Exception:
        return []

    entries = []
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        lines = block.strip().split('\n')
        for i, line in enumerate(lines):
            match = re.match(
                r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', line
            )
            if not match:
                continue
            start_s = parse_vtt_ts(match.group(1))
            text = '\n'.join(lines[i + 1:])
            text = re.sub(r'<[^>]+>', '', text).strip()
            if text:
                entries.append({'text': text, 'start': start_s})
            break

    deduped = []
    for entry in entries:
        if not deduped or entry['text'] != deduped[-1]['text']:
            deduped.append(entry)
    return deduped


def parse_vtt_ts(ts: str) -> float:
    h, m, rest = ts.split(':')
    s = float(rest)
    return int(h) * 3600 + int(m) * 60 + s


def format_timestamp(seconds: float) -> str:
    h, remainder = divmod(int(seconds), 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]+', '-', value)
    value = re.sub(r'\s+', ' ', value).strip()
    value = value.strip('.')
    return value or "untitled-video"


def run_yt_dlp_json(url: str, browser: str) -> Optional[dict]:
    cmd = ['yt-dlp', '--dump-single-json', '--skip-download', url]
    if browser:
        cmd.extend(['--cookies-from-browser', browser])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def write_delivery_txt(url: str, title: str, fetch_date: str, language: str, subtitles: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(title)
    out_path = OUTPUT_DIR / f"youtube-{safe_title}-{fetch_date}.txt"

    lines = [
        f"视频标题：{title}",
        f"抓取日期：{fetch_date}",
        f"原始链接：{url}",
        f"字幕语言：{language}",
        "",
        "字幕内容：",
        "",
    ]
    for entry in subtitles:
        lines.append(f"[{format_timestamp(entry['start'])}] {entry['text']}")

    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out_path


def fetch_subtitles(url: str, video_id: str, languages: list[str], browser: str) -> dict:
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        'yt-dlp',
        '--write-sub', '--write-auto-sub',
        '--sub-lang', ','.join(languages),
        '--sub-format', 'vtt',
        '--skip-download',
        '-o', str(SUBTITLES_DIR / '%(id)s.%(ext)s'),
        url,
    ]
    if browser:
        cmd.extend(['--cookies-from-browser', browser])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60,
        )
    except FileNotFoundError:
        return {'success': False, 'error': 'yt-dlp not installed. Run: pip install yt-dlp'}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'yt-dlp timed out after 60s'}

    vtt_files = sorted(SUBTITLES_DIR.glob(f'{video_id}*.vtt'))
    if not vtt_files:
        stderr = proc.stderr.strip() if proc.stderr else ''
        return {
            'success': False,
            'error': f'No subtitle files downloaded.\nyt-dlp stderr: {stderr}',
            'video_id': video_id,
        }

    all_subtitles = {}
    saved_files = []
    for vtt_path in vtt_files:
        lang = vtt_path.stem.replace(f'{video_id}.', '', 1)
        entries = parse_vtt(vtt_path)
        if entries:
            all_subtitles[lang] = entries
            saved_files.append(str(vtt_path))

    if not all_subtitles:
        return {
            'success': False,
            'error': 'Downloaded subtitle files were empty or unparseable.',
            'video_id': video_id,
            'files': [str(f) for f in vtt_files],
        }

    primary_lang = None
    for lang in languages:
        if lang in all_subtitles:
            primary_lang = lang
            break
    if primary_lang is None:
        primary_lang = next(iter(all_subtitles))

    return {
        'success': True,
        'subtitles': all_subtitles[primary_lang],
        'language': primary_lang,
        'all_languages': list(all_subtitles.keys()),
        'files': saved_files,
        'video_id': video_id,
        'count': len(all_subtitles[primary_lang]),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Fetch YouTube subtitles via yt-dlp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=xxx"
  %(prog)s "https://youtu.be/xxx" --lang "en,zh-Hans" --browser chrome

Environment:
  YT_COOKIES_BROWSER   Default value for --browser
        """,
    )
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument(
        '--browser',
        default=os.environ.get('YT_COOKIES_BROWSER', DEFAULT_BROWSER),
        help=f'yt-dlp --cookies-from-browser value (default: {DEFAULT_BROWSER})',
    )
    parser.add_argument('--lang', default='en', help='Subtitle language codes, comma-separated')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    normalized_url = normalize_youtube_url(args.url)
    video_id = extract_video_id(args.url)
    languages = [lang.strip() for lang in args.lang.split(',') if lang.strip()]
    result = fetch_subtitles(
        url=normalized_url,
        video_id=video_id,
        languages=languages,
        browser=args.browser,
    )

    if result.get('success'):
        metadata = run_yt_dlp_json(normalized_url, args.browser) or {}
        title = metadata.get('title') or video_id
        fetch_date = datetime.now().strftime('%Y%m%d')
        delivery_path = write_delivery_txt(
            url=normalized_url,
            title=title,
            fetch_date=fetch_date,
            language=result['language'],
            subtitles=result['subtitles'],
        )
        result['title'] = title
        result['fetch_date'] = fetch_date
        result['delivery_file'] = str(delivery_path)

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    for entry in result['subtitles']:
        print(f"[{format_timestamp(entry['start'])}] {entry['text']}")


if __name__ == '__main__':
    main()
