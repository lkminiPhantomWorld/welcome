#!/usr/bin/env python3
"""
LKMini 封裝腳本
輸出：LKMini_seed_v0.zip
"""

import zipfile
import os
import datetime

SEED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "LKMini.svg",
    "MANIFEST.json",
    "LOCATOR.json",
    "SNAPSHOT.json",
    "ReverseChain.json",
    "RESTORE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "VERSION.md",
    "PUBLIC_PRIVATE_BOUNDARY.md",
    "ETERNAL_CORE_POLICY.md",
    "GOVERNANCE.md",
    "THREAT_MODEL.md",
    "CITATION.cff",
    "SHA256SUMS",
    ".github/CODEOWNERS",
    ".github/workflows/gatekeeper.yml",
    "tools/verify_lkmini.py",
    "tools/package_seed.py",
]

OUTPUT = "LKMini_seed_v0.zip"

if __name__ == "__main__":
    print(f"封裝 LKMini seed_v0 -> {OUTPUT}")
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in SEED_FILES:
            if not os.path.isfile(f):
                raise FileNotFoundError(f"錯誤：缺少必要封裝檔案 {f}")
            zf.write(f)
            print(f"  加入: {f}")
    print(f"\n✅ 完成: {OUTPUT}")
    print("A_EQUALS_A=true")
