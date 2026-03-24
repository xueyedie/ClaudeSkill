---
name: ai-practice-info
user-invocable: true
description: "AI 实战技巧日报 — 不追新闻热点，只追'今天能用'的 AI 技巧。聚焦 AI 编程、AI 美术工作流、AI 提效工具和 GitHub 热门。触发词：'AI实战'、'AI技巧'、'AI practice'、'AI编程技巧'、'AI美术工作流'、'AI工具推荐'。"
---

# AI 实战技巧日报

> **核心定位：不追新闻热点，只追"今天能用"的 AI 技巧。**
> 聚焦可立刻应用到工作中的技术分享：AI 编程实战、AI 美术工作流、AI 提效工具。
>
> **多智能体并行架构**：主智能体作为调度器，通过 Agent tool 并行派发 6 个 Worker 子智能体分别负责不同分类的搜索与抓取，最后由主智能体汇总、去重、过滤、格式化并输出。搜索阶段从串行 ~20 分钟压缩到并行 ~5 分钟。
>
> **检查点机制**：每个 Worker 将原始结果写入 `output/.cache/practice-{category}-YYYYMMDD.md`。如果执行中断，再次触发时自动跳过已完成的 Worker，只补跑缺失分类。
>
> **稳定性原则**：主智能体判断 Worker 是否完成时，**只以 cache 文件是否成功落盘为准**，不要把“子智能体自动回传的完成消息”当作唯一或必要信号。自动回传消息可以作为辅助信息，但即使没等到，也应继续通过文件检查推进流程。
>
> **内容获取方式**：优先使用 `opencli` 获取平台内的结构化结果或已登录内容；只有当 `opencli` 未适配、执行失败或确实需要通用网页探索时，才回退到 WebFetch 或托管浏览器（browser）。B站视频内容优先使用 `opencli` 的站内读取能力或字幕能力；无合适适配器时，再抓取字幕文件、视频简介和评论区精华。
>
> **架构总览**：
> ```
> 主智能体（调度器）
>   ├─ 阶段 0.5：读历史日报，构建去重清单
>   ├─ 阶段 A：检查点检测（跳过已有 cache 的分类）
>   ├─ 阶段 B：并行派发 6 个 Worker（Agent tool）
>   │   ├─ Worker 1：AI 编程实战（coding）
>   │   ├─ Worker 2：开源 Agent 实战（agent）
>   │   ├─ Worker 3：AI 美术工作流（art）
>   │   ├─ Worker 4：AI 提效工具 + GitHub Trending（tools-github）
>   │   ├─ Worker 5：B站精选（bilibili）
>   │   └─ Worker 6：知乎精选（zhihu）
>   │   → 每个 Worker 写入 output/.cache/practice-{category}-YYYYMMDD.md
>   └─ 阶段 C：汇总（读 cache → 去重 → 过滤 → 分类 → 格式化 → 保存）
> ```

## 用户画像

> 以下画像用于阶段 C 汇总时做个性化过滤、优先级加权和落地建议生成。

| 维度 | 描述 |
|------|------|
| **角色** | TA（技术美术）+ 美术副总监，兼顾技术深度与团队管理 |
| **公司类型** | 手游 SLG 公司 |
| **主力引擎** | Unity / Unreal Engine |
| **关注领域** | 游戏美术全管线（原画、模型、动作、特效、地编、UI）、渲染/Shader/TA、AI 辅助美术生产、AI 编程提效 |
| **内容偏好权重** | 游戏美术管线/TA/Shader/渲染 > Unity/Unreal AI 工具 > 可被团队采纳推广的通用 AI 工具 > 纯 Web/前端 AI |
| **价值判断标准** | 能否在 SLG 美术团队中落地？投入产出比如何？哪些角色最受益？ |

---

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

1. **列出 cache 文件**：查找 `output/.cache/practice-{category}-YYYYMMDD.md`，其中 category 为：`coding`、`agent`、`art`、`tools-github`、`bilibili`、`zhihu`
2. **全部存在**（6 个 cache 文件都有）→ 跳过阶段 B，直接进入阶段 C（汇总）
3. **部分存在** → 只派发缺失分类对应的 Worker
4. **全部不存在** → 正常派发全部 6 个 Worker
5. **cache 目录不存在** → 自动创建 `output/.cache/`，然后派发全部 Worker

