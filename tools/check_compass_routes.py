"""Regression checks for automatic and manually selected compass routes."""

import ast
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main_1.0.5.py"


class Label:
    def __init__(self):
        self.text = None

    def setText(self, text):
        self.text = text


def load_methods():
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    names = {"_select_compass_route", "refresh_compass_state"}
    methods = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    namespace = {}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


def automatic_route_recalculates_after_position_change():
    namespace = load_methods()
    refresh = namespace["refresh_compass_state"]
    routes = {
        "value": (
            (8, "4→", [(1, 1), (5, 5)]),
            (3, "Transit", [(1, 1), (2, 2), (8, 8)]),
        )
    }
    app = SimpleNamespace(
        destination=(8, 8),
        manual_route_selection=False,
        selected_route_label=None,
        selected_route_description=None,
        selected_route_path=None,
        ap_direction_label=Label(),
        get_compass_routes=lambda: routes["value"],
    )
    app._select_compass_route = namespace["_select_compass_route"].__get__(app)
    refresh(app)
    assert app.selected_route_label == "Transit Route"
    assert app.selected_route_path == routes["value"][1][2]

    routes["value"] = (
        (2, "→", [(4, 4), (8, 8)]),
        (9, "Transit", [(4, 4), (5, 5), (8, 8)]),
    )
    refresh(app)
    assert app.selected_route_label == "Direct Route"
    assert app.selected_route_path == routes["value"][0][2]
    assert app.ap_direction_label.text == "Compass: →"


def manual_route_selection_remains_sticky():
    namespace = load_methods()
    refresh = namespace["refresh_compass_state"]
    direct = (2, "→", [(4, 4), (8, 8)])
    transit = (9, "Transit", [(4, 4), (5, 5), (8, 8)])
    app = SimpleNamespace(
        destination=(8, 8),
        manual_route_selection=True,
        selected_route_label="Transit Route",
        selected_route_description=None,
        selected_route_path=None,
        ap_direction_label=Label(),
        get_compass_routes=lambda: (direct, transit),
    )
    app._select_compass_route = namespace["_select_compass_route"].__get__(app)
    refresh(app)
    assert app.selected_route_label == "Transit Route"
    assert app.selected_route_path == transit[2]
    assert app.ap_direction_label.text == "Compass: Transit"


if __name__ == "__main__":
    automatic_route_recalculates_after_position_change()
    manual_route_selection_remains_sticky()
    print("all compass-route checks passed")
