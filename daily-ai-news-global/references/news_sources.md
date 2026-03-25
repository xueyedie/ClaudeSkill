# AI 新闻来源数据库 — 国际版

国际 AI 新闻来源综合列表，按层级和关注领域组织。

## 访问方式标签（2026-03-24 本机缓存）

- `web_fetch（已验证）`：本机已确认可直接抓取
- `opencli（已验证）`：本机已确认适配器可用，优先走结构化结果
- `托管浏览器（已验证需要）`：本机已确认 `web_fetch` / 裸 HTTP 不稳定或失败，直接走托管浏览器
- `待验证，默认 web_fetch`：尚未单独复核，先按 `web_fetch` 处理；若失败再按 `SKILL.md` 的降级规则切换
- `待验证，默认 opencli`：尚未单独复核，但来源类型与现有适配器匹配，先按 `opencli` 处理

## 一级来源：主要来源（每日检查）

这些来源提供全面的 AI 新闻报道，每日更新。

### 1. VentureBeat AI
- **URL**：https://venturebeat.com/category/ai/
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每日
- **关注领域**：行业新闻、产品发布、AI 应用
- **最适合**：商业和产品新闻
- **优势**：AI 行业动态的全面报道

### 2. TechCrunch AI
- **URL**：https://techcrunch.com/category/artificial-intelligence/
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每日
- **关注领域**：创业融资、公司新闻、产品发布
- **最适合**：创业公司和投资新闻
- **优势**：融资轮次和收购的早期报道

### 3. The Verge AI
- **URL**：https://www.theverge.com/ai-artificial-intelligence
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每日
- **关注领域**：消费级 AI、产品评测、行业分析
- **最适合**：面向消费者的 AI 产品和服务
- **优势**：深度产品评测和分析

### 4. MIT Technology Review AI（麻省理工科技评论）
- **URL**：https://www.technologyreview.com/topic/artificial-intelligence/
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每日
- **关注领域**：深度分析、研究突破、伦理影响
- **最适合**：深思熟虑的分析和研究报道
- **优势**：高质量新闻报道和专家洞察

### 5. AI News
- **URL**：https://artificialintelligence-news.com/
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每日
- **关注领域**：AI 行业综合报道
- **最适合**：AI 新闻的广泛概览
- **优势**：聚合式报道，覆盖所有 AI 话题

### 6. AI Hub Today
- **URL**：https://ai.hubtoday.app/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每日
- **关注领域**：AI 新闻聚合和最新动态
- **最适合**：快速获取精选 AI 新闻
- **优势**：AI 行业新闻的集中枢纽

---

## 二级来源：公司博客（每周检查）

主要 AI 公司的官方博客，最适合获取官方公告和产品更新。

### 1. OpenAI 博客
- **URL**：https://openai.com/blog
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周（不固定）
- **关注领域**：GPT 更新、研究发布、产品公告
- **最适合**：OpenAI 官方公告
- **核心内容**：模型发布、功能更新、研究论文

### 2. Google AI 博客
- **URL**：https://blog.google/technology/ai/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：研究更新、产品集成、Gemini 新闻
- **最适合**：Google 的 AI 计划
- **核心内容**：研究突破、Google 产品 AI 功能

### 3. DeepMind 博客
- **URL**：https://deepmind.google/discover/blog/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：研究突破、科学发现
- **最适合**：前沿 AI 研究
- **核心内容**：AlphaFold、强化学习进展、科学应用

### 4. Anthropic 工程博客
- **URL**：https://www.anthropic.com/engineering
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：Claude 更新、工程实践
- **最适合**：Anthropic 工程和产品更新

### 5. Anthropic 新闻
- **URL**：https://www.anthropic.com/news
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每周
- **关注领域**：Claude 更新、安全研究、Constitutional AI
- **最适合**：Anthropic 产品和研究更新

### 6. Microsoft AI 博客
- **URL**：https://blogs.microsoft.com/ai/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：Azure AI、Copilot 更新、企业 AI
- **最适合**：Microsoft 的 AI 产品和集成

### 7. Meta AI 博客
- **URL**：https://ai.meta.com/blog/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：LLaMA、开源、研究发布
- **最适合**：Meta 的开源 AI 计划

---

## 三级来源：研究来源（每周检查）

学术和研究导向的来源，获取最新 AI 研究论文和突破。

### 1. arXiv.org
- **URL**：https://arxiv.org/list/cs.AI/recent
- **访问方式**：`待验证，默认 opencli`
- **更新频率**：每日
- **关注领域**：预印本研究论文
- **最适合**：发表前的最新研究
- **核心分类**：cs.AI、cs.LG、cs.CL、cs.CV

### 2. Hugging Face
- **URL**：https://huggingface.co/blog
- **访问方式**：`web_fetch（已验证）`
- **更新频率**：每周
- **关注领域**：模型发布、开源、NLP、计算机视觉
- **最适合**：开源模型和工具

### 3. Papers with Code
- **URL**：https://paperswithcode.com/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每日
- **关注领域**：附带实现代码的研究论文
- **最适合**：查找研究的实际实现