---

## 阶段 B：并行搜索派发

**使用 Agent tool 同时派发 6 个子智能体**，每个 Worker 独立完成一个分类的搜索、抓取和初筛，将结果写入对应的 cache 文件。

> **关键指令**：必须在一次响应中同时调用 6 个 Agent tool（或根据阶段 A 的检测结果，只调用缺失分类的 Worker），实现真正的并行执行。
>
> **关键稳定性要求**：
> - 派发完成后，主智能体**不要依赖子智能体的 completion announce / 自动回传消息**来判断流程是否可以继续。
> - 主智能体应维护一个“待完成分类列表”，并以 `output/.cache/practice-{category}-YYYYMMDD.md` 是否存在且可读作为完成条件。
> - 如果某个 Worker 的自动回传消息迟到、丢失或超时，只要 cache 已写出，就视为该 Worker 已完成。
> - 如果在等待窗口结束后 cache 仍未出现，则将该分类记为缺失项并继续汇总，不要让整个日报卡死。

### 通用 Worker 规则

- 每个 Worker 的 prompt 中必须包含：该分类的完整搜索查询列表、来源抓取列表、筛选标准
- 每个 Worker 完成后，将结果写入：`<skills根目录>/output/.cache/practice-{category}-YYYYMMDD.md`
- 写入格式必须遵循下方"Cache 文件格式规范"
- 如果某来源抓取失败 → 跳过并继续，不要中断整个 Worker
- Worker 的最终文本回复应尽量简短，最多只做一句完成说明；**主智能体不要等待这条回复作为继续条件**

### 阶段 B.1：派发后的完成检测

在派发缺失分类对应的 Worker 后，主智能体按下面的方式检查完成状态：

1. 记录本轮缺失分类列表，例如：`coding`、`agent`、`art`、`tools-github`、`bilibili`、`zhihu`
2. 进入**文件检查循环**，每轮只检查这些分类对应的 cache 文件是否已存在且可读
3. 检查方式优先使用 `read` / `ls` / `find` / `rg --files` 之类的轻量工具；不要靠子智能体回传消息做阻塞等待
4. 每轮检查后，将已落盘的分类从待完成列表移除
5. 若仍有未完成分类，则短暂等待后再检查；建议使用递增退避，例如 10s → 20s → 30s → 60s
6. **总等待窗口建议控制在 8 分钟内**
7. 超过等待窗口后，仍未落盘的分类直接标记为缺失项，继续进入阶段 C

### 阶段 B.2：主智能体的禁止事项

- 不要因为“只剩某个 Worker 没回消息”而一直卡住
- 不要把“announce 超时”解释成整个任务失败
- 不要在一个长时间循环里频繁刷 `subagents list` 或等待 completion announce
- 不要要求 6 个分类必须全部完成才允许进入阶段 C

#### 搜索与抓取工具使用规则

