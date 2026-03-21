#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate an image, then explicitly send it back through OpenClaw.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import generate_image


def normalize_send_target(channel: str, target: str) -> str:
    if channel == "dingtalk":
        if target.startswith("user:"):
            return target[5:]
        if target.startswith("group:"):
            return target[6:]
    return target


def build_message_send_command(
    *,
    channel: str,
    target: str,
    media_path: Path,
    caption: str | None,
    account: str | None,
) -> list[str]:
    normalized_target = normalize_send_target(channel, target)
    command = [
        "openclaw",
        "message",
        "send",
        "--channel",
        channel,
        "--target",
        normalized_target,
        "--media",
        str(media_path),
        "--json",
    ]
    if caption:
        command.extend(["--message", caption])
    if account:
        command.extend(["--account", account])
    return command


def send_generated_image(
    *,
    channel: str,
    target: str,
    media_path: Path,
    caption: str | None,
    account: str | None,
) -> None:
    command = build_message_send_command(
        channel=channel,
        target=target,
        media_path=media_path,
        caption=caption,
        account=account,
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or "openclaw message send failed"
        raise RuntimeError(detail)

    payload = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"raw": result.stdout.strip()}

    normalized_target = normalize_send_target(channel, target)
    message_id = payload.get("result", {}).get("messageId") or payload.get("messageId")
    print(f"Image sent via {channel} to {normalized_target}.")
    if message_id:
        print(f"Message ID: {message_id}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an image and explicitly send it through OpenClaw"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        dest="input_images",
        metavar="IMAGE",
        help="Input image path(s) for editing/composition. Can be specified multiple times."
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["512", "1K", "2K", "4K"],
        default=None,
        help="Output resolution"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=generate_image.SUPPORTED_ASPECT_RATIOS,
        default=None,
        help="Output aspect ratio"
    )
    parser.add_argument("--api-key", "-k", help="Gemini API key")
    parser.add_argument("--model", "-m", default=None, help="Model alias or raw Gemini model id")
    parser.add_argument(
        "--channel",
        default="dingtalk",
        help="Outbound OpenClaw channel (default: dingtalk)"
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Outbound target. For DingTalk this can be a user id or conversationId."
    )
    parser.add_argument(
        "--caption",
        default=None,
        help="Optional message/caption sent with the image"
    )
    parser.add_argument(
        "--account",
        default=None,
        help="Optional OpenClaw channel account id"
    )

    args = parser.parse_args()

    try:
        output_path = generate_image.generate_image_file(
            prompt=args.prompt,
            filename=args.filename,
            input_image_paths=args.input_images,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            api_key=args.api_key,
            model=args.model,
            verbose=True,
            emit_media_token=False,
        )
        send_generated_image(
            channel=args.channel,
            target=args.target,
            media_path=output_path,
            caption=args.caption,
            account=args.account,
        )
    except ValueError:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error generating or sending image: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
