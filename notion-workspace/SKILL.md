---
name: notion-workspace
user-invocable: true
description: |
  通过 Notion API 读取和写入你的 Notion 工作区内容。
  适用于搜索页面、读取页面正文、查询数据库、创建页面、更新页面属性、
  以及向页面追加正文内容等场景。
  触发词：notion、Notion、查 Notion、写入 Notion、更新页面、创建页面、查询数据库、同步到 notion。
  注意：只能访问已授权给当前 Notion integration 的页面和数据库，不能自动读取整个账号的所有内容。
---

# Notion Workspace Skill

这个 skill 通过 Notion 官方 API 访问你的 Notion 内容，覆盖当前最常用的读写操作。

## 能力边界

- 可以读取：
  - 已分享给当前 Notion integration 的页面
  - 已分享给当前 Notion integration 的数据库
- 可以写入：
  - 在已授权页面下创建子页面
  - 在已授权数据库中创建记录
  - 更新页面属性
  - 向页面正文追加段落/列表
- 不能直接读取：
  - 没有分享给 integration 的私人页面
  - 你整个 Notion 账号的所有内容

如果用户说“读写我的 Notion”，默认理解为：
“读写这个 integration 已被授权访问的 Notion 内容”。

## 首次配置

1. 在 Notion 创建一个 internal integration，并拿到 token。
2. 把要读写的页面或数据库 share 给这个 integration。
3. 在本机设置环境变量：

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_DEFAULT_DATABASE_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # 可选
export NOTION_DEFAULT_PARENT_PAGE_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # 可选
```

## 脚本位置

```bash
python3 /Users/bot/.openclaw/workspace/skills/notion-workspace/scripts/notion_cli.py --help
```

## 常用用法

### 1. 搜索页面 / 数据库

```bash
python3 scripts/notion_cli.py search "项目周报"
python3 scripts/notion_cli.py search "客户A" --page-size 5
```

### 2. 读取页面

```bash
python3 scripts/notion_cli.py get-page <page_id>
python3 scripts/notion_cli.py get-page <page_id> --format text
```

### 3. 查询数据库

```bash
python3 scripts/notion_cli.py query-database <database_id>
python3 scripts/notion_cli.py query-database default --page-size 10
```

如果 `database_id` 写 `default`，脚本会使用 `NOTION_DEFAULT_DATABASE_ID`。

### 4. 创建页面

在默认父页面下创建普通页面：

```bash
python3 scripts/notion_cli.py create-page \
  --parent-page-id default \
  --title "OpenClaw 测试页面" \
  --content "第一段\n第二段"
```

在默认数据库里创建记录：

```bash
python3 scripts/notion_cli.py create-page \
  --database-id default \
  --title "客户周报 2026-03-14" \
  --content "已自动同步自 OpenClaw"
```

### 5. 更新页面属性

```bash
python3 scripts/notion_cli.py update-page \
  <page_id> \
  --properties-json '{"Status":{"status":{"name":"Done"}}}'
```

### 6. 追加正文

```bash
python3 scripts/notion_cli.py append-text \
  <page_id> \
  --content "新增一段说明\n- 待办1\n- 待办2"
```

## 何时优先用这个 skill

- 用户明确要查 Notion 页面、数据库、客户资料、项目记录
- 用户要把当前结果同步到 Notion
- 用户要自动创建日报、周报、客户页、任务页

## 执行建议

- 先用 `search` 找到候选页面/数据库，再执行写入，减少误写。
- 批量写入前先向用户确认目标页面或数据库。
- 如果用户只说“写到 Notion”，优先使用默认父页面或默认数据库。
- 如果 API 返回权限错误，优先提醒用户去 Notion 里把页面/数据库 share 给 integration。
