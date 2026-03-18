---
name: daily-ai-news-global
user-invocable: true
description: "聚合并总结来自多个来源的最新国际 AI 新闻。单智能体架构，内联大神模块。触发词：'today's AI news'、'AI updates'、'latest AI developments'、'daily AI briefing'。"
---

# AI 每日新闻简报 — 国际版

> 单智能体架构：不使用子智能体调度。所有网页抓取、搜索、过滤、分类和格式化均在主对话中完成。

## 何时使用此技能

当用户出现以下情况时激活此技能：
- 询问今天的 AI 新闻或最新 AI 动态
- 请求每日 AI 简报或更新
- 提到想了解 AI 领域正在发生什么
- 询问 AI 行业新闻、趋势或突破
- 想要近期 AI 公告的摘要
- 说出："today's AI news"、"AI updates"、"latest AI developments"、"daily AI briefing"


## 输出语言与格式要求（必须遵守）

- **最终面向用户的输出必须为简体中文**（标题、摘要、要点、总结和结尾文字）。
- 专有名词（公司/产品/模型/论文名称）可保留英文；如有帮助，首次出现时可附简短中文说明。
- URL 必须保持原样。
- 如果原始标题为英文，可显示**中文标题**，并可选择在括号中附上**英文原文**。
- **输出必须是格式排版清晰的中文 Markdown 文档**：
  - 使用清晰的标题层级（`#`、`##`、`###`）组织内容结构
  - 合理使用分隔线 `---` 区分板块
  - 列表、表格、引用块等 Markdown 元素使用规范，确保渲染后美观易读
  - 段落间留有适当空行，避免内容拥挤
  - 锚点链接、目录索引完整可跳转

---

## 阶段 0：输出目录（固定）

日报文件固定保存到 skills 公共输出目录 `<skills根目录>/output/`，无需询问用户。如目录不存在，自动创建。

**输出模板**：固定使用深度版模板（详见 `references/output_templates.md`）。

---

## 阶段 0.5：历史日报去重（必须执行）

在开始抓取新闻之前，先读取近三天的历史日报，构建"已报道主题清单"，避免重复内容。

### 执行步骤

1. **扫描输出目录**：从 `<skills根目录>/output/` 中，查找最近 3 天的日报文件（`daily-ai-news-YYYYMMDD.md`）
2. **提取已报道主题**：读取找到的日报文件，提取每条新闻的标题、来源 URL、核心主题关键词，汇总为"已报道清单"
3. **后续阶段引用**：在阶段 5（过滤与去重）中，将新抓取的新闻与此清单比对

### 去重规则

- **完全相同的事件**（标题相似或 URL 相同）→ 直接跳过，不纳入今日日报
- **同一主题有新进展**（如：前天报道了某公司融资消息，今天该公司公布了具体金额或新合作方）→ 保留，但在摘要中注明"此前已报道，今日有新进展"并简述增量信息
- **无历史日报可读时**（首次运行或目录为空）→ 跳过此阶段，正常执行后续流程

---

## 阶段 1：网站抓取

使用 **WebFetch** 从 3-5 个一级来源抓取最新内容：

- VentureBeat AI：https://venturebeat.com/category/ai/
- TechCrunch AI：https://techcrunch.com/category/artificial-intelligence/
- The Verge AI：https://www.theverge.com/ai-artificial-intelligence
- MIT Technology Review AI：https://www.technologyreview.com/topic/artificial-intelligence/
- AI News：https://artificialintelligence-news.com/
- Hugging Face 博客：https://huggingface.co/blog

如果某个站点抓取失败，跳过并继续。

---

## 阶段 2：网络搜索

使用 **WebSearch** 执行 3-4 条英文搜索查询：

1. `"AI news today" OR "artificial intelligence breakthrough"`（最近 24 小时）
2. `"AI research paper" OR "machine learning breakthrough"`（最近 24 小时）
3. `"AI startup funding" OR "AI company news" OR "new AI tool"`（最近 24 小时）
4. （可选）公司专项：`"OpenAI" OR "Google AI" OR "Anthropic" OR "Meta AI" announcement`（最近 24 小时）

更多查询模板请参考 `references/search_queries.md`。

### 搜索失败止损规则（必须遵守）

- 如果搜索结果页出现 `429`、`captcha`、`PoW`、`Brave Search` 验证页或明显的人机校验页面，**立即停止重试该查询**。
- 同一条查询最多只允许一次降级尝试（例如从 `web_fetch` 切到 `browser`，或反过来）。
- 降级后仍失败：直接跳过该查询，继续使用其他查询和一级来源，不要反复重试。
- 不要把验证码页、拦截页、反爬页的大段原文继续带入后续摘要和整理流程。

