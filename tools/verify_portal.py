#!/usr/bin/env python3
"""Fail-closed verifier for the disabled historical GitHub Pages projection."""
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
SHRINE = ROOT / "ui" / "shrine" / "index.html"
CAPSULE = ROOT / "capsules" / "🚪膠囊入口｜CapsuleGateway.json"
REGISTRY = ROOT / "🧭命名空間入口定位登記｜NamespacePortalLocatorRegistry.md"

ROOT_SHA256 = "6c0f6f487d8af27de4a8cee9f3fc853f0fbcf417cbd21acb56ac65c55adfcf34"
ROOT_PROTOCOL = "LKMINI://"
CURRENT_WEB = "https://lkmini-wiring-hub.ky46738.chatgpt.site"
CURRENT_PROGRAM = "lkminiPhantomWorld/LaoK-System@main"
ENTRY_GATE = "🥳歡迎光臨"
LEGACY_URL = "https://lkminiphantomworld.github.io/welcome/"


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"JSON 無法解析：{path.relative_to(ROOT)}：{exc}")
    if not isinstance(value, dict):
        fail(f"JSON 根節點不是 object：{path.relative_to(ROOT)}")
    return value


def require_historical_disabled(value: dict, label: str) -> None:
    if value.get("active") is not False:
        fail(f"{label} active 必須為 false")
    if value.get("authorized") is not False:
        fail(f"{label} authorized 必須為 false")


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
        target = ROOT / rel
        if not target.is_file():
            fail(f"雜湊目標不存在：{rel}")
        if sha256_file(target) != expected:
            fail(f"雜湊不一致：{rel}")
    required = {
        "index.html",
        "mini/index.html",
        "ui/shrine/index.html",
        "PORTAL_MANIFEST.json",
        "PORTAL_LOCATOR.json",
        "PORTAL_REVERSECHAIN.json",
        "tools/verify_portal.py",
        "capsules/🚪膠囊入口｜CapsuleGateway.json",
        "🧭命名空間入口定位登記｜NamespacePortalLocatorRegistry.md",
    }
    missing = required - seen
    if missing:
        fail(f"SHA256SUMS 缺少必要項目：{sorted(missing)}")


def check_current_fields(value: dict, label: str) -> None:
    current = value.get("current_canonical", {})
    if current.get("logical_entry_gate") != ENTRY_GATE:
        fail(f"{label} entryGate 不正確")
    if current.get("web_projection") != CURRENT_WEB:
        fail(f"{label} Sites URL 不正確")
    if current.get("program_coordinate") != CURRENT_PROGRAM:
        fail(f"{label} 程式座標不正確")


def check_controls() -> None:
    manifest = load_json(MANIFEST)
    locator = load_json(LOCATOR)
    reverse = load_json(REVERSE)
    capsule = load_json(CAPSULE)

    for value, label in ((manifest, "Manifest"), (locator, "Locator"), (reverse, "ReverseChain"), (capsule, "CapsuleGateway")):
        require_historical_disabled(value, label)
        if value.get("status") != "完成":
            fail(f"{label} 修復狀態必須為完成")

    if manifest.get("root_protocol") != ROOT_PROTOCOL or manifest.get("root_sha256") != ROOT_SHA256:
        fail("Manifest 根協議或 root SHA256 不正確")
    check_current_fields(manifest, "Manifest")
    check_current_fields(locator, "Locator")
    check_current_fields(capsule, "CapsuleGateway")

    portal = manifest.get("portal_authorization", {})
    required_portal = {
        "portal_id",
        "target_identity",
        "root",
        "locator_ref",
        "entry_surface",
        "entry_action",
        "permission_or_hook",
        "fallback_projection",
        "reverse_chain",
        "status",
    }
    missing = required_portal - portal.keys()
    if missing:
        fail(f"Portal 缺少欄位：{sorted(missing)}")
    require_historical_disabled(portal, "Portal")
    if portal.get("status") != "錯誤":
        fail("未授權歷史 Portal 的正式狀態必須為錯誤")
    if portal.get("entry_action") not in {"open", "mount", "read", "route", "absorb"}:
        fail("Portal entry_action 不在允許清單")
    if portal.get("entry_surface") != LEGACY_URL or portal.get("fallback_projection") != CURRENT_WEB:
        fail("Portal 舊入口或 fallback 不正確")
    if not str(portal.get("permission_or_hook", "")).startswith("disabled:"):
        fail("Portal 未封閉授權鉤子")

    legacy = locator.get("legacy_projection", {})
    require_historical_disabled(legacy, "Locator legacy_projection")
    if legacy.get("status") != "錯誤" or legacy.get("fallback_projection") != CURRENT_WEB:
        fail("Locator 歷史投影隔離不完整")

    chain = reverse.get("chain", [])
    if len(chain) < 5:
        fail("ReverseChain 節點不足")
    require_historical_disabled(chain[0], "ReverseChain legacy node")
    if chain[0].get("entry_surface") != LEGACY_URL or chain[0].get("forwards_to") != CURRENT_WEB:
        fail("ReverseChain 舊入口未正確轉送 Sites")
    if chain[1].get("entry_gate") != ENTRY_GATE or chain[1].get("url") != CURRENT_WEB:
        fail("ReverseChain 現行 Sites 節點不正確")
    if chain[1].get("active") is not True or chain[1].get("authorized") is not True:
        fail("ReverseChain 現行 Sites 節點未啟用")
    if chain[2].get("coordinate") != CURRENT_PROGRAM or chain[2].get("returns_to") != "🧩LKMINI":
        fail("ReverseChain 程式座標或根回指不正確")
    if chain[-1].get("formal_container") != "🪞幻影膠囊":
        fail("ReverseChain 未回到唯一正式容器")

    mount = capsule.get("mount", {})
    if mount.get("enabled") is not False or mount.get("fallback_projection") != CURRENT_WEB:
        fail("CapsuleGateway 歷史掛載未封閉")


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


