---
name: daily-ai-news-global
description: "Aggregates and summarizes the latest international AI news from multiple sources. Single-agent architecture with inlined Karpathy module. Activates on 'today's AI news', 'AI updates', 'latest AI developments', 'daily AI briefing'."
---

# Daily AI News Briefing — International Edition

> Single-Agent architecture: no sub-agent dispatch. All web fetching, searching, filtering, categorization, and formatting happen in the main conversation.

## When to Use This Skill

Activate this skill when the user:
- Asks for today's AI news or latest AI developments
- Requests a daily AI briefing or updates
- Mentions wanting to know what's happening in AI
- Asks for AI industry news, trends, or breakthroughs
- Wants a summary of recent AI announcements
- Says: "today's AI news", "AI updates", "latest AI developments", "daily AI briefing"

**Do NOT activate** for Chinese domestic AI news requests (use `daily-ai-news-cn` instead) or AI practice/tips requests (use `daily-ai-practice` instead).

## Output Language Requirements (Must Follow)

- **Final user-facing output must be in Simplified Chinese** (titles, summaries, bullet points, takeaways, and closing text).
- Proper nouns (company/product/model/paper names) may remain in English; if helpful, add a brief Chinese explanation on first mention.
- URLs must be kept as-is.
- If an original headline is English, you may show **Chinese headline** and optionally append the **English original in parentheses**.

---

## Phase 0: Template Selection (Must Ask)

Before fetching any data, ask the user in Chinese which output template they'd like. Default to **Standard** if no preference.

**Prompt**:
- "你希望用哪个模板输出今天的 AI 日报？回复编号或名称即可（默认：1 标准）。"

**Available Templates** (see `references/output_templates.md`):

1. **Standard** — categorized with summaries + key points (default)
2. **Brief** — headlines/links + short summary only
3. **Deep** — includes in-depth analysis and implications
4. **Chronological** — organized by time (morning/afternoon/evening)
5. **By-Company** — organized by company
6. **Research-Only** — papers and academic breakthroughs only

**Shortcut**: If the user already specified a style (e.g. "brief", "deep", "research only"), select that template without asking.

---

## Phase 1: Website Fetching

Fetch latest content from 3-5 Tier 1 sources using **WebFetch**:

- VentureBeat AI: https://venturebeat.com/category/ai/
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence
- MIT Technology Review AI: https://www.technologyreview.com/topic/artificial-intelligence/
- AI News: https://artificialintelligence-news.com/
- Hugging Face Blog: https://huggingface.co/blog

If a site fails, skip it and continue.

---

## Phase 2: Web Search

Execute 3-4 English search queries using **WebSearch**:

1. `"AI news today" OR "artificial intelligence breakthrough"` (last 24h)
2. `"AI research paper" OR "machine learning breakthrough"` (last 24h)
3. `"AI startup funding" OR "AI company news" OR "new AI tool"` (last 24h)
4. (Optional) Company-specific: `"OpenAI" OR "Google AI" OR "Anthropic" OR "Meta AI" announcement` (last 24h)

Refer to `references/search_queries.md` for more query templates.

---

## Phase 3: Full-Text Fetching

From Phase 1 + 2 results, select the **10-15 most important articles** and use **WebFetch** to get full text for accurate summarization.

---

## Phase 4: Karpathy Module (Inline)

Search for Andrej Karpathy's latest activity (last 24-72 hours):

1. **WebSearch** queries:
   - `"karpathy"` (last 3 days)
   - `site:x.com karpathy` (recent posts)
   - `site:karpathy.ai OR site:karpathy.bearblog.dev` (recent articles)

2. **WebFetch** any found content to confirm details and timing.

3. Select **1-3 most valuable** insights/posts.

4. If nothing found in 72 hours, note "最近 72 小时内 Karpathy 无新公开内容" in the guru section.

**Karpathy Sources** (priority order):
- X/Twitter: https://x.com/karpathy
- Personal site: https://karpathy.ai/
- Bear Blog: https://karpathy.bearblog.dev/
- YouTube: https://www.youtube.com/andrejkarpathy
- GitHub: https://github.com/karpathy
- Medium: https://karpathy.medium.com/

---

## Phase 5: Filter & Deduplicate

**Keep**:
- News from last 24-48 hours (prefer today)
- Major releases (product launches, model releases, research breakthroughs)
- Industry moves (funding, partnerships, acquisitions, regulation)
- Technical advances (new models, new techniques, new benchmarks)
- Major company updates (OpenAI, Google, Anthropic, Microsoft, Meta, etc.)

