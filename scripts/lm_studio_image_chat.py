#!/usr/bin/env python3
"""
Call LM Studio /api/v1/chat with a local image (base64 data URL) and a text prompt.

Usage:
  python scripts/lm_studio_image_chat.py <image_path> [--prompt "..." ] [--model ...]
"""

import argparse
import base64
import os
import sys

import requests

DEFAULT_PROMPT = "Describe this image in two sentences"
DEFAULT_MODEL = "zai-org/glm-4.6v-flash"
DEFAULT_BASE_URL = "http://localhost:53985"
EXT_TO_MEDIA_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def image_to_data_url(path: str) -> str:
    """Read image file and return a data URL (data:image/...;base64,...)."""
    ext = os.path.splitext(path)[1].lower()
    media_type = EXT_TO_MEDIA_TYPE.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        raw = f.read()
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"data:{media_type};base64,{b64}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send an image and prompt to LM Studio chat API."
    )
    parser.add_argument(
        "image_path",
        help="Path to the image file (e.g. .jpg, .png)",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Text prompt (default: %(default)r)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model id (default: %(default)r)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"LM Studio base URL (default: %(default)r)",
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=2048,
        help="Context length in tokens (default: 2048)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (default: 0)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("LM_API_TOKEN", ""),
        help="API token (or set LM_API_TOKEN); omit if LM Studio has no auth",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.image_path):
        print(f"Error: not a file: {args.image_path}", file=sys.stderr)
        sys.exit(1)

    data_url = image_to_data_url(args.image_path)
    url = f"{args.base_url.rstrip('/')}/api/v1/chat"
    payload = {
        "model": args.model,
        "input": [
            {"type": "text", "content": args.prompt},
            {"type": "image", "data_url": data_url},
        ],
        "context_length": args.context_length,
        "temperature": args.temperature,
    }
    headers = {"Content-Type": "application/json"}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)

    data = r.json()
    output = data.get("output") or []
    for item in output:
        if isinstance(item, dict) and item.get("type") == "message":
            content = item.get("content")
            if content is not None:
                print(content)
                break
    else:
        print(r.text)


if __name__ == "__main__":
    main()
