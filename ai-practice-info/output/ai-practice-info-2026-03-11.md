# AI 实战技巧日报 - 2026-03-11

> 主题：AI 编程、AI 美术工作流、AI 提效工具、GitHub 热门、B 站实战内容
> 说明：按 skill 要求进行多源收集；B 站“关注分组”未获得可用登录态，已改用公开搜索结果补足并明确标注。

## TL;DR

今天最值得关注的不是“又出了什么模型”，而是 **AI 工具正在从单次对话，进入可持续执行的工作流时代**：
- AI 编程：重点从“写代码”转向 **自动化审查、上下文工程、长任务编排、IDE 深度集成**。
- AI 美术：重点从“单张图更好看”转向 **视频/工作流/控制信号/社区可复用模板**。
- AI 工具：好用的方向越来越集中在 **自动运行、事件触发、可观测、记忆、与现有工具链融合**。
- GitHub 热门：热点明显偏向 **agent 框架、agent 工作流、AI 安全评测、页面代理、语音/TTS**。
- 中文内容生态：B 站仍然在快速放大 **Cursor / Claude Code / OpenClaw / Skill / MCP** 这类“马上能用”的实践型内容。

---

## 一、AI 编程（今天能用的实战信息）

### 1. Anthropic：上下文工程正在取代“只卷 prompt”
来源：Anthropic Engineering《Effective context engineering for AI agents》

关键信号：
- 重点不再是单条 prompt 怎么写，而是 **整个上下文如何被组织、压缩、检索和持续维护**。
- 对 agent 来说，系统提示、工具、消息历史、外部数据、记忆文件，都是上下文工程的一部分。
- 长任务里最关键的几个动作是：**compaction（压缩上下文）**、**structured note-taking（结构化笔记）**、**sub-agent architectures（子代理架构）**。

今天就能抄的做法：
- 给你的 agent 项目加一个 `NOTES.md` / `MEMORY.md`，让它把关键决定写出去，而不是全靠会话历史。
- 不要把所有资料一次性塞进上下文，改成“**引用 + 按需读取**”模式：只传路径、摘要、索引、URL，需要时再读。
- 对长会话做“**阶段性压缩总结**”，保留决策、未完成项、关键文件，不保留冗长工具输出。

适合谁：
- 用 Claude Code / Cursor / OpenClaw / 自建 agent 做复杂编码任务的人。

---

### 2. Cursor：自动化 agent 开始从 IDE 走向持续运行
来源：Cursor Blog《Build agents that run automatically》

关键信号：
- Cursor Automations 支持 **定时** 或 **事件触发** agent，例如 Slack 消息、Linear issue、PR 合并、PagerDuty incident。
- 官方案例已覆盖：**安全审查、CodeOwners 分配、事故排查、周报、补测试、bug triage**。
- 自动化 agent 不只是“提醒”，而是能在云端沙盒里运行、校验输出、复用记忆。

今天就能抄的做法：
- 把“每周变更总结”“PR 风险分级”“每日测试补全建议”这类重复脑力活交给定时 agent。
- 优先挑 **低风险、高重复、可验证** 的任务自动化，而不是一上来就让 agent 直接改生产系统。
- 如果你团队还没上 Cursor Automations，也能用 OpenClaw cron / GitHub Actions / 自建 webhook 做同类骨架。

---

### 3. Cursor × JetBrains：ACP 让 agent 深入传统 IDE 用户群
来源：Cursor Blog《Cursor is now available in JetBrains IDEs》

关键信号：
- Cursor 通过 **ACP（Agent Client Protocol）** 进入 IntelliJ / PyCharm / WebStorm 等 JetBrains IDE。
- 这说明“AI 编程”不再只属于新 IDE，而是在往 **现有工程组织的主战场** 渗透。
- 对 Java / 多语言 / 企业开发团队来说，这比单纯“换个编辑器”现实得多。

今天就能抄的做法：
- 如果团队离不开 JetBrains，优先评估 ACP 兼容方案，而不是强推所有人切换工具链。
- 选模型时按任务分流：**架构/重构/长任务用强推理模型，小修小补用快模型**。

