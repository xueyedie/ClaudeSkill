---
name: daily-ai-news-global
user-invocable: true
description: "聚合并总结来自多个来源的最新国际 AI 新闻。单智能体架构，内联大神模块。触发词：'today's AI news'、'AI updates'、'latest AI developments'、'daily AI briefing'。"
---

# AI 每日新闻简报 — 国际版

> 单智能体架构：不使用子智能体调度。所有网页抓取、搜索、过滤、分类和格式化均在主对话中完成。

## 执行硬约束（必须遵守）

- **禁止使用任何子智能体机制**：不要调用 `sessions_spawn`、`sessions_yield`、subagent、后台 worker，必须在当前会话内完成全流程。
- **禁止把“我开始写了”“我已经收集够了”“我接下来要落盘”这类阶段性说明单独作为一次最终回复发出**。
- **在最终 Markdown 文件真实写入磁盘并校验成功之前，禁止以纯文本 stop 结束当前轮次**。
- 如果你已经说出“开始整理”“开始写入”“进入阶段 5-8”之类的话，**下一步必须是实际工具调用**，例如 `write` 或带完整命令的 `exec`，而不是再次输出计划说明。
- 如果抓取阶段已经拿到足够素材，后续优先级必须固定为：**整理正文 → 写文件 → 校验文件 → 回写状态文件**；不要重新回到泛抓取状态，也不要停在口头汇报。
- 如果无法继续落盘，必须明确输出失败原因，并把失败原因写回状态文件；**禁止静默悬停**。

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

## 阶段 0.6：来源访问方式缓存（2026-03-25 本机复核）

先使用这份缓存决定抓取方式，**不要在每次日报里从零开始验证同一来源**。  
只有在以下情况之一发生时，才允许重新验证并更新本节：
- 某来源连续 2 次按缓存方式失败
- 站点结构明显变化
- 用户明确要求复核

### 已验证访问矩阵

| 来源 / 域名 | 默认方式 | 本机结论 | 备注 |
|------|------|------|------|
| `venturebeat.com/category/ai/` | `web_fetch` | 成功 | 一级来源，栏目页可直接抓 |
| `techcrunch.com/category/artificial-intelligence/` | `web_fetch` | 成功 | 一级来源，栏目页可直接抓 |
| `theverge.com/ai-artificial-intelligence` | `web_fetch` | 成功 | 一级来源，栏目页可直接抓 |
| `technologyreview.com/topic/artificial-intelligence/` | `web_fetch` | 成功 | topic 页较浅，必要时跟进单篇 |
| `artificialintelligence-news.com/` | `web_fetch` | 成功 | 一级来源，栏目页可直接抓 |
| `huggingface.co/blog` | `web_fetch` | 成功 | 一级来源，博客页可直接抓 |
| `anthropic.com/news` / `anthropic.com/research` | `web_fetch` | 成功 | 大神模块 / 官方来源优先 |
| `blogs.nvidia.com/` / `nvidianews.nvidia.com/` / `nvidia.com/gtc/keynote/` | `web_fetch` | 成功 | NVIDIA 白名单可直接抓 |
| `karpathy.ai` / `karpathy.bearblog.dev` | `web_fetch` | 成功 | Karpathy 白名单主页可直接抓 |
| `opencli bloomberg tech -f json` | `opencli` | 成功 | 适合找线索，不必先走搜索引擎 |
| `opencli reuters search "<query>" -f json` | `opencli` | 成功 | 适合找线索，避免直接碰 Reuters 页面限制 |
| `opencli hackernews top -f json` | `opencli` | 成功 | 公共适配器稳定 |
| `opencli hf top -f json` | `opencli` | 成功 | 公共适配器稳定 |
| `opencli youtube search "<query>" -f json` | `opencli` | 成功 | YouTube 线索入口可用 |
| `opencli twitter profile <username> -f json` | `opencli` | 成功 | `xai` / `elonmusk` / `karpathy` 账号元信息可用 |
| `https://x.com/karpathy` / `https://x.com/elonmusk` / `https://x.com/xai` | `opencli`（连接本地已登录浏览器） | 成功 | 使用 `opencli` 连接本地已登录浏览器检查最近帖子、时间线与帖子上下文 |
| `opencli twitter search "<query>" -f json` | 不作为默认路由 | 不再优先使用 | X 关键词搜索与最新动态统一优先走 `opencli` 连接本地已登录浏览器 |
| `https://x.ai/` | `opencli`（连接本地已登录浏览器） | 成功 | `web_fetch`/HTTP 仍可能失败，但 `opencli` 可借助本地浏览器会话继续访问与验证 |
| `https://www.tesla.com/AI` / `https://www.tesla.com/blog` | 托管浏览器 | `web_fetch`/HTTP 失败 | `web_fetch` 超时，HTTP 403 Access Denied，且无 `opencli` Tesla 适配器 |

