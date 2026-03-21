---
name: stream-grab-pro
description: |
  Download the highest-quality video and best available subtitles for links from YouTube, TikTok, 抖音, B站, 腾讯视频, 优酷, 爱奇艺, 芒果TV, 快手, 小红书, and 西瓜视频. Use when a user gives a video link in OpenClaw and wants the video plus subtitle files delivered back to IM without timing out. Prefer existing managed-browser login state or a local cookies.txt file. When platform subtitles are unavailable, ask the user whether to continue with Whisper instead of auto-running it. Also use this skill when the user replies “需要/继续/转录” to resume a pending Whisper subtitle job for the latest StreamGrabPro task in the same IM chat.
---

# StreamGrabPro

把 `StreamGrabPro_293042bb` 封装成一个直接可调用的下载 skill。

## 适用场景

- 用户给出支持平台的视频链接，想直接下载最高质量视频
- 用户希望同时保存可用字幕文件
- 用户通常在 OpenClaw 里使用，需要优先复用托管浏览器登录态

## 支持平台

- YouTube
- TikTok
- 抖音
- B站
- 腾讯视频
- 优酷
- 爱奇艺
- 芒果TV
- 快手
- 小红书
- 西瓜视频

## 默认行为

- 下载最高质量视频到 `{baseDir}/output/<job>/video/`
- 尽量抓取最佳可用字幕到 `{baseDir}/output/<job>/subtitles/`
- 长任务默认走“持久化 job + watcher”后台流程，避免当前会话超时后断尾
- 如果平台字幕抓取失败，先把视频发回 IM，再询问用户是否需要继续用 `whisper`
- 用户确认“需要”后，再启动独立的 Whisper 后台 job，默认模型是 `small`
- 字幕优先顺序：
  - 人工字幕优先于自动字幕
  - 默认语言优先尝试：`zh-Hans`、`zh-CN`、`zh`、`zh-TW`、`en`
- 同时保存：
  - 原始字幕文件
  - `srt`
  - 便于阅读的 `txt`

## 运行方式

优先使用后台 job 编排脚本：

```bash
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID"
```

常用参数：

```bash
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --auth managed_browser
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --auth cookies
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --browser-profile openclaw
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --lang zh-Hans
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --subtitle-source automatic
python3 {baseDir}/scripts/streamgrab_jobs.py start-whisper --channel dingtalk --target "TARGET_ID" --whisper-model small
```

## 授权规则

默认使用 `--auth auto`：

- 如果 `{baseDir}/cookies.txt` 存在，优先复用它
- 如果 `~/.openclaw/browser/openclaw/user-data` 存在，也会尝试复用托管浏览器登录态

如果脚本返回：

- `auth_required: true`
- 或报错里出现 `login`、`bot`、`cookies`

则暂停并询问用户二选一：

1. 托管浏览器登录（OpenClaw 内推荐）
2. 提供 `cookies.txt`

### 托管浏览器登录流程

如果用户选择托管浏览器登录，运行：

```bash
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open "VIDEO_URL"
```

让用户完成登录后，再用：

```bash
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --auth managed_browser
```

### cookies.txt 流程

- 让用户提供 Netscape 格式 `cookies.txt`
- 保存到 `{baseDir}/cookies.txt`
- 然后重新运行：

```bash
python3 {baseDir}/scripts/streamgrab_jobs.py start-download "VIDEO_URL" --channel dingtalk --target "TARGET_ID" --auth cookies
```

## 交付要求

- 成功时，告诉用户：
  - 视频文件路径
  - 字幕文件路径
  - 使用了哪种授权来源
- 下载阶段必须通过后台 watcher 收尾：
  - 当前会话里可以先告诉用户“已开始后台处理”
  - 真正的视频和字幕附件由 watcher 在任务完成后自动发回 IM
- 如果平台字幕存在：
  - watcher 先发视频附件
  - 再发主字幕文件
  - 发完字幕后立刻发送一段结构化总结
- 如果平台字幕不存在：
  - watcher 先发视频附件
  - 再询问用户是否需要继续用 Whisper 转录
  - 用户明确回复“需要/继续/转录”后，再启动 `start-whisper`
- 如果 `whisper` 成功：
  - 明确告诉用户这是 `whisper` 回退字幕
  - watcher 先发字幕文件
  - 发完字幕后立刻发送一段结构化总结
- 如果在 OpenClaw 里需要发回 IM：
  - 优先用当前会话的 channel/target 启动后台 job
  - 后台 watcher 使用 `openclaw message send` 自动发文本和附件
  - 如果当前会话没有明确的 IM target，先问用户发到哪里，不要启动后台 job
- 推荐执行顺序：
  - 首次收到视频链接时，运行 `start-download`
  - 如果用户是在同一 IM 会话里回复“需要/继续/转录”，优先检查是否存在 `awaiting_whisper_confirm` 的 StreamGrabPro job
  - 如果存在，就运行 `start-whisper`
  - 如果 `start-whisper` 找到多个待转录 job，再让用户指定 job id
- 总结风格：
  - 参考 `summarize` skill 的“tight summary first”思路
  - 用中文输出清晰结构，至少包含：
    - 一句话概览
    - 核心要点
    - 关键论据或例子
    - 对用户的启发
- 如果平台字幕和 `whisper` 都失败：
  - 明确告诉用户视频已下载，但当前没能生成字幕
  - 仍然交付视频文件路径

## 注意事项

- `whisper` 首次运行可能需要下载模型，默认模型目录是 `/tmp/whisper-models`
- 总结只基于字幕文本，不基于画面理解
- 某些平台即使有登录态，也可能没有可抓取字幕
- B站字幕可能需要浏览器登录态回退抓取
- 后台 job 状态保存在 `{baseDir}/output/jobs/<job_id>/state.json`
- 不要再临时使用 `nohup whisper ... &` 这种一次性后台进程来收尾，它没有自动续跑闭环
