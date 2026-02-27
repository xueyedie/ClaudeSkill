# 初始化模式

为项目搭建工作流脚手架，或在已有基础上开始新 plan。

**安全保证：只创建/修改 `.agent/` 目录，绝不删除或覆盖已有代码。禁止修改 `CLAUDE.md`。**

### I-1: 获取需求（最先执行）

立即提示用户输入需求，不要做任何其他事情。输出如下提示：

> 请描述你的需求（功能、目标、或粘贴计划文档），我会为你拆分为可执行的 Todo 清单。

等待用户输入后，再继续后续步骤。

如果当前需求涉及之前已归档的功能，可查阅 `.agent/history/` 中相关的 `summary.md` 获取上下文。

### I-2: 检查是否需要先归档

如果 `.agent/feature-list.json` 存在且不为空（`[]`）：
- **有 pending todo** → 警告用户还有未完成任务，建议先用开发模式完成或 replan 清理，确认后再继续
- **全部 done** → 先执行归档（参照 dev.md 的 D-11 步骤），再继续初始化

### I-3: 项目类型检测 + 环境确认（禁止硬编码）

#### 第一步：自动检测项目类型

扫描项目根目录中的标志文件，确定项目类型。以下为常见参考表（**不是完整列表**，Agent 应根据实际文件判断）：

| 项目类型 | 标志文件 | 所需工具 |
|---------|---------|---------|
| Unity | `ProjectSettings/ProjectVersion.txt` | Unity Hub + 对应版本 Editor、Git |
| Godot | `project.godot` | Godot Engine、Git |
| Python | `pyproject.toml` / `setup.py` / `requirements.txt` / `Pipfile` | Python、包管理器（pip/poetry/uv）、Git |
| Node.js | `package.json`（且无小程序标志） | Node.js、包管理器（npm/yarn/pnpm）、Git |
| 微信小程序 | `app.json` + `project.config.json` | 微信开发者工具、Node.js、Git |
| Rust | `Cargo.toml` | Rust 工具链（rustc、cargo）、Git |
| Go | `go.mod` | Go、Git |
| Flutter | `pubspec.yaml` | Flutter SDK、Dart、Git |
| Java/Kotlin (Gradle) | `build.gradle` / `build.gradle.kts` | JDK、Gradle/Wrapper、Git |
| Java (Maven) | `pom.xml` | JDK、Maven、Git |
| C/C++ (CMake) | `CMakeLists.txt` | CMake、编译器（gcc/clang/MSVC）、Git |
| C/C++ (Make) | `Makefile`（且无其他构建系统标志） | make、编译器（gcc/clang）、Git |
| Ruby | `Gemfile` | Ruby、Bundler、Git |
| Elixir | `mix.exs` | Elixir、Erlang/OTP、Git |
| Swift (SPM) | `Package.swift` | Swift 工具链、Git |
| iOS/macOS | `*.xcodeproj` / `*.xcworkspace` | Xcode、CocoaPods/SPM、Git |
| Android | `settings.gradle` + `app/build.gradle` | Android SDK、JDK、Gradle、Git |
| .NET/C# | `*.sln` / `*.csproj`（非 Unity） | .NET SDK、Git |
| PHP (Composer) | `composer.json` | PHP、Composer、Git |
| Zig | `build.zig` | Zig、Git |

若检测到多种标志文件（混合项目），列出所有检测到的类型。

#### 未匹配已知类型时的兜底探测

若未匹配上表任何类型，**不要直接标记为"通用项目"**，而是执行以下探测：

1. **扫描构建系统标志**：在根目录及一级子目录查找 `Makefile`、`Justfile`、`Taskfile.yml`、`build.sh`、`Dockerfile`、`docker-compose.yml` 等
2. **扫描语言标志**：查找源代码文件扩展名分布（`.py`、`.js`、`.ts`、`.go`、`.rs`、`.java`、`.cs`、`.cpp` 等），推断主要语言
3. **读取 README/docs**：如果有 `README.md`，快速扫描其中是否提及安装步骤、构建命令、开发环境要求

若探测后仍无法确定，用 AskUserQuestion 向用户确认：

question: "无法自动识别项目类型。请提供以下信息："
header: "项目信息"
options:
1. label: "我来说明", description: "告诉 Agent 项目类型、所需工具、构建和测试命令"
2. label: "跳过，仅需 Git", description: "当作通用项目处理，后续手动补充构建/测试信息"

若用户选择"我来说明"，等待用户输入项目类型、构建命令、测试命令、所需工具等信息，记录到 progress.md。

#### 第二步：环境确认

用 AskUserQuestion 确认工具已安装：

question: "检测到项目类型：{detected_type}。需要以下工具：{tool_list}。请确认："
header: "环境确认"
options:
1. label: "已安装，继续 (Recommended)", description: "{tool_list} 均已安装并可用"
2. label: "需要安装或配置", description: "暂停执行，先安装相关工具"

