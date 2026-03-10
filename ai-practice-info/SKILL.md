---
name: ai-practice-info
user-invocable: true
description: "AI 实战技巧日报 — 不追新闻热点，只追'今天能用'的 AI 技巧。聚焦 AI 编程、AI 美术工作流、AI 提效工具和 GitHub 热门。触发词：'AI实战'、'AI技巧'、'AI practice'、'AI编程技巧'、'AI美术工作流'、'AI工具推荐'。"
---

# AI 实战技巧日报

> **核心定位：不追新闻热点，只追"今天能用"的 AI 技巧。**
> 聚焦可立刻应用到工作中的技术分享：AI 编程实战、AI 美术工作流、AI 提效工具。
>
> **多智能体并行架构**：主智能体作为调度器，通过 Agent tool 并行派发 5 个 Worker 子智能体分别负责不同分类的搜索与抓取，最后由主智能体汇总、去重、过滤、格式化并输出。搜索阶段从串行 ~20 分钟压缩到并行 ~5 分钟。
>
> **检查点机制**：每个 Worker 将原始结果写入 `output/.cache/practice-{category}-YYYYMMDD.md`。如果执行中断，再次触发时自动跳过已完成的 Worker，只补跑缺失分类。
>
> **内容获取方式**：优先使用 WebFetch 直接抓取页面内容；遇到需要登录或动态渲染的页面（如 B站关注列表、小红书），使用托管浏览器（browser）配合操作。B站视频内容通过抓取字幕文件整理核心技术点，无字幕时抓取视频简介和评论区精华。
>
> **架构总览**：
> ```
> 主智能体（调度器）
>   ├─ 阶段 0.5：读历史日报，构建去重清单
>   ├─ 阶段 A：检查点检测（跳过已有 cache 的分类）
>   ├─ 阶段 B：并行派发 5 个 Worker（Agent tool）
>   │   ├─ Worker 1：AI 编程实战（coding）
>   │   ├─ Worker 2：开源 Agent 实战（agent）
>   │   ├─ Worker 3：AI 美术工作流（art）
>   │   ├─ Worker 4：AI 提效工具 + GitHub Trending（tools-github）
>   │   └─ Worker 5：B站精选（bilibili）
>   │   → 每个 Worker 写入 output/.cache/practice-{category}-YYYYMMDD.md
>   └─ 阶段 C：汇总（读 cache → 去重 → 过滤 → 分类 → 格式化 → 保存）
> ```

## 何时使用此技能

当用户出现以下情况时激活此技能：
- 说出："AI实战" / "AI技巧" / "AI practice"
- 说出："AI编程技巧" / "Claude Code 最佳实践" / "Cursor 技巧"
- 说出："AI美术工作流" / "SD技巧" / "Flux教程" / "AI视频生成"
- 说出："AI工具推荐" / "AI提效" / "AI工具发现"
- 说出："AI Agent实战" / "开源Agent" / "AutoGen" / "CrewAI" / "OpenClaw"
- 询问实用的 AI 技巧、窍门或工作流
- 想要可操作的 AI 技术（而非行业新闻）

**不要激活**：当用户请求 AI 新闻时（请使用 `daily-ai-news-global` 或 `daily-ai-news-cn`）。

## 输出语言与格式要求（必须遵守）

- **最终面向用户的输出必须为简体中文**（标题、摘要、要点、总结和结尾文字）。
- 技术术语、工具名称、代码片段可保留英文。
- URL 必须保持原样。
- **输出必须是格式排版清晰的中文 Markdown 文档**：
  - 使用清晰的标题层级（`#`、`##`、`###`）组织内容结构
  - 合理使用分隔线 `---` 区分板块
  - 列表、表格、引用块等 Markdown 元素使用规范，确保渲染后美观易读
  - 段落间留有适当空行，避免内容拥挤
  - 锚点链接、目录索引完整可跳转

---

## 阶段 0：输出目录与方向（固定）

日报文件固定保存到 skills 公共输出目录 `<skills根目录>/output/`，无需询问用户。如目录不存在，自动创建。

