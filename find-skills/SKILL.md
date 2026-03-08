---
name: find-skills
user-invocable: true
description: 当用户询问"如何做 X"、"查找 X 的 skill"、"有没有能做 X 的 skill"，或者希望扩展 Agent 能力时，使用此 skill 帮助用户发现并安装 agent skill。
---

# 查找 Skills

此 skill 帮助你从开放 agent skill 生态系统中发现并安装 skill。

## 何时使用此 Skill

当用户出现以下情况时使用：

- 询问"如何做 X"，而 X 可能是某个已有 skill 覆盖的常见任务
- 说"帮我找 X 的 skill"或"有没有 X 的 skill"
- 询问"你能做 X 吗"，而 X 是某种专项能力
- 希望扩展 agent 的能力
- 想搜索工具、模板或工作流
- 提到希望在某个特定领域（设计、测试、部署等）获得帮助

## 什么是 Skills CLI？

Skills CLI（`npx skills`）是开放 agent skill 生态系统的包管理器。Skill 是模块化的包，通过专业知识、工作流和工具来扩展 agent 的能力。

**核心命令：**

- `npx skills find [关键词]` - 交互式搜索或按关键词搜索 skill
- `npx skills add <包名>` - 从 GitHub 或其他来源安装 skill
- `npx skills check` - 检查 skill 更新
- `npx skills update` - 更新所有已安装的 skill

**浏览 skill：** https://skills.sh/

## 额外的精选搜索来源

如果你想要一个额外的精选目录来发现 skill（尤其是 Claude/agent 向的 skill 包），也可以使用：

- **Awesome Claude Skills（网页目录）：** https://awesomeclaude.ai/awesome-claude-skills

用途：
- 浏览分类和精选条目
- 发现候选仓库/包，然后通过 `npx skills add <owner/repo@skill>` 安装

## 如何帮助用户查找 Skill

### 第一步：理解用户需求

当用户寻求帮助时，识别以下信息：

1. 所属领域（如 React、测试、设计、部署）
2. 具体任务（如编写测试、创建动画、审查 PR）
3. 该任务是否足够常见，以至于可能已有对应 skill

### 第二步：搜索 Skill

使用相关关键词运行查找命令：

```bash
npx skills find [关键词]
```

示例：

- 用户问"如何让我的 React 应用更快？" → `npx skills find react performance`
- 用户问"能帮我做 PR review 吗？" → `npx skills find pr review`
- 用户说"我需要生成 changelog" → `npx skills find changelog`

命令返回结果示例：

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第二步（备选）：CLI 结果较少时，搜索精选目录

如果 `npx skills find` 没有找到合适的结果，也可以查看：

- https://awesomeclaude.ai/awesome-claude-skills

找到合适条目后，将其映射到可安装的包/仓库（如有），再执行 `npx skills add ...`。

### 第三步：向用户展示选项

找到相关 skill 后，向用户展示：

1. Skill 名称及其功能
2. 可运行的安装命令
3. 在 skills.sh 上了解更多的链接（如果是从精选目录找到的，也附上对应链接）

示例回复：

```
我找到了一个可能有帮助的 skill！"vercel-react-best-practices" skill 提供了
来自 Vercel 工程团队的 React 和 Next.js 性能优化指南。

安装命令：
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第四步：提议帮助安装

如果用户希望继续，可以帮他们安装：

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` 表示全局安装（用户级别），`-y` 跳过确认提示。

## 常见 Skill 分类

搜索时可参考以下常见分类：

| 分类     | 示例关键词                               |
| -------- | ---------------------------------------- |
| Web 开发 | react, nextjs, typescript, css, tailwind |
| 测试     | testing, jest, playwright, e2e           |
| DevOps   | deploy, docker, kubernetes, ci-cd        |
| 文档     | docs, readme, changelog, api-docs        |
| 代码质量 | review, lint, refactor, best-practices   |
| 设计     | ui, ux, design-system, accessibility     |
| 效率提升 | workflow, automation, git                |

## 高效搜索技巧

1. **使用具体关键词**："react testing" 比单独的 "testing" 效果更好
2. **尝试近义词**：如果 "deploy" 没有结果，试试 "deployment" 或 "ci-cd"
3. **查看热门来源**：
   - https://skills.sh/
   - `vercel-labs/agent-skills`
   - **Awesome Claude Skills：** https://awesomeclaude.ai/awesome-claude-skills

## 未找到 Skill 时

如果没有找到相关 skill：

1. 告知用户未找到现有 skill
2. 提议直接用通用能力帮助完成任务
3. 建议用户通过 `npx skills init` 创建自己的 skill

示例：

```
我搜索了与 "xyz" 相关的 skill，但没有找到匹配项。
我仍然可以直接帮你完成这个任务！需要我继续吗？

如果这是你经常需要做的事情，可以创建自己的 skill：
npx skills init my-xyz-skill
```