---

## 阶段 3：全文抓取

从阶段 1 + 2 的结果中，选择**最重要的 10-15 篇文章**，使用 **WebFetch** 获取全文以确保摘要准确。

---

## 阶段 4：大神模块（内联）

搜索最近 24-72 小时内重要 AI 巨头、创始人或技术领袖的公开观点/更新：

1. **优先候选人**：
   - Andrej Karpathy
   - Jensen Huang / NVIDIA
   - Elon Musk / xAI / Tesla AI
   - Dario Amodei / Anthropic
   - Jack Clark / Anthropic

2. **WebSearch** 查询：
   - `"karpathy"`（最近 3 天）
   - `site:x.com karpathy OR site:karpathy.ai OR site:karpathy.bearblog.dev`
   - `"Jensen Huang" OR site:nvidia.com/gtc/keynote OR site:nvidianews.nvidia.com`
   - `"Elon Musk" AND (xAI OR Grok OR Tesla AI)`（最近 3 天）
   - `"Dario Amodei" OR "Jack Clark" site:anthropic.com/news OR site:anthropic.com/research`

3. **WebFetch** 抓取找到的内容以确认细节和时间。

4. 选择**最有价值的 1-3 条**观点/帖子/演讲摘要，放入"🧠 大神模块：重要 AI 巨头/创始人最新观点"板块。

5. 如果 72 小时内未找到有效内容，在该板块注明"最近 72 小时内未获取到大神模块的有效公开内容"。

### 大神模块来源规则（必须遵守）

- 优先级：**官方 keynote / 官方新闻稿 / 官方博客 / 本人白名单主页** > 白名单社交账号 > 高质量采访或转录。
- **禁止**自行臆造、替换、扩展任何人物相关账号、个人主页或镜像域名。
- **禁止**访问与下列白名单不一致的 X/Twitter 账号、第三方搬运号、拼写变体、粉丝号或媒体号。
- 若搜索结果指向的不是白名单 URL 或官方域名，直接视为无效结果，跳过。
- 若 X/Twitter 或 Nitter 返回通用错误页、空响应、登录墙、验证码页或其他不可验证内容，直接记为“本轮未获取有效内容”，不要再尝试其他陌生账号。
- 这一模块的目标是补充**本人或官方渠道**的近期公开观点；宁可缺失，也不要误抓到无关账号。

**Andrej Karpathy 白名单**：
- `https://x.com/karpathy`
- `https://karpathy.ai/`
- `https://karpathy.bearblog.dev/`
- `https://www.youtube.com/andrejkarpathy`
- `https://github.com/karpathy`
- `https://karpathy.medium.com/`

**Jensen Huang / NVIDIA 白名单**：
- `https://www.nvidia.com/gtc/keynote/`
- `https://nvidianews.nvidia.com/`
- `https://blogs.nvidia.com/`
- `https://www.youtube.com/@NVIDIA`

**Elon Musk / xAI / Tesla AI 白名单**：
- `https://x.com/elonmusk`
- `https://x.com/xai`
- `https://x.ai/`
- `https://www.tesla.com/AI`
- `https://www.tesla.com/blog`

**Anthropic 创始人 / 官方白名单**：
- `https://www.anthropic.com/news`
- `https://www.anthropic.com/research`
- `https://www.anthropic.com/`

---

## 阶段 5：过滤与去重

### 5.1 与历史日报去重（引用阶段 0.5 的已报道清单）

将新抓取的新闻逐条与"已报道清单"比对：
- **标题相似或 URL 相同** → 跳过
- **同一主题有新进展** → 保留，摘要中标注"📌 此前已报道，今日有新进展"并简述增量信息
- **全新主题** → 正常保留

### 5.2 当日内容过滤

**保留**：
- 最近 24-48 小时的新闻（优先今天的）
- 重大发布（产品发布、模型发布、研究突破）
- 行业动态（融资、合作、收购、监管）
- 技术进展（新模型、新技术、新基准）
- 主要公司动态（OpenAI、Google、Anthropic、Microsoft、Meta 等）

**移除**：
- 重复报道（同一事件来自多个来源——保留最完整的版本）
- 营销软文或无实质内容的文章
- 超过 3 天的旧闻
- 非 AI 或仅边缘相关的内容

---

## 阶段 6：分类 + 金字塔标注

### 6.1 五大分类

将每条新闻分配到一个分类：

