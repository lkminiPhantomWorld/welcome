#!/usr/bin/env python3
"""LKMini seed_v0 integrity verifier. A_EQUALS_A=true."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "LKMini.svg",
    "PUBLIC_PRIVATE_BOUNDARY.md",
    "SHA256SUMS",
    ".github/workflows/gatekeeper.yml",
    "tools/verify_lkmini.py",
]
PRIVATE_MARKERS = ("PRIVATE_ENGINE", "ENGINE_REGISTRY_PRIVATE")
DECLARATION_ALLOWLIST = {"PUBLIC_PRIVATE_BOUNDARY.md"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_required_files() -> bool:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    if missing:
        print(f"FAIL: 缺少必要檔案：{missing}")
        return False
    print("PASS: 必要檔案存在")
    return True


def check_a_equals_a() -> bool:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    ok = "A_EQUALS_A=true" in text
    print("PASS: A=A 標記存在" if ok else "FAIL: README 缺少 A=A 標記")
    return ok


def check_sha256sums() -> bool:
    ok = True
    seen = set()
    for raw in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            print(f"FAIL: 非法 SHA256SUMS 行：{raw}")
            ok = False
            continue
        expected, rel = parts
        if rel in seen:
            print(f"FAIL: 重複雜湊項目：{rel}")
            ok = False
            continue
        seen.add(rel)
        path = ROOT / rel
        if not path.is_file():
            print(f"FAIL: 雜湊目標不存在：{rel}")
            ok = False
            continue
        actual = sha256_file(path)
        if actual != expected:
            print(f"FAIL: 雜湊不一致：{rel}")
            ok = False
        else:
            print(f"OK: {rel}")
    return ok


def check_no_private_leak() -> bool:
    ok = True
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in DECLARATION_ALLOWLIST:
            continue
        if path.suffix.lower() not in {".md", ".json", ".txt", ".html", ".yml", ".yaml"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for marker in PRIVATE_MARKERS:
            if marker in content:
                print(f"FAIL: 公開檔案含私有標記：{marker} @ {rel}")
                ok = False
    if ok:
        print("PASS: 私有標記掃描完成；政策宣告檔採明確白名單")
    return ok


if __name__ == "__main__":
    checks = [
        check_required_files(),
        check_a_equals_a(),
        check_sha256sums(),
        check_no_private_leak(),
    ]
    if all(checks):
        print("PASS: LKMini seed gate verified")
        raise SystemExit(0)
    print("FAIL: LKMini seed gate verification failed")
    raise SystemExit(1)
