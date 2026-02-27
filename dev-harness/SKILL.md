---
name: dev-harness
description: 通用项目跨 Session Agent 工作流脚手架，支持 Python/Node.js/Unity/Godot/Rust/Go/Flutter/微信小程序等。
argument-hint: [todo-id | replan | init]
disable-model-invocation: true
---

# Dev Agent 工作流

查看 `<command-message>` 标签中 "dev-harness" 后面是否有文本参数。

## 有参数 → 直接读取模式文件执行

| 参数 | 动作 |
|------|------|
| `init` | Read `.claude/skills/dev-harness/modes/init.md`，按步骤执行 |
| `replan` | Read `.claude/skills/dev-harness/modes/replan.md`，按步骤执行 |
| 其他值 | Read `.claude/skills/dev-harness/modes/dev.md`，将参数作为 todo-id 执行 |

## 没有参数 → 立即调用 AskUserQuestion

不要读取任何文件。不要运行任何命令。不要做任何分析。你的第一个工具调用必须是 AskUserQuestion：

question: "选择要执行的操作："
header: "模式"
options:
1. label: "继续开发 (Recommended)", description: "自动选择下一个待办 todo 并执行"
2. label: "初始化 (init)", description: "为项目搭建工作流脚手架或追加新功能"
3. label: "变更计划 (replan)", description: "修改/新增/删除/拆分待办 todo"
4. label: "取消", description: "不执行任何操作"

等待用户回答后：
- 继续开发 → Read `.claude/skills/dev-harness/modes/dev.md`，按步骤执行
- 初始化 → Read `.claude/skills/dev-harness/modes/init.md`，按步骤执行
- 变更计划 → Read `.claude/skills/dev-harness/modes/replan.md`，按步骤执行
- 取消 → 回复"已取消"
- 用户在 Other 中输入了文本 → 作为 todo-id，Read `.claude/skills/dev-harness/modes/dev.md` 执行
