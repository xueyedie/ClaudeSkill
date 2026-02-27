# 开发模式

连续执行 Todo，每完成一个自动继续下一个，直到需要停止。

### D-1: 环境检查

在运行任何命令之前，先读取 `.agent/progress.md` 顶部的项目信息，确认项目类型和所需工具。

然后用 AskUserQuestion 确认工具已就绪：

question: "即将运行环境检查，本项目类型为 {project_type}，需要以下工具：{tool_list}。请确认："
header: "环境确认"
options:
1. label: "已安装，继续执行 (Recommended)", description: "{tool_list} 均已安装并可用"
2. label: "需要安装或配置环境", description: "暂停执行，先安装相关工具再继续"

若用户选择"需要安装或配置"：
- 根据项目类型列出所需工具及简要安装说明
- **停止执行**，提示用户安装完成后重新运行 `/dev-harness`

若用户确认已安装，继续执行：

```bash
bash .agent/init.sh
```
失败则尝试修复，不能修复则停止报告。

### D-2: 恢复上下文

1. 读 CLAUDE.md（编码规范）
2. 读 `.agent/progress.md`
3. 读 `.agent/feature-list.json`

如果当前任务可能涉及之前已归档的功能，可去 `.agent/history/` 查找相关历史记录的 `summary.md`，按需深入读取对应的 `feature-list.json` 或 `progress.md`。正常情况下不读历史。

### D-3: 选择 Todo

- 有指定 todo-id → 选该 todo
- 否则 → 自动选第一个 pending 且 depends_on 全部 done 的 todo
- 无可选 todo → 全部完成，执行 **D-11 归档**

### D-4: 人工任务

`requires_human: true` → 告知用户需手工操作的内容，确认后标记 done，跳到 D-8。

### D-5: 实现

遵守 CLAUDE.md 全部编码规范。遵循项目已有的代码风格和架构模式。

### D-6: 构建验证

若 todo 的 `requires_build_check` 为 true，执行 `.agent/progress.md` 项目信息区块中记录的**构建命令**。

> **命令来源优先级**：progress.md 中明确记录的命令 > 下方参考表 > 向用户询问。
> 若 progress.md 中构建命令为"无"，跳过此步。

**常见项目类型构建方式参考**（非完整列表）：
- **Unity**：先检测 Unity Editor 是否正在运行（Windows: `tasklist /FI "IMAGENAME eq Unity.exe" /NH`；macOS/Linux: `pgrep -f Unity`）：
  - **Editor 运行中** → 使用 `dotnet build *.sln`（项目根目录的 `.sln` 文件）编译，搜索输出中的 `error CS`。前提：`.sln`/`.csproj` 必须存在（Unity 打开过项目即自动生成）且已安装 .NET SDK
  - **Editor 未运行** → 使用 Unity batch-mode 编译，搜索 `error CS`
- **Godot**：`godot --headless --export-debug` 或项目约定方式
- **Python**：无编译步骤 / `python -m py_compile` / `mypy`（按项目约定）
- **Node.js**：`npm run build` / `yarn build` / `pnpm build`
- **Rust**：`cargo build`
- **Go**：`go build ./...`
- **Flutter**：`flutter build`
- **Java (Gradle)**：`./gradlew build` / `gradle build`
- **Java (Maven)**：`mvn compile`
- **C/C++ (CMake)**：`cmake --build build/`
- **C/C++ (Make)**：`make`
- **.NET/C#**：`dotnet build`
- **其他**：按 progress.md 记录执行；若无记录，向用户询问后补记

有错 → 修复并重新构建，循环至通过。

### D-7: 测试验证（如有 test_command）

若 todo 的 `test_command` 不为 null，执行对应测试命令。若 todo 未指定但 progress.md 中记录了项目级测试命令，也执行。

> **命令来源优先级**：todo 的 `test_command` > progress.md 中项目级测试命令 > 下方参考表 > 向用户询问。

**常见项目类型测试方式参考**（非完整列表）：
- **Unity**：先检测 Unity Editor 是否正在运行：
  - **Editor 运行中** → 提示用户在 Editor 中运行测试（Window → General → Test Runner），等待用户确认测试结果后继续
  - **Editor 未运行** → `-runTests -testPlatform EditMode -testFilter "{test_class}"`（不加 `-quit`；无 `Assert.DoesNotThrowAsync`，用 `Assert.DoesNotThrow(() => task.GetAwaiter().GetResult())`）
- **Godot**：GUT / GdUnit 框架
- **Python**：`pytest` / `python -m unittest`
- **Node.js**：`npm test` / `jest` / `vitest`
- **Rust**：`cargo test`
- **Go**：`go test ./...`
- **Flutter**：`flutter test`
- **Java (Gradle)**：`./gradlew test`
- **Java (Maven)**：`mvn test`
- **C/C++**：`ctest` / `make test`
- **.NET/C#**：`dotnet test`
- **其他**：按 progress.md 记录执行；若无记录，向用户询问后补记