- **默认优先级**：`opencli` 结构化读取 / 站内搜索 / 已登录内容 > WebFetch 直接抓取目标页面 > 托管浏览器（browser）通用探索。
- **搜索查询**：优先使用 `opencli` 的平台适配器执行站内搜索、热门列表、时间线、订阅源、历史记录等能力；只有目标平台未适配或 `opencli` 返回失败时，才使用 WebFetch 访问搜索引擎页面或用托管浏览器执行通用搜索。
- **页面内容抓取**：如果 `opencli` 已经返回足够的结构化结果，直接基于结果筛选，不再额外抓整页全文；只有在需要补充正文细节时，才用 WebFetch 抓目标 URL。
- **需要登录态的页面**（如 B站关注列表、小红书等）：优先使用 `opencli` 复用 Chrome 登录态；若 `opencli` 不可用，再使用托管浏览器（browser）。
- **降级策略**：`opencli` 失败时先判断是否存在直接 URL 可抓，再尝试 WebFetch；WebFetch 失败时，最后尝试托管浏览器访问同一 URL；浏览器也失败则跳过该来源。

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
```
"Unity" AI plugin OR "AI Shader" OR "procedural generation" tutorial
```
```
"Unreal Engine" AI plugin OR "AI NPC" OR "behavior tree" AI integration
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

搜索 SD/Flux、AI 美术制作技巧，以及 GDC/SIGGRAPH/Unity/Unreal 游戏美术管线内容（覆盖原画、模型、动作、特效、地编、UI、渲染/Shader/TA）。

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

#### GDC / SIGGRAPH 游戏美术查询
```
GDC "art pipeline" OR "technical art" OR "rendering" OR "shader" 2025 2026
```
```
SIGGRAPH "game art" OR "real-time rendering" OR "procedural" 2025 2026
```
```
GDC OR SIGGRAPH "concept art" OR "3D modeling" OR "animation" OR "VFX" AI
```
```
GDC OR SIGGRAPH "level design" OR "UI" OR "environment art" AI workflow
```

#### Unity / Unreal 美术管线查询
```
"Unity" "AI terrain" OR "AI texture" OR "AI animation" OR "AI VFX" tutorial
```
```
"Unreal Engine" "AI art pipeline" OR "AI texture" OR "procedural" OR "AI animation"
```
```
"Unity" OR "Unreal" "AI shader" OR "AI rendering" OR "technical art" workflow
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

#### 中文游戏美术 AI 搜索
```
"游戏美术" AI OR "AI美术管线" OR "AI原画" OR "AI建模" 实战 OR 教程
```
```
"技术美术" OR "TA" AI OR "AI Shader" OR "AI渲染" 实战 OR 教程
```
```
"Unity" OR "Unreal" AI美术 OR AI动画 OR AI特效 教程 OR 实战
```

#### 美术来源抓取（选 2-3 个）
- Civitai：https://civitai.com/
- LiblibAI：https://www.liblib.art/

#### 游戏行业来源抓取（选 2-3 个）
- GDC Vault：https://gdcvault.com/ （搜索 AI art / technical art / rendering）
- Unity Blog：https://unity.com/blog （搜索 AI 相关）
- Unreal Blog：https://www.unrealengine.com/blog （搜索 AI 相关）
- 游戏葡萄：https://youxiputao.com/ （搜索 AI 美术）
- GameRes：https://www.gameres.com/ （搜索 AI / TA）
- GameLook：https://www.gamelook.com.cn/ （搜索 AI 美术 / 技术美术）

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
```
"Unity" AI tool OR plugin OR asset 2026
```
```
"Unreal Engine" AI plugin OR tool OR marketplace 2026
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

### Worker 6：知乎精选（category: zhihu）

**写入路径**：`output/.cache/practice-zhihu-YYYYMMDD.md`

通过 `opencli` 访问用户知乎关注动态和收藏夹，筛选 AI 实战相关内容，提取核心技术点。游戏美术/TA/Unity/Unreal 相关内容额外加权。

> **访问方式**：优先使用 `opencli` 复用 Chrome 登录态访问知乎；`opencli` 不可用时降级到托管浏览器；最后回退到 WebFetch `site:zhihu.com` 搜索。

#### 执行步骤

1. **获取关注动态时间线**：使用 `opencli` 访问知乎关注动态（首页 → 关注），获取近期文章和回答（优先 7 天内，最多 14 天）
2. **扫描收藏夹**：使用 `opencli` 访问用户收藏夹列表，扫描近期收藏的内容
3. **站内搜索补充**：如果关注动态和收藏夹中 AI 实战内容不足 3 条，使用以下查询补充搜索：
   ```
   site:zhihu.com "AI实战" OR "AI工作流" OR "AI编程" 教程 OR 实战
   ```
   ```
   site:zhihu.com "游戏美术" AI OR "技术美术" AI OR "TA" AI Shader
   ```
   ```
   site:zhihu.com "Unity" OR "Unreal" AI 工具 OR 插件 OR 工作流
   ```
4. **筛选标准**：只保留与 AI 编程/Agent/工具/美术工作流/游戏开发相关的内容，纯观点/情绪向内容跳过
5. **加权规则**：游戏美术/TA/Unity/Unreal 相关内容优先收录

#### 降级策略

```
opencli（知乎适配器）
  ↓ 失败