def check_html() -> None:
    welcome = WELCOME.read_text(encoding="utf-8")
    reader = READER.read_text(encoding="utf-8")
    shrine = SHRINE.read_text(encoding="utf-8")
    for text, label in ((welcome, "Welcome"), (reader, "Reader"), (shrine, "Shrine")):
        for marker in ('data-projection-status="historical"', 'data-active="false"', 'data-authorized="false"', CURRENT_WEB):
            if marker not in text:
                fail(f"{label} 缺少歷史隔離標記：{marker}")

    required_welcome = (
        "📚歷史 Projection｜Historical Projection",
        "entryGate=🥳歡迎光臨",
        "CURRENT WEB PROJECTION",
        'href="https://lkmini-wiring-hub.ky46738.chatgpt.site"',
        '<a class="card history" href="mini/"',
        'id="historical-claims"',
    )
    for marker in required_welcome:
        if marker not in welcome:
            fail(f"Welcome 缺少現行或歷史標記：{marker}")
    if '<a class="card entry" href="mini/"' in welcome:
        fail("mini/ 仍被宣告為 current unique href")

    required_reader = (
        "LEGACY_PROJECTION_DISABLED=true",
        "CURRENT_WEB_PROJECTION='https://lkmini-wiring-hub.ky46738.chatgpt.site'",
        "const allPass=!LEGACY_PROJECTION_DISABLED&&",
        "active=false and authorized=false",
        "historical Reader / Gateway",
    )
    for marker in required_reader:
        if marker not in reader:
            fail(f"Reader 缺少封閉失敗標記：{marker}")
    if "const allPass=shaMatch&&" in reader:
        fail("Reader 仍可繞過歷史停用旗標")

    href_re = re.compile(r'href=["\']([^"\']*)["\']', re.I)
    for html in (WELCOME, READER, SHRINE):
        for href in href_re.findall(html.read_text(encoding="utf-8")):
            target = resolve_internal(html, href)
            if target is not None and not target.is_file():
                fail(f"連結目標不存在：{html.relative_to(ROOT)} -> {href}")


def check_registry() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    for marker in (CURRENT_WEB, CURRENT_PROGRAM, "現行邏輯入口: 🥳歡迎光臨", "active=false；authorized=false", "📚歷史原文摘要"):
        if marker not in text:
            fail(f"Registry 缺少標記：{marker}")


def main() -> None:
    required = (MANIFEST, LOCATOR, REVERSE, SUMS, WELCOME, READER, SHRINE, CAPSULE, REGISTRY)
    for path in required:
        if not path.is_file():
            fail(f"缺少必要檔案：{path.relative_to(ROOT)}")
    check_hashes()
    check_controls()
    check_html()
    check_registry()
    print("完成: PUBLIC_FILE_EXISTENCE")
    print("完成: SHA256_INTEGRITY")
    print("完成: HISTORICAL_ACTIVE_FALSE")
    print("完成: HISTORICAL_AUTHORIZED_FALSE")
    print("完成: ENTRY_GATE=🥳歡迎光臨")
    print(f"完成: CURRENT_WEB_PROJECTION={CURRENT_WEB}")
    print(f"完成: CURRENT_PROGRAM={CURRENT_PROGRAM}")
    print("完成: REVERSECHAIN_TO_🪞幻影膠囊")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"錯誤: {exc}")
        raise SystemExit(1)
