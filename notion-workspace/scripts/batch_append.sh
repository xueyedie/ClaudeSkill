#!/bin/bash
# 将大 MD 文件分批追加到 Notion 页面（每批最多 80 行，留余量）
# 用法: batch_append.sh <page_id> <md_file_path>

PAGE_ID="$1"
MD_FILE="$2"
BATCH_SIZE=80
CLI="/Users/bot/.openclaw/workspace/skills/notion-workspace/scripts/notion_cli.py"

if [ -z "$PAGE_ID" ] || [ -z "$MD_FILE" ]; then
  echo "Usage: batch_append.sh <page_id> <md_file_path>"
  exit 1
fi

TOTAL_LINES=$(wc -l < "$MD_FILE")
echo "File: $MD_FILE ($TOTAL_LINES lines)"

START=1
BATCH=1
while [ $START -le $TOTAL_LINES ]; do
  END=$((START + BATCH_SIZE - 1))
  CHUNK=$(sed -n "${START},${END}p" "$MD_FILE")
  
  if [ -z "$CHUNK" ]; then
    START=$((END + 1))
    continue
  fi
  
  echo "Appending batch $BATCH (lines $START-$END)..."
  python3 "$CLI" append-text "$PAGE_ID" --content "$CHUNK"
  
  if [ $? -ne 0 ]; then
    echo "ERROR: Batch $BATCH failed at lines $START-$END"
    exit 1
  fi
  
  START=$((END + 1))
  BATCH=$((BATCH + 1))
  sleep 0.5
done

echo "Done! Appended $((BATCH - 1)) batches."