---

### 4. OpenAI Cookbook：多工具编排与 Agents SDK 正在变成标准拼装方式
来源：OpenAI Cookbook《Multi-Tool Orchestration with RAG...》《Building a Voice Assistant with the Agents SDK》

关键信号：
- 官方示例越来越强调 **工具编排 + 检索 + 路由**，而不是“一个万能 prompt”。
- Agents SDK 的典型做法是：**分工 agent + triage agent + 工具函数 + tracing**。
- Voice 场景也开始直接用 agent workflow 承接，而不是完全单独设计。

今天就能抄的做法：
- 把你的 AI 应用拆成 3 层：**入口分流、领域 agent、工具层**。
- 所有生产 agent 都加 tracing / logs，不然效果好坏只能靠感觉。
- 如果做客服、知识库、内部助手，优先做“**实时搜索 agent / 知识库 agent / 账号/动作 agent**”三分法。

---

### 5. LangGraph：长时、可恢复、可插人类的 agent 基础设施更成熟了
来源：LangGraph Overview

关键信号：
- LangGraph 明确把定位放在 **低层 orchestration**：durable execution、human-in-the-loop、memory、deployment。
- 这套思路适合需要 **长任务、状态恢复、人工中断、生产部署** 的系统。

今天就能抄的做法：
- 若你只是做单轮助手，别上复杂框架。
- 若你要做多步骤、可恢复、可审计 agent，LangGraph / AutoGen / CrewAI 这类框架才有意义。
- 先做最小图：`入口 -> 工具节点 -> 校验节点 -> 人工确认 -> 输出`。

---

### 6. 开源 agent 框架趋势：AutoGen 继续维护，CrewAI 更强调企业自动化
来源：GitHub README / 官网文档

**AutoGen**
- 定位：多 agent 编程框架。
- 新手入口被明确引导到 Microsoft Agent Framework，但 AutoGen 仍持续维护与打补丁。
- 优势：多 agent、MCP、消息传递模型、Studio/Bench 生态。

**CrewAI**
- 定位：偏生产自动化与企业流程。
- 核心概念：**Crews（自治协作）+ Flows（事件驱动控制）**。
- 优势：比较强调流程控制、企业落地、控制面板、观测性。

今天怎么选：
- 想做研究型、多 agent 对话编排：先看 **AutoGen**。
- 想做业务流程自动化、事件驱动、多步骤编排：先看 **CrewAI**。
- 想自己掌控状态图和恢复逻辑：先看 **LangGraph**。

---

## 二、AI 美术 / 工作流（今天能用的实战信息）

### 1. Runway 的主线已经非常明确：图像生成正在向“世界模拟 + 视频工作流”移动
来源：Runway Research

关键信号：
- Runway 研究首页持续强调：**multimodal simulators of the world**。
- 近一年重点方向包括：
  - Gen-4 / Gen-4.5
  - Game Worlds
  - Act-One
  - Frames
  - A2D（从自回归 VLM 适配到 diffusion 解码）
  - Dual-Process Image Generation（让图像生成器学会从 VLM 的“审稿”中学任务）

对创作者的实际意义：
- 工具重点在变：从“出一张图”变成 **镜头一致性、控制信号、多轮迭代、视频级创作**。
- 未来竞争点是 **工作流能力**，不是只拼一次出图的偶然效果。

今天就能抄的做法：
- 建立自己的“镜头模板库”：人物设定、镜头语言、光照、景别、镜头运动、材质词汇分开保存。
- 做视频前先固定 **角色描述 + 场景描述 + 镜头约束 + 风格锚点**，不要每次全靠即兴 prompt。

---

### 2. 社区工作流正在强调：ComfyUI 的“工作流产品化”速度很快
来源：Reddit /r/StableDiffusion RSS

关键信号：
- Reddit 热帖显示 **ComfyUI launches App Mode and ComfyHub**。
- 这代表节点流工具在向更可交付、更可分享、更低门槛的“应用模式”靠近。
- 另一个热帖来自 LTX Desktop：强调 **Linux 支持、IC-LoRA 集成、时间线视频工作流、官方开源协作**。

