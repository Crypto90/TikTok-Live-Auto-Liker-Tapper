import json
import threading

import storage
from storage import backup_path, read_json, write_json


def test_write_then_read_round_trip(tmp_path):
    path = tmp_path / "favorites.json"
    write_json(str(path), {"creator": True})
    assert read_json(str(path)) == {"creator": True}
    assert not (tmp_path / "favorites.json.tmp").exists()


def test_missing_file_returns_default_without_using_backup(tmp_path):
    path = tmp_path / "settings.json"
    (tmp_path / "settings.json.bak").write_text(json.dumps({"old": 1}))
    assert read_json(str(path), {"default": True}) == {"default": True}


def test_damaged_file_recovers_previous_version(tmp_path):
    path = str(tmp_path / "favorites.json")
    write_json(path, {"a": True})
    write_json(path, {"a": True, "b": True})
    assert json.loads(open(backup_path(path)).read()) == {"a": True}

    with open(path, "w") as f:
        f.write('{"a": tr')  # crash in the middle of an old-style direct write
    assert read_json(path, {}) == {"a": True}


def test_damaged_file_never_replaces_good_backup(tmp_path):
    path = str(tmp_path / "favorites.json")
    write_json(path, {"a": True})
    write_json(path, {"a": True, "b": True})  # backup = {"a": True}
    with open(path, "w") as f:
        f.write("garbage")
    write_json(path, {"c": True})
    assert json.loads(open(backup_path(path)).read()) == {"a": True}
    assert read_json(path) == {"c": True}


def test_interrupted_write_leaves_original_intact(tmp_path, monkeypatch):
    path = str(tmp_path / "cookies.json")
    write_json(path, {"cookies": [1]})

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(storage.json, "dump", boom)
    try:
        write_json(path, {"cookies": [2]})
    except OSError:
        pass
    monkeypatch.undo()
    assert read_json(path) == {"cookies": [1]}


def test_concurrent_writers_never_produce_a_broken_file(tmp_path):
    path = str(tmp_path / "settings.json")
    errors = []

    def writer(n):
        try:
            for i in range(50):
                write_json(path, {"writer": n, "i": i, "pad": "x" * 2000})
        except Exception as exc:  # pragma: no cover - reported below
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    data = json.loads(open(path).read())
    assert data["i"] == 49
