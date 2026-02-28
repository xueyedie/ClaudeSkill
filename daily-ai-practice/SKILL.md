---
name: daily-ai-practice
description: "AI 实战技巧日报 — 不追新闻热点，只追'今天能用'的 AI 技巧。聚焦 AI 编程、AI 美术工作流、AI 提效工具和 GitHub 热门。Activates on 'AI实战', 'AI技巧', 'AI practice', 'AI编程技巧', 'ComfyUI教程', 'AI工具推荐'."
---

# AI 实战技巧日报

> **核心定位：不追新闻热点，只追"今天能用"的 AI 技巧。**
> 聚焦可立刻应用到工作中的技术分享：AI 编程实战、AI 美术工作流、AI 提效工具。
> Single-Agent architecture, no sub-agent dispatch.

## When to Use This Skill

Activate this skill when the user:
- Says: "AI实战" / "AI技巧" / "AI practice"
- Says: "AI编程技巧" / "Claude Code 最佳实践" / "Cursor 技巧"
- Says: "ComfyUI教程" / "AI美术工作流" / "SD技巧" / "Flux教程"
- Says: "AI工具推荐" / "AI提效" / "AI工具发现"
- Asks about practical AI tips, tricks, or workflows
- Wants actionable AI techniques (not industry news)

**Do NOT activate** for general AI news (use `daily-ai-news-global` or `daily-ai-news-cn`).

## Output Language Requirements

- **Final output must be in Simplified Chinese**
- Technical terms, tool names, code snippets may remain in English
- URLs must be kept as-is

---

## Phase 0: Focus Selection

Ask the user which focus areas they want. Default: **All**.

**Prompt**: "你想看哪个方向的 AI 实战技巧？回复编号即可（默认：4 全部）。"

1. **🖥️ AI 编程实战** — Claude Code、Cursor、提示词工程、LLM 集成
2. **🎨 AI 美术工作流** — ComfyUI、SD/Flux、AI 3D/视频、游戏美术管线
3. **🔧 AI 提效工具** — 新工具发现、插件、自动化方案
4. **全部**（默认）— 编程 + 美术 + 工具 + GitHub 热门

**Shortcut**: If user already specified a direction, select directly.

---

## Phase 1: AI Coding Practice Search

Search for practical AI coding tips and best practices.

### 1.1 WebSearch Queries (English)
```
"Claude Code" best practices OR tips OR workflow
```
```
"Cursor" AI coding tips OR tricks OR tutorial
```
```
"prompt engineering" practical tips OR best practices 2026
```
```
"LLM" integration OR API best practices tutorial
```

### 1.2 WebFetch Engineering Blogs (pick 2-3)
- Anthropic Engineering: https://www.anthropic.com/engineering
- OpenAI Cookbook: https://cookbook.openai.com
- Vercel AI Blog: https://vercel.com/blog
- LangChain Blog: https://blog.langchain.dev
- Cursor Blog: https://cursor.com/blog

### 1.3 WebSearch Expert Content
```
site:simonwillison.net AI OR LLM
```
```
site:latent.space AI engineering
```
```
"karpathy" tutorial OR lesson OR method
```

---

## Phase 2: AI Art Workflow Search

Search for ComfyUI, SD/Flux, and AI art production tips.

### 2.1 WebSearch Queries
```
"ComfyUI" workflow OR tutorial OR new node 2026
```
```
"Stable Diffusion" OR "Flux" tips OR tricks OR workflow
```
```
"AI 3D" generation OR modeling tutorial
```
```
"AI video" generation OR "Sora" OR "Kling" OR "Runway" tutorial
```

### 2.2 Chinese Art Searches
```
"ComfyUI" 工作流 OR 教程 OR 节点
```
```
"AI绘画" 技巧 OR 教程 OR 工作流
```
```
"AI美术" 实战 OR 管线 OR pipeline
```
```
site:xiaohongshu.com "ComfyUI" OR "AI绘画" OR "SD" 教程
```

### 2.3 WebFetch Art Sources (pick 1-2)
- Civitai: https://civitai.com/
- LiblibAI: https://www.liblib.art/
- ComfyUI GitHub: https://github.com/comfyanonymous/ComfyUI

---

## Phase 3: AI Efficiency Tools Search

Search for new AI tools and productivity solutions.

