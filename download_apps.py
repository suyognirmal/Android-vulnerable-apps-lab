#!/usr/bin/env python3
"""Download prebuilt vulnerable APKs listed in download_urls.json."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
MIN_SIZE = 1000
RETRIES = 3
RETRY_DELAY = 2


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def is_valid_artifact(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.stat().st_size <= MIN_SIZE:
        return False
    with path.open("rb") as f:
        return f.read(2) == b"PK"


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            part.write_bytes(data)
            part.replace(dest)
            return
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            last_err = exc
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY)
    part.unlink(missing_ok=True)
    raise RuntimeError(f"download failed after {RETRIES} attempts: {last_err}") from last_err


def load_apps(root: Path) -> list[dict]:
    config_path = root / "download_urls.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return list(data.get("apps", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Download vulnerable APKs from download_urls.json")
    parser.add_argument(
        "--only",
        help="Comma-separated folder names to download (e.g. DIVA,VulnerableRN)",
    )
    args = parser.parse_args()
    root = repo_root()
    only = {x.strip() for x in args.only.split(",")} if args.only else None

    ok = skipped = failed = 0
    for entry in load_apps(root):
        folder = entry["folder"]
        if only and folder not in only:
            continue
        framework = entry["framework"]
        artifact = entry["artifact"]
        url = entry["url"]
        dest = root / framework / folder / artifact

        if is_valid_artifact(dest):
            print(f"SKIP (exists): {framework}/{folder}/{artifact}")
            skipped += 1
            continue

        print(f"GET {url}")
        try:
            download_url(url, dest)
            size = dest.stat().st_size
            print(f"OK {framework}/{folder}/{artifact} ({size} bytes)")
            ok += 1
        except RuntimeError as exc:
            print(f"FAIL {framework}/{folder}/{artifact}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nDone: downloaded={ok} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
