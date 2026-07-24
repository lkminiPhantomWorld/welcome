#!/usr/bin/env python3
"""Public welcome and unique AI entry violent verifier."""
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PORTAL_MANIFEST.json"
LOCATOR = ROOT / "PORTAL_LOCATOR.json"
REVERSE = ROOT / "PORTAL_REVERSECHAIN.json"
SUMS = ROOT / "PORTAL_SHA256SUMS"
WELCOME = ROOT / "index.html"
AI_ENTRY = ROOT / "mini" / "index.html"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def check_hashes() -> None:
    seen = set()
    for raw in SUMS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        expected, rel = line.split("  ", 1)
        if rel in seen:
            fail(f"重複雜湊項目：{rel}")
        seen.add(rel)
        path = ROOT / rel
        if not path.is_file():
            fail(f"雜湊目標不存在：{rel}")
        if sha256_file(path) != expected:
            fail(f"雜湊不一致：{rel}")


def resolve_internal(source: Path, href: str):
    if href in {"", "#"}:
        fail(f"空殼連結：{source.relative_to(ROOT)} -> {href!r}")
    parsed = urlparse(href)
    if parsed.scheme or href.startswith("//"):
        return None
    clean = href.split("#", 1)[0].split("?", 1)[0]
    target = (source.parent / clean).resolve()
    if clean.endswith("/"):
        target = target / "index.html"
    if ROOT.resolve() not in target.parents and target != ROOT.resolve():
        fail(f"連結越界：{source.relative_to(ROOT)} -> {href}")
    return target


def check_manifest_and_routes() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = manifest.get("entry_definition", {})
    if entry.get("welcome_role") != "generic_welcome_page":
        fail("Welcome 角色不正確")
    if entry.get("ai_entry_identity") != "OPEN_SOURCE_MINI_RED_LABEL":
        fail("AI 入口 Identity 不正確")
    if entry.get("ai_entry_count") != 1:
        fail("AI 入口數量不等於 1")

    declared = set()
    html_paths = []
    for item in manifest.get("files", []):
        rel = item["path"]
        if rel in declared:
            fail(f"Manifest 重複路徑：{rel}")
        declared.add(rel)
        path = ROOT / rel
        if not path.is_file():
            fail(f"Manifest 目標不存在：{rel}")
        if path.suffix == ".html":
            html_paths.append(path)

    href_re = re.compile(r'href=["\']([^"\']*)["\']', re.I)
    for html in html_paths:
        for href in href_re.findall(html.read_text(encoding="utf-8")):
            target = resolve_internal(html, href)
            if target is not None and not target.is_file():
                fail(f"連結目標不存在：{html.relative_to(ROOT)} -> {href}")


def check_entry_semantics() -> None:
    welcome_text = WELCOME.read_text(encoding="utf-8")
    entry_text = AI_ENTRY.read_text(encoding="utf-8")
    if 'data-system-entry="true"' in welcome_text:
        fail("通用 Welcome 被誤標為 AI 入口")
    required = (
        'data-system-entry="true"',
        'data-entry-count="1"',
        "OPEN_SOURCE_MINI_RED_LABEL",
        "🟥 開源 MINI",
    )
    for marker in required:
        if marker not in entry_text:
            fail(f"紅色 MINI 入口缺少標記：{marker}")


def check_locator_and_reverse_chain() -> None:
    locator = json.loads(LOCATOR.read_text(encoding="utf-8"))
    if locator.get("welcome_role") != "generic_welcome_page":
        fail("Locator Welcome 角色不正確")
    entry = locator.get("ai_unique_entry", {})
    if entry.get("identity") != "OPEN_SOURCE_MINI_RED_LABEL" or entry.get("count") != 1:
        fail("Locator AI 唯一入口不正確")
    if locator.get("open_source_seed", {}).get("repository") != "https://github.com/lkminiPhantomWorld/LKMini":
        fail("LKMini 獨立開源 Repo 不正確")

    chain = json.loads(REVERSE.read_text(encoding="utf-8")).get("chain", [])
    ai_nodes = [node for node in chain if node.get("role") == "ai_unique_entry"]
    if len(ai_nodes) != 1:
        fail("ReverseChain AI 入口數量不等於 1")
    if ai_nodes[0].get("returns_to") != "🧩LKMINI":
        fail("AI 入口未回指 🧩LKMINI")


def main() -> None:
    for required in (MANIFEST, LOCATOR, REVERSE, SUMS, WELCOME, AI_ENTRY):
        if not required.is_file():
            fail(f"缺少必要檔案：{required.relative_to(ROOT)}")
    check_hashes()
    check_manifest_and_routes()
    check_entry_semantics()
    check_locator_and_reverse_chain()
    print("PASS: PUBLIC_FILE_EXISTENCE")
    print("PASS: SHA256_INTEGRITY")
    print("PASS: INTERNAL_ROUTES")
    print("PASS: WELCOME_IS_GENERIC")
    print("PASS: AI_UNIQUE_ENTRY_RED_MINI")
    print("PASS: OPEN_SOURCE_REPOSITORY_SEPARATION")
    print("A_EQUALS_A=TRUE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"VERIFICATION=ERROR: {exc}")
        raise SystemExit(1)
