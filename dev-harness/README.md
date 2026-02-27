# /dev-harness 使用说明

基于 Anthropic [《Effective Harnesses for Long-Running Agents》](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 的通用项目跨 Session 开发工作流。

---

## 解决什么问题

AI Agent 每次新开 Session 都是"失忆"的。如果一个功能需要多次 Session 才能完成，Agent 会：
- 不知道上次做到哪了
- 重复做已经完成的工作
- 过早宣布项目完成

**Harness（工作流脚手架）** 通过三个持久化文件解决这个问题：

```
Session 1 ──写入进度──→  .agent/  ──读取进度──→  Session 2 ──写入──→ ...
```

| 文件 | 作用 |
|------|------|
| `feature-list.json` | 任务清单：做什么、做到哪了、什么依赖什么 |
| `progress.md` | 交接日志：每次 Session 做了什么、遇到什么问题 |
| `init.sh` | 环境检查：新 Session 开始前确认一切就绪 |

---

## 支持的项目类型

以下为常见支持类型（非完整列表，Agent 会根据实际文件自动判断）：

| 项目类型 | 标志文件 | 所需工具 |
|---------|---------|---------|
| Unity | `ProjectSettings/ProjectVersion.txt` | Unity Hub + Editor、Git |
| Godot | `project.godot` | Godot Engine、Git |
| Python | `pyproject.toml` / `setup.py` / `requirements.txt` | Python、pip/poetry/uv、Git |
| Node.js | `package.json` | Node.js、npm/yarn/pnpm、Git |
| 微信小程序 | `app.json` + `project.config.json` | 微信开发者工具、Node.js、Git |
| Rust | `Cargo.toml` | rustc、cargo、Git |
| Go | `go.mod` | Go、Git |
| Flutter | `pubspec.yaml` | Flutter SDK、Dart、Git |
| Java/Kotlin | `build.gradle` / `pom.xml` | JDK、Gradle/Maven、Git |
| C/C++ | `CMakeLists.txt` / `Makefile` | CMake/Make、编译器、Git |
| .NET/C# | `*.sln` / `*.csproj` | .NET SDK、Git |
| Ruby | `Gemfile` | Ruby、Bundler、Git |
| Elixir | `mix.exs` | Elixir、Erlang/OTP、Git |
| Swift | `Package.swift` | Swift 工具链、Git |
| PHP | `composer.json` | PHP、Composer、Git |

初始化时自动检测项目类型。未匹配已知类型时会主动探测构建系统标志文件，仍无法确定则询问用户。

---

## 命令用法

```bash
/dev-harness                  # 自动判断：没初始化 → 初始化；有待办 → 做下一个
/dev-harness my-todo-id       # 指定做某个 todo
/dev-harness init             # 强制进入初始化（或为已完成项目追加新功能）
/dev-harness replan           # 修改计划（新增/删除/调整 todo）
```

### 路由逻辑

```
/dev-harness
  │
  ├─ 参数是 "init"?      → 初始化模式
  ├─ 参数是 "replan"?    → 变更计划模式
  ├─ .agent/ 不存在?     → 初始化模式
  ├─ 有 pending todo?    → 开发模式（参数可指定 todo-id）
  └─ 全部 done?          → 提示追加新功能或调整计划
```

---

## 三种模式详解

### 1. 初始化模式

**触发条件**：项目没有 `.agent/` 目录，或使用 `/dev-harness init`

**做的事情**：
1. 自动检测项目类型、语言版本、运行时路径（不硬编码）
2. 确认所需工具已安装（未安装则暂停并提示）
3. 从用户需求或计划文件生成 todo 清单
4. 创建 `.agent/` 目录及三个核心文件
5. 修正 `.gitignore`（如有问题）
6. 提交 baseline

**安全保证**：只创建 `.agent/` 和检查 `.gitignore`，不删除或覆盖已有代码。禁止修改 `CLAUDE.md`。

**已有 .agent/ 时的行为**：
- 有未完成 todo → 拒绝重新初始化，引导使用开发模式
- 全部完成 → 提供「追加模式」（保留历史）或「归档重建」两个选择

### 2. 开发模式

**触发条件**：`.agent/` 存在且有 pending todo

**每次 Session 的流程**：

```
环境确认 → 环境检查 → 恢复上下文 → 选择 todo → 实现 → 构建验证 → 测试验证 → 更新进度 → 提交 → 报告
```

**核心原则**：
- 一次只做一个 todo
- 每次留下干净、可构建的状态
- 构建和测试通过后才提交
- 遵循项目特定的提交规则（记录在 progress.md 中）

**异常处理**：
- 构建/测试修不好 → 记录问题，不标记 done
- todo 太大/不合理 → 建议 `/dev-harness replan`
- 上下文即将耗尽 → 保存部分进度后退出

### 3. 变更计划模式

**触发条件**：`/dev-harness replan`

**支持的操作**：
- 新增 todo
- 删除 pending todo（检查依赖链）
- 修改 todo 描述/文件/依赖
- 拆分大 todo 为多个小 todo
- 调整优先级

**安全规则**：已完成的 todo 不可修改，所有变更需用户确认。

---

## 文件结构

初始化后项目中会多出：

```
项目根目录/
├── .agent/
│   ├── init.sh                    # 环境验证脚本
│   ├── feature-list.json          # Todo 清单
│   ├── progress.md                # 跨 Session 进度日志
│   └── test-results/              # 构建/测试输出（git 忽略）
└── CLAUDE.md                      # 项目规范（用户维护，Agent 不修改）
```

### feature-list.json 单条 Todo 结构

```json
{
  "id": "kebab-case-id",
  "phase": 1,
  "title": "人类可读的标题",
  "description": "具体做什么",
  "output_files": ["src/path/to/file"],
  "depends_on": ["other-id"],
  "requires_human": false,
  "requires_build_check": true,
  "test_command": null,
  "status": "pending",
  "completed_in_session": null,
  "notes": null
}
```

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识，kebab-case |
| `phase` | 阶段编号，用于分组 |
| `depends_on` | 依赖的 todo id 列表，这些必须 done 后才能开始 |
| `requires_human` | 需要在 GUI/IDE 中手工操作（如 Unity Editor 配置、微信开发者工具调试等） |
| `requires_build_check` | 完成后是否需要执行构建验证 |
| `test_command` | 对应的测试命令，无测试则 null |
| `status` | `pending` → `done` |

---

## 典型使用流程

### 全新项目

```
会话 1:  /dev-harness          → 自动初始化，生成 todo 清单
会话 2:  /dev-harness          → 自动选第一个 todo 开始开发
会话 3:  /dev-harness          → 自动选第二个 todo ...
会话 N:  /dev-harness          → 全部完成！
```

### 已有项目，新增功能

```
会话 1:  /dev-harness init     → 为已有项目搭建脚手架 + 生成新功能 todo
会话 2:  /dev-harness          → 开始开发
```

### 中途需要改计划

```
会话 N:  /dev-harness replan   → 新增/删除/拆分 todo
会话 N+1:/dev-harness          → 按新计划继续
```

### 指定做某个 todo

```
/dev-harness my-specific-todo-id
```

---

## 参考

- 原文：[Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Skill 位置：`.claude/skills/dev-harness/`
