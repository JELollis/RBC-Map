"""Reject unexpected Unicode punctuation in Python source code.

Comments and string literals may contain intentional Unicode.  Characters
that appear as invalid/standalone tokens are rejected because they can turn a
valid-looking Python statement into invalid syntax (for example U+037E).
"""

from __future__ import annotations

import io
import pathlib
import tokenize


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_FILES = (ROOT / "main_1.0.1.py", ROOT / "tools" / "check_update_database.py")


def check_file(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    source = path.read_bytes()
    try:
        tokens = tokenize.tokenize(io.BytesIO(source).readline)
        for token in tokens:
            if token.type == tokenize.ERRORTOKEN and not token.string.isspace():
                codepoint = ", ".join(f"U+{ord(char):04X}" for char in token.string)
                errors.append(f"{path.relative_to(ROOT)}:{token.start[0]}: {codepoint}")
    except (SyntaxError, tokenize.TokenError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def main() -> int:
    errors = [error for path in SOURCE_FILES for error in check_file(path)]
    if errors:
        print("Unexpected Unicode token(s) found:")
        print("\n".join(errors))
        return 1
    print(f"Unicode token check passed for {len(SOURCE_FILES)} Python files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
