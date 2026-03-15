---
name: notion-knowledge-manager
description: 用于管理基于 Notion 的结构化知识库。适用于以下场景：用户给出链接、Markdown、原始笔记并希望整理后放入合适主题；希望为页面补充或更新 Knowledge Index 索引；希望重整知识库的分类、命名、父子结构；希望查找某个主题下的相关文章并返回链接；希望删除某篇文章并清理相关索引与关联关系；希望设计或执行 AI 辅助的知识库管理流程。该 skill 默认优先节省上下文，只在需要时读取知识库规则和现有内容，不会在每个新对话里无差别重扫整个知识库。Use when user mentions Notion knowledge management, Knowledge Index maintenance, or asks to run /notion-knowledge-manager command. Trigger command: /notion-knowledge-manager.
metadata:
  short-description: 管理 Notion 知识库的新增、索引、检索、重组、删除清理与 AI 协同流程
---

## 命令

### `/notion-knowledge-manager`

用这个斜杠命令直接进入本 skill，处理知识入库、索引维护、结构调整、巡检和删除清理。

**使用方式**: 输入 `/notion-knowledge-manager`，然后继续描述你的目标，例如“把这个链接整理进 AI 主题”或“巡检一个 Knowledge Index”。

# Notion 知识库管理

这个 skill 用来管理一套已经有明确结构的 Notion 知识库，尤其适合这类工作：

- 给一个链接、Markdown 或原始内容，整理并归入合适主题
- 创建或更新 `Knowledge Index` 里的索引条目
- 调整知识库结构、分类方式、命名方式
- 查询某个主题下的相关笔记并返回链接
- 删除指定文章，并清理相关链接、索引和结构
- 为后续 AI 自动化管理设计工作流

## 一、先理解这套知识库的两层结构

处理这套知识库时，始终要把对象分成两层。

### 内容层

这是 `Knowledge Index` 真正要管理的内容对象，例如：

- `AI`
- `游戏`
- 各类手册页
- 各类 guide、diagram、case、note、source 页面

### 管理层

这是知识库的基础设施，不是普通内容条目：

- `Knowledge Hub`
- `Knowledge Index`
- `Inbox`
- `Index Archive`

默认规则：

- 管理层对象用于导航、收件、归档、索引控制
- 不要把管理层对象当成普通知识内容来处理
- 除非用户明确要求，否则不要把它们作为普通内容条目长期纳入索引表

## 二、第一步：选择最小上下文加载级别

这个 skill 的核心原则之一，是**不要浪费上下文**。

处理任务前，先判断当前只需要加载多少信息。

### Level 0：不额外加载

适用场景：

- 当前对话里已经读过相关规则和页面
- 用户只是继续上一个操作

执行方式：

- 不重新读取规则页
- 不重新扫描知识库

### Level 1：只读取规则

适用场景：

- 这是一个新对话
- 任务涉及索引、分类、管理规则
- 你不确定这套知识库目前怎么定义内容层和管理层

执行方式：

- 先读取 `Knowledge Index 使用说明`
- 如果任务涉及结构，再按需读取 `Knowledge Hub`

### Level 2：只读取目标主题相关内容

适用场景：

- 任务集中在一个主题或一篇文章
- 属于新增、查询、局部更新

执行方式：

- 搜索标题、主题词或分支名称
- 只 fetch 相关页面和索引行

### Level 3：读取结构上下文

适用场景：

- 用户要重整结构
- 用户要删除内容
- 用户要调整一个分支的组织方式

执行方式：

- 读取相关 topic hub
- 读取对应索引行
- 读取可能受影响的关联页面

总规则：

- 默认不要全库扫描
- 同一对话里，已经加载过的规则页不要重复读取
- 只有当任务真的需要时，才升级上下文加载级别

如需更细规则，读取 [references/context-policy.md](references/context-policy.md)。

## 三、触发场景

当用户出现下面这些表达时，应该触发本 skill：

- “帮我把这个链接整理进知识库”
- “把这段 Markdown 加进我的 Notion 笔记”
- “帮我放到合适主题下面”
- “帮我加索引”
- “帮我整理一下知识库结构”
- “帮我重新梳理 AI 主题/游戏主题”
- “查一下这个主题下有哪些相关文章”
- “把相关链接发给我”
- “删除这篇文章并清理相关内容”
- “帮我设计 AI 管理知识库的流程”
- “帮我维护 Knowledge Index”
- “帮我 review 一下笔记框架”
- “帮我做一次知识库体检”
- “帮我巡检索引问题”
- “帮我出一份每周知识库巡检报告”

## 四、工作流 1：新增笔记

适用输入：

- 一个 URL
- 一段 Markdown
- 一段原始笔记
- 一篇文章内容
- 一个需要吸收入库的资料