若用户选择"需要安装或配置"：
- 根据项目类型列出所需工具及简要安装说明
- **停止执行**，等用户安装完成后重新运行 `/dev-harness init`

#### 第三步：检测环境详情

若用户确认已安装，继续检测：

| 项目 | 方式 |
|------|------|
| 项目根目录 | `git rev-parse --show-toplevel` |
| 语言/框架版本 | 从项目配置文件读取（如 `ProjectVersion.txt`、`pyproject.toml`、`package.json` 的 `engines` 等） |
| 运行时/编译器路径 | `which` / `command -v` / 平台特定路径检测 |
| 包管理器 | 检测 lock 文件确定（如 `poetry.lock` → poetry、`yarn.lock` → yarn、`pnpm-lock.yaml` → pnpm） |

环境检测结果记录到 `.agent/progress.md` 项目信息区块，供后续 session 复用。

**项目特定检测**（按需，以下为常见参考，非完整列表）：
- **Unity**：从 `ProjectVersion.txt` 读版本 → 拼接 Editor 二进制路径 → 确认 C# 版本（2021.2+ → C# 9，禁止 file-scoped namespace）
- **Python**：检测虚拟环境（.venv/venv）、Python 版本、包管理器
- **Node.js**：检测 node 版本、包管理器版本、是否已 install
- **Godot**：从 `project.godot` 读版本 → 检测 Godot 二进制路径
- **Rust**：`rustc --version`、`cargo --version`
- **Go**：`go version`
- **Flutter**：`flutter --version`、`dart --version`
- **Java/Kotlin**：`java -version`、`gradle --version` 或 `./gradlew --version`、`mvn --version`
- **C/C++**：`cmake --version`、`gcc --version` / `clang --version` / `cl`
- **.NET/C#**：`dotnet --version`
- **Ruby**：`ruby --version`、`bundle --version`
- **Elixir**：`elixir --version`、`mix --version`
- **微信小程序**：检测开发者工具 CLI 路径
- **其他/通用**：对在第一步中检测到的工具逐一运行 `which`/`command -v` 确认可用

### I-4: 拆分需求为 Todo

将用户在 I-1 中提供的需求拆分为原子 Todo（每个 ≈ 一个 Session 工作量），向用户展示 Todo 清单并确认。

### I-5: 创建文件

**`.agent/feature-list.json`** — Todo 数组：
```json
{
  "id": "kebab-case-id",
  "phase": 1,
  "title": "标题",
  "description": "做什么、文件路径、注意事项",
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

**`.agent/init.sh`** — 环境验证脚本（如已存在则保留，只在首次初始化时创建）：
- 根据检测到的项目类型生成对应检查项：
  - 通用：Git、项目根目录、.agent/ 文件完整性
  - 项目特定：运行时/编译器可执行、包管理器可用、关键目录/文件存在
- 输出 Todo 统计
- 全部通过 exit 0，否则 exit 1

**`.agent/progress.md`** — 进度日志，顶部必须包含以下项目信息区块（供后续 session 直接读取）：

```markdown
## 项目信息
- 项目类型：{detected_type}
- 语言/框架版本：{version_info}
- 运行时路径：{runtime_path}
- 包管理器：{package_manager}
- 构建命令：{build_command}（无则填"无"）
- 测试命令：{test_command}（无则填"无"）
- 所需工具：{tool_list}
- 提交注意事项：{commit_rules}（如 Unity 的 .meta 规则、Node 的 node_modules 等）
```

底部为 Session History 区块。

### I-6: 检查 .gitignore

**禁止修改 CLAUDE.md** — 它是项目规范文件，由用户维护，不由 Agent 修改。

以下为 .gitignore 检查：

- 确保 `.agent/` 被追踪
- 添加 `.agent/test-results/*.txt` 和 `.agent/test-results/*.xml` 排除
- 检查项目特定的忽略规则是否合理，常见遗漏（参考，非完整列表）：
  - Unity：`Library/`、`Temp/`、`obj/`、`Logs/`；`Packages/` 整体排除应改为仅排除 `Packages/packages-lock.json`
  - Node.js：`node_modules/`、`dist/`
  - Python：`__pycache__/`、`*.pyc`、`.venv/`、`*.egg-info/`
  - Rust：`target/`
  - Go：无特殊（二进制文件名加入忽略即可）
  - Godot：`.godot/`（Godot 4）/ `.import/`（Godot 3）
  - Flutter：`.dart_tool/`、`build/`
  - Java/Kotlin：`build/`、`.gradle/`、`*.class`
  - C/C++：`build/`、`*.o`、`*.a`、`*.so`、`*.dylib`
  - .NET/C#：`bin/`、`obj/`
  - Ruby：`vendor/bundle/`
  - PHP：`vendor/`
  - 其他：根据检测到的构建产物目录和临时文件模式，确保已被忽略

### I-7: 提交 + 报告

提交 `.agent/` + `.gitignore`（如有变更），输出初始化报告。
