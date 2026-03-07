---
name: youtube-analyzer
user-invocable: true
description: |
  Analyze YouTube video content using Gemini's native video understanding.
  Use when: (1) Understanding what a YouTube video is about,
  (2) Extracting key information from video content,
  (3) Summarizing or describing video scenes,
  (4) Analyzing gameplay, tutorials, presentations, or any visual content.
  Triggers: "analyze this youtube", "what's in this video", "summarize this video",
  "describe this youtube", "分析这个视频", "这个视频讲了什么", "youtube视频内容"
  Limitations: Only works with YouTube URLs, max ~1 hour video, requires public/unlisted videos.
---

# YouTube Video Analyzer

Analyze YouTube videos using Gemini's native video understanding. No download required.

## Prerequisites

```bash
pip install google-genai
export GEMINI_API_KEY="your-key"  # Get from https://aistudio.google.com/apikey
```

## Usage

```bash
python scripts/analyze_youtube.py "YOUTUBE_URL" "YOUR_PROMPT"
```

**Options:**
- `--model MODEL` - Gemini model (default: gemini-3-pro-preview)
- `--format json` - Output as JSON instead of text
- `--api-key KEY` - Override GEMINI_API_KEY env var

## Examples

```bash
# 基础分析
python scripts/analyze_youtube.py "https://youtu.be/xxx" "描述视频内容"

# 游戏玩法分析
python scripts/analyze_youtube.py "URL" "分析核心玩法：1.操作方式 2.游戏目标 3.反馈系统"

# 广告创意分析  
python scripts/analyze_youtube.py "URL" "分析广告的Hook、卖点、CTA、目标受众"

# 快速模型
python scripts/analyze_youtube.py "URL" "简要总结" --model gemini-3-flash
```

## Key Limitations

| Limitation | Workaround |
|------------|------------|
| YouTube only | Non-YT videos need File API upload |
| Public/Unlisted only | Private/age-restricted fail |
| ~1 hour max | Split long videos into segments |
| No precise timestamps | Ask for approximate time descriptions |

For detailed limits, models, and alternatives, see [references/gemini-video-limits.md](references/gemini-video-limits.md).
