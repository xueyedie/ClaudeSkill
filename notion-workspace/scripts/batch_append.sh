#!/bin/bash
# 将大 MD 文件分批追加到 Notion 页面（每批最多 80 行，留余量）
# 用法: batch_append.sh <page_id> <md_file_path>
#
# 重要：不得在 ``` 围栏未闭合处切断，否则 notion_cli 会把后续正文误解析成
# 多段代码块/段落，Notion 客户端易出现「正在加载 Plain Text 代码」与金字塔残缺。
# 实际切分由同目录 md_batch_append.py 完成。

PAGE_ID="$1"
MD_FILE="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$PAGE_ID" ] || [ -z "$MD_FILE" ]; then
  echo "Usage: batch_append.sh <page_id> <md_file_path>"
  exit 1
fi

exec python3 "$HERE/md_batch_append.py" "$PAGE_ID" "$MD_FILE" --batch-lines 80 --sleep 0.5
