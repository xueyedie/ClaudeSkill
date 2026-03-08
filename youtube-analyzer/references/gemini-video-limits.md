# Gemini 视频理解 - 限制与优化

## API 限制

### 视频时长
| 模型 | 最大时长 | 备注 |
|------|----------|------|
| gemini-3-pro-preview | 约 1 小时 | 质量最佳 |
| gemini-3-flash | 约 1 小时 | 更快、更便宜 |
| gemini-2.5-flash | 约 1 小时 | 备选方案 |

### 速率限制（免费套餐）
- **RPM（每分钟请求数）**：15
- **TPM（每分钟 Token 数）**：1,000,000
- **RPD（每日请求数）**：1,500

### Token 消耗
视频处理会消耗大量 Token：
- 短视频（约 1 分钟）：约 1,000–2,000 tokens
- 中等视频（约 10 分钟）：约 10,000–20,000 tokens
- 长视频（30 分钟以上）：约 50,000+ tokens

## 支持的 URL 格式

```
✅ 支持：
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID
- https://www.youtube.com/shorts/VIDEO_ID
- https://www.youtube.com/v/VIDEO_ID

❌ 不支持：
- https://vimeo.com/...
- https://www.tiktok.com/...
- https://example.com/video.mp4
- 任何非 YouTube 链接
```

## 视频访问要求

| 视频类型 | 是否支持 | 备注 |
|----------|----------|------|
| 公开视频 | ✅ | 正常使用 |
| 不公开列出 | ✅ | 有链接即可访问 |
| 私密视频 | ❌ | 无法访问 |
| 年龄限制 | ❌ | 需要登录 |
| 会员专属 | ❌ | 需要订阅 |
| 地区限制 | ⚠️ | 取决于 Google 服务器，可能失败 |
| 已删除 | ❌ | 无法访问 |

## 优化策略

### 针对长视频
1. **指定时间段**："前 5 分钟发生了什么？"
2. **请求摘要**："用要点形式总结"
3. **分段分析**：针对不同时间段发起多次请求

### 针对速率限制
1. 请求之间加延迟：免费套餐使用 `time.sleep(4)`
2. 尽量在单次请求中合并多个提示词
3. 对非关键分析使用 flash 模型

### 提升结果质量
1. **具体描述需求**："描述游戏机制" 优于 "视频里有什么"
2. **要求结构化输出**："列出涵盖的主要话题"
3. **提供背景信息**："作为游戏分析师，评估……"

## 替代方案

当 Gemini YouTube 分析不可用时：

### 1. 字幕提取（仅文本）
```bash
pip install youtube-transcript-api
```
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('VIDEO_ID')
```

### 2. 下载 + 帧提取（视觉内容）
```bash
# 下载视频
yt-dlp -f "best[height<=720]" "URL" -o video.mp4

# 提取帧
ffmpeg -i video.mp4 -vf "fps=0.1" frames/frame_%04d.jpg
```

### 3. File API 上传（非 YouTube 视频）
```python
from google import genai

client = genai.Client(api_key=API_KEY)
video_file = client.files.upload(file="video.mp4")
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[video_file, "描述这个视频"]
)
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Cannot fetch content from URL` | 视频私密或受限 | 改用公开视频 |
| `RESOURCE_EXHAUSTED` | 触发速率限制 | 等待后重试 |
| `INVALID_ARGUMENT` | URL 格式错误 | 检查 URL 有效性 |
| `DEADLINE_EXCEEDED` | 视频过长或超时 | 尝试更短的视频 |
| `NoneType object` | API 响应异常 | 重试或检查 SDK 版本 |

## 视频分析模型对比

| 模型 | 速度 | 质量 | 成本 | 适用场景 |
|------|------|------|------|----------|
| gemini-3-pro-preview | 慢 | 最佳 | 高 | 深度分析 |
| gemini-3-flash | 快 | 良好 | 低 | 快速摘要 |
| gemini-2.5-pro | 中等 | 优秀 | 中等 | 均衡使用 |
| gemini-2.5-flash | 最快 | 良好 | 最低 | 批量处理 |