步骤：

1. 读取来源内容
2. 如有必要，先读取规则页
3. 判断它属于哪个 `Domain`
4. 判断它应该放到哪个 `Parent Topic`
5. 搜索现有 canonical 页面和相关页面
6. 判断应该：
   - 补充到已有页面
   - 新建为子页面
   - 新建为新的主题页或独立页
7. 更新或创建内容页
8. 更新或创建 `Knowledge Index` 索引行
9. 只在需要时补 `Related Pages`、`Source Pages`、`Type` 等字段
10. 向用户说明最终放置位置和原因

优先原则：

- 能归入已有 canonical 页面时，优先归入
- 只有在内容明显独立、继续塞进旧页会造成混乱时，才新建页面

## 五、工作流 2：重整知识库结构

适用场景：

- 用户要求重整分类
- 用户要求调整命名
- 用户要求优化某个主题分支
- 用户希望重新梳理框架

步骤：

1. 使用 Level 3 上下文加载
2. 除非用户明确要求，否则只处理目标分支，不做全库重构
3. 检查以下问题：
   - 命名不一致
   - 页面重复
   - 缺少 canonical 页面
   - `Parent Topic` 不合理或缺失
   - `Domain` 缺失
   - `Related Pages` 失真
4. 如果变更范围较大，先给出简短方案
5. 按用户确认执行更新
6. 同步更新索引

## 六、工作流 3：查找相关文章

适用场景：

- 用户要找某个主题相关的笔记
- 用户想查看当前问题的相关资料
- 用户要相关页面链接

步骤：

1. 先查 `Knowledge Index`
2. 优先返回：
   - canonical 条目
   - 高 `Confidence` 条目
   - 同一 `Domain`、同一 `Parent Topic` 下的条目
3. 仅当标题和索引信息不足以判断时，再读取正文
4. 返回链接时附一行简短说明，解释为什么相关

## 七、工作流 4：删除文章并清理

适用场景：

- 用户明确要求删除某篇文章
- 用户希望删除并整理相关结构

步骤：

1. 使用 Level 3 上下文加载
2. 先判断目标是内容层对象还是管理层对象
3. 读取目标页面和对应索引行
4. 找出引用它的页面、相关索引字段和结构关系
5. 只有在用户明确要求时才删除内容页
6. 同步删除或更新索引行
7. 清理 `Related Pages`、来源引用和附近结构
8. 向用户说明改动范围

注意：

- 不要把日常内容删除操作扩展到管理层页面
- 如果删除会影响结构枢纽页、子页面或数据库，需要先停下来确认

## 八、Knowledge Index 的使用原则

`Knowledge Index` 是知识库的控制面，不是正文阅读区。

它主要用于回答这些问题：

- 这条知识是什么
- 它属于哪里
- 它是不是正式主版本
- 它靠不靠谱
- 它来自哪里
- 它和哪些页面有关
- 它什么时候该复查

只有当任务涉及分类、索引、清理、复查时，才需要细读索引规则。

如需字段和决策规则，读取 [references/index-rules.md](references/index-rules.md)。

## 九、回复风格要求

执行本 skill 时：

- 明确告诉用户内容被放到了哪里
- 用一句话说明为什么这么分类
- 不要冗长复述已经在当前对话中确认过的规则
- 优先做小而准确的改动，不要默认大规模重构
- 当任务影响面较大时，先压缩成简短方案再执行

## 十、什么时候读取额外参考文件

- 判断要不要重新加载上下文时：读 [references/context-policy.md](references/context-policy.md)
- 判断索引字段怎么填、管理层对象是否该入索引时：读 [references/index-rules.md](references/index-rules.md)
- 处理新增、重整、查询、删除等较复杂任务时：读 [references/workflows.md](references/workflows.md)
- 处理每周巡检或健康报告时：读 [references/weekly-inspection-procedure.md](references/weekly-inspection-procedure.md)

## 十一、索引体检

当任务偏向“批量巡检”而不是单篇内容处理时，优先读取 [references/inspection.md](references/inspection.md)。

默认原则：

- 优先使用 Notion MCP 直接做巡检
- 只有在当前工具链无法有效覆盖时，才退回 CSV 脚本方案

当前配套：

- `references/inspection.md`
  - 说明如何直接读取 `Knowledge Index` 做体检
  - 说明在什么情况下退回 CSV 方案
- `assets/weekly-hygiene-report-template.md`
  - 每周巡检完成后可直接套用的报告模板
- `scripts/index_hygiene.py`
  - CSV 补充方案
  - 用于离线批量检查缺失字段、重复标题、重复 URL、误入索引的管理层对象、复查过期项