### 使用规则（严格遵守）

1. **缓存里标记为 `web_fetch` 成功**：直接用 `web_fetch`，不要再先试托管浏览器。  
2. **缓存里标记为 `opencli` 成功**：直接用 `opencli`，不要先走搜索引擎或手工网页抓取。  
3. **缓存里标记为“托管浏览器”**：直接走托管浏览器，**不要**再先用 `web_fetch` / 裸 HTTP 重试同一站点。  
4. **X/Twitter 例外**：当前机器上只有本地浏览器登录了 X，托管浏览器不视为已登录。  
   - 账号元信息：优先 `opencli twitter profile`
   - 最近帖子 / 关键词搜索 / 白名单账号最新动态 / 帖子上下文：优先 `opencli` 连接本地已登录浏览器

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

### 一级来源抓取止损规则（必须遵守）

- 抓取前先对照“阶段 0.6 来源访问方式缓存”；**缓存已标记为托管浏览器的站点，不要先用 `web_fetch` 试错**。
- 一级来源优先抓取**栏目页、归档页、官方博客首页**，不要一上来就深挖大量单篇文章。
- 如果站点返回 `401`、`403`、`429`、`Please enable JS`、登录墙、验证码页、Cloudflare / PoW / Bot check 页面，**直接把该站点记为本轮不可用并跳过**。
- 对同一个站点最多只允许一次降级尝试（`web_fetch` 和 `browser` 二选一再试一次）。
- 若降级后仍失败，不要继续围绕该站点重试；改用其他一级来源或官方原始来源。
- **禁止**把拦截页、空白壳页、登录墙、验证码页继续当作正文来源。

---

## 阶段 2：网络搜索

默认先使用 `opencli` 已适配的平台能力寻找线索，尤其是 X/Twitter、Reddit、Hacker News、YouTube、知乎、B 站、小红书、Bloomberg、Reuters 等；只有目标来源不在 `opencli` 适配范围内，或 `opencli` 无法返回有效结果时，才回退到 **WebSearch** 执行下面 3-4 条英文搜索查询：

1. `"AI news today" OR "artificial intelligence breakthrough"`（最近 24 小时）
2. `"AI research paper" OR "machine learning breakthrough"`（最近 24 小时）
3. `"AI startup funding" OR "AI company news" OR "new AI tool"`（最近 24 小时）
4. （可选）公司专项：`"OpenAI" OR "Google AI" OR "Anthropic" OR "Meta AI" announcement`（最近 24 小时）

更多查询模板请参考 `references/search_queries.md`。

### 搜索失败止损规则（必须遵守）

- 对于 `opencli` 已适配的平台，优先使用 `opencli` 返回的结构化结果，不要先走搜索引擎结果页。
- 对于已在“阶段 0.6”验证过的来源，优先沿用已验证方式：
  - `Bloomberg` / `Reuters` / `Hacker News` / `HF` / `YouTube`：优先 `opencli`
  - `x.ai`：优先 `opencli` 连接本地已登录浏览器
  - `tesla.com/AI` / `tesla.com/blog`：直接托管浏览器
  - `X/Twitter` 关键词搜索、白名单账号最近动态、帖子展开：优先 `opencli` 连接本地已登录浏览器
- 只把 **WebSearch** 当作“发现线索”的工具；**不要**对搜索引擎结果页本身再做 `web_fetch` 全文抓取。
- 如果搜索结果页出现 `429`、`captcha`、`PoW`、`Brave Search` 验证页或明显的人机校验页面，**立即停止重试该查询**。
- 同一条查询最多只允许一次降级尝试（例如从 `web_fetch` 切到 `browser`，或反过来）。
- 降级后仍失败：直接跳过该查询，继续使用其他查询和一级来源，不要反复重试。
- 不要把验证码页、拦截页、反爬页的大段原文继续带入后续摘要和整理流程。
- 如果搜索命中的是 Reuters / Bloomberg / FT / WSJ / X 登录墙 / 其他强反爬页面，优先寻找**同一事件的官方新闻稿、公司博客、论文页、项目页或其他高质量二手报道**，不要在受限页面上反复消耗重试次数。
- 若候选事件涉及 `OpenAI`、`Google`、`Anthropic`、`Meta` 等主要公司，且首个命中结果来自 Reuters / Axios / Bloomberg / FT / WSJ / 其他受限媒体，必须继续补找该公司的**官方博客、官方新闻页、研究页、产品页或发布页**；只有在官方源与高质量可访问二手源都不可用时，才允许放弃该候选。

---

## 阶段 3：全文抓取

从阶段 1 + 2 的结果中，选择**最重要的 10-15 篇文章**，使用 **WebFetch** 获取全文以确保摘要准确。