**方向选择**：默认覆盖全部方向（编程 + 美术 + 工具 + GitHub 热门）。如用户已明确指定方向，按用户指定执行。

**输出模板**：固定使用实战清单模板（详见 `references/output_templates.md`）。

---

## 阶段 0.5：历史日报去重（必须执行）

在开始搜索之前，先读取**最近 1 次**已生成的历史日报，构建"已收录内容清单"，避免重复推荐。**注意：按文件数量而非日期天数计算，适配不定期运行的场景。**

### 执行步骤

1. **扫描输出目录**：从 `<skills根目录>/output/` 中，列出所有 `ai-practice-info-YYYYMMDD.md` 文件，按日期降序排列
2. **取最近 1 个文件**：只取最新的那一份（目录为空则跳过）
3. **提取已收录内容**：读取该文件，提取每条内容的标题、来源 URL、核心主题关键词，汇总为"已收录清单"
4. **后续阶段引用**：在阶段 C（汇总）中，将新搜索的内容与此清单比对

### 去重规则

- **完全相同的内容**（标题相似或 URL 相同）→ 直接跳过
- **同一工具/技巧有重大更新**（如：上次推荐了某工具 v1，今天 v2 发布了）→ 保留，但在摘要中注明"📌 此前已推荐，今日有重大更新"
- **无历史日报可读时**（首次运行或目录为空）→ 跳过此阶段，正常执行后续流程

---

## 阶段 A：检查点检测

在派发 Worker 之前，检查 `<skills根目录>/output/.cache/` 目录下是否存在今天日期的 cache 文件。

### 检测逻辑

1. **列出 cache 文件**：查找 `output/.cache/practice-{category}-YYYYMMDD.md`，其中 category 为：`coding`、`agent`、`art`、`tools-github`、`bilibili`
2. **全部存在**（5 个 cache 文件都有）→ 跳过阶段 B，直接进入阶段 C（汇总）
3. **部分存在** → 只派发缺失分类对应的 Worker
4. **全部不存在** → 正常派发全部 5 个 Worker
5. **cache 目录不存在** → 自动创建 `output/.cache/`，然后派发全部 Worker

---

## 阶段 B：并行搜索派发

**使用 Agent tool 同时派发 5 个子智能体**，每个 Worker 独立完成一个分类的搜索、抓取和初筛，将结果写入对应的 cache 文件。

> **关键指令**：必须在一次响应中同时调用 5 个 Agent tool（或根据阶段 A 的检测结果，只调用缺失分类的 Worker），实现真正的并行执行。

### 通用 Worker 规则

- 每个 Worker 的 prompt 中必须包含：该分类的完整搜索查询列表、来源抓取列表、筛选标准
- 每个 Worker 完成后，将结果写入：`<skills根目录>/output/.cache/practice-{category}-YYYYMMDD.md`
- 写入格式必须遵循下方"Cache 文件格式规范"
- 抓取策略：优先 WebFetch 直接抓取；需要登录的页面使用托管浏览器
- 如果某来源抓取失败 → 跳过并继续，不要中断整个 Worker

---

### Worker 1：AI 编程实战（category: coding）

**写入路径**：`output/.cache/practice-coding-YYYYMMDD.md`

#### 搜索查询（英文）
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

#### 工程博客抓取（选 2-3 个）
- Anthropic Engineering：https://www.anthropic.com/engineering
- OpenAI Cookbook：https://cookbook.openai.com
- Vercel AI Blog：https://vercel.com/blog
- LangChain Blog：https://blog.langchain.dev
- Cursor Blog：https://cursor.com/blog

#### 大牛内容搜索
```
site:simonwillison.net AI OR LLM
```
```
site:latent.space AI engineering
```
```
"karpathy" tutorial OR lesson OR method
```

更多查询模板请参考 `references/search_queries.md`。

---

### Worker 2：开源 Agent 实战（category: agent）

**写入路径**：`output/.cache/practice-agent-YYYYMMDD.md`