今天就能抄的做法：
- 别把 ComfyUI 只当“高级玩家玩具”，它正在变成 **可封装工作流产品**。
- 维护 3 套自己的固定流程：
  1. 文生图风格图
  2. 图生视频/视频转风格
  3. LoRA + ControlNet / pose / depth 控制流程
- 每个流程保留一份“最少参数版”，方便复用和交接。

---

### 3. AI 美术正在从“审美炫技”走向“个人记忆 / 叙事表达”
来源：Reddit /r/StableDiffusion 热帖

关键信号：
- 有创作者使用 childhood photos 微调 SDXL LoRA，用于模拟“记忆召回”质感。
- 这类项目的价值点不只是模型训练，而是 **AI 作为个人叙事媒介**。

今天就能抄的做法：
- 如果你做内容，不要只卷“更高清”。
- 更值得做的是：**个人风格库、系列化角色、长期世界观、情绪化叙事主题**。
- 你的训练素材最好围绕一个主题聚类，而不是杂乱堆图。

---

## 三、AI 提效工具（今天能用的）

### 1. Product Hunt 上“成熟 AI 工具”的共识：不是花哨，是能嵌进工作流
来源：Product Hunt / Artificial Intelligence

页面上比较突出的方向：
- OpenAI：多模态 API、函数调用 agent、实时语音
- Claude：长上下文、代码、企业安全工具调用
- Cursor：IDE 内 agent、重构、PR review

实用判断：
- 好工具越来越像“基础设施”而不是“玩具”。
- 你选 AI 工具时优先看 4 件事：
  1. 能不能接入现有工作流
  2. 能不能自动运行
  3. 能不能被审计/回放
  4. 能不能分任务选模型

---

### 2. Simon Willison 的持续观察：真正好用的 agent，核心是“能执行、能验证、能防注入”
来源：Simon Willison’s Weblog

关键信号：
- 他在“Agentic manual testing”里强调：**不要默认 LLM 写的代码能工作，必须执行验证。**
- 他转发的安全案例“Clinejection”再次说明：**prompt injection + 自动执行工具** 会直接带来供应链/缓存投毒等风险。

今天就能抄的做法：
- Agent 默认权限最小化。
- 对外部输入（issue、PR、网页、邮件）一律当不可信内容处理。
- 把“生成代码”和“执行/发布代码”拆权限。
- 引入自动化时，先自动生成报告，再让人确认，不要一键上线。

---

## 四、GitHub 热门（与 AI 实战最相关的）

来源：GitHub Trending（今日）

### 1. agency-agents
- 描述：完整 AI agency 角色集合。
- 信号：大家仍然很吃“**一套可复用角色/技能库**”这种资产化思路。
- 启发：把你常做的工作写成 agent skill / prompt pack / SOP，比每次临场聊天强得多。

### 2. promptfoo
- 描述：测试 prompts、agents、RAG，做红队/漏洞扫描/性能对比。
- 信号：AI 应用开始更认真对待 **评测、安全、回归测试**。
- 启发：任何要上线的 AI 功能，都应该配一套最小 eval 集。

### 3. superpowers
- 描述：agentic skills framework & software development methodology。
- 信号：说明“技能化、方法论化、流程化”仍是热方向。
- 启发：把高频任务沉淀成 skill，比堆更多模型更划算。

### 4. alibaba/page-agent
- 描述：网页内 GUI agent，自然语言控制 web interfaces。
- 信号：浏览器/页面自动化仍是高热方向，尤其适合表单、后台、运营流程。
- 启发：很多“文员型工作”会先被页面 agent 吃掉。

### 5. fish-speech
- 描述：SOTA 开源 TTS。
- 信号：语音能力仍在快速实用化，尤其适合内容生产、陪伴、助手类产品。

### 6. hermes-agent
- 描述：The agent that grows with you。
- 信号：agent memory / 长期陪伴 / 个性化持续上下文，依旧很热。

### 7. MiroFish
- 描述：通用群体智能引擎。
- 信号：AI 圈之外，大家也在重新关注 swarm / 多智能体协作概念。

