"""Run the repository's fail-closed integrity gates under pytest."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run_gate(relative_path: str, success_marker: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert success_marker in output, output


def test_historical_portal_gate() -> None:
    run_gate("tools/verify_portal.py", "完成: REVERSECHAIN_TO_🪞幻影膠囊")


def test_public_seed_gate() -> None:
    run_gate("tools/verify_lkmini.py", "PASS: LKMini seed gate verified")