搜索 OpenClaw、AutoGen、CrewAI、LangGraph 等开源 AI Agent 框架的技术落地分享和发展动态。

#### 搜索查询（英文）
```
"OpenClaw" AI agent tutorial OR deployment OR use case
```
```
"AutoGen" OR "AG2" agent workflow OR tutorial OR best practices after:[week_ago]
```
```
"CrewAI" tutorial OR production OR deployment after:[week_ago]
```
```
"LangGraph" agent OR workflow tutorial OR guide after:[week_ago]
```
```
"open source AI agent" framework comparison OR tutorial 2026
```
```
"multi-agent" system tutorial OR architecture OR production after:[week_ago]
```
```
"AI agent" deployment OR production OR "real world" use case after:[yesterday]
```

#### 中文搜索
```
"AI Agent" 落地 OR 实战 OR 部署 OR 案例 after:[yesterday]
```
```
"开源 Agent" OR "AutoGen" OR "CrewAI" 教程 OR 实战 after:[week_ago]
```
```
"多智能体" 系统 OR 框架 OR 实战 after:[week_ago]
```
```
site:mp.weixin.qq.com "AI Agent" 落地 OR 实战 after:[yesterday]
```
```
site:juejin.cn "AI Agent" OR "多智能体" 实战 OR 教程 after:[week_ago]
```

#### 重点来源抓取
- AutoGen GitHub：https://github.com/microsoft/autogen
- CrewAI GitHub：https://github.com/crewAIInc/crewAI
- LangGraph Docs：https://langchain-ai.github.io/langgraph/
- AgentOps Blog：https://blog.agentops.ai

#### 筛选重点
- **技术落地**：优先选有实际部署经验、踩坑记录、性能数据的内容
- **架构演进**：框架版本更新带来的新能力和迁移指南
- **发展方向**：Agent 记忆、规划、工具调用的新模式
- **国内实践**：国内团队用开源 Agent 框架的落地案例

---

### Worker 3：AI 美术工作流（category: art）

**写入路径**：`output/.cache/practice-art-YYYYMMDD.md`

搜索 SD/Flux 和 AI 美术制作技巧。

#### 搜索查询（英文）
```
"Stable Diffusion" OR "Flux" tips OR tricks OR workflow
```
```
"AI 3D" generation OR modeling tutorial
```
```
"AI video" generation OR "Sora" OR "Kling" OR "Runway" tutorial
```

#### 中文美术搜索
```
"AI绘画" 技巧 OR 教程 OR 工作流
```
```
"AI美术" 实战 OR 管线 OR pipeline
```
```
site:xiaohongshu.com "AI绘画" OR "SD" OR "Flux" 教程
```

#### 美术来源抓取（选 1-2 个）
- Civitai：https://civitai.com/
- LiblibAI：https://www.liblib.art/

---

### Worker 4：AI 提效工具 + GitHub Trending（category: tools-github）

**写入路径**：`output/.cache/practice-tools-github-YYYYMMDD.md`

搜索新的 AI 工具、生产力方案，以及 GitHub Trending AI 仓库。

#### 工具搜索查询（英文）
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

#### 中文工具搜索
```
"AI工具" 推荐 OR 新上线 OR 测评
```
```
"AI提效" OR "AI自动化" 工具 OR 方案
```
```
site:xiaohongshu.com "AI工具" OR "效率工具"
```

#### GitHub Trending 抓取
- https://github.com/trending（今日或本周）

#### GitHub 搜索补充
```
GitHub trending AI repository 2026
```
```
GitHub "machine learning" OR "LLM" OR "AI" trending stars
```

#### GitHub 筛选标准
- 必须与 AI 相关（LLM、ML、AI 工具、AI 美术等）
- 优先选择：README 清晰、提交活跃、有实际用途的仓库
- 选出 3-5 个最相关的仓库

---

### Worker 5：B站精选（category: bilibili）

**写入路径**：`output/.cache/practice-bilibili-YYYYMMDD.md`

扫描用户 B站账号 AI 分组关注列表中博主的近期视频，通过字幕提取核心技术内容。

