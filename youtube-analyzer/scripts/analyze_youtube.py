#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 视频分析器 - 使用 Gemini 原生视频理解能力分析 YouTube 视频。

用法：
    python analyze_youtube.py <youtube_url> <提示词> [--format text|json] [--model MODEL]
    python analyze_youtube.py <youtube_url> --subtitles [--lang en] [--browser BROWSER] [--format text|json]

示例：
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" "描述视频内容"
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" --subtitles --browser chrome
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" --subtitles --lang "en,zh-Hans" --browser "chrome:/path/to/profile"

环境变量：
    GEMINI_API_KEY       - 视频分析模式必填。从 https://aistudio.google.com/apikey 获取
    YT_COOKIES_BROWSER   - yt-dlp --cookies-from-browser 的值（如 chrome、edge、"chrome:/path/to/profile"）
"""

import os
import sys
import argparse
import json
import re
import subprocess
from pathlib import Path

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Clear proxy settings that may interfere
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)

DEFAULT_MODEL = "gemini-3-pro-preview"
DEFAULT_BROWSER = "chrome:C:/Users/bot/.openclaw/browser/openclaw/user-data"
SKILL_DIR = Path(__file__).resolve().parent.parent
SUBTITLES_DIR = SKILL_DIR / "subtitles"


def get_api_key(provided_key: str = None) -> str:
    """Get API key from argument, environment, or fail with helpful message."""
    key = provided_key or os.environ.get('GEMINI_API_KEY')
    if not key:
        print("Error: GEMINI_API_KEY not set.", file=sys.stderr)
        print("Get your key at: https://aistudio.google.com/apikey", file=sys.stderr)
        print("Then: export GEMINI_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)
    return key


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
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
    """Normalize YouTube URL to standard format."""
    video_id = extract_video_id(url)
    return f"https://www.youtube.com/watch?v={video_id}"


def fetch_subtitles(url: str, video_id: str, languages: list[str],
                    browser: str = None, output_dir: Path = None) -> dict:
    """
    Fetch subtitles using yt-dlp with optional browser cookie support.

    Args:
        url: YouTube video URL
        video_id: YouTube video ID
        languages: Language codes (e.g. ['en', 'zh-Hans'])
        browser: yt-dlp --cookies-from-browser value (e.g. 'chrome', 'chrome:/path/to/profile')
        output_dir: Directory to save subtitle files (default: SUBTITLES_DIR)

    Returns:
        dict with 'success', 'subtitles', 'files', or 'error'
    """
    if output_dir is None:
        output_dir = SUBTITLES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        'yt-dlp',
        '--write-sub', '--write-auto-sub',
        '--sub-lang', ','.join(languages),
        '--sub-format', 'vtt',
        '--skip-download',
        '-o', str(output_dir / '%(id)s.%(ext)s'),
        url,
    ]
    if browser:
        cmd.extend(['--cookies-from-browser', browser])

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8', timeout=60,
        )
    except FileNotFoundError:
        return {'success': False, 'error': 'yt-dlp not installed. Run: pip install yt-dlp'}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'yt-dlp timed out after 60s'}

    # Find downloaded VTT files for this video
    vtt_files = sorted(output_dir.glob(f'{video_id}*.vtt'))
    if not vtt_files:
        stderr = proc.stderr.strip() if proc.stderr else ''
        return {
            'success': False,
            'error': f'No subtitle files downloaded.\nyt-dlp stderr: {stderr}',
            'video_id': video_id,
        }

    # Parse all downloaded VTT files
    all_subtitles = {}
    saved_files = []
    for vtt_path in vtt_files:
        # Extract language from filename: VIDEO_ID.LANG.vtt
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

    # Pick the first matching language for primary output
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


def parse_vtt(vtt_path: Path) -> list[dict]:
    """Parse a VTT subtitle file into structured data."""
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
            if match:
                start_s = _parse_vtt_ts(match.group(1))
                text = '\n'.join(lines[i + 1:])
                text = re.sub(r'<[^>]+>', '', text).strip()
                if text:
                    entries.append({'text': text, 'start': start_s})
                break

    # Deduplicate consecutive identical texts (common in auto-generated subs)
    deduped = []
    for entry in entries:
        if not deduped or entry['text'] != deduped[-1]['text']:
            deduped.append(entry)
    return deduped


def _parse_vtt_ts(ts: str) -> float:
    """Convert VTT timestamp HH:MM:SS.mmm to seconds."""
    h, m, rest = ts.split(':')
    s = float(rest)
    return int(h) * 3600 + int(m) * 60 + s


def format_timestamp(seconds: float) -> str:
    """Format seconds to MM:SS or HH:MM:SS."""
    h, remainder = divmod(int(seconds), 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def analyze_video(url: str, prompt: str, model: str = DEFAULT_MODEL, api_key: str = None) -> dict:
    """
    Analyze a YouTube video using Gemini.
    
    Args:
        url: YouTube video URL
        prompt: Analysis prompt/question
        model: Gemini model to use
        api_key: API key (required)
    
    Returns:
        dict with 'success', 'result' or 'error', and metadata
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {
            'success': False,
            'error': 'google-genai not installed. Run: pip install google-genai'
        }
    
    normalized_url = normalize_youtube_url(url)
    video_id = extract_video_id(url)
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part(file_data=types.FileData(file_uri=normalized_url)),
                types.Part(text=prompt),
            ],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        
        return {
            'success': True,
            'result': response.text,
            'video_id': video_id,
            'video_url': normalized_url,
            'model': model,
        }
        
    except Exception as e:
        error_msg = str(e)
        
        if 'Cannot fetch content' in error_msg:
            error_msg = f"Cannot fetch video. Likely private/age-restricted/login-required.\nOriginal: {e}"
        elif 'RESOURCE_EXHAUSTED' in error_msg:
            error_msg = f"Rate limit exceeded. Wait and retry.\nOriginal: {e}"
        elif 'INVALID_ARGUMENT' in error_msg:
            error_msg = f"Invalid request. Check URL format.\nOriginal: {e}"
        
        return {
            'success': False,
            'error': error_msg,
            'video_id': video_id,
            'video_url': normalized_url,
        }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze YouTube videos using Gemini, or extract subtitles via yt-dlp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=xxx" "描述这个视频的内容"
  %(prog)s "https://youtu.be/xxx" --subtitles --browser chrome
  %(prog)s "https://youtu.be/xxx" --subtitles --lang "en,zh-Hans" --browser "chrome:/path/to/profile"

