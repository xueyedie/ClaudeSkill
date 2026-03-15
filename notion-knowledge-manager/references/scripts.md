# 辅助脚本

## `scripts/index_hygiene.py`

这个脚本用于检查 `Knowledge Index` 的 CSV 导出文件，快速发现索引层面的结构问题。它现在是补充方案，不再是默认主流程。

它会重点检查：

- 缺失字段，如 `Domain`、`Parent Topic`、`Type`、`URL`
- `Domain` 是否超出允许值
- 是否把管理层对象误放进索引表
- 标题是否重复
- URL 是否重复
- 是否超过 `Review Cycle` 规定的复查周期

### 适合什么时候用

- 想离线快速做一次索引体检
- 当前环境没有足够的 Notion 数据查询能力
- 想在重整知识库前先看有哪些明显问题
- 想把人工巡检变成半自动流程

### 输入要求

输入文件应为 `Knowledge Index` 从 Notion 导出的 CSV 文件。

### 用法示例

如果本机有 Python，可运行：

```bash
python notion-knowledge-manager/scripts/index_hygiene.py knowledge-index.csv
```

输出 JSON：

```bash
python notion-knowledge-manager/scripts/index_hygiene.py knowledge-index.csv --format json
```

跳过复查周期检查：

```bash
python notion-knowledge-manager/scripts/index_hygiene.py knowledge-index.csv --skip-stale-review
```

### 输出说明

脚本会输出：

- 总行数
- 问题总数
- 按严重度统计的问题数
- 按问题类型统计的问题数
- 每条问题对应的标题、行号与说明

### 当前限制

- 它依赖 Notion 的 CSV 导出，而不是直接连 Notion API
- 当前环境里未检测到 `python` 命令，因此脚本未在本机完成运行验证
- 如果后续你希望直接连 Notion 做自动巡检，应优先使用 `inspection.md` 中描述的 MCP 巡检流程