> **访问方式**：B站关注列表需要登录态，使用**托管浏览器**访问。视频内容通过**字幕抓取**整理，无字幕时抓取简介 + 评论区精华。

#### 执行步骤

1. **获取关注列表**：使用托管浏览器访问 `https://space.bilibili.com/` 我的主页 → 关注 → 找到"AI"分组，获取该分组下的博主列表
2. **扫描近期视频**：对每位博主，访问其主页视频列表，筛选最近发布的视频（优先 7 天内，最多扩展到 14 天）
3. **字幕提取**：
   - 有字幕：通过 WebFetch 调用 B站字幕 API 获取字幕文本，整理核心技术点
   - 无字幕：抓取视频简介 + 置顶评论 + 热门评论，提炼要点
4. **筛选标准**：只保留与 AI 编程/Agent/工具/美术工作流相关的视频，纯娱乐/vlog 跳过

#### 字幕抓取方法

```
步骤 1：获取视频 cid
WebFetch: https://api.bilibili.com/x/web-interface/view?bvid={BVID}
→ 取 data.cid

步骤 2：获取字幕列表
WebFetch: https://api.bilibili.com/x/player/wbi/v2?bvid={BVID}&cid={CID}
→ 取 data.subtitle.subtitles[0].subtitle_url

步骤 3：下载字幕 JSON
WebFetch: {subtitle_url}
→ 提取所有 content 字段，拼接为完整文本
```

#### 内容整理要求

从字幕/简介中提炼：
- **核心技术点**：视频讲了什么技术/工具/方法
- **关键步骤**：可操作的具体步骤（如有）
- **工具/资源**：提到的工具名、GitHub 链接、文档地址
- **亮点结论**：最值得记住的 1-2 句话

#### 筛选重点
- 优先选择有具体操作演示的视频（而非纯讲解）
- 优先选择近 7 天内发布的内容
- 每次日报最多收录 3 条 B站视频，避免比例失衡

---

## Cache 文件格式规范

每个 Worker 写入的 cache 文件必须使用以下 Markdown 格式（方便 LLM 直接读写，减少格式错误）：

```markdown
# AI Practice Raw Cache — {分类名}
# Generated: YYYY-MM-DD HH:MM
# Category: coding | agent | art | tools-github | bilibili

## Item 1
- **标题**: xxx
- **URL**: xxx
- **来源**: xxx
- **日期**: xxx
- **摘要**: xxx
- **要点**:
  - xxx
  - xxx

## Item 2
...
```

---

## 阶段 C：汇总（主智能体）

所有 Worker 完成后（或从检查点恢复后），主智能体执行汇总。

### C.1 读取 Cache 文件

读取 `output/.cache/` 下所有 5 个分类的 cache 文件，合并为统一的候选内容池。

### C.2 与历史日报去重（引用阶段 0.5 的已收录清单）

将候选内容逐条与"已收录清单"比对：
- **标题相似或 URL 相同** → 跳过
- **同一工具/技巧有重大更新** → 保留，摘要中标注"📌 此前已推荐，今日有重大更新"
- **全新内容** → 正常保留

### C.3 质量过滤 — 核心标准：**可操作性**

**保留**（必须可操作）：
- 分步教程或指南
- 具体的工作流/管线描述
- 代码片段或配置示例
- 工具对比与实用推荐
- 带具体示例的最佳实践
- 新工具发布 + "如何上手"

**移除**：
- 纯理论无实际应用
- 行业新闻/融资/公司公告（那是新闻 skill 的内容）
- 营销软文无实质内容
- 超过 7 天的旧内容
- 重复/重叠内容

从候选池中选出最有价值的 10-15 条结果。

### C.4 分类 + 评级 + 标签

#### 六大分类

