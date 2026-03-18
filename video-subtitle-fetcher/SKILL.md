---
name: video-subtitle-fetcher
user-invocable: true
description: |
  抓取视频字幕，当前支持 YouTube 和 B 站。
  适用场景：(1) 提取 YouTube 原始字幕或自动字幕，
  (2) 抓取 B 站网页可访问的字幕，
  (3) 生成便于阅读的纯文本转录，
  (4) 在需要时保留原始字幕文件。
  触发词："get subtitles"、"fetch subtitles"、"提取字幕"、"抓字幕"、
  "获取字幕"、"youtube 字幕"、"b站字幕"、"B站字幕抓取"
  限制：这里只负责字幕抓取，不负责 Gemini 视频内容分析。
---

# 视频字幕抓取器

统一处理 YouTube 和 B 站的视频字幕抓取需求。

如果用户要分析 YouTube 视频内容、总结画面、拆解玩法或做视觉理解，请改用 `youtube-analyzer`。  
如果用户明确要“抓字幕 / 导出字幕 / 提取转录”，优先使用本 skill。

## 平台分流规则

- YouTube 链接：走 `yt-dlp` 字幕抓取脚本
- B 站链接：走浏览器登录态 + 页面 API 抓取流程
- 其他平台：当前不在本 skill 支持范围内

## YouTube 字幕抓取

### 前置条件

```bash
pip install yt-dlp
export YT_COOKIES_BROWSER="chrome:/Users/bot/.openclaw/browser/openclaw/user-data"  # 可选，默认读取当前 OpenClaw 浏览器 profile
```

### 用法

```bash
python scripts/fetch_youtube_subtitles.py "YOUTUBE_URL"
python scripts/fetch_youtube_subtitles.py "YOUTUBE_URL" --lang "en,zh-Hans"
python scripts/fetch_youtube_subtitles.py "YOUTUBE_URL" --format json
python scripts/fetch_youtube_subtitles.py "YOUTUBE_URL" --browser "chrome:/path/to/profile"
```

### 输出

- 原始字幕文件：保存在 `subtitles/` 目录
- 默认文本输出：按时间顺序打印字幕内容
- `--format json`：输出结构化结果，包含语言、条目数和已保存文件路径
- 抓取完成后，整理一份可交付文本文件保存到工作区根目录的 `output/` 目录，即 `~/.openclaw/workspace/output/`
- 输出文件名应明确包含视频标题和抓取日期，建议格式：
  - YouTube：`youtube-<视频标题>-<YYYYMMDD>.txt`
  - B 站：`bilibili-<视频标题>-<YYYYMMDD>.txt`
- 文件名中的标题应做基础清洗，避免 `/`、`\\`、`:`、`*`、`?`、`"`、`<`、`>`、`|` 等非法字符
- 生成的 txt 文件开头应明确写出原始视频链接地址，便于回溯来源

## B 站字幕抓取

### 前置条件

- OpenClaw 浏览器 `profile=openclaw` 需要已登录 B 站账号
- 登录 cookie 持久化在浏览器 `user-data` 目录中

### 用法

```bash
python scripts/fetch_bilibili_subtitles.py "https://www.bilibili.com/video/BVxxxx"
python scripts/fetch_bilibili_subtitles.py "https://www.bilibili.com/video/BVxxxx" --format json
```

### 执行步骤

1. 从 URL 提取 BV 号，例如 `BV13EwJzfEbx`
2. 获取 `cid`

```bash
curl -s 'https://api.bilibili.com/x/web-interface/view?bvid=<BV号>' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Referer: https://www.bilibili.com/'
```

从返回 JSON 的 `data.cid` 取值，同时可获得标题、时长等信息。

3. 启动浏览器并打开视频页

```text
browser action=start profile=openclaw target=host
browser action=navigate url=https://www.bilibili.com/video/<BV号>/
```

等待页面加载完成。

4. 在页面内执行 JS，获取带签名的字幕 URL

```js
fetch('https://api.bilibili.com/x/player/v2?bvid=<BV号>&cid=<CID>', {
  credentials: 'include',
  headers: { Referer: 'https://www.bilibili.com/' }
}).then(r => r.json()).then(d => JSON.stringify(d.data.subtitle))
```

关键点：
- 必须带 `credentials: 'include'`，这样才能带上登录 cookie
- 从返回的 `subtitles[0].subtitle_url` 获取 CDN 地址
- `subtitle_url` 前面需要补 `https:` 前缀

5. 下载字幕 JSON

```bash
curl -s 'https:<subtitle_url>' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Referer: https://www.bilibili.com/'
```

返回 JSON 后，读取 `body` 数组，其中每项包含：
- `from`：起始秒数
- `to`：结束秒数
- `content`：字幕文本

6. 转换并保存

- 生成 SRT 文件并保存到工作区根目录的 `output/` 目录
- 生成纯文本文件并保存到工作区根目录的 `output/` 目录
- 文件名应包含视频标题和抓取日期，例如：
  - `bilibili-视频标题-20260314.txt`
- 原始字幕 JSON 可保存到 skill 的 `subtitles/` 目录作为调试产物
- 交付版 txt 文件顶部需包含：
  - 视频标题
  - 抓取日期
  - 原始链接地址
- 正文部分再写入整理后的字幕文本

7. 如果用户要求回传文件，将 SRT 作为附件发送

## 注意事项

- 字幕抓取不等于视频理解；涉及视频内容分析时请切换到 `youtube-analyzer`
- YouTube 不保证每个视频都有字幕；若没有字幕文件，优先向用户说明而不是反复重试
- B 站字幕签名 URL 有时效，过期后会返回 `403`，需要重新获取
- B 站若 `subtitles` 数组为空，说明该视频当前没有可用字幕
- 如果 B 站浏览器未登录，需要先提醒用户手动登录一次
- 无论是 YouTube 还是 B 站，最终交付给用户的 txt 文件都应写明原始视频链接地址
