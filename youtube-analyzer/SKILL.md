---
name: youtube-analyzer
user-invocable: true
description: |
  使用 Gemini 原生视频理解能力分析 YouTube 视频内容。
  适用场景：(1) 了解 YouTube 视频的内容，
  (2) 从视频中提取关键信息，
  (3) 总结或描述视频画面，
  (4) 分析游戏玩法、教程、演示或任何视觉内容。
  (5) 提取视频原始字幕（需视频本身有字幕）。
  触发词："analyze this youtube"、"what's in this video"、"summarize this video"、
  "describe this youtube"、"分析这个视频"、"这个视频讲了什么"、"youtube视频内容"、
  "get subtitles"、"提取字幕"、"获取字幕"
  限制：仅支持 YouTube 链接，视频最长约 1 小时，需为公开或不公开列出的视频。
---

# YouTube 视频分析器

使用 Gemini 原生视频理解能力分析 YouTube 视频，无需下载。

## 前置条件

```bash
pip install google-genai  # 视频分析
pip install yt-dlp        # 字幕提取
export GEMINI_API_KEY="your-key"        # 从 https://aistudio.google.com/apikey 获取（仅视频分析需要）
export YT_COOKIES_BROWSER="chrome"      # 可选，yt-dlp 使用的浏览器 cookie 来源
```

## 用法

```bash
# 视频分析（需要 GEMINI_API_KEY）
python scripts/analyze_youtube.py "YOUTUBE_URL" "你的提示词"

# 字幕提取（通过 yt-dlp，字幕文件保存到 subtitles/ 目录）
python scripts/analyze_youtube.py "YOUTUBE_URL" --subtitles --browser chrome
```

**参数说明：**
- `--model MODEL` - 指定 Gemini 模型（默认：gemini-3-pro-preview）
- `--format json` - 以 JSON 格式输出，而非纯文本
- `--api-key KEY` - 覆盖环境变量 GEMINI_API_KEY
- `--subtitles` - 通过 yt-dlp 提取字幕，而非 Gemini 分析
- `--browser BROWSER` - yt-dlp cookie 来源（如 `chrome`、`edge`、`"chrome:/path/to/profile"`），或设置环境变量 `YT_COOKIES_BROWSER`
- `--lang LANGS` - 字幕语言，逗号分隔（默认：en）

## 示例

```bash
# 基础分析
python scripts/analyze_youtube.py "https://youtu.be/xxx" "描述视频内容"

# 游戏玩法分析
python scripts/analyze_youtube.py "URL" "分析核心玩法：1.操作方式 2.游戏目标 3.反馈系统"

# 广告创意分析
python scripts/analyze_youtube.py "URL" "分析广告的Hook、卖点、CTA、目标受众"

# 使用快速模型
python scripts/analyze_youtube.py "URL" "简要总结" --model gemini-3-flash

# 提取字幕（使用浏览器 cookie 绕过 IP 限制）
python scripts/analyze_youtube.py "URL" --subtitles --browser chrome

# 提取字幕（JSON 格式）
python scripts/analyze_youtube.py "URL" --subtitles --browser chrome --format json

# 指定字幕语言 + 自定义浏览器 profile
python scripts/analyze_youtube.py "URL" --subtitles --lang "en,zh-Hans" --browser "chrome:/path/to/profile"
```

## 主要限制

| 限制 | 解决方案 |
|------|----------|
| 仅支持 YouTube | 非 YouTube 视频需通过 File API 上传 |
| 仅支持公开/不公开列出的视频 | 私密/年龄限制视频无法访问 |
| 最长约 1 小时 | 将长视频拆分为多段分析 |
| 无法精确定位时间戳 | 改为询问大致时间段描述 |

详细限制、模型对比及替代方案，请参阅 [references/gemini-video-limits.md](references/gemini-video-limits.md)。
