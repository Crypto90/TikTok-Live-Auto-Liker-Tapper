import ast
import os
import shutil
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def extract_tapper_script() -> str:
    """Read TAPPER_IN_PAGE_SCRIPT without importing webview_engine (which needs a browser backend)."""
    with open(os.path.join(ROOT, "webview_engine.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TAPPER_IN_PAGE_SCRIPT":
            return node.value.value
    raise AssertionError("TAPPER_IN_PAGE_SCRIPT not found")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not installed")
def test_in_page_tapper_behaviour(tmp_path):
    script = tmp_path / "tapper.js"
    script.write_text(extract_tapper_script(), encoding="utf-8")
    result = subprocess.run(
        ["node", os.path.join(HERE, "js", "tapper.test.mjs"), str(script)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