**Remove**:
- Duplicate coverage (same event from multiple sources — keep the most complete version)
- Marketing fluff or content-free articles
- News older than 3 days
- Non-AI or only tangentially related content

---

## Phase 6: Categorize + Pyramid Annotation

### 6.1 Five Categories

Assign each news item to one category:

- 🔥 **Major Releases** (major): product launches, model releases, major announcements
- 🔬 **Research & Papers** (research): academic breakthroughs, new papers, new techniques
- 💰 **Industry & Business** (industry): funding, M&A, partnerships, market trends
- 🛠️ **Tools & Applications** (tools): new tools, frameworks, open source releases
- 🌍 **Policy & Ethics** (policy): regulation, safety discussions, societal impact

### 6.2 Five-Layer Pyramid (Jensen Huang / NVIDIA AI Industry Framework)

Assign each news item a primary layer:

| Layer | Name | Tag | Scope |
|-------|------|-----|-------|
| L1 | Energy | `⚡ L1-能源` | Power supply, data center energy, power efficiency |
| L2 | Chips | `🔧 L2-芯片` | GPU/TPU/ASIC, chip performance, HBM, manufacturing |
| L3 | Infrastructure | `🏗️ L3-基建` | Data centers, cluster stability, cloud infrastructure |
| L4 | Large Models | `🧠 L4-大模型` | Model releases, training paradigms, scaling laws, architecture |
| L5 | Applications | `🚀 L5-应用` | AI products, Chatbot/Copilot/Agent, commercialization |

**Rules**:
1. One primary layer per item
2. Cross-layer items go to the layer of their core contribution
3. Policy items go by impact layer (chip export controls → L2, AI app regulation → L5)
4. Business items go by the company's primary business layer

---

## Phase 7: Format Output by Template

Use the selected template from Phase 0. See `references/output_templates.md` for full template specs.

### Directory Index Rules (Mandatory)

- **Directory must list every news item**: Under "📑 目录", nest each item title as a link under its category
- **Every news item must have a stable anchor**: Insert `<a id="xxx"></a>` above each item
- **Anchor naming**:
  - Major Releases: `maj-01`, `maj-02`…
  - Research: `res-01`, `res-02`…
  - Industry: `biz-01`, `biz-02`…
  - Tools: `tool-01`, `tool-02`…
  - Policy: `pol-01`, `pol-02`…
  - Karpathy: `guru-01`, `guru-02`…

### Pyramid Visualization (After TOC, Before Categories)

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
```

### Layer Tag on Each Summary

```
**摘要**： `🧠 L4-大模型` [用 1 句中文概括]
```

### Karpathy Section

Place Karpathy content in "🧠 技术大牛最新观点分享" using `guru-01`, `guru-02` anchors. If no content found, note "最近 72 小时无新公开内容".

---

## Phase 8: Save to Disk (Mandatory)

- **Output directory**: `./daily-AI-News/Output/`
- **Filename**: `daily-ai-news-YYYYMMDD.md` (YYYYMMDD = generation date)
- **Content**: Exact same Markdown as the final output
- **If file exists**: Overwrite with latest content

---

## Phase 9: Optional Follow-up

After saving, offer the user these options:

1. **Focus Areas**: "你希望我重点关注哪些方向？" (research/products/industry/specific company)
2. **Depth Level**: "你希望内容多详细？" (brief/standard/deep)
3. **Time Range**: "时间范围看多久？" (24h/3d/1w)

**Deep Dive**: "展开讲讲 [新闻 X]" → WebFetch full text + detailed summary

---

## Quality Standards

### Validation Checklist
- All links are valid and accessible
- No duplicate stories across categories
- All items have timestamps (preferably today)
- Summaries are accurate (not hallucinated)
- Links lead to original sources, not aggregators
- Mix of sources (not all from one publication)
- Balance between hype and substance
- **Output language is Simplified Chinese (except URLs and proper nouns)**

### Error Handling
- If a source fails → Note in final report, proceed with available data
- If search returns no results → Note "该类别今日无相关新闻"
- If too many results → Increase significance threshold
- If content is paywalled → Use available excerpt and note limitation

## Additional Resources

- `references/news_sources.md` - International AI news sources (Tier 1-5)
- `references/search_queries.md` - English search query templates
- `references/output_templates.md` - All 6 output format templates
