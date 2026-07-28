#!/usr/bin/env python3
"""Fail-closed verifier for Welcome -> Reader/Gateway -> Mount."""
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
READER = ROOT / "mini" / "index.html"
ROOT_SHA256 = "6c0f6f487d8af27de4a8cee9f3fc853f0fbcf417cbd21acb56ac65c55adfcf34"
ENTRY_IDENTITY = "PHANTOM_WORLD_READER_GATEWAY"

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
        if rel in seen: fail(f"重複雜湊項目：{rel}")
        seen.add(rel)
        path = ROOT / rel
        if not path.is_file(): fail(f"雜湊目標不存在：{rel}")
        if sha256_file(path) != expected: fail(f"雜湊不一致：{rel}")
    required = {"index.html","mini/index.html","PORTAL_MANIFEST.json","PORTAL_LOCATOR.json","PORTAL_REVERSECHAIN.json","tools/verify_portal.py"}
    missing = required - seen
    if missing: fail(f"SHA256SUMS 缺少必要項目：{sorted(missing)}")

def resolve_internal(source: Path, href: str):
    if href in {"", "#"}: fail(f"空殼連結：{source.relative_to(ROOT)} -> {href!r}")
    parsed = urlparse(href)
    if parsed.scheme or href.startswith("//"): return None
    clean = href.split("#",1)[0].split("?",1)[0]
    target = (source.parent / clean).resolve()
    if clean.endswith("/"): target = target / "index.html"
    if ROOT.resolve() not in target.parents and target != ROOT.resolve(): fail(f"連結越界：{source.relative_to(ROOT)} -> {href}")
    return target

def check_manifest_and_routes() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = manifest.get("entry_definition", {})
    if entry.get("welcome_role") != "generic_welcome_page": fail("Welcome 角色不正確")
    if entry.get("ai_entry_identity") != ENTRY_IDENTITY: fail("Reader/Gateway Identity 不正確")
    if entry.get("ai_entry_count") != 1: fail("AI 入口數量不等於 1")
    if entry.get("validation_policy") != "fail_closed_all_checks_required": fail("入口不是 fail-closed")
    declared=set(); html_paths=[]
    for item in manifest.get("files",[]):
        rel=item["path"]
        if rel in declared: fail(f"Manifest 重複路徑：{rel}")
        declared.add(rel); path=ROOT/rel
        if not path.is_file(): fail(f"Manifest 目標不存在：{rel}")
        if path.suffix==".html": html_paths.append(path)
    href_re=re.compile(r'href=["\']([^"\']*)["\']',re.I)
    for html in html_paths:
        for href in href_re.findall(html.read_text(encoding="utf-8")):
            target=resolve_internal(html,href)
            if target is not None and not target.is_file(): fail(f"連結目標不存在：{html.relative_to(ROOT)} -> {href}")

def check_entry_semantics() -> None:
    welcome=WELCOME.read_text(encoding="utf-8")
    reader=READER.read_text(encoding="utf-8")
    if welcome.count('href="mini/"') != 1: fail("Welcome 必須只有一個 Reader 導向")
    for marker in ("🟥 開源 MINI","SYSTEM UNIQUE AI ENTRY","AI 進入🥃老K系統的唯一紅色標籤。"):
        if marker not in welcome: fail(f"Welcome 紅色標籤缺少標記：{marker}")
    required_reader=("🪞幻影世界 Reader","🥃老K系統入口","LKMINI","唯一入口 Reader / Gateway",ROOT_SHA256,"A=A","拒絕掛載 · 不得進入","const allPass=shaMatch&&locatorPass&&payloadPass&&identityPass&&axiomPass")
    for marker in required_reader:
        if marker not in reader: fail(f"Reader 缺少 fail-closed 標記：{marker}")
    forbidden=("A == A","A==A","A ≠ A","A!=A")
    for marker in forbidden:
        if marker in welcome or marker in reader: fail(f"入口出現錯誤公理寫法：{marker}")

def check_locator_and_reverse_chain() -> None:
    locator=json.loads(LOCATOR.read_text(encoding="utf-8"))
    if locator.get("root_sha256") != ROOT_SHA256: fail("Root SHA256 不正確")
    entry=locator.get("ai_unique_entry",{})
    if entry.get("identity") != ENTRY_IDENTITY or entry.get("count") != 1: fail("Locator Reader 唯一入口不正確")
    if entry.get("validation_policy") != "fail_closed_all_checks_required": fail("Locator 未宣告 fail-closed")
    chain=json.loads(REVERSE.read_text(encoding="utf-8")).get("chain",[])
    nodes=[n for n in chain if n.get("role")=="ai_unique_entry_reader_gateway"]
    if len(nodes)!=1: fail("ReverseChain Reader/Gateway 數量不等於 1")
    if nodes[0].get("returns_to")!="🧩LKMINI": fail("Reader/Gateway 未回指 🧩LKMINI")
    if nodes[0].get("on_failure")!="reject_mount_and_deny_entry": fail("ReverseChain 失敗策略不正確")

def main() -> None:
    for required in (MANIFEST,LOCATOR,REVERSE,SUMS,WELCOME,READER):
        if not required.is_file(): fail(f"缺少必要檔案：{required.relative_to(ROOT)}")
    check_hashes(); check_manifest_and_routes(); check_entry_semantics(); check_locator_and_reverse_chain()
    print("PASS: PUBLIC_FILE_EXISTENCE")
    print("PASS: SHA256_INTEGRITY")
    print("PASS: WELCOME_TO_READER_ROUTE")
    print("PASS: READER_FAIL_CLOSED")
    print("PASS: A=A")
    print("ENTRY_POLICY=ALL_CHECKS_REQUIRED")
    print("ON_FAILURE=REJECT_MOUNT_AND_DENY_ENTRY")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(f"VERIFICATION=ERROR: {exc}")
        raise SystemExit(1)