| 分类 | 锚点 | 内容范围 |
|------|------|----------|
| 🖥️ AI 编程实战 | `code-01` | Claude Code 工作流、Cursor 技巧、提示词工程、LLM 集成 |
| 🤖 开源 Agent 实战 | `agent-01` | OpenClaw/AutoGen/CrewAI/LangGraph 落地分享、多智能体架构、Agent 技术方向 |
| 🎨 AI 美术工作流 | `art-01` | SD/Flux 技巧、AI 3D/视频、游戏美术管线 |
| 🔧 AI 提效工具 | `tool-01` | 新工具发现、插件、自动化方案 |
| 📺 B站精选 | `bili-01` | 关注列表 AI 分组博主近期视频，字幕提取核心技术点 |
| 🔥 GitHub 热门 | `gh-01` | 值得试用的 Trending AI 仓库 |

#### 难度评级（每条内容）

- ⭐ **入门** — 任何人都能跟着做，无前置要求
- ⭐⭐ **进阶** — 需要该领域的基础知识
- ⭐⭐⭐ **高级** — 需要丰富经验，高级技巧

#### 适用标签（每条内容，可多选）

- 🎮 **游戏开发** — 与游戏开发相关
- 🎨 **美术创作** — 与美术/设计创作相关
- 💻 **日常编码** — 与日常编程相关
- ⚡ **效率提升** — 通用生产力提升

### C.5 按模板格式化输出

按 `references/output_templates.md` 中的实战清单模板格式化最终输出。

#### 目录索引规则（必须遵守）

- **目录必须列出每条内容**：在"📑 目录"下，将每条内容标题作为链接嵌套在其分类下
- **每条内容必须有稳定锚点**：在每条内容上方插入 `<a id="xxx"></a>`
- **锚点命名**：
  - 今日推荐：`pick-01`、`pick-02`…
  - 编程实战：`code-01`、`code-02`…
  - 开源 Agent：`agent-01`、`agent-02`…
  - 美术工作流：`art-01`、`art-02`…
  - 提效工具：`tool-01`、`tool-02`…
  - B站精选：`bili-01`、`bili-02`…
  - GitHub 热门：`gh-01`、`gh-02`…

#### 与新闻 skill 的关键区别

- **无金字塔可视化**（那是新闻框架，不适用于实战内容）
- **无新闻分类**（使用实战分类）
- **可操作性为王** — 每条内容必须告诉读者能做什么
- **今日实战清单** — 结尾 3-5 个 checkbox 项，读者今天就能动手试

### C.6 保存到磁盘（必须执行）

- **输出目录**：`<skills根目录>/output/`
- **文件名**：`ai-practice-info-YYYYMMDD.md`（YYYYMMDD = 生成日期）
- **内容**：与最终输出完全相同的 Markdown
- **如文件已存在**：用最新内容覆盖
- **如目录不存在**：自动创建

### C.7 清理 Cache（可选）

日报保存成功后，可删除 `output/.cache/practice-*-YYYYMMDD.md` 文件以节省空间。也可保留用于调试。

---

## 阶段 9：可选后续操作

保存后，向用户提供以下选项：

1. **聚焦方向**："你希望我重点关注哪个方向？"（编程/美术/工具/GitHub）
2. **深入展开**："展开讲讲 [技巧 X]" → 抓取全文 + 详细步骤
3. **难度筛选**："只看入门级" / "只看高级"
4. **时间范围**："扩大到本周的内容"

---

## 质量标准

### 验证清单
- 每条内容都是可操作的（读者知道能做什么）
- 难度评级准确
- 适用标签与内容匹配
- 没有混入行业新闻（那属于新闻 skill）
- 链接有效且指向原始来源
- 中英文来源均有覆盖
- 各方向内容均衡
- **输出语言为简体中文（URL 和技术术语除外）**

### 错误处理
- 如果某来源抓取失败 → 跳过并继续
- 如果某分类无结果 → 注明"今日该方向暂无新实战内容"
- 如果结果过多 → 按可操作性和时效性优先排序

## 附加资源

- `references/practice_sources.md` — 实战技巧信息源（中英文全覆盖）
- `references/search_queries.md` — 实战专用搜索查询模板
- `references/output_templates.md` — 实战清单输出格式模板