Environment:
  GEMINI_API_KEY       Required for video analysis. Get from https://aistudio.google.com/apikey
  YT_COOKIES_BROWSER   Default value for --browser (e.g. chrome, edge, "chrome:/path/to/profile")
        """
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('prompt', nargs='?', default=None,
                       help='Analysis prompt/question (not needed with --subtitles)')
    parser.add_argument('--subtitles', action='store_true',
                       help='Extract subtitles via yt-dlp instead of Gemini analysis')
    parser.add_argument('--browser',
                       default=os.environ.get('YT_COOKIES_BROWSER', DEFAULT_BROWSER),
                       help=f'yt-dlp --cookies-from-browser value (default: {DEFAULT_BROWSER})')
    parser.add_argument('--lang', default='en',
                       help='Subtitle language codes, comma-separated (default: en)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--model', default=DEFAULT_MODEL,
                       help=f'Gemini model (default: {DEFAULT_MODEL})')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY)')

    args = parser.parse_args()
    video_id = extract_video_id(args.url)

    if args.subtitles:
        languages = [lang.strip() for lang in args.lang.split(',')]
        print(f"[YouTube Analyzer] Subtitles: {video_id}", file=sys.stderr)
        print(f"[YouTube Analyzer] Languages: {languages}", file=sys.stderr)
        if args.browser:
            print(f"[YouTube Analyzer] Browser cookies: {args.browser}", file=sys.stderr)

        result = fetch_subtitles(
            url=normalize_youtube_url(args.url),
            video_id=video_id,
            languages=languages,
            browser=args.browser,
        )

        if result.get('files'):
            for f in result['files']:
                print(f"[YouTube Analyzer] Saved: {f}", file=sys.stderr)

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result['success']:
                for entry in result['subtitles']:
                    ts = format_timestamp(entry['start'])
                    print(f"[{ts}] {entry['text']}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
    else:
        if not args.prompt:
            parser.error('prompt is required when not using --subtitles')

        api_key = get_api_key(args.api_key)

        print(f"[YouTube Analyzer] Video: {video_id}", file=sys.stderr)
        print(f"[YouTube Analyzer] Model: {args.model}", file=sys.stderr)

        result = analyze_video(
            url=args.url,
            prompt=args.prompt,
            model=args.model,
            api_key=api_key,
        )

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result['success']:
                print(result['result'])
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)


if __name__ == '__main__':
    main()
