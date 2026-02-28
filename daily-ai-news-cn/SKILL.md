---
name: daily-ai-news-cn
description: "Aggregates and summarizes the latest Chinese domestic AI news. Single-agent architecture with game/art vertical coverage. Activates on '国内AI新闻', '中国AI动态', '国内AI资讯', '国产大模型'."
---

# AI 每日资讯简报 — 国内版

> Single-Agent architecture: no sub-agent dispatch. All web fetching, searching, filtering, categorization, and formatting happen in the main conversation.

## When to Use This Skill

Activate this skill when the user:
- Says: "国内AI新闻" / "中国AI动态" / "国内AI资讯"
- Says: "国产大模型有什么新消息"
- Says: "国内AI公司最近有什么动态"
- Asks about Chinese domestic AI developments
- Asks about Chinese LLMs (DeepSeek, Qwen, GLM, Kimi, etc.)
- Asks about AI+游戏 or AI美术 in Chinese context

**Do NOT activate** for international AI news (use `daily-ai-news-global`) or AI practice tips (use `daily-ai-practice`).

## Output Language Requirements (Must Follow)

- **Final output must be in Simplified Chinese**
- Proper nouns (company/product/model names) may remain in English
- URLs must be kept as-is

---

## Phase 0: Template Selection (Must Ask)

Before fetching, ask the user which template to use. Default: **Standard**.

**Prompt**: "你希望用哪个模板输出今天的国内 AI 日报？回复编号即可（默认：1 标准）。"

**Available Templates** (see `references/output_templates.md`):

1. **Standard** — categorized with summaries + key points (default)
2. **Brief** — headlines + short summary only
3. **Deep** — includes in-depth analysis and implications

**Shortcut**: If user already specified a style, select directly without asking.

---

## Phase 1: Domestic Media Fetching

Fetch latest content from domestic AI media using **WebFetch**:

**Required (at least 3)**:
- 36氪 AI: https://36kr.com/information/AI/
- 机器之心: https://www.jiqizhixin.com/
- 量子位: https://www.qbitai.com/

**Optional (1-2 more)**:
- 新智元: https://www.ai-era.com/
- InfoQ AI 前线: https://www.infoq.cn/topic/AI
- AI科技评论（雷锋网）: https://www.leiphone.com/category/ai

If a site fails, skip and continue.

---

## Phase 2: Chinese Web Search

Execute 3-4 Chinese search queries using **WebSearch**:

1. `"AI 新闻" OR "人工智能" OR "大模型" 最新动态`
2. `"百度AI" OR "通义千问" OR "智谱AI" OR "DeepSeek" OR "豆包" OR "Kimi"`
3. `"国产大模型" OR "国内AI" OR "中国AI"`
4. (Optional) `"AI监管" OR "开源大模型"`

Also try site-specific searches:
- `site:36kr.com AI OR 大模型`
- `site:jiqizhixin.com 最新`
- `site:qbitai.com 最新`

Refer to `references/search_queries.md` for more templates.

---

## Phase 3: Game & Art Vertical Search (Dedicated Phase — Higher Priority)

This is a **dedicated phase** to ensure game/art content is not overlooked.

### 3.1 Game + AI Search
```
"AI游戏" OR "AI+游戏" OR "游戏AI" OR "AI NPC" OR "AI辅助游戏开发"
```
```
site:youxiputao.com AI OR 人工智能
```

### 3.2 AI Art Search
```
"AI绘画" OR "AI美术" OR "AIGC美术" OR "AI生成资产" OR "AI美术资产"
```
```
"Stable Diffusion" OR "Flux" OR "ComfyUI" 最新 OR 教程 OR 工作流
```
```
"AI视频生成" OR "AI动画" OR "Sora" OR "可灵" OR "Kling" OR "Runway"
```

### 3.3 Vertical Source WebFetch (at least 1)
- 游戏葡萄: https://youxiputao.com/
- LiblibAI: https://www.liblib.art/
- 站酷 ZCOOL: https://www.zcool.com.cn/

---

## Phase 4: Full-Text Fetching

From Phase 1-3 results, select the **10-15 most important articles** and use **WebFetch** to get full text for accurate summarization.

---

## Phase 5: Filter, Deduplicate & Tag

### 5.1 Keep
- News from last 24-48 hours (prefer today)
- Chinese LLM releases/updates (DeepSeek, Qwen, GLM, Kimi, etc.)
- Domestic AI company major moves (funding, products, strategy)
- Chinese AI policy/regulation updates
- Chinese research institution papers/results
- Domestic AI tools/applications launches
- AI+Game: AI NPC, AI-assisted game dev, game engine AI features
- AI Art: new models/tools, ComfyUI workflows, AI 3D generation
- Xiaohongshu/Bilibili AI trending topics

