# 变更计划模式

修改 feature-list.json 中的 pending todo。

### R-1: 展示当前状态

读取 feature-list.json，统计 done/pending/human 数量。

如果 feature-list.json 为空或不存在，提示用户先用 `/dev-harness init` 创建 plan。

### R-2: 执行变更

支持的操作：

| 操作 | 说明 |
|------|------|
| 新增 | 追加 pending todo，检查 id 不重复、依赖无循环 |
| 删除 | 只删 pending todo，检查无其他 todo 依赖它 |
| 修改 | 只改 pending todo 的 description/output_files/depends_on 等 |
| 拆分 | pending todo → 多个小 todo，依赖关系自动调整 |
| 调整优先级 | 改 phase 或 depends_on |

如需参考已归档的历史 plan，可查阅 `.agent/history/` 中相关的 `summary.md`。

**规则：已完成的 todo 不可修改（历史记录）。所有变更需用户确认后执行。**

### R-3: 保存 + 提交

1. 修改 feature-list.json
2. 在 progress.md 追加变更记录（日期、操作、原因）
3. `git commit -m "replan: {变更描述}"`

**禁止修改 CLAUDE.md** — 它是项目规范文件，不记录进度。
