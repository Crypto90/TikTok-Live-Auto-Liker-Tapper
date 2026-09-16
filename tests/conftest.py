import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def headless_module(tmp_path_factory):
    """Import headless_runner with a throwaway data folder (it picks the cwd when settings.json exists)."""
    pytest.importorskip("PyQt6.QtWidgets")
    data_dir = tmp_path_factory.mktemp("headless_data")
    (data_dir / "settings.json").write_text(json.dumps({}))
    old_cwd = os.getcwd()
    os.chdir(data_dir)
    try:
        import headless_runner
    finally:
        os.chdir(old_cwd)
    return headless_runner