托管浏览器（browser）访问 zhihu.com，复用登录态
  ↓ 失败
WebFetch site:zhihu.com 搜索
  ↓ 失败
跳过该来源
```

#### 内容整理要求

从文章/回答中提炼：
- **核心技术点**：讲了什么技术/工具/方法
- **关键步骤**：可操作的具体步骤（如有）
- **工具/资源**：提到的工具名、GitHub 链接、文档地址
- **亮点结论**：最值得记住的 1-2 句话

#### 筛选重点
- 优先选择有具体操作步骤或代码的内容（而非纯讨论）
- 游戏美术/TA/Shader/渲染相关内容额外加权
- Unity/Unreal AI 工具相关内容额外加权
- 每次日报最多收录 3 条知乎内容，避免比例失衡

---

## Cache 文件格式规范

每个 Worker 写入的 cache 文件必须使用以下 Markdown 格式（方便 LLM 直接读写，减少格式错误）：

```markdown
# AI Practice Raw Cache — {分类名}
# Generated: YYYY-MM-DD HH:MM
# Category: coding | agent | art | tools-github | bilibili | zhihu

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

所有已成功落盘的 Worker 完成后（或从检查点恢复后），主智能体执行汇总。对于超时未落盘的分类，直接作为缺失项处理，不阻塞主流程。

### C.1 读取 Cache 文件

读取 `output/.cache/` 下本轮**实际成功落盘**的 cache 文件，合并为统一的候选内容池。

- 如果 6 个分类都落盘 → 正常全量汇总
- 如果只有部分分类落盘 → 只汇总已落盘分类，并在最终文档中明确列出缺失分类及原因
- 至少有 2 个分类成功落盘时，就应继续产出日报，避免因为单一来源失败导致整单中断

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

**用户画像加权**（参考"用户画像"章节）：
- 游戏美术管线/TA/Shader/渲染 → 提升优先级
- Unity/Unreal AI 工具 → 提升优先级
- 可被团队采纳推广的内容 → 提升优先级
- 与游戏无关的纯 Web/前端 AI → 降低优先级

从候选池中选出最有价值的 8-12 条结果，贵精不贵多，每条写深写透。

### C.4 分类 + 评级 + 标签

#### 七大分类

| 分类 | 锚点 | 内容范围 |
|------|------|----------|
| 🖥️ AI 编程实战 | `code-01` | Claude Code 工作流、Cursor 技巧、提示词工程、LLM 集成、Unity/Unreal AI 编程 |
| 🤖 开源 Agent 实战 | `agent-01` | OpenClaw/AutoGen/CrewAI/LangGraph 落地分享、多智能体架构、Agent 技术方向 |
| 🎨 AI 美术工作流 | `art-01` | SD/Flux 技巧、AI 3D/视频、游戏美术管线（原画/模型/动作/特效/地编/UI/渲染/Shader/TA）、GDC/SIGGRAPH |
| 🔧 AI 提效工具 | `tool-01` | 新工具发现、插件、自动化方案、Unity/Unreal AI 工具 |
| 📺 B站精选 | `bili-01` | 关注列表 AI 分组博主近期视频，字幕提取核心技术点 |
| 📖 知乎精选 | `zhihu-01` | 关注动态 + 收藏夹中的 AI 实战文章/回答，游戏美术/TA 内容加权 |
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
  - 知乎精选：`zhihu-01`、`zhihu-02`…
  - GitHub 热门：`gh-01`、`gh-02`…

#### 团队价值评估与角色标签（每条内容必须包含）

每条内容在"快速上手"或"工作流概述"之后，追加以下字段：

- **🎯 对团队的价值**：评估该内容与 SLG 美术团队的相关性、可采纳性、投入产出比（1-2 句话）
- **💡 落地建议**：告诉用户怎么在 SLG 美术团队里落地（具体到谁来做、怎么做、预期效果）
- **角色标签**（至少选一个）：
  - `TA必看` — 技术美术直接相关的 Shader/渲染/管线内容
  - `管理者关注` — 影响团队效率或流程的决策级内容
  - `团队可推广` — 可以在团队内培训推广的实操技巧
  - `技术预研` — 需要进一步评估但值得关注的前沿方向

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
