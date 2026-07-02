#!/usr/bin/env python3
"""Build or fetch APKs defined in build_config.json."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

MIN_SIZE = 1000
TEMURIN_URL = (
    "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/"
    "hotspot/normal/eclipse?project=jdk"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def is_valid_artifact(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.stat().st_size <= MIN_SIZE:
        return False
    with path.open("rb") as f:
        return f.read(2) == b"PK"


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    subprocess.run(cmd, cwd=cwd, env=merged, check=True)


def find_javac() -> str | None:
    return shutil.which("javac")


def ensure_java(env: dict[str, str]) -> None:
    if find_javac():
        if "JAVA_HOME" not in env and (javac := shutil.which("javac")):
            env["JAVA_HOME"] = str(Path(javac).resolve().parent.parent)
        return
    jdk_root = Path(tempfile.gettempdir()) / "vulnerable-apps-jdk"
    jdk_home = jdk_root / "jdk"
    javac_path = jdk_home / "bin" / "javac"
    if javac_path.is_file():
        env["JAVA_HOME"] = str(jdk_home)
        env["PATH"] = f"{jdk_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
        return

    print("Downloading portable JDK 21...")
    jdk_root.mkdir(parents=True, exist_ok=True)
    archive = jdk_root / "temurin-21.tar.gz"
    urllib.request.urlretrieve(TEMURIN_URL, archive)
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(jdk_root)
    for candidate in jdk_root.glob("jdk-*"):
        if (candidate / "bin" / "javac").is_file():
            jdk_home = candidate
            break
    env["JAVA_HOME"] = str(jdk_home)
    env["PATH"] = f"{jdk_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    if not find_javac():
        raise RuntimeError("JDK installation failed — ensure javac is available or set JAVA_HOME")


def resolve_android_sdk(env: dict[str, str]) -> str:
    sdk = env.get("ANDROID_SDK_ROOT") or env.get("ANDROID_HOME")
    if not sdk:
        raise RuntimeError("Set ANDROID_SDK_ROOT (or ANDROID_HOME) to your Android SDK path")
    env["ANDROID_SDK_ROOT"] = sdk
    env["ANDROID_HOME"] = sdk
    return sdk


def resolve_flutter(env: dict[str, str]) -> str:
    flutter = env.get("FLUTTER") or shutil.which("flutter")
    if not flutter:
        raise RuntimeError("Set FLUTTER to your flutter binary or add flutter to PATH")
    env["FLUTTER"] = flutter
    return flutter


def git_clone(url: str, dest: Path, branch: str | None = None) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["-b", branch])
    cmd.extend([url, str(dest)])
    run(cmd, cwd=dest.parent)


def apply_patches(work: Path, patches: list[dict]) -> None:
    for patch in patches:
        rel = patch["file"]
        target = work / rel
        text = target.read_text(encoding="utf-8")
        text = text.replace(patch["find"], patch["replace"])
        target.write_text(text, encoding="utf-8")


def build_entry(entry: dict, tmp: Path, root: Path, env: dict[str, str]) -> None:
    dest = root / entry["framework"] / entry["folder"] / entry["dest_artifact"]
    if is_valid_artifact(dest):
        print(f"SKIP (exists): {entry['framework']}/{entry['folder']}/{entry['dest_artifact']}")
        return

    requires = set(entry.get("requires", []))
    if "java" in requires:
        ensure_java(env)
    if "android_sdk" in requires:
        resolve_android_sdk(env)
    flutter_bin: str | None = None
    if "flutter" in requires:
        flutter_bin = resolve_flutter(env)

    clone_dir = tmp / entry["id"]
    git_clone(entry["clone_url"], clone_dir, entry.get("branch"))

    recipe = entry["recipe"]
    if recipe == "shell":
        for cmd in entry.get("commands", []):
            run(["bash", "-lc", cmd], cwd=clone_dir, env=env)
    elif recipe == "gradle_debug":
        for cmd in entry.get("commands", []):
            run(["bash", "-lc", cmd], cwd=clone_dir, env=env)
    elif recipe == "copy_prebuilt":
        pass
    elif recipe == "flutter_release":
        assert flutter_bin
        run([flutter_bin, "pub", "get"], cwd=clone_dir, env=env)
        run([flutter_bin, "build", "apk", "--release"], cwd=clone_dir, env=env)
    elif recipe == "flutter_securebank":
        assert flutter_bin
        run([flutter_bin, "create", ".", "--platforms=android"], cwd=clone_dir, env=env)
        apply_patches(
            clone_dir,
            [
                {
                    "file": "lib/theme/app_theme.dart",
                    "find": "CardTheme(",
                    "replace": "CardThemeData(",
                },
                {
                    "file": "lib/widgets/account_card.dart",
                    "find": "AccountType.checking",
                    "replace": "AccountType.current",
                },
            ],
        )
        run([flutter_bin, "pub", "get"], cwd=clone_dir, env=env)
        run(
            [flutter_bin, "pub", "run", "build_runner", "build", "--delete-conflicting-outputs"],
            cwd=clone_dir,
            env=env,
        )
        run([flutter_bin, "build", "apk", "--release"], cwd=clone_dir, env=env)
    else:
        raise RuntimeError(f"Unknown recipe: {recipe}")

    src = clone_dir / entry["output_in_clone"]
    if not src.is_file():
        raise RuntimeError(f"Build output missing: {src}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    if not is_valid_artifact(dest):
        raise RuntimeError(f"Invalid artifact after copy: {dest}")
    print(f"OK {entry['framework']}/{entry['folder']}/{entry['dest_artifact']} ({dest.stat().st_size} bytes)")


def load_builds(root: Path) -> list[dict]:
    data = json.loads((root / "build_config.json").read_text(encoding="utf-8"))
    return list(data.get("builds", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build vulnerable APKs from build_config.json")
    parser.add_argument(
        "--only",
        help="Comma-separated build ids (e.g. vulnlab,securebank)",
    )
    args = parser.parse_args()
    root = repo_root()
    only = {x.strip() for x in args.only.split(",")} if args.only else None

    tmp_base = os.environ.get("BUILD_TMP") or str(Path(tempfile.gettempdir()) / "vulnerable-apps-build")
    tmp = Path(tmp_base)
    tmp.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    failed = 0
    for entry in load_builds(root):
        if only and entry["id"] not in only:
            continue
        print(f"BUILD {entry['id']}...")
        try:
            build_entry(entry, tmp, root, env)
        except (subprocess.CalledProcessError, RuntimeError, OSError) as exc:
            print(f"FAIL {entry['id']}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nDone: failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
