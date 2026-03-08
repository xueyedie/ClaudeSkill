---
name: youtube-analyzer
user-invocable: true
description: |
  使用 Gemini 原生视频理解能力分析 YouTube 视频内容。
  适用场景：(1) 了解 YouTube 视频的内容，
  (2) 从视频中提取关键信息，
  (3) 总结或描述视频画面，
  (4) 分析游戏玩法、教程、演示或任何视觉内容。
  触发词："analyze this youtube"、"what's in this video"、"summarize this video"、
  "describe this youtube"、"分析这个视频"、"这个视频讲了什么"、"youtube视频内容"
  限制：仅支持 YouTube 链接，视频最长约 1 小时，需为公开或不公开列出的视频。
---

# YouTube 视频分析器

使用 Gemini 原生视频理解能力分析 YouTube 视频，无需下载。

## 前置条件

```bash
pip install google-genai
export GEMINI_API_KEY="your-key"  # 从 https://aistudio.google.com/apikey 获取
```

## 用法

```bash
python scripts/analyze_youtube.py "YOUTUBE_URL" "你的提示词"
```

**参数说明：**
- `--model MODEL` - 指定 Gemini 模型（默认：gemini-3-pro-preview）
- `--format json` - 以 JSON 格式输出，而非纯文本
- `--api-key KEY` - 覆盖环境变量 GEMINI_API_KEY

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
```

## 主要限制

| 限制 | 解决方案 |
|------|----------|
| 仅支持 YouTube | 非 YouTube 视频需通过 File API 上传 |
| 仅支持公开/不公开列出的视频 | 私密/年龄限制视频无法访问 |
| 最长约 1 小时 | 将长视频拆分为多段分析 |
| 无法精确定位时间戳 | 改为询问大致时间段描述 |

详细限制、模型对比及替代方案，请参阅 [references/gemini-video-limits.md](references/gemini-video-limits.md)。
