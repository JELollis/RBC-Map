"""Regression checks for cookie rejection and default-character login paths."""

from __future__ import annotations

import ast
import json
import logging
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main_1.0.4.py"


def class_method(tree: ast.Module, name: str) -> ast.FunctionDef:
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    matches = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(matches) == 1, f"expected one {name} method"
    return matches[0]


def check_rejected_cookie_queues_password(tree: ast.Module) -> None:
    method = class_method(tree, "_handle_cookie_login_page")
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)

    calls: list[str] = []
    fake = type("FakeWindow", (), {})()
    fake._pending_cookie_request_id = 4
    fake._pending_cookie_character = "Alice"
    fake._queue_password_login = lambda name: calls.append(f"queue:{name}")
    fake.login_selected_character = lambda: calls.append("login")

    namespace["_handle_cookie_login_page"](fake, 4, "Alice", True)
    assert calls == ["queue:Alice", "login"]
    assert fake._pending_cookie_request_id is None
    assert fake._pending_cookie_character is None

    calls.clear()
    fake._pending_cookie_request_id = 5
    fake._pending_cookie_character = "Alice"
    namespace["_handle_cookie_login_page"](fake, 4, "Alice", True)
    assert calls == [], "stale cookie-page callbacks must not start another login"


def check_password_change_and_default_paths(tree: ast.Module) -> None:
    modify_source = ast.unparse(class_method(tree, "modify_character"))
    assert "active_cookie" in modify_source
    assert "delete_secret" in modify_source
    assert "COOKIE_SECRET_NAMESPACE" in modify_source

    default_source = ast.unparse(class_method(tree, "set_default_character"))
    assert "_queue_password_login" in default_source
    assert "switch_to_character" in default_source


def check_login_detector_matches_injector(tree: ast.Module) -> None:
    """Keep cookie detection and credential injection on the same finder."""
    for method in ("on_webview_load_finished", "login_selected_character"):
        source = ast.unparse(class_method(tree, method))
        assert "LOGIN_FORM_FINDER_JS" in source, f"{method} must share the login form finder"


def check_login_finder_behavior(tree: ast.Module) -> None:
    node_executable = shutil.which("node")
    if node_executable is None:
        raise SystemExit(
            "Auto-login regression checks require Node.js. Install Node.js and ensure 'node' is on PATH."
        )

    names = {"LOGIN_FORM_FIELDS", "LOGIN_FORM_FINDER_JS"}
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in names
    ]
    namespace = {"json": json}
    exec(compile(ast.Module(body=assignments, type_ignores=[]), str(MAIN), "exec"), namespace)
    subprocess.run(
        [node_executable, str(ROOT / "tools" / "check_login_finder.js")],
        input=namespace["LOGIN_FORM_FINDER_JS"],
        text=True,
        check=True,
    )


def check_pending_map_state_initialized(tree: ast.Module) -> None:
    """AUD-030/L1: __init__ must initialize pending_character_id_for_map
    before any webview loadFinished callback can read it."""
    init = class_method(tree, "__init__")
    assigned = {
        target.attr
        for node in ast.walk(init)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
    }
    assert "pending_character_id_for_map" in assigned


def main() -> int:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    check_rejected_cookie_queues_password(tree)
    check_password_change_and_default_paths(tree)
    check_login_detector_matches_injector(tree)
    check_login_finder_behavior(tree)
    check_pending_map_state_initialized(tree)
    print("auto-login checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
