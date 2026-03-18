#!/usr/bin/env python3
"""Minimal Notion CLI for the OpenClaw workspace skill.

Uses only Python stdlib so it can run in a bare environment.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from typing import Any


NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = os.environ.get("NOTION_API_VERSION", "2022-06-28")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DEFAULT_DATABASE_ID = os.environ.get("NOTION_DEFAULT_DATABASE_ID", "").strip()
DEFAULT_PARENT_PAGE_ID = os.environ.get("NOTION_DEFAULT_PARENT_PAGE_ID", "").strip()


def fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def require_token() -> str:
    if NOTION_TOKEN:
        return NOTION_TOKEN
    fail(
        "Missing NOTION_TOKEN. Set a Notion internal integration token first, "
        'for example: export NOTION_TOKEN="secret_xxx"'
    )


def resolve_default_id(raw: str, env_value: str, env_name: str) -> str:
    if raw != "default":
        return raw
    if env_value:
        return env_value
    fail(f'Missing {env_name}. Set it or pass an explicit id instead of "default".')


def notion_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = require_token()
    url = f"{NOTION_API_BASE}{path}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        fail(f"Notion API error ({exc.code}): {error_body}")
    except urllib.error.URLError as exc:
        fail(f"Failed to reach Notion API: {exc}")

    if not body.strip():
        return {}
    return json.loads(body)


def rich_text(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}}]


def title_property(text: str) -> dict[str, Any]:
    return {"title": rich_text(text)}


def paragraph_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text(text)},
    }


def bulleted_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text)},
    }


def numbered_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": rich_text(text)},
    }


def quote_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "quote",
        "quote": {"rich_text": rich_text(text)},
    }


def blocks_from_text(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("- "):
            blocks.append(bulleted_block(line[2:].strip()))
        elif line[:2].isdigit() and line[1:3] == ". ":
            blocks.append(numbered_block(line[3:].strip()))
        elif line.startswith("> "):
            blocks.append(quote_block(line[2:].strip()))
        else:
            blocks.append(paragraph_block(line.strip()))
    return blocks


def extract_plain_text(items: list[dict[str, Any]] | None) -> str:
    if not items:
        return ""
    return "".join(item.get("plain_text", "") for item in items)


def page_title(page: dict[str, Any]) -> str:
    properties = page.get("properties", {})
    for value in properties.values():
        if isinstance(value, dict) and value.get("type") == "title":
            return extract_plain_text(value.get("title")) or "(untitled)"
    return "(untitled)"


def summarize_result(item: dict[str, Any]) -> dict[str, Any]:
    item_type = item.get("object", "unknown")
    title = ""
    if item_type == "page":
        title = page_title(item)
    elif item_type == "database":
        title = extract_plain_text(item.get("title")) or "(untitled database)"
    return {
        "object": item_type,
        "id": item.get("id"),
        "url": item.get("url"),
        "title": title,
    }


def list_block_text(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for block in blocks:
        block_type = block.get("type", "")
        payload = block.get(block_type, {})
        text = extract_plain_text(payload.get("rich_text"))
        lines.append({"type": block_type, "text": text})
    return lines


def cmd_search(args: argparse.Namespace) -> None:
    payload = {
        "query": args.query,
        "page_size": args.page_size,
    }
    if args.filter:
        payload["filter"] = {"property": "object", "value": args.filter}
    data = notion_request("POST", "/search", payload)
    output = {
        "results": [summarize_result(item) for item in data.get("results", [])],
        "has_more": data.get("has_more", False),
        "next_cursor": data.get("next_cursor"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_get_page(args: argparse.Namespace) -> None:
    page = notion_request("GET", f"/pages/{args.page_id}")
    children = notion_request("GET", f"/blocks/{args.page_id}/children?page_size=100")
    summary = {
        "page": summarize_result(page),
        "properties": page.get("properties", {}),
        "children": list_block_text(children.get("results", [])),
    }
    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    print(f"Title: {summary['page']['title']}")
    print(f"Page ID: {summary['page']['id']}")
    print(f"URL: {summary['page']['url']}")
    print("")
    for line in summary["children"]:
        block_type = line["type"]
        text = line["text"]
        if not text:
            continue
        prefix = {
            "bulleted_list_item": "- ",
            "numbered_list_item": "1. ",
            "quote": "> ",
            "to_do": "[ ] ",
        }.get(block_type, "")
        print(f"{prefix}{text}")


def cmd_query_database(args: argparse.Namespace) -> None:
    database_id = resolve_default_id(args.database_id, DEFAULT_DATABASE_ID, "NOTION_DEFAULT_DATABASE_ID")
    payload: dict[str, Any] = {"page_size": args.page_size}
    if args.filter_json:
        payload["filter"] = json.loads(args.filter_json)
    if args.sorts_json:
        payload["sorts"] = json.loads(args.sorts_json)
    data = notion_request("POST", f"/databases/{database_id}/query", payload)
    output = {
        "database_id": database_id,
        "results": [summarize_result(item) for item in data.get("results", [])],
        "has_more": data.get("has_more", False),
        "next_cursor": data.get("next_cursor"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def find_title_property_name(database: dict[str, Any]) -> str:
    properties = database.get("properties", {})
    for name, value in properties.items():
        if isinstance(value, dict) and value.get("type") == "title":
            return name
    return "Name"


def cmd_create_page(args: argparse.Namespace) -> None:
    content_blocks = blocks_from_text(args.content or "")
    payload: dict[str, Any] = {}

    if args.database_id:
        database_id = resolve_default_id(args.database_id, DEFAULT_DATABASE_ID, "NOTION_DEFAULT_DATABASE_ID")
        database = notion_request("GET", f"/databases/{database_id}")
        title_name = find_title_property_name(database)
        payload["parent"] = {"database_id": database_id}
        properties = json.loads(args.properties_json) if args.properties_json else {}
        properties[title_name] = title_property(args.title)
        payload["properties"] = properties
    else:
        parent_page_id = resolve_default_id(
            args.parent_page_id or "default",
            DEFAULT_PARENT_PAGE_ID,
            "NOTION_DEFAULT_PARENT_PAGE_ID",
        )
        payload["parent"] = {"page_id": parent_page_id}
        payload["properties"] = {"title": title_property(args.title)}

    if content_blocks:
        payload["children"] = content_blocks

    data = notion_request("POST", "/pages", payload)
    print(json.dumps(summarize_result(data), ensure_ascii=False, indent=2))


def cmd_update_page(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {}
    if args.properties_json:
        payload["properties"] = json.loads(args.properties_json)
    if args.archived is not None:
        payload["archived"] = args.archived
    if not payload:
        fail("Nothing to update. Pass --properties-json and/or --archived true|false.")
    data = notion_request("PATCH", f"/pages/{args.page_id}", payload)
    print(json.dumps(summarize_result(data), ensure_ascii=False, indent=2))


def cmd_append_text(args: argparse.Namespace) -> None:
    children = blocks_from_text(args.content)
    if not children:
        fail("No content to append.")
    payload = {"children": children}
    data = notion_request("PATCH", f"/blocks/{args.page_id}/children", payload)
    output = {
        "page_id": args.page_id,
        "appended": len(data.get("results", [])),
        "results": list_block_text(data.get("results", [])),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read and write Notion pages/databases for the OpenClaw workspace skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Environment variables:
              NOTION_TOKEN                  Required. Internal integration token.
              NOTION_DEFAULT_DATABASE_ID    Optional default database id.
              NOTION_DEFAULT_PARENT_PAGE_ID Optional default parent page id.
              NOTION_API_VERSION            Optional, default: 2022-06-28.
            """
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search pages and databases")
    search.add_argument("query")
    search.add_argument("--page-size", type=int, default=10)
    search.add_argument("--filter", choices=["page", "database"])
    search.set_defaults(func=cmd_search)

    get_page = subparsers.add_parser("get-page", help="Read page metadata and first-level child blocks")
    get_page.add_argument("page_id")
    get_page.add_argument("--format", choices=["json", "text"], default="json")
    get_page.set_defaults(func=cmd_get_page)

    query_db = subparsers.add_parser("query-database", help="Query a database")
    query_db.add_argument("database_id", help='Database id, or "default"')
    query_db.add_argument("--page-size", type=int, default=10)
    query_db.add_argument("--filter-json")
    query_db.add_argument("--sorts-json")
    query_db.set_defaults(func=cmd_query_database)

    create_page = subparsers.add_parser("create-page", help="Create a page under a page or in a database")
    create_page.add_argument("--title", required=True)
    create_page.add_argument("--content", default="")
    create_page.add_argument("--parent-page-id", help='Parent page id, or "default"')
    create_page.add_argument("--database-id", help='Database id, or "default"')
    create_page.add_argument("--properties-json")
    create_page.set_defaults(func=cmd_create_page)

    update_page = subparsers.add_parser("update-page", help="Update page properties or archive state")
    update_page.add_argument("page_id")
    update_page.add_argument("--properties-json")
    update_page.add_argument("--archived", type=lambda value: value.lower() == "true")
    update_page.set_defaults(func=cmd_update_page)

    append_text = subparsers.add_parser("append-text", help="Append plain text as Notion blocks")
    append_text.add_argument("page_id")
    append_text.add_argument("--content", required=True)
    append_text.set_defaults(func=cmd_append_text)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
