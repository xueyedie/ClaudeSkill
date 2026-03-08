#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 视频分析器 - 使用 Gemini 原生视频理解能力分析 YouTube 视频。

用法：
    python analyze_youtube.py <youtube_url> <提示词> [--format text|json] [--model MODEL]
    python analyze_youtube.py <youtube_url> --subtitles [--lang zh-Hans,en] [--format text|json]

示例：
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" "描述视频内容"
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" --subtitles
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" --subtitles --lang "en,ja"

环境变量：
    GEMINI_API_KEY - 视频分析模式必填。从 https://aistudio.google.com/apikey 获取
"""

import os
import sys
import argparse
import json
import re

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Clear proxy settings that may interfere
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)

DEFAULT_MODEL = "gemini-3-pro-preview"


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


def fetch_subtitles(video_id: str, languages: list[str] = None) -> dict:
    """
    Fetch original subtitles/captions from YouTube.

    Args:
        video_id: YouTube video ID
        languages: Language priority list (default: ['zh-Hans', 'en'])

    Returns:
        dict with 'success', 'subtitles' or 'error'
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return {
            'success': False,
            'error': 'youtube-transcript-api not installed. Run: pip install youtube-transcript-api'
        }

    if languages is None:
        languages = ['zh-Hans', 'en']

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages)
        subtitles = [{'text': s.text, 'start': s.start, 'duration': s.duration} for s in transcript]
        return {
            'success': True,
            'subtitles': subtitles,
            'video_id': video_id,
            'count': len(subtitles),
        }
    except Exception as e:
        error_msg = str(e)
        if 'No transcripts were found' in error_msg or 'Could not retrieve' in error_msg:
            error_msg = f"No subtitles found for this video (may not have captions).\nOriginal: {e}"
        return {
            'success': False,
            'error': error_msg,
            'video_id': video_id,
        }


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
        description='Analyze YouTube videos using Gemini, or extract subtitles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=xxx" "描述这个视频的内容"
  %(prog)s "https://youtu.be/xxx" "分析游戏玩法机制" --format json
  %(prog)s "https://youtu.be/xxx" --subtitles
  %(prog)s "https://youtu.be/xxx" --subtitles --lang "en,ja" --format json

Environment:
  GEMINI_API_KEY    Required for video analysis. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('prompt', nargs='?', default=None,
                       help='Analysis prompt/question (not needed with --subtitles)')
    parser.add_argument('--subtitles', action='store_true',
                       help='Extract original subtitles instead of Gemini analysis')
    parser.add_argument('--lang', default='zh-Hans,en',
                       help='Subtitle language priority, comma-separated (default: zh-Hans,en)')
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

        result = fetch_subtitles(video_id, languages)

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
