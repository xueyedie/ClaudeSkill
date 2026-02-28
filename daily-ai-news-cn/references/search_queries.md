# 搜索查询模板 — 国内版

以下查询模板专门用于采集中国国内 AI 新闻，配合 `news_sources.md` 使用。

## 日期格式

使用动态日期插入：
- **今天**: `[current_date]`
- **昨天**: `[current_date - 1 day]`
- **本周**: `[current_date - 7 days]`

---

## 综合国内 AI 新闻

### 每日综合
```
"AI 新闻" OR "人工智能" OR "大模型" 最新动态 after:[yesterday]
```

### 国内 AI 行业
```
"国内AI" OR "中国人工智能" OR "国产大模型" after:[yesterday]
```

### 大模型发布/更新
```
"大模型发布" OR "大模型更新" OR "国产大模型" OR "开源大模型" after:[yesterday]
```

---

## 国内公司动态

### 百度 / 文心一言
```
"百度AI" OR "文心一言" OR "文心大模型" OR "百度智能云" after:[yesterday]
```

### 阿里 / 通义千问 / Qwen
```
"通义千问" OR "Qwen" OR "阿里AI" OR "达摩院" after:[yesterday]
```

### 腾讯 / 混元
```
"腾讯AI" OR "混元大模型" OR "腾讯混元" after:[yesterday]
```

### 华为 / 昇腾
```
"华为AI" OR "昇腾" OR "昇思" OR "MindSpore" OR "华为云AI" after:[yesterday]
```

### 字节跳动 / 豆包
```
"豆包" OR "字节AI" OR "火山引擎AI" OR "豆包大模型" after:[yesterday]
```

### 智谱 AI / GLM
```
"智谱AI" OR "ChatGLM" OR "GLM模型" after:[yesterday]
```

### 月之暗面 / Kimi
```
"月之暗面" OR "Kimi" OR "Moonshot AI" after:[yesterday]
```

### DeepSeek
```
"DeepSeek" OR "深度求索" after:[yesterday]
```

### 零一万物
```
"零一万物" OR "01.AI" OR "Yi模型" after:[yesterday]
```

### 商汤 / 科大讯飞
```
"商汤科技" OR "日日新大模型" OR "科大讯飞" OR "星火大模型" after:[yesterday]
```

---

## 国内政策与监管

### AI 监管政策
```
"AI监管" OR "人工智能监管" OR "生成式AI管理" OR "算法备案" after:[yesterday]
```

### 数据安全与隐私
```
"数据安全法" OR "个人信息保护" OR "AI数据合规" after:[week_ago]
```

### 国家 AI 战略
```
"人工智能发展规划" OR "AI产业政策" OR "新一代人工智能" after:[week_ago]
```

### 芯片/算力政策
```
"芯片出口管制" OR "国产芯片" OR "AI算力" OR "智算中心" after:[week_ago]
```

---

## 国内研究与论文

### 中国 AI 研究
```
"中国AI研究" OR "清华AI" OR "北大AI" OR "中科院AI" after:[yesterday]
```

### 国内 AI 论文
```
"中国团队" AI 论文 OR "清华大学" "人工智能" 论文 after:[week_ago]
```

### 国内 AI 会议
```
"CCAI" OR "中国人工智能大会" OR "WAIC" OR "世界人工智能大会" after:[week_ago]
```

---

## 国内 AI 产品与工具

### 国产 AI 应用
```
"AI应用" OR "AI助手" OR "AI工具" 国内 after:[yesterday]
```

### 国产开源项目
```
"开源大模型" OR "国产开源" OR "中文大模型" after:[yesterday]
```

---

## AI+游戏（重点关注）

### AI 游戏综合
```
"AI游戏" OR "AI+游戏" OR "游戏AI" OR "AI NPC" OR "AI辅助游戏开发" after:[yesterday]
```

### 游戏引擎 AI 功能
```
"Unity AI" OR "Unreal AI" OR "游戏引擎" "人工智能" OR "PCG" "程序化生成" after:[week_ago]
```

### AI 游戏应用
```
"AI游戏开发" OR "AI角色" OR "智能NPC" OR "AI关卡生成" OR "AI游戏测试" after:[yesterday]
```

