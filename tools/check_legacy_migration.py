"""Regression check for the pre-1.0.0 data migration in main_1.0.0.py.

Extracts ``_count_characters`` and ``migrate_legacy_data`` from the main
script without importing it (importing would start the Qt app), then runs
them against temporary folders.

Usage: python tools/check_legacy_migration.py [path/to/main_1.0.0.py]
Exits non-zero on the first failure.
"""
import ast
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "main_1.0.0.py"
WANTED = {"_count_characters", "migrate_legacy_data"}


def load_functions():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in WANTED]
    assert {n.name for n in nodes} == WANTED, f"missing functions in {MAIN.name}"
    # Default arguments reference module globals; bind placeholders, tests pass real values.
    ns = {"Path": Path, "os": os, "shutil": shutil, "sqlite3": sqlite3,
          "SESSIONS_DIR": Path("unused"), "LEGACY_SESSIONS_DIRS": [],
          "LEGACY_DB_NAME": "rbc_map_data.db"}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MAIN), "exec"), ns)
    return ns["migrate_legacy_data"], ns["_count_characters"]


def make_db(path: Path, characters: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    conn.executemany("INSERT INTO characters (name, password) VALUES (?, '')",
                     [(c,) for c in characters])
    conn.commit()
    conn.close()


def names(path: Path):
    conn = sqlite3.connect(path)
    try:
        return sorted(r[0] for r in conn.execute("SELECT name FROM characters"))
    finally:
        conn.close()


def run(name, fn):
    with tempfile.TemporaryDirectory() as tmp:
        fn(Path(tmp))
    print(f"ok   {name}")


migrate, count = load_functions()


def fresh_install_no_legacy(t: Path):
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert not (t / "new").exists()


def migrates_root_sessions(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "app/sessions/profile").mkdir()
    (t / "app/sessions/profile/Cookies").write_text("c")
    msg = migrate(t / "new", [t / "app/sessions", t / "app/testing/sessions"])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Alice"]
    assert (t / "new/profile/Cookies").read_text() == "c"
    assert names(t / "app/sessions/rbc_map_data.db") == ["Alice"], "original changed"
    assert not (t / "new/rbc_map_data.db.migrating").exists()


def prefers_newest_legacy(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Old"])
    make_db(t / "app/testing/sessions/rbc_map_data.db", ["Newer"])
    os.utime(t / "app/sessions/rbc_map_data.db", (1, 1))
    migrate(t / "new", [t / "app/sessions", t / "app/testing/sessions"])
    assert names(t / "new/rbc_map_data.db") == ["Newer"]


def replaces_empty_new_db_with_backup(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "new/rbc_map_data.db", [])  # created by an earlier 1.0.0 launch
    msg = migrate(t / "new", [t / "app/sessions"])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Alice"]
    assert (t / "new/rbc_map_data.db.pre-migration").is_file()


def keeps_populated_new_db(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "new/rbc_map_data.db", ["Bob"])
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert names(t / "new/rbc_map_data.db") == ["Bob"]


def second_run_is_noop(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    migrate(t / "new", [t / "app/sessions"])
    assert migrate(t / "new", [t / "app/sessions"]) is None


def same_dir_is_ignored(t: Path):
    make_db(t / "s/rbc_map_data.db", ["Alice"])
    assert migrate(t / "s", [t / "s"]) is None


def failure_leaves_no_partial_db(t: Path):
    legacy = t / "app/sessions"
    legacy.mkdir(parents=True)
    (legacy / "rbc_map_data.db").write_bytes(b"not a database" * 100)
    msg = migrate(t / "new", [legacy])
    assert msg and "failed" in msg, msg
    assert not (t / "new/rbc_map_data.db").exists()
    assert not (t / "new/rbc_map_data.db.migrating").exists()


def empty_legacy_does_not_replace_new_db(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", [])
    make_db(t / "new/rbc_map_data.db", [])
    assert migrate(t / "new", [t / "app/sessions"]) is None


for case in [fresh_install_no_legacy, migrates_root_sessions, prefers_newest_legacy,
             replaces_empty_new_db_with_backup, keeps_populated_new_db, second_run_is_noop,
             same_dir_is_ignored, failure_leaves_no_partial_db,
             empty_legacy_does_not_replace_new_db]:
    run(case.__name__, case)
print("all legacy-migration checks passed")