- 🔥 **重要发布**（major）：产品发布、模型发布、重大公告
- 🔬 **研究与论文**（research）：学术突破、新论文、新技术
- 💰 **产业与商业**（industry）：融资、并购、合作、市场趋势
- 🛠️ **工具与应用**（tools）：新工具、框架、开源发布
- 🌍 **政策与伦理**（policy）：监管、安全讨论、社会影响

### 6.2 AI 产业五层架构

> AI 产业自下而上分为五层：能源 → 芯片 → 基建 → 大模型 → 应用。越底层影响越大但变化越慢；越上层迭代越快但更易被替代。

为每条新闻分配一个主要层级：

| 层级 | 名称 | 标签 | 范围 |
|------|------|------|------|
| L1 | 能源 | `⚡ L1-能源` | 电力供应、数据中心能源、能效 |
| L2 | 芯片 | `🔧 L2-芯片` | GPU/TPU/ASIC、芯片性能、HBM、制造 |
| L3 | 基建 | `🏗️ L3-基建` | 数据中心、集群稳定性、云基础设施 |
| L4 | 大模型 | `🧠 L4-大模型` | 模型发布、训练范式、缩放定律、架构 |
| L5 | 应用 | `🚀 L5-应用` | AI 产品、Chatbot/Copilot/Agent、商业化 |

**规则**：
1. 每条新闻一个主要层级
2. 跨层新闻归入其核心贡献所在层级
3. 政策类新闻按影响层级归类（芯片出口管制 → L2，AI 应用监管 → L5）
4. 商业类新闻按公司主营业务层级归类

---

## 阶段 7：按深度版模板格式化输出

按 `references/output_templates.md` 中的深度版模板格式化最终输出。

### 目录索引规则（必须遵守）

- **目录必须列出每条新闻**：在"📑 目录"下，将每条新闻标题作为链接嵌套在其分类下
- **每条新闻必须有稳定锚点**：在每条新闻上方插入 `<a id="xxx"></a>`
- **锚点命名**：
  - 重要发布：`maj-01`、`maj-02`…
  - 研究：`res-01`、`res-02`…
  - 产业：`biz-01`、`biz-02`…
  - 工具：`tool-01`、`tool-02`…
  - 政策：`pol-01`、`pol-02`…
  - 大神模块：`guru-01`、`guru-02`…

### 金字塔可视化（目录之后、分类之前）

```
## 🔺 今日新闻五层架构分布

> AI 产业自下而上分为五层：能源 → 芯片 → 基建 → 大模型 → 应用。
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

### 每条摘要的层级标签

```
**摘要**： `🧠 L4-大模型` [用 1 句中文概括]
```

### 大神模块

将重要 AI 巨头、创始人或技术领袖的内容放在"🧠 大神模块：重要 AI 巨头/创始人最新观点"中，使用 `guru-01`、`guru-02` 锚点。如未找到内容，注明"最近 72 小时内未获取到大神模块的有效公开内容"。

---

## 阶段 8：保存到磁盘（必须执行）

- **输出目录**：`<skills根目录>/output/`
- **文件名**：`daily-ai-news-YYYYMMDD.md`（YYYYMMDD = 生成日期）
- **内容**：与最终输出完全相同的 Markdown
- **如文件已存在**：用最新内容覆盖
- **如目录不存在**：自动创建

---

## 阶段 9：可选后续操作

保存后，向用户提供以下选项：

1. **关注方向**："你希望我重点关注哪些方向？"（研究/产品/产业/特定公司）
2. **详细程度**："你希望内容多详细？"（简洁/标准/深度）
3. **时间范围**："时间范围看多久？"（24小时/3天/1周）

**深入展开**："展开讲讲 [新闻 X]" → WebFetch 全文 + 详细摘要

---

## 质量标准

### 验证清单
- 以下检查**仅针对最终写入日报的条目**执行，不要求对已淘汰候选逐条验证：
- 所有最终保留链接有效且可访问
- 最终各分类间无重复报道
- 最终条目有时间戳（最好是今天的）
- 最终摘要准确（非虚构）
- 最终链接指向原始来源，而非聚合站
- 最终来源多样化（不全来自同一媒体）
- 最终内容在炒作与实质之间保持平衡
- **最终输出语言为简体中文（URL 和专有名词除外）**

### 错误处理
- 如果某来源抓取失败 → 在最终报告中注明，继续使用可用数据
- 如果搜索无结果 → 注明"该类别今日无相关新闻"
- 如果结果过多 → 提高重要性阈值
- 如果内容有付费墙 → 使用可用摘要并注明限制

## 附加资源

- `references/news_sources.md` — 国际 AI 新闻来源（一级至五级）
- `references/search_queries.md` — 英文搜索查询模板
- `references/output_templates.md` — 深度版输出格式模板
