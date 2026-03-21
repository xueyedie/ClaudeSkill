---
name: google-workspace-rest
user-invocable: true
description: |
  通过 Google 官方 OAuth 与 REST API 直接访问当前机器上已经授权的 Google Workspace 内容。
  适用于 Google Drive 文件搜索/读取、Google Sheets 元数据和单元格读取、
  Google Docs 文档读取、Google Calendar 事件查询等场景。
  不依赖 gws 或任何第三方 Google CLI。
  触发词：Google Workspace、Google Drive、Google Sheets、Google Docs、Google Calendar、
  读取 Google 文件、查 Drive 文件、查表格、读 Google Doc、查日历、Google API。
---

# Google Workspace REST Skill

这个 skill 的目标是让后续会话统一按“本地已授权凭据 + Google 官方 REST API”的方式访问 Google Workspace。

## 何时使用

- 用户要读取或搜索 Google Drive 里的文件
- 用户要读取 Google Sheets 的工作表或单元格
- 用户要读取 Google Docs 文档内容
- 用户要查询 Google Calendar 事件
- 用户明确要求不要依赖 `gws`、`gog` 等第三方 CLI

## 不要使用的路径

- 不要再调用 `gws`
- 不要假设本机装有任何第三方 Google Workspace CLI
- 不要重新做 OAuth，除非当前本地凭据确实失效

## 当前凭据来源

默认读取下面这些本地文件：

- `~/.config/gws/credentials.enc`
- `~/.config/gws/.encryption_key`
- `~/.config/gws/token_cache.json`
- `~/.config/gws/client_secret.json` 仅作为备用配置保留，不应作为主要依赖

脚本会先解密 `credentials.enc`，取出 `client_id`、`client_secret`、`refresh_token`，
再向 Google 官方 token endpoint 刷新 `access_token`，随后直接调用 Google 官方 REST API。

## 授权边界

- 当前只应默认认为已授权：`Drive`、`Sheets`、`Docs`、`Calendar`
- 不要默认使用 `Gmail`
- 如果 REST API 返回 `403` / `401` / `insufficient permissions`，优先判断是 scope 或资源权限问题，而不是先重做登录

## 脚本位置

```bash
node /Users/bot/.openclaw/workspace/skills/google-workspace-rest/scripts/google_workspace_rest.mjs --help
```

## 推荐工作流

### 1. 先确认 token 可刷新

```bash
node scripts/google_workspace_rest.mjs token-info
```

### 2. Drive 搜索文件

```bash
node scripts/google_workspace_rest.mjs drive-list --page-size 10
node scripts/google_workspace_rest.mjs drive-list --query "trashed=false and mimeType='application/vnd.google-apps.spreadsheet'"
node scripts/google_workspace_rest.mjs drive-list --fields "files(id,name,mimeType,modifiedTime,webViewLink)"
```

### 3. Sheets 读取

```bash
node scripts/google_workspace_rest.mjs sheets-metadata <spreadsheet_id>
node scripts/google_workspace_rest.mjs sheets-values <spreadsheet_id> "Sheet1!A1:D20"
```

### 4. Docs 读取

```bash
node scripts/google_workspace_rest.mjs docs-get <document_id>
```

### 5. Calendar 查询

```bash
node scripts/google_workspace_rest.mjs calendar-events primary --time-min 2026-03-19T00:00:00Z --time-max 2026-03-20T00:00:00Z
```

### 6. 需要更底层时，直接打任意官方 API

```bash
node scripts/google_workspace_rest.mjs request GET "https://www.googleapis.com/drive/v3/files?pageSize=5&fields=files(id,name)"
node scripts/google_workspace_rest.mjs request GET "https://sheets.googleapis.com/v4/spreadsheets/<sheet_id>"
```

## 执行建议

- 如果用户只说“看看我的 Google 文件”，优先从 `drive-list` 开始
- 如果先知道文件名、不知道 ID，先走 Drive 搜索，再进入 Sheets/Docs
- 读取表格时，先看 `sheets-metadata`，再决定读哪个工作表范围
- 如果要读 Google Docs 正文，优先 `docs-get`，不要误把 Docs 当普通二进制文件下载
- 如果要给用户一个稳定链接，优先返回 `webViewLink`

## 常见问题

- `401 invalid credentials`
  - 说明 access token 失效且 refresh 失败，先检查本地凭据链是否还完整
- `403 insufficient permissions`
  - 说明当前 OAuth scope 或目标资源权限不够
- 找不到文件
  - 先确认该文件是否确实对当前账号可见
- 只想看授权是否通
  - 先跑 `token-info`，再跑一次 `drive-list --page-size 3`

## 返回结果要求

- 给用户展示结果时，优先整理成简洁列表
- 引用 Google 资源时，尽量带 `id`、`name`、`mimeType`
- 若只做了只读查询，明确说明未修改任何 Google 内容