### 全文抓取优先级与失败预算（必须遵守）

- 全文抓取优先级：**官方博客 / 官方新闻稿 / 论文原文 / 项目主页 / 一级来源可访问文章** > 聚合媒体 > 明显受限站点。
- 如果候选链接返回 `401`、`403`、`404`、`429`、登录墙、`Please enable JS`、验证码页、空白壳页或明显错误页，直接判定该链接本轮不可用。
- 单篇文章最多只允许一次降级尝试；失败后立即换源，不要在同一链接上循环重试。
- 连续出现 3 次全文抓取失败后，必须暂停“全文补抓”模式，改为优先使用已成功获取的可访问来源完成日报。
- 如果某条重要新闻只能拿到二手来源，正文中明确注明“基于二手报道整理，原始来源本轮不可访问”。
- 对于 `OpenAI` 相关候选，若 Reuters / Axios 等受限链接抓取失败，默认下一步不是放弃，而是立即检查 `https://openai.com/blog`、对应产品页、官方公告页，以及其他可访问原始来源；仅当这些替代源也无法验证时，才把该事件记为失败来源。
- 对于任何博客、新闻页、研究页、产品页候选，若单篇链接不是从列表页、站内搜索结果、RSS、官方 sitemap 或页面 HTML 中**明确抽取到的真实 URL**，禁止仅根据标题直接猜测 slug 并构造 URL 发起全文抓取；必须先回到对应官方页面确认真实链接后再抓取。

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

4. 选择**最有价值的至少 3 条**观点/帖子/演讲摘要，放入"🧠 大神模块：重要 AI 巨头/创始人最新观点"板块；如素材充足，可控制在 3-5 条。

5. 如果最近 72 小时内不足 3 条有效内容，**仅允许在现有白名单 URL 或官方域名内**，将时间范围扩展到最近 7 天补足到至少 3 条；**不得**因为补数量而放宽来源标准。

6. 只有在白名单/官方来源中最近 7 天仍无法凑够 3 条有效内容时，才允许少于 3 条，并且必须在该板块开头注明"最近 7 天内仅获取到 [N] 条可验证的大神模块公开内容，已按白名单来源补足但仍不足 3 条"。

### 大神模块来源规则（必须遵守）

- 优先级：**官方 keynote / 官方新闻稿 / 官方博客 / 本人白名单主页** > 白名单社交账号 > 高质量采访或转录。
- **禁止**自行臆造、替换、扩展任何人物相关账号、个人主页或镜像域名。
- **禁止**访问与下列白名单不一致的 X/Twitter 账号、第三方搬运号、拼写变体、粉丝号或媒体号。
- 若搜索结果指向的不是白名单 URL 或官方域名，直接视为无效结果，跳过。
- 若 X/Twitter 或 Nitter 在 **`opencli` 连接本地已登录浏览器** 后仍返回通用错误页、空响应、验证码页或其他不可验证内容，才记为“本轮未获取有效内容”，不要再尝试其他陌生账号。
- 若使用 `opencli twitter search` 或其他搜索方式拿到 X 候选内容，**必须**按 `author` 字段与白名单账号再次过滤，并核对链接是否对应白名单 URL；未同时满足这两个条件的结果，禁止写入日报正文。
- 当前机器的白名单抓取路由默认按“阶段 0.6 来源访问方式缓存”执行：
  - `x.com/elonmusk` / `x.com/xai` / `x.com/karpathy`：账号元信息先用 `opencli twitter profile`
  - 若要看最近帖子、搜索关键词、帖子上下文或确认最新公开动态：优先通过 `opencli` 连接本地已登录浏览器，不要先依赖托管浏览器
  - `x.ai`：优先通过 `opencli` 连接本地已登录浏览器；若 `web_fetch` 失败，不视为站点不可用
  - `tesla.com/AI` / `tesla.com/blog`：直接托管浏览器
  - `anthropic.com/*` / `nvidia*` / `karpathy.ai` / `karpathy.bearblog.dev`：优先 `web_fetch`
- 这一模块的目标是补充**本人或官方渠道**的近期公开观点；宁可缺失，也不要误抓到无关账号。
- 为满足日报稳定输出，**优先按“不同人物/公司、不同原始材料、不同主题”凑足至少 3 条**；若候选不足，可在白名单范围内扩展时间窗到最近 7 天，但仍需保持每条内容是独立、可验证的公开更新。

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
- 明显不可验证的拦截页、验证码页、登录墙、空白壳页、404 页面

### 最低交付保障（必须遵守）

- 即使搜索或抓取有部分失败，只要还能整理出 **5 条以上**可验证新闻，也必须生成并保存一份当日日报。
- 当有效新闻不足 10 条时，可以输出“精简版日报”，但仍需完成：
  - 保存 Markdown
  - 写回状态文件
  - 能发则发到消息渠道
