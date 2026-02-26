#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Video Analyzer - Analyze YouTube videos using Gemini's native video understanding.

Usage:
    python analyze_youtube.py <youtube_url> <prompt> [--format text|json] [--model MODEL]

Examples:
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" "描述视频内容"
    python analyze_youtube.py "https://www.youtube.com/watch?v=xxx" "分析游戏玩法" --format json

Environment:
    GEMINI_API_KEY - Required. Get from https://aistudio.google.com/apikey
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
        description='Analyze YouTube videos using Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=xxx" "描述这个视频的内容"
  %(prog)s "https://youtu.be/xxx" "分析游戏玩法机制" --format json

Environment:
  GEMINI_API_KEY    Required. Get from https://aistudio.google.com/apikey
        """
    )
    
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('prompt', help='Analysis prompt/question')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--model', default=DEFAULT_MODEL,
                       help=f'Gemini model (default: {DEFAULT_MODEL})')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY)')
    
    args = parser.parse_args()
    
    api_key = get_api_key(args.api_key)
    video_id = extract_video_id(args.url)
    
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
