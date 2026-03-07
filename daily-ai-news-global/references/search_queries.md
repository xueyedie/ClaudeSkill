# 搜索查询模板 — 国际版

预定义的搜索查询模板，用于发现国际 AI 新闻。执行时根据当前日期动态替换日期占位符。

## 日期占位符

- `[yesterday]`：当前日期 - 1 天
- `[week_ago]`：当前日期 - 7 天

---

## 核心查询（每日必用，选 3-4 条）

```
# 综合新闻
"AI news today" OR "artificial intelligence breakthrough" after:[yesterday]

# 研究突破
"AI research paper" OR "machine learning breakthrough" after:[yesterday]

# 产业动态
"AI startup funding" OR "AI company news" OR "new AI tool" after:[yesterday]

# 主要公司（可选）
"OpenAI" OR "Google AI" OR "Anthropic" OR "Meta AI" announcement after:[yesterday]
```

---

## 公司专项查询（按需选用）

```
"OpenAI announcement" OR "GPT update" OR "ChatGPT news" after:[yesterday]
"Google AI announcement" OR "Gemini update" after:[yesterday]
"Anthropic news" OR "Claude update" after:[yesterday]
"Meta AI announcement" OR "LLaMA update" after:[yesterday]
"Microsoft AI" OR "Copilot update" OR "Azure AI news" after:[yesterday]
"DeepMind research" OR "Google DeepMind" after:[week_ago]
```

---

## 扩展查询（结果不足时补充）

```
# 开源与工具
"open source AI" OR "AI model release" OR "LLM release" after:[yesterday]

# 学术论文
arXiv "cs.AI" OR "cs.LG" paper after:[yesterday]

# 会议论文（会议季重点使用）
"NeurIPS" OR "ICML" OR "ACL" OR "ICLR" AI paper after:[week_ago]

# 行业投融资
"AI acquisition" OR "AI partnership" OR "artificial intelligence investment" after:[week_ago]

# 政策监管
"AI regulation" OR "AI policy" OR "AI ethics" after:[week_ago]

# 垂直领域
"AI" AND "healthcare" OR "medical AI" after:[week_ago]
"AI" AND "finance" OR "fintech AI" after:[week_ago]
"AI" AND "robotics" OR "embodied AI" after:[week_ago]
```

---

## 排除噪音

在任何查询后可追加排除项：
```
NOT "cryptocurrency" NOT "blockchain" NOT "web3"
```

---

## 使用策略

1. 每日简报先跑"核心查询"4 条，覆盖综合/研究/产业/公司
2. 如果某类别结果不足，从"扩展查询"中补充对应类别
3. 如果结果过多，缩短日期范围（`after:[yesterday]`）或添加更具体的关键词
4. 始终检查返回结果的发布日期，确保内容是最新的