- 大神模块默认也必须**至少输出 3 条**；若最近 72 小时内不足 3 条，只能通过白名单/官方来源扩展到最近 7 天补足，**不能**通过降低来源质量补数量。
- 只有在**完全拿不到足够可验证内容**时，才允许任务失败；失败时必须把失败原因写入状态文件，而不是静默中断。

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

### 本轮失败来源汇总（必须输出）

- 在最终 Markdown 的**结尾总结区域**，必须新增一个固定板块：`## ⚠️ 本轮失败来源`
- 汇总本轮所有**抓取失败 / 搜索失败 / 全文抓取失败 / 白名单访问失败**的信息源
- 每条至少写清：
  - **来源**（域名、平台或命令入口）
  - **阶段**（一级抓取 / 搜索 / 全文抓取 / 大神模块白名单等）
  - **失败原因**（如 `403`、`429`、Cloudflare、Access Denied、timeout、登录墙、`opencli` 路由失败等）
  - **处理结果**（已跳过 / 已改用其他来源 / 基于二手来源整理）
- 不要把完整报错日志整段贴进去；只保留便于后续排查的最小必要信息
- 如果本轮没有失败来源，也必须输出：
  - `- 无（本轮主要来源抓取与搜索未出现需要记录的失败）`

### 目录索引规则（必须遵守）

- **目录必须列出每条新闻**：在"📑 目录"下，将每条新闻标题作为链接嵌套在其分类下
- **每条新闻必须有稳定锚点**：在每条新闻上方插入 `<a id="xxx"></a>`
- **锚点命名**：
  - 重要发布：`maj-01`、`maj-02`…
  - 研究：`res-01`、`res-02`…
  - 产业：`biz-01`、`biz-02`…
  - 工具：`tool-01`、`tool-02`…
  - 政策：`pol-01`、`pol-02`…
  - 大神模块：`guru-01`、`guru-02`、`guru-03`…

### 金字塔可视化（目录之后、分类之前）

**Notion 同步硬性要求**：ASCII 金字塔必须用**无语言**围栏（单独一行 \`\`\` 开始、单独一行 \`\`\` 结束），**禁止**使用 \`\`\`text。`text` 语言标识曾触发 Notion API 校验失败；失败后若改用按字符切块，会在围栏中间截断，Notion 端表现为「正在加载 Plain Text 代码」的异常代码块 + 仅显示金字塔底部（L2/L1）几行正文。

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

将重要 AI 巨头、创始人或技术领袖的内容放在"🧠 大神模块：重要 AI 巨头/创始人最新观点"中，至少输出 3 条，使用 `guru-01`、`guru-02`、`guru-03` 锚点。优先使用最近 72 小时内容；若不足 3 条，仅可在白名单/官方来源中扩展到最近 7 天补足。如仍不足，注明"最近 7 天内仅获取到 [N] 条可验证的大神模块公开内容，已按白名单来源补足但仍不足 3 条"。

---

## 阶段 8：保存到磁盘（必须执行）

- **输出目录**：`<skills根目录>/output/`
- **文件名**：`daily-ai-news-YYYYMMDD.md`（YYYYMMDD = 生成日期）
- **内容**：与最终输出完全相同的 Markdown
- **如文件已存在**：用最新内容覆盖
- **如目录不存在**：自动创建

### 落盘强约束（必须遵守）

- 当你判断“素材已经足够、开始整理正文”后，必须先在内存中形成完整 Markdown，再立即执行落盘。
- **禁止**在未调用落盘工具前输出类似“我现在开始写”“我去整理完整报告”的独立回复。
- 落盘后必须立即二次校验目标文件是否存在、是否非空、路径是否正确。
- 若落盘失败，必须立刻重试正确的落盘动作或输出明确错误；**禁止**停留在“准备写入”状态。
- 状态文件 `~/.openclaw/workspace/memory/daily-ai-news-state-YYYYMMDD.json` 必须在文件校验成功后立即更新至少这几个字段：
  - `phase`: `file_saved`
  - `file_verified`: `true`
  - `report_path`: 实际 Markdown 路径

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
- **最终结尾必须包含 `## ⚠️ 本轮失败来源` 板块，且内容与本轮实际失败情况一致**

### 错误处理
- 如果某来源抓取失败 → 在最终报告中注明，继续使用可用数据
- 如果搜索无结果 → 注明"该类别今日无相关新闻"
- 如果结果过多 → 提高重要性阈值
- 如果内容有付费墙 → 使用可用摘要并注明限制

## 附加资源

- `references/news_sources.md` — 国际 AI 新闻来源（一级至五级）
- `references/search_queries.md` — 英文搜索查询模板
- `references/output_templates.md` — 深度版输出格式模板
