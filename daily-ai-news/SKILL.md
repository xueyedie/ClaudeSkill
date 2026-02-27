---
name: daily-ai-news
description: "Aggregates and summarizes the latest AI news from multiple sources including AI news websites and web search. Provides concise news briefs with direct links to original articles. Activates when user asks for 'today's AI news', 'AI updates', 'latest AI developments', or mentions wanting a 'daily AI briefing'."
---

# Daily AI News Briefing

> Aggregates the latest AI news from multiple sources and delivers concise summaries with direct links

## When to Use This Skill

Activate this skill when the user:
- Asks for today's AI news or latest AI developments
- Requests a daily AI briefing or updates
- Mentions wanting to know what's happening in AI
- Asks for AI industry news, trends, or breakthroughs
- Wants a summary of recent AI announcements
- Says: "给我今天的AI资讯" (Give me today's AI news)
- Says: "AI有什么新动态" (What's new in AI)

## Workflow Overview

This skill uses a 7-phase workflow to select a template, gather, filter, categorize, classify by pyramid layer, format, and save AI news:

```
Phase 0: Template Selection
  └─ Ask user which output template to use (default: Standard)
      ↓
Phase 1: Information Gathering
  ├─ Direct website fetching (3-5 major AI news sites)
  └─ Web search with date filters
      ↓
Phase 2: Content Filtering
  ├─ Keep: Last 24-48 hours, major announcements
  └─ Remove: Duplicates, minor updates, old content
      ↓
Phase 3: Categorization
  └─ Organize into 5 categories
      ↓
Phase 3.5: Five-Layer Pyramid Classification (NEW)
  └─ Classify each news item into Huang's 5-layer AI stack
      ↓
Phase 4: Output Formatting
  └─ Per-news TOC index + Pyramid visualization + Layer-tagged news (use the selected template)
      ↓
Phase 5: Save to Markdown File
  └─ Write the final briefing to `./daily-AI-News/Output/`
```

## Output Language Requirements (Must Follow)

- **Final user-facing output must be in Simplified Chinese** (titles, summaries, bullet points, takeaways, and closing text).
- Proper nouns (company/product/model/paper names) may remain in English; if helpful, add a brief Chinese explanation on first mention.
- URLs must be kept as-is.
- If an original headline is English, you may show **Chinese headline** and optionally append the **English original in parentheses**.
- 最终简报还必须**落盘保存为 Markdown 文件**（见 Phase 5）。

## Phase 0: 选择输出模板（必问）

当技能被触发后，在开始抓取信息前，先用中文询问用户希望使用哪种“日报输出模板”。如果用户没有明确选择，则默认使用 **Standard（标准模板）**。

**询问话术（直接问）**：

- “你希望用哪个模板输出今天的 AI 日报？回复编号或名称即可（默认：1 标准）。”

**可选模板（与 `references/output_templates.md` 对应）**：

1. **标准（Standard）**：按分类输出，含摘要+要点（默认）
2. **简版（Brief）**：只看标题/链接 + 简短总结
3. **深度（Deep）**：包含更深入的分析、影响与洞察
4. **时间线（Chronological）**：按时间顺序组织（早/中/晚）
5. **按公司（By-Company）**：按公司聚合（OpenAI/Google/Anthropic 等）
6. **仅研究（Research-Only）**：只输出研究/论文相关内容

**快捷规则**：

- 如果用户在请求里已经明确说了“简版/深度/时间线/按公司/只看研究”，则直接选对应模板，不必再追问。
- 模板一旦确定，Phase 4 必须按该模板排版，并在 Phase 5 落盘保存。

## Phase 1: Information Gathering

### Step 1.1: Fetch from Primary AI News Sources

Use `mcp__web_reader__webReader` to fetch content from 3-5 major AI news websites:

**Recommended Primary Sources** (choose 3-5 per session):
- VentureBeat AI: https://venturebeat.com/category/ai/
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence
- MIT Technology Review AI: https://www.technologyreview.com/topic/artificial-intelligence/
- AI News: https://artificialintelligence-news.com/
- AI Hub Today: https://ai.hubtoday.app/

**Parameters**:
- `return_format`: markdown
- `with_images_summary`: false (focus on text content)
- `timeout`: 20 seconds per source

### Step 1.2: Execute Web Search Queries

Use `WebSearch` with date-filtered queries to discover additional news:

**Query Template** (adjust dates dynamically):
```
General: "AI news today" OR "artificial intelligence breakthrough" after:[2025-12-23]
Research: "AI research paper" OR "machine learning breakthrough" after:[2025-12-23]
Industry: "AI startup funding" OR "AI company news" after:[2025-12-23]
Products: "AI application launch" OR "new AI tool" after:[2025-12-23]
```

**Best Practices**:
- Always use current date or yesterday's date in filters
- Execute 2-3 queries across different categories
- Limit to top 10-15 results per query
- Prioritize sources from last 24-48 hours

### Step 1.3: Fetch Full Articles

For the top 10-15 most relevant stories from search results:
- Extract URLs from search results
- Use `mcp__web_reader__webReader` to fetch full article content
- This ensures accurate summarization vs. just using snippets

### Step 1.4: 技术大牛观点/知识分享抓取（必做）

为日报增加一个独立模块「技术大牛最新观点分享」，至少覆盖 1 位“技术大牛”的**最近 24–72 小时**观点/更新（默认：Andrej Karpathy）。

**优先信息源（Andrej Karpathy）**（详见 `references/news_sources.md` Tier 5）：
- https://karpathy.ai/
- https://karpathy.bearblog.dev/
- https://karpathy.medium.com/
- https://x.com/karpathy
- https://www.youtube.com/andrejkarpathy
- https://github.com/karpathy / https://gist.github.com/karpathy

**抓取策略**：
- 优先抓取“最新发布/最近更新”的页面或条目；只选 1-3 条放入日报模块（避免刷屏）
- 若页面难以直接判断时间，使用 WebSearch 辅助（例如 `site:karpathy.ai after:[yesterday] karpathy`、`site:x.com karpathy after:[yesterday]`）
- 同一观点如果多平台重复发布，保留最权威/最完整的那条，并在摘要中注明“同主题多平台同步”

## Phase 2: Content Filtering

### Filter Criteria

**Keep**:
- News from last 24-48 hours (preferably today)
- Major announcements (product launches, model releases, research breakthroughs)
- Industry developments (funding, partnerships, regulations, acquisitions)
- Technical advances (new models, techniques, benchmarks)
- Significant company updates (OpenAI, Google, Anthropic, etc.)

**Remove**:
- Duplicate stories (same news across multiple sources)
- Minor updates or marketing fluff
- Content older than 3 days unless highly significant
- Non-AI content or tangentially related articles

### Deduplication Strategy

When the same story appears in multiple sources:
- Keep the most comprehensive version
- Note alternative sources in the summary
- Prioritize authoritative sources (company blogs > news aggregators)

## Phase 3: Categorization

Organize news into 5 categories:

### 🔥 Major Announcements
- Product launches (new AI tools, services, features)
- Model releases (GPT updates, Claude features, Gemini capabilities)
- Major company announcements (OpenAI, Google, Anthropic, Microsoft, Meta)

### 🔬 Research & Papers
- Academic breakthroughs
- New research papers from top conferences
- Novel techniques or methodologies
- Benchmark achievements

### 💰 Industry & Business
- Funding rounds and investments
- Mergers and acquisitions
- Partnerships and collaborations
- Market trends and analysis

### 🛠️ Tools & Applications
- New AI tools and frameworks
- Practical AI applications
- Open source releases
- Developer resources

### 🌍 Policy & Ethics
- AI regulations and policies
- Safety and ethics discussions
- Social impact studies
- Government initiatives

## Phase 3.5: Five-Layer Pyramid Classification（黄仁勋五层架构分类 — 必做）

完成分类后，必须对每条新闻进行"五层金字塔"层级标注。该框架源自 NVIDIA 黄仁勋的观点：AI 产业自下而上分为五层，每一层被下一层"卡脖子"。

### 五层定义（自底向上）

| 层级 | 名称 | 标签 | 涵盖内容 |
|------|------|------|----------|
| L1 | 能源 | `⚡ L1-能源` | 电力供应、数据中心电力规划、能源成本、核电/可再生能源与AI、功耗效率 |
| L2 | 芯片 | `🔧 L2-芯片` | GPU/TPU/ASIC 新品、芯片性能、HBM 高带宽内存、NVLink 互联、芯片制造工艺、芯片供应链 |
| L3 | 基建 | `🏗️ L3-基建` | 数据中心建设、集群稳定性与利用率、训练中断问题、云计算基础设施、网络与存储架构 |
| L4 | 大模型 | `🧠 L4-大模型` | 模型发布、训练范式（预训练/SFT/RLHF）、Scaling Law、模型架构创新、基准测试、开源模型 |
| L5 | 应用 | `🚀 L5-应用` | AI 产品发布、Chatbot/Copilot/Agent/Autonomous AI、商业化、用户增长、应用层创新、提示词技巧 |

### 分类规则

1. **每条新闻必须标注一个主层级**（选最匹配的一层）
2. 如果一条新闻跨多层，选其**最核心贡献**所在层；可在摘要中备注关联层
3. 政策/伦理/监管类新闻：根据其影响的层级归类（例如芯片出口管制 → L2，AI 应用监管 → L5）
4. 产业与商业类（融资、并购）：根据公司主营业务所在层归类
5. 技术大牛观点：根据观点讨论的核心议题所在层归类

### 金字塔可视化模块（放在目录之后、正文分类之前）

在输出时，必须生成一个 **Mermaid 金字塔图** 或 **ASCII 文本金字塔**，将今日新闻条目数量按五层展示。格式示例：

```
## 🔺 今日新闻五层架构分布（黄仁勋 AI 产业金字塔）

> 框架来源：NVIDIA 黄仁勋 — AI 产业自下而上分为五层：能源 → 芯片 → 基建 → 大模型 → 应用。
> 越底层影响越大但变化越慢；越上层迭代越快但更易被替代。

                        ┌─────────┐
                       │ 🚀 应用  │ ← [N] 条
                      │  L5-应用  │
                     ├───────────┤
                    │ 🧠 大模型   │ ← [N] 条
                   │  L4-大模型   │
                  ├─────────────┤
                 │ 🏗️ 基建       │ ← [N] 条
                │  L3-基建       │
               ├───────────────┤
              │ 🔧 芯片          │ ← [N] 条
             │  L2-芯片          │
            ├─────────────────┤
           │ ⚡ 能源              │ ← [N] 条
          │  L1-能源              │
         └───────────────────┘

### 各层新闻一览

**⚡ L1-能源**：[新闻标题1]、[新闻标题2]…
**🔧 L2-芯片**：[新闻标题3]…
**🏗️ L3-基建**：[新闻标题4]…
**🧠 L4-大模型**：[新闻标题5]、[新闻标题6]…
**🚀 L5-应用**：[新闻标题7]、[新闻标题8]…

### 💡 层级洞察

- [用 1-2 句中文点评今日新闻在五层中的分布特点，例如"今日新闻集中在 L4 大模型层，反映出行业正处于模型迭代高峰期"]
- [若某层为空，可点评"L1 能源层今日无相关新闻，但能源仍是 AI 产业的终极瓶颈"]
```

### 新闻摘要层级标注格式

在每条新闻的 **摘要** 前面添加层级标签，格式为：

```
**摘要**： `⚡ L1-能源` [用 1 句中文概括]
```

或

```
**摘要**： `🧠 L4-大模型` [用 1 句中文概括]
```

标签使用行内代码格式（反引号包裹），紧跟在"**摘要**："之后、正文之前。

## Phase 4: Output Formatting

Use the following template for consistent output:

### 目录索引规则（新增 — 必做）

为避免“只有大框架目录”，最终 Markdown 必须包含 **每篇新闻的可点击目录索引**。

**硬性要求**：
- **目录必须细到每条新闻**：在「📑 目录」下，按分类做**二级嵌套**，列出该分类下每条新闻标题的链接。
- **每条新闻必须有稳定锚点**：在每条新闻标题上方插入一行 HTML 锚点：`<a id="xxx"></a>`，目录用 `(#xxx)` 进行链接，避免依赖不同渲染器的自动标题锚点规则。
- **锚点命名规则**：使用“分类缩写 + 两位序号”，同一份简报内唯一且连续。
  - 重要发布：`maj-01`、`maj-02`…
  - 研究与论文：`res-01`、`res-02`…
  - 产业与商业：`biz-01`、`biz-02`…
  - 工具与应用：`tool-01`、`tool-02`…
  - 政策与伦理：`pol-01`、`pol-02`…
  - 技术大牛观点：`guru-01`、`guru-02`…
- **可选但推荐**：在「🔺 今日新闻五层架构分布」里，“各层新闻一览”也尽量用同样的锚点链接到正文对应新闻条目。

```markdown
# 📰 AI 每日资讯简报

**日期**： [当前日期，例如 2026-02-23]
**来源**：来自 [Y] 个信息源，共 [X] 篇
**覆盖范围**：最近 24 小时

---

## 📑 目录

- [🔺 今日新闻五层架构分布（黄仁勋 AI 产业金字塔）](#-今日新闻五层架构分布黄仁勋-ai-产业金字塔)
- [🔥 重要发布](#-重要发布)
  - [（maj-01）新闻标题 1](#maj-01)
  - [（maj-02）新闻标题 2](#maj-02)
- [🔬 研究与论文](#-研究与论文)
  - [（res-01）论文/新闻标题 1](#res-01)
  - [（res-02）论文/新闻标题 2](#res-02)
- [💰 产业与商业](#-产业与商业)
  - [（biz-01）新闻标题 1](#biz-01)
- [🛠️ 工具与应用](#-工具与应用)
  - [（tool-01）新闻标题 1](#tool-01)
- [🌍 政策与伦理](#-政策与伦理)
  - [（pol-01）新闻标题 1](#pol-01)
- [🧠 技术大牛最新观点分享](#-技术大牛最新观点分享)
  - [（guru-01）观点标题 1](#guru-01)
- [🎯 今日要点](#-今日要点)

---

## 🔺 今日新闻五层架构分布（黄仁勋 AI 产业金字塔）

> 框架来源：NVIDIA 黄仁勋 — AI 产业自下而上分为五层：能源 → 芯片 → 基建 → 大模型 → 应用。
> 越底层影响越大但变化越慢；越上层迭代越快但更易被替代。

[ASCII 五层金字塔图 — 详见 Phase 3.5 说明]

### 各层新闻一览

**⚡ L1-能源**：[新闻标题](#maj-01)…
**🔧 L2-芯片**：[新闻标题](#biz-01)…
**🏗️ L3-基建**：[新闻标题](#res-01)…
**🧠 L4-大模型**：[新闻标题](#maj-02)…
**🚀 L5-应用**：[新闻标题](#tool-01)…

### 💡 层级洞察

- [今日分布特点点评]

---

## 🔥 重要发布

<a id="maj-01"></a>
### [新闻标题 1（中文，可选附英文原文）]

**摘要**： `🧠 L4-大模型` [用 1 句中文概括]

**要点**：
- [关键信息 1]
- [关键信息 2]
- [关键信息 3]

**影响/意义**： [为什么重要，用 1 句中文说明]

📅 **来源**： [媒体/机构] • [发布日期]
🔗 **链接**： [原文 URL]

---

<a id="maj-02"></a>
### [新闻标题 2]

[Same format as above, with layer tag before summary text]

---

## 🔬 研究与论文

<a id="res-01"></a>
### [新闻标题 3 / 论文标题]

[Same format as above, with layer tag before summary text]

---

## 💰 产业与商业

<a id="biz-01"></a>
### [新闻标题 4]

[Same format as above, with layer tag before summary text]

---

## 🛠️ 工具与应用

<a id="tool-01"></a>
### [新闻标题 5]

[Same format as above, with layer tag before summary text]

---

## 🌍 政策与伦理

<a id="pol-01"></a>
### [新闻标题 6]

[Same format as above, with layer tag before summary text]

---

## 🧠 技术大牛最新观点分享

<a id="guru-01"></a>
### [观点标题 1（例如：Karpathy 最新文章/推文主题）]

**摘要**： `🧠 L4-大模型` [用 1 句中文概括]

**要点**：
- [要点 1]
- [要点 2]

📅 **来源**： [作者/平台] • [发布日期]
🔗 **链接**： [原文 URL]

---

## 🎯 今日要点

1. [今日最重要的一条——1 句中文]
2. [第二重要——1 句中文]
3. [值得关注的趋势——1 句中文]

---

**生成时间**： [时间戳]
**下次更新**：欢迎明天再来获取最新 AI 资讯
```

## Phase 5: 保存为 Markdown 文件（必做）

完成 Phase 4 的最终排版后，必须把“最终简报 Markdown 内容”保存为一个 `.md` 文件。

- **输出目录**：`./daily-AI-News/Output/`
- **文件名**：`daily-ai-news-YYYYMMDD.md`（YYYYMMDD 为生成日期，例如 `20260223`）
- **文件内容**：必须与最终输出的简报 Markdown **完全一致**（不要额外包一层说明文字）
- **同名文件已存在时**：用最新内容直接覆盖

在最终对话回复里：
- 返回你写入的 **相对路径**，例如 `daily-AI-News/Output/daily-ai-news-20260223.md`
- 可选：附上 3-5 行中文预览（不必重复全文）

## 自定义选项（可选）

在你输出并落盘保存简报后，可以继续询问用户是否需要调整关注点、详略、时间范围或输出模板（如需更换模板，可按新模板重新排版并覆盖落盘文件）。

### 1. Focus Areas
“你希望我重点关注哪些方向？”
- 仅研究/论文
- 产品发布与工具
- 产业动态与融资
- 指定公司（OpenAI / Google / Anthropic 等）
- 技术教程与开发者资源

### 2. Depth Level
“你希望内容多详细？”
- **简版**：只看标题（每条 2-3 个要点）
- **标准**：摘要 + 要点（默认）
- **深入**：补充分析与影响判断

### 3. Time Range
“时间范围看多久？”
- 最近 24 小时（默认）
- 最近 3 天
- 最近 1 周
- 自定义范围

### 4. Format Preference
“你希望怎么组织内容？”
- 按分类（默认）
- 按时间线
- 按公司
- 按重要性排序

## Follow-up Interactions

### User: “展开讲讲 [新闻 X]”
**Action**: Use `mcp__web_reader__webReader` to fetch the full article, provide detailed summary + analysis

### User: “业内/专家怎么看 [话题 Y]？”
**Action**: Search for expert opinions, Twitter reactions, analysis pieces

### User: “找一些和 [新闻 Z] 类似的报道”
**Action**: Search related topics, provide comparative summary

### User: “只看研究/论文”
**Action**: Filter and reorganize output, exclude industry news

## Quality Standards

### Validation Checklist
- All links are valid and accessible
- No duplicate stories across categories
- All items have timestamps (preferably today)
- Summaries are accurate (not hallucinated)
- Links lead to original sources, not aggregators
- Mix of sources (not all from one publication)
- Balance between hype and substance
- **Output language is Simplified Chinese (except URLs and proper nouns where appropriate)**

### Error Handling
- If `webReader` fails for a URL → Skip and try next source
- If search returns no results → Expand date range or try different query
- If too many results → Increase threshold for significance
- If content is paywalled → Use available excerpt and note limitation

## Examples

### Example 1: Basic Request

**User**: "给我今天的AI资讯"

**AI Response**:
[Executes 4-phase workflow and presents formatted briefing with 5-10 stories across categories]

---

### Example 2: Time-specific Request

**User**: "What's new in AI this week?"

**AI Response**:
[Adjusts date filters to last 7 days, presents weekly summary]

---

### Example 3: Category-specific Request

**User**: "Any updates on AI research?"

**AI Response**:
[Focuses on Research & Papers category, includes recent papers and breakthroughs]

---

### Example 4: Follow-up Deep Dive

**User**: "Tell me more about the GPT-5 announcement"

**AI Response**:
[Fetches full article, provides detailed summary, offers to find expert reactions]

## Additional Resources

For comprehensive lists of news sources, search queries, and output templates, refer to:
- `references/news_sources.md` - Complete database of AI news sources
- `references/search_queries.md` - Search query templates by category
- `references/output_templates.md` - Alternative output format templates