### 5.2 Remove
- Pure translations of international news (unless with unique domestic perspective)
- Marketing fluff / content-free articles
- News older than 3 days
- Duplicates of international news already covered in global edition

### 5.3 game_art_tag Annotation
For each news item, assign a tag:
- `game` — if related to AI + gaming
- `art` — if related to AI art / painting / 3D / video generation
- `none` — otherwise

---

## Phase 6: Categorize + Pyramid + Game/Art Labels

### 6.1 Five Categories

- 🔥 **重要发布** (major) — 国产大模型发布/更新、国内 AI 产品上线
- 🔬 **研究与论文** (research) — 国内高校/研究机构论文、中国团队顶会论文
- 💰 **产业与商业** (industry) — 国内 AI 融资、BAT/字节等巨头布局
- 🛠️ **工具与应用** (tools) — 国产 AI 工具、国内开源项目、AI 美术资产生成工具
- 🌍 **政策与伦理** (policy) — 中国 AI 监管政策、算法备案、数据安全

### 6.2 Five-Layer Pyramid (Same as Global)

| Layer | Name | Tag | Scope |
|-------|------|-----|-------|
| L1 | 能源 | `⚡ L1-能源` | 电力供应、数据中心电力、功耗效率 |
| L2 | 芯片 | `🔧 L2-芯片` | GPU/TPU/ASIC、芯片性能、HBM、制造工艺 |
| L3 | 基建 | `🏗️ L3-基建` | 数据中心建设、集群稳定性、云基础设施 |
| L4 | 大模型 | `🧠 L4-大模型` | 模型发布、训练范式、Scaling Law、架构创新 |
| L5 | 应用 | `🚀 L5-应用` | AI 产品、Chatbot/Copilot/Agent、商业化 |

### 6.3 Game/Art Labels in Titles

- `game_art_tag: game` → add `🎮 游戏` label in the summary line
- `game_art_tag: art` → add `🎨 美术` label in the summary line
- These items also appear in the dedicated "🎮🎨 游戏与美术专区" section

---

## Phase 7: Format Output

Use the selected template from Phase 0. See `references/output_templates.md`.

### Header Format
```markdown
# 📰 AI 每日资讯简报（国内版）

**日期**： [当前日期]
**来源**：来自 [Y] 个国内信息源，共 [X] 篇
**覆盖范围**：最近 24 小时（聚焦中国国内 AI 动态）
```

### Directory Index Rules (Mandatory)
- Directory must list every news item
- Every item must have a stable anchor: `<a id="xxx"></a>`
- Anchor naming: `maj-01`, `res-01`, `biz-01`, `tool-01`, `pol-01`, `game-01`, `art-01`

### Pyramid Visualization (Same as Global)
Include the full pyramid visualization block after the TOC.

### Game & Art Section (Dedicated)
After all 5 category sections, include:

```markdown
## 🎮🎨 游戏与美术专区

> 聚焦 AI+游戏开发和 AI 美术资产生成领域的最新动态。

### 🎮 AI+游戏

<a id="game-01"></a>
#### [游戏相关新闻标题]
**摘要**： `🚀 L5-应用` 🎮 游戏 [用 1 句中文概括]
...

### 🎨 AI 美术

<a id="art-01"></a>
#### [美术相关新闻标题]
**摘要**： `🚀 L5-应用` 🎨 美术 [用 1 句中文概括]
...
```

**Note**: Game/art items appear BOTH in their primary category AND in this dedicated section (cross-referenced).

---

## Phase 8: Save to Disk (Mandatory)

- **Output directory**: `./daily-AI-News/Output/`
- **Filename**: `daily-ai-news-cn-YYYYMMDD.md` (with `-cn` suffix)
- **Content**: Exact same Markdown as the final output
- **If file exists**: Overwrite with latest content

---

## Quality Standards

### Validation Checklist
- All links are valid and accessible
- No duplicate stories across categories
- All items have timestamps (preferably today)
- Summaries are accurate (not hallucinated)
- Links lead to original sources
- Mix of sources (not all from one publication)
- Game/art tagged items appear in both category and dedicated section
- **Output language is Simplified Chinese**

### Error Handling
- If a source fails → Note in final report, proceed with available data
- If search returns no results → Note "该类别今日无相关新闻"
- If too many results → Increase significance threshold
- If content is paywalled → Use available excerpt and note limitation

## Additional Resources

- `references/news_sources.md` - Chinese domestic AI news sources
- `references/search_queries.md` - Chinese search query templates
- `references/output_templates.md` - 3 output format templates (Standard/Brief/Deep)