### 4. Google DeepMind 出版物
- **URL**：https://deepmind.google/research/publications/
- **访问方式**：`待验证，默认 web_fetch`
- **更新频率**：每周
- **关注领域**：同行评审的研究论文

---

## 四级来源：细分来源（按需检查）

专注于 AI 特定方面的专业出版物。

### 1. AI Ethics Newsletter（AI 伦理通讯）
- **URL**：https://aiethicsnewsletter.com/
- **访问方式**：`待验证，默认 web_fetch`
- **关注领域**：AI 伦理、政策、社会影响

### 2. Synced Review（机器之心英文版）
- **URL**：https://syncedreview.com/
- **访问方式**：`待验证，默认 web_fetch`
- **关注领域**：中国 AI 新闻、技术深度解析

### 3. KDnuggets
- **URL**：https://www.kdnuggets.com/
- **访问方式**：`待验证，默认 web_fetch`
- **关注领域**：数据科学、机器学习教程、行业新闻

### 4. VentureBeat AI Beat
- **URL**：https://venturebeat.com/category/ai/
- **访问方式**：`web_fetch（已验证）`
- **关注领域**：AI 行业深度报道

### 5. Towards Data Science
- **URL**：https://towardsdatascience.com/
- **访问方式**：`待验证，默认 web_fetch`
- **关注领域**：数据科学教程、机器学习技术

---

## 五级来源：专家声音 / Karpathy（每日/隔日检查）

### Andrej Karpathy — 全平台

**博客 / 个人网站**
- **个人主页**：https://karpathy.ai/
- **访问方式**：`web_fetch（已验证）`
- **旧博客（Jekyll）**：http://karpathy.github.io/
- **访问方式**：`待验证，默认 web_fetch`

**社交媒体**
- **X（Twitter）**：https://x.com/karpathy
- **访问方式**：`托管浏览器（最近动态）` + `opencli twitter profile（账号元信息，已验证）`

**视频**
- **YouTube**：https://www.youtube.com/andrejkarpathy
- **访问方式**：`opencli（已验证）`

**课程**
- **Neural Networks: Zero To Hero**：https://karpathy.ai/zero-to-hero.html
- **访问方式**：`待验证，默认 web_fetch`

**代码/笔记**
- **GitHub**：https://github.com/karpathy
- **访问方式**：`待验证，默认 web_fetch`
- **GitHub Gist**：https://gist.github.com/karpathy
- **访问方式**：`待验证，默认 web_fetch`

**其他**
- **斯坦福**：https://cs.stanford.edu/people/karpathy/advice.html
- **访问方式**：`待验证，默认 web_fetch`

---

## 使用指南

### 每日新闻采集（国际版）
1. 从**一级来源**中选择 3-5 个
2. 添加 1-2 个**二级来源**（检查重大公告）
3. 使用网络搜索发现突发新闻
4. 检查**五级来源**（Karpathy 等技术领袖/官方渠道）获取至少 3 条近期洞察（优先最近 24-72 小时；如不足，仅在白名单/官方来源内扩展到最近 7 天补足）

### 每周研究汇总
1. 检查**三级来源**（arXiv、Hugging Face）
2. 回顾主要公司博客（**二级来源**）的近期论文
3. 聚焦突破性论文和热门研究

### 来源选择策略

**全面覆盖**：
- 混合 3 个一级来源（不同优势）
- 添加 2 个二级来源（主要公司）
- 包含 1 个三级来源（研究）

**快速更新**：
- 聚焦 AI News（聚合器）和 AI Hub Today
- 添加 TechCrunch AI（快速突发新闻）
- 检查 Twitter/X 获取实时更新
  - 账号元信息：优先 `opencli twitter profile`
  - 最近帖子 / 搜索：当前机器直接用托管浏览器，不再先试 `opencli twitter search`

**深度分析**：
- MIT Technology Review
- VentureBeat 深度文章
- 公司博客文章（完整公告）

### 大神模块补充来源（2026-03-24 本机缓存）

为避免与 `SKILL.md` 脱节，下面这些官方/白名单来源也统一记录访问方式：

- **NVIDIA**
  - `https://blogs.nvidia.com/` → `web_fetch（已验证）`
  - `https://nvidianews.nvidia.com/` → `web_fetch（已验证）`
  - `https://www.nvidia.com/gtc/keynote/` → `web_fetch（已验证）`
  - `https://www.youtube.com/@NVIDIA` → `opencli（已验证，youtube search 可用）`

- **Anthropic**
  - `https://www.anthropic.com/news` → `web_fetch（已验证）`
  - `https://www.anthropic.com/research` → `web_fetch（已验证）`
  - `https://www.anthropic.com/engineering` → `待验证，默认 web_fetch`

- **Elon Musk / xAI / Tesla AI**
  - `https://x.com/elonmusk` → `托管浏览器（最近动态）` + `opencli twitter profile（账号元信息，已验证）`
  - `https://x.com/xai` → `托管浏览器（最近动态）` + `opencli twitter profile（账号元信息，已验证）`
  - `https://x.ai/` → `托管浏览器（已验证需要）`
  - `https://www.tesla.com/AI` → `托管浏览器（已验证需要）`
  - `https://www.tesla.com/blog` → `托管浏览器（已验证需要）`