---

## 五、B 站实战内容观察（公开搜索替代“关注分组”）

> 说明：skill 原要求查看“B站关注分组：AI技术分享 + AI绘画社区”。本次无法获取可用登录态/关注列表，改用公开搜索结果做替代观察。

### 1. Claude Code 相关内容热度非常高，而且正在明显教程化、职业化
来源：B 站搜索 `Claude Code`

观察到的典型标题：
- 《Claude Code 从 0 到 1 全攻略：MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理 / 后台任务》
- 《手把手教你在国内使用Claude Code》
- 《15分钟Claude Code小白入门》
- 《Claude Code 的 Skill 是什么，怎么用？》
- 《Claude Code接入飞书教程，手机远程操纵电脑写代码》

实用结论：
- 中文用户最关心的不是原理，而是 **安装、能不能在国内用、工作流、Skill、MCP、实战案例**。
- 这类内容说明市场已经从“尝鲜”进入“生产力迁移”。

### 2. Cursor 内容同样强势，但更偏“零基础上手 + 快速交付”
来源：B 站搜索 `Cursor 教程`

观察到的典型标题：
- 《普通人也可以看的 AI 编程指南 | Cursor 教程》
- 《Cursor使用教程，2小时玩转cursor》
- 《如何用Cursor开发大项目，全流程讲解》
- 《Cursor 新手教程：Cursor rules 让 AI 更懂你》
- 《挑战用Cursor30分钟搭建完整小程序》

实用结论：
- Cursor 的传播优势在于：**更容易被包装成“普通人也能用”的生产工具**。
- 中文实战内容开始把重点放到：**rules、项目工作流、从需求到上线**。

### 3. OpenClaw 也已进入中文教程与讨论视野
来源：Claude Code 搜索结果联动出现的公开视频

观察到的典型标题：
- 《一个视频搞懂OpenClaw！》
- 《OpenClaw到底是什么？一只龙虾如何搅动整个AI圈！》
- 《别再乱买AI工具了！Claude Code和OpenClaw，到底谁才是打工人的神？》

实用结论：
- OpenClaw 已被当成“AI 助手/代理工作流平台”进入比较视野。
- 这类内容对新用户教育价值高，说明“本地/半自动/跨渠道”助手是有市场的。

---

## 六、今天最值得马上尝试的 10 个动作

1. 给你的 AI 编程项目加一个 `NOTES.md`，把关键决策写出去。  
2. 把长任务拆成“入口 agent + 专家 agent + 校验”三段式。  
3. 给 agent 工具权限做分级：读 > 写 > 执行 > 发布。  
4. 给 AI 应用加最小 eval 集，至少覆盖 10 个常见用例。  
5. 把重复脑力活做成定时自动化：周报、PR 摘要、风险检查。  
6. 在 Cursor / Claude Code 中建立固定的 rules / skills / memory 文件。  
7. AI 美术流程不要只留 prompt，保留“工作流模板 + 参数说明”。  
8. 视频生成优先追求“角色一致性 + 控制信号”，不要只追单帧惊艳。  
9. 关注 B 站实战教程时，优先看有真实项目和失败案例复盘的内容。  
10. 把“今天看到的一个技巧”立刻试到自己项目里，不要只收藏。  

---

## 七、夏夏的判断

如果只看“今天能不能立刻用”，我会给出这三个结论：

1. **AI 编程的核心能力已经不是补全，而是工作流编排。**  
2. **AI 美术真正拉开差距的，不是单张图，而是可复用的工作流与叙事能力。**  
3. **未来 3 个月最值钱的不是知道更多新词，而是把 1 个自动化场景真正跑起来。**

---

## 参考来源（本次实际访问）
- Anthropic Engineering
- OpenAI Cookbook / Developers
- Cursor Blog
- LangGraph Docs
- GitHub Trending
- Microsoft AutoGen GitHub
- CrewAI GitHub
- Runway Research
- Product Hunt / Artificial Intelligence
- Simon Willison’s Weblog
- Reddit /r/StableDiffusion RSS
- B 站公开搜索：`Claude Code`、`Cursor 教程`
