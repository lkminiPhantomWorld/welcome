#!/usr/bin/env python3
"""Public portal violent verifier: existence, hashes, routes, locator and reverse chain."""
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
        actual = sha256_file(path)
        if actual != expected:
            fail(f"雜湊不一致：{rel}")


def resolve_internal(source: Path, href: str):
    if href in {"", "#"}:
        fail(f"空殼連結：{source.relative_to(ROOT)} -> {href!r}")
    parsed = urlparse(href)
    if parsed.scheme or href.startswith("//"):
        return None
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return source
    target = (source.parent / clean).resolve()
    if clean.endswith("/"):
        target = target / "index.html"
    if ROOT.resolve() not in target.parents and target != ROOT.resolve():
        fail(f"連結越界：{source.relative_to(ROOT)} -> {href}")
    return target


def check_manifest_and_routes() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if not files:
        fail("Manifest 沒有檔案")
    declared = set()
    html_paths = []
    for item in files:
        rel = item["path"]
        if rel in declared:
            fail(f"Manifest 重複路徑：{rel}")
        declared.add(rel)
        path = ROOT / rel
        if not path.is_file():
            fail(f"Manifest 目標不存在：{rel}")
        if item.get("role") == "page":
            html_paths.append(path)
    href_re = re.compile(r'href=["\']([^"\']*)["\']', re.I)
    for html in html_paths:
        text = html.read_text(encoding="utf-8")
        for href in href_re.findall(text):
            target = resolve_internal(html, href)
            if target is not None and not target.is_file():
                fail(f"連結目標不存在：{html.relative_to(ROOT)} -> {href}")


def check_locator_and_reverse_chain() -> None:
    locator = json.loads(LOCATOR.read_text(encoding="utf-8"))
    if locator.get("active_portal") != "https://lkminiphantomworld.github.io/welcome/":
        fail("Locator active_portal 不正確")
    if locator.get("active_projection_repo") != "lkminiPhantomWorld/welcome":
        fail("Locator projection repo 不正確")
    chain = json.loads(REVERSE.read_text(encoding="utf-8")).get("chain", [])
    if len(chain) < 2:
        fail("ReverseChain 少於兩個節點")
    if chain[0].get("identity") != "LKMini/seed_v0":
        fail("ReverseChain 根節點不正確")
    if chain[-1].get("projection") != "lkminiPhantomWorld/welcome":
        fail("ReverseChain 末端投影不正確")


def main() -> None:
    for required in (MANIFEST, LOCATOR, REVERSE, SUMS):
        if not required.is_file():
            fail(f"缺少必要檔案：{required.name}")
    check_hashes()
    check_manifest_and_routes()
    check_locator_and_reverse_chain()
    print("PASS: PORTAL_EXISTENCE")
    print("PASS: PORTAL_HASHES")
    print("PASS: PORTAL_ROUTES")
    print("PASS: PORTAL_LOCATOR")
    print("PASS: PORTAL_REVERSECHAIN")
    print("PORTAL_COMPLETION=VERIFIED_TRUE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PORTAL_COMPLETION=ERROR: {exc}")
        raise SystemExit(1)
