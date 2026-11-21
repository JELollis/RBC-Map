"""Regression checks for ShoppingListTool charisma repricing (AUD-048)."""

from __future__ import annotations

import ast
import logging
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main_1.0.4.py"

PRICE_COLUMNS = ("base_price", "charisma_level_1", "charisma_level_2", "charisma_level_3")


class FakeCursor:
    def __init__(self, prices: dict[tuple[str, str], int]) -> None:
        self.prices = prices
        self.queries: list[str] = []
        self._rows: list[tuple] = []

    def execute(self, sql: str, params=()) -> None:
        self.queries.append(sql)
        column = next((c for c in PRICE_COLUMNS if c in sql), "base_price")
        shop = params[0] if params else ""
        if "item_name IN" in sql:
            names = params[1:]
        else:
            names = list(dict.fromkeys(
                name for (s, name, _c) in self.prices if s == shop
            ))
        self._rows = [
            (name, self.prices[(shop, name, column)])
            for name in names
            if (shop, name, column) in self.prices
        ]

    def fetchall(self):
        return self._rows


def class_method(tree: ast.Module, name: str) -> ast.FunctionDef:
    cls = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "ShoppingListTool"
    )
    matches = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(matches) == 1, f"expected one {name} method"
    return matches[0]


def check_charisma_reloads_available_items(tree: ast.Module) -> None:
    methods = [
        class_method(tree, name)
        for name in ("_refresh_prices", "load_items", "_price_column", "_refresh_shopping_list")
    ]
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)

    prices = {
        ("Discount Magic", "Diamond Ring", "base_price"): 70000,
        ("Discount Magic", "Diamond Ring", "charisma_level_1"): 67900,
        ("Discount Magic", "Sprint Potion", "base_price"): 105,
        ("Discount Magic", "Sprint Potion", "charisma_level_1"): 102,
    }

    available: list[str] = []
    cart_display: list[str] = []

    class Combo:
        def __init__(self, text): self._text = text
        def currentText(self): return self._text

    class ItemList:
        def __init__(self, sink): self.sink = sink
        def clear(self): pass
        def addItem(self, text): self.sink.append(text)

    fake = type("FakeTool", (), {})()
    fake.sqlite_cursor = FakeCursor(prices)
    fake.shop_combobox = Combo("Discount Magic")
    fake.charisma_combobox = Combo("Charisma 1")
    fake.available_items_list = ItemList(available)
    fake.shopping_list = ItemList(cart_display)
    fake.shopping_items = {}
    fake.update_total = lambda: None
    fake.load_items = lambda: namespace["load_items"](fake)
    fake._price_column = lambda: namespace["_price_column"](fake)
    fake._refresh_shopping_list = lambda: namespace["_refresh_shopping_list"](fake)

    namespace["_refresh_prices"](fake)

    assert any("charisma_level_1" in q for q in fake.sqlite_cursor.queries), (
        "available items must reload at the selected charisma price column"
    )
    assert "Diamond Ring - 67900 Coins" in available, available
    assert "Sprint Potion - 102 Coins" in available, available


def check_charisma_reprices_cart(tree: ast.Module) -> None:
    methods = [
        class_method(tree, name)
        for name in ("_refresh_prices", "load_items", "_price_column", "_refresh_shopping_list")
    ]
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)

    prices = {
        ("Discount Magic", "Diamond Ring", "base_price"): 70000,
        ("Discount Magic", "Diamond Ring", "charisma_level_1"): 67900,
        ("Discount Magic", "Sprint Potion", "base_price"): 105,
        ("Discount Magic", "Sprint Potion", "charisma_level_1"): 102,
    }

    cart_display: list[str] = []

    class Combo:
        def __init__(self, text): self._text = text
        def currentText(self): return self._text

    class ItemList:
        def __init__(self, sink): self.sink = sink
        def clear(self): self.sink.clear()
        def addItem(self, text): self.sink.append(text)

    fake = type("FakeTool", (), {})()
    fake.sqlite_cursor = FakeCursor(prices)
    fake.shop_combobox = Combo("Discount Magic")
    fake.charisma_combobox = Combo("Charisma 1")
    fake.available_items_list = ItemList([])
    fake.shopping_list = ItemList(cart_display)
    fake.shopping_items = {"Diamond Ring": {"price": 70000, "quantity": 2}}
    fake.update_total = lambda: None
    fake.load_items = lambda: namespace["load_items"](fake)
    fake._price_column = lambda: namespace["_price_column"](fake)
    fake._refresh_shopping_list = lambda: namespace["_refresh_shopping_list"](fake)

    namespace["_refresh_prices"](fake)

    assert fake.shopping_items["Diamond Ring"]["price"] == 67900
    assert cart_display == ["Diamond Ring - 67900 Coins - 2x"], cart_display


def main() -> int:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    check_charisma_reloads_available_items(tree)
    check_charisma_reprices_cart(tree)
    print("shopping-list checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