### 3.1 WebSearch Queries
```
"AI tool" new OR launch OR release 2026
```
```
"AI productivity" tool OR plugin OR extension
```
```
"AI automation" workflow OR tool
```
```
site:producthunt.com AI tool
```

### 3.2 Chinese Tool Searches
```
"AI工具" 推荐 OR 新上线 OR 测评
```
```
"AI提效" OR "AI自动化" 工具 OR 方案
```
```
site:xiaohongshu.com "AI工具" OR "效率工具"
```

---

## Phase 4: GitHub Trending Scan

### 4.1 WebFetch GitHub Trending
- https://github.com/trending (today or this week)

### 4.2 WebSearch
```
GitHub trending AI repository 2026
```
```
GitHub "machine learning" OR "LLM" OR "AI" trending stars
```

### 4.3 Filter Criteria
- Must be AI-related (LLM, ML, AI tools, ComfyUI nodes, etc.)
- Prefer repos with: clear README, active commits, practical use
- Select 3-5 most relevant repos

---

## Phase 5: Full-Text Fetch + Quality Filter

### 5.1 Full-Text Fetch
Use **WebFetch** to get full content from the 10-15 most promising results across all phases.

### 5.2 Quality Filter — Core Criterion: **Actionability**

**Keep** (must be actionable):
- Step-by-step tutorials or guides
- Specific workflow/pipeline descriptions
- Code snippets or configuration examples
- Tool comparisons with practical recommendations
- Best practices with concrete examples
- New tool announcements with "how to get started"

**Remove**:
- Pure theory without practical application
- Industry news/funding/company announcements (that's for the news skills)
- Marketing content without substance
- Content older than 7 days
- Duplicate/overlapping content

---

## Phase 6: Categorize + Rate + Tag

### 6.1 Four Categories

| Category | Anchor | Content |
|----------|--------|---------|
| 🖥️ AI 编程实战 | `code-01` | Claude Code workflows, Cursor tips, prompt engineering, LLM integration |
| 🎨 AI 美术工作流 | `art-01` | ComfyUI workflows, SD/Flux tips, AI 3D/video, game art pipeline |
| 🔧 AI 提效工具 | `tool-01` | New tool discovery, plugins, automation solutions |
| 🔥 GitHub 热门 | `gh-01` | Trending AI repos worth trying |

### 6.2 Difficulty Rating (per item)

- ⭐ **入门** — Anyone can follow, no prerequisites
- ⭐⭐ **进阶** — Requires basic knowledge of the domain
- ⭐⭐⭐ **高级** — Requires significant experience, advanced techniques

### 6.3 Applicability Tags (per item, multiple allowed)

- 🎮 **游戏开发** — Relevant to game development
- 🎨 **美术创作** — Relevant to art/design creation
- 💻 **日常编码** — Relevant to everyday programming
- ⚡ **效率提升** — General productivity improvement

---

## Phase 7: Format Output

Use the practice-oriented template from `references/output_templates.md`.

### Key Differences from News Skills
- **No pyramid visualization** (that's a news framework, not applicable here)
- **No news categories** (use the 4 practice categories instead)
- **Actionability is king** — every item must tell the reader what to DO
- **"Today's Action List"** at the end — 3-5 checkbox items the reader can try today

---

## Phase 8: Save to Disk (Mandatory)

- **Output directory**: `./daily-AI-News/Output/`
- **Filename**: `daily-ai-practice-YYYYMMDD.md`
- **Content**: Exact same Markdown as the final output
- **If file exists**: Overwrite with latest content

---

## Quality Standards

### Validation Checklist
- Every item is actionable (reader knows what to DO)
- Difficulty ratings are accurate
- Applicability tags match the content
- No industry news mixed in (that belongs in news skills)
- Links are valid and lead to original sources
- Mix of English and Chinese sources
- Balance across selected focus areas
- **Output language is Simplified Chinese**

### Error Handling
- If a source fails → Skip and continue
- If a category has no results → Note "今日该方向暂无新实战内容"
- If too many results → Prioritize by actionability and recency

## Additional Resources

- `references/practice_sources.md` - Practice-focused sources (English + Chinese)
- `references/search_queries.md` - Practice-specific search queries
- `references/output_templates.md` - Practice checklist output template