失败 → 修复并重跑。

### D-8: 更新进度

1. **progress.md** 追加 Session 条目（编号递增）
2. **feature-list.json** 标记 `status: "done"` + `completed_in_session`

**禁止修改 CLAUDE.md** — 它是项目规范文件，不记录进度。

### D-9: 提交

```bash
# 1. 检查所有变更
git status

# 2. 添加实现文件（按 todo 的 output_files 及实际变更）
git add {changed_files}

# 3. 进度文件
git add .agent/progress.md .agent/feature-list.json

# 4. 禁止提交构建产物和临时文件（应已在 .gitignore 中排除）
```

提交消息：`feat({phase/layer}): {todo-title}`

**提交注意事项以 `.agent/progress.md` 项目信息区块中的记录为准。** 以下为常见参考：
- **Unity**：.cs/.uxml/.uss/.asmdef 文件必须连同 .meta 一起提交；禁止手工创建/修改 .meta；禁止提交 Library/、Temp/、obj/
- **Godot**：.import/（Godot 3）或 .godot/（Godot 4）不提交
- **Node.js**：禁止提交 node_modules/
- **Python**：禁止提交 __pycache__/、.venv/、*.pyc
- **Rust**：禁止提交 target/
- **Java/Kotlin**：禁止提交 build/、.gradle/、*.class
- **C/C++**：禁止提交 build/、*.o、*.a、二进制产物
- **.NET/C#**：禁止提交 bin/、obj/
- **其他**：遵循 .gitignore 规则；若 progress.md 中有项目特定记录则按其执行

### D-10: 报告 + 判断是否继续

输出完成的 Todo、产出文件、构建/测试结果、总进度（done/total）。

然后判断：

**自动继续（条件全部满足）：**
1. 还有 pending todo 且依赖已满足
2. 下一个 todo 的 `requires_human` 为 false
3. 当前 todo 构建和测试全部通过

→ 输出 `--- 自动继续: {next_todo_title} ---`，回到 D-3。无需重复 D-1、D-2。

**停止并提醒用户开新 session（任一满足）：**
1. 上下文即将耗尽（对话已经很长、已完成多个 todo）
2. 下一个 todo 需要人工操作（`requires_human: true`）
3. 当前 todo 有未解决的构建/测试错误
4. 遇到需要用户决策的设计问题

→ 输出停止原因、已完成的 todo 列表、下一个推荐 Todo（如有），并提示用户：`请开新 session 执行 /dev-harness 继续`。

**所有 todo 已完成 → 执行 D-11 归档。**

### D-11: 归档（仅当本次 plan 全部 todo 完成时执行）

将当前 plan 的 `feature-list.json` 和 `progress.md` 归档到历史目录：

1. **确定归档目录名**：`.agent/history/{YYYY-MM-DD}_{NNN}_{plan-slug}/`
   - `YYYY-MM-DD`：归档日期
   - `NNN`：三位数递增编号（检查 history/ 下已有目录，取最大编号 +1）
   - `plan-slug`：2~4 个英文单词概括本次 plan（如 `phase1-6-core`、`phase7-ui-redesign`）

2. **移动文件**：
   ```bash
   mkdir -p .agent/history/{dirname}
   mv .agent/feature-list.json .agent/history/{dirname}/
   mv .agent/progress.md .agent/history/{dirname}/
   ```

3. **生成 summary.md**：在归档目录内创建，内容为：
   ```markdown
   # {plan 简述}
   - 日期：{归档日期}
   - Todo 总数：{total}（done: {done}, human: {human}）
   - 关键产出：{列出主要 output_files 或模块名}
   - 备注：{简要说明，1~2 句}
   ```

4. **重置工作区**：创建空的 `.agent/feature-list.json`（`[]`）和空的 `.agent/progress.md`

5. **提交归档**：
   ```bash
   git add .agent/history/{dirname}/ .agent/feature-list.json .agent/progress.md
   git commit -m "archive: {plan-slug} 全部完成，归档至 history"
   ```

6. **报告**：输出归档完成信息，提示用户可用 `/dev-harness init` 开始新 plan。

### 异常处理

| 情况 | 处理 |
|------|------|
| 构建/测试修不好 | 记录 progress.md，不标记 done，**停止**，告知用户 |
| Todo 与需求不符 | **停止**，建议 `/dev-harness replan` |
| 发现需要额外 Todo | 记录 progress.md，建议 `/dev-harness replan` |
| Todo 太大 | 记录部分进展，建议 `/dev-harness replan` 拆分 |
| 上下文即将耗尽 | 立即保存进度，即使未完成也记录部分进展，**停止**，提醒开新 session |