### 游戏行业 AI 趋势
```
site:youxiputao.com AI OR 人工智能 after:[yesterday]
```
```
site:gameres.com AI OR 人工智能 OR AIGC after:[yesterday]
```

---

## AI 美术资产生成（重点关注）

### AI 绘画/生成综合
```
"AI绘画" OR "AI美术" OR "AIGC美术" OR "AI生成资产" OR "AI美术资产" after:[yesterday]
```

### Stable Diffusion / Flux / ComfyUI
```
"Stable Diffusion" OR "Flux" OR "ComfyUI" 最新 OR 教程 OR 工作流 after:[yesterday]
```

### AI 3D / 材质 / 贴图生成
```
"AI建模" OR "AI 3D生成" OR "AI材质" OR "AI贴图" OR "AI纹理生成" after:[week_ago]
```

### AI 视频/动画生成
```
"AI视频生成" OR "AI动画" OR "Sora" OR "可灵" OR "Kling" OR "Runway" after:[yesterday]
```

### 游戏美术 + AI
```
"游戏美术" "AI" OR "AI游戏美术" OR "AI概念设计" OR "AI角色设计" after:[week_ago]
```

---

## 小红书 AI 热点

### 小红书 AI 工具分享
```
site:xiaohongshu.com "AI工具" OR "AI绘画" OR "AI教程" after:[yesterday]
```

### 小红书 AI 游戏/美术
```
site:xiaohongshu.com "AI游戏" OR "AI美术" OR "Stable Diffusion" OR "Midjourney" OR "ComfyUI" after:[yesterday]
```

### 小红书大模型体验
```
site:xiaohongshu.com "大模型" OR "ChatGPT" OR "Kimi" OR "豆包" OR "通义千问" after:[yesterday]
```

---

## 站点限定查询（Site-Specific）

### 36氪 AI
```
site:36kr.com AI OR 大模型 OR 人工智能 after:[yesterday]
```

### 机器之心
```
site:jiqizhixin.com after:[yesterday]
```

### 量子位
```
site:qbitai.com after:[yesterday]
```

### 微信公众号（辅助发现）
```
site:mp.weixin.qq.com "AI" OR "大模型" OR "人工智能" after:[yesterday]
```

### 知乎 AI 讨论
```
site:zhihu.com "AI" OR "大模型" OR "人工智能" after:[yesterday]
```

---

## 查询组合示例

### 国内每日综合
```
Query 1: "AI 新闻" OR "人工智能" OR "大模型" 最新 after:[yesterday]
Query 2: "国产大模型" OR "国内AI" OR "中国AI" after:[yesterday]
Query 3: site:36kr.com OR site:jiqizhixin.com OR site:qbitai.com AI after:[yesterday]
```

### 国内公司聚焦
```
Query 1: "百度AI" OR "通义千问" OR "腾讯AI" OR "华为AI" after:[yesterday]
Query 2: "智谱AI" OR "月之暗面" OR "DeepSeek" OR "豆包" after:[yesterday]
Query 3: "商汤" OR "科大讯飞" OR "零一万物" OR "MiniMax" after:[yesterday]
```

### 国内政策聚焦
```
Query 1: "AI监管" OR "人工智能政策" OR "算法备案" after:[week_ago]
Query 2: "AI算力" OR "智算中心" OR "国产芯片" after:[week_ago]
```

### 游戏美术聚焦
```
Query 1: "AI游戏" OR "AI NPC" OR "AI辅助游戏开发" after:[yesterday]
Query 2: "AI绘画" OR "ComfyUI" OR "Stable Diffusion" 最新 after:[yesterday]
Query 3: "AI视频生成" OR "AI 3D" OR "AI美术资产" after:[yesterday]
```

---

## 查询优化建议

1. **限制结果**: 搜索工具默认返回 10-15 条结果，通常足够
2. **优先最新**: 始终使用日期过滤确保新鲜内容
3. **来源多元**: 使用能覆盖不同类型来源的查询
4. **调整范围**: 结果太少则扩大日期范围或使用更宽泛的词
5. **验证时效**: 始终检查发布日期确保内容确实是最新的
