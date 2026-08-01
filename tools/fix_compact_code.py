"""Fix compact one-line class/def bodies that Python cannot parse."""

from __future__ import annotations

import pathlib
import re
import sys


def split_top(s: str) -> list[str]:
    """Split on top-level semicolons, respecting brackets and quotes."""
    parts: list[str] = []
    cur: list[str] = []
    depth = 0
    quote: str | None = None
    i = 0
    while i < len(s):
        c = s[i]
        if quote is not None:
            cur.append(c)
            if c == quote and (i == 0 or s[i - 1] != "\\"):
                quote = None
            i += 1
            continue
        if c in "\"'":
            quote = c
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            depth -= 1
            cur.append(c)
        elif c == ";" and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


DEF_RE = re.compile(r"^(\s*)(def \w+\([^)]*\):)(.*)$")
CLASS_RE = re.compile(r"^(\s*class \w+(?:\([^)]*\))?:\s*)(.+)$")


def expand_parts(indent: str, body: str) -> list[str]:
    """Expand a semicolon-separated body into indented lines."""
    lines: list[str] = []
    for part in split_top(body):
        m = DEF_RE.match(part)
        if m:
            header, rest = m.group(2), m.group(3).strip()
            lines.append(indent + header + "\n")
            if rest:
                lines.extend(expand_parts(indent + "    ", rest))
        else:
            lines.append(indent + part + "\n")
    return lines


def fix_file(path: pathlib.Path) -> bool:
    """Return True if the file was changed."""
    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    out: list[str] = []
    changed = False
    pending_merge: list[str] | None = None
    pending_indent = ""

    i = 0
    while i < len(lines):
        line = lines[i]

        # Merge continuation lines into the previous expanded def block.
        if pending_merge is not None:
            stripped = line.rstrip("\n")
            if stripped.strip() and len(stripped) - len(stripped.lstrip()) > len(pending_indent):
                pending_merge.append(stripped + "\n")
                i += 1
                continue
            out.extend(pending_merge)
            pending_merge = None

        raw = line.rstrip("\n")
        indent = raw[: len(raw) - len(raw.lstrip())]
        content = raw.strip()

        cm = CLASS_RE.match(raw)
        if cm and cm.group(2).strip():
            header, body = cm.group(1), cm.group(2)
            out.append(header.rstrip() + "\n")
            out.extend(expand_parts(indent + "    ", body))
            changed = True
            i += 1
            continue

        dm = DEF_RE.match(raw)
        if dm:
            indent, header, body = dm.group(1), dm.group(2), dm.group(3).strip()
            if body:
                out.append(indent + header + "\n")
                out.extend(expand_parts(indent + "    ", body))
                changed = True
                pending_merge = []
                pending_indent = indent
                i += 1
                continue

        out.append(line)
        i += 1

    if pending_merge is not None:
        out.extend(pending_merge)

    if changed:
        with path.open("w", encoding="utf-8", newline="\n") as f:
            f.writelines(out)
    return changed


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: fix_compact_code.py <file-or-dir> ...")
        return 1
    skip_dirs = {".venv", "node_modules", ".git", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache"}
    changed_files = 0
    for arg in argv:
        p = pathlib.Path(arg)
        files = [p] if p.is_file() else list(p.rglob("*.py"))
        for f in files:
            if any(part in skip_dirs for part in f.parts):
                continue
            try:
                if fix_file(f):
                    print(f"fixed: {f}")
                    changed_files += 1
            except Exception as exc:  # pragma: no cover
                print(f"skip {f}: {exc}", file=sys.stderr)
    print(f"total fixed: {changed_files}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
