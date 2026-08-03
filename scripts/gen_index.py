#!/usr/bin/env python3
"""Generate a directory-listing-style index.html of all solutions."""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def title_of(doc: Path) -> str:
    if not doc.exists():
        return ""
    for line in doc.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            return re.sub(r"^#+\s*", "", line)
    return ""


def entry_page(d: Path) -> Path | None:
    index = d / "index.html"
    if index.exists():
        return index
    pages = sorted(d.glob("*.html"))
    return pages[0] if pages else None


def solutions_in(work: Path):
    out = []
    for sub in sorted(work.iterdir()):
        if not sub.is_dir():
            continue
        page = entry_page(sub)
        if page:
            out.append((sub.name, page.relative_to(ROOT).as_posix()))
    return out


def works():
    numbered = [
        d for d in ROOT.iterdir() if d.is_dir() and re.fullmatch(r"\d+", d.name)
    ]
    for d in sorted(numbered, key=lambda d: int(d.name)):
        yield f"#{int(d.name)}", d / "instructions.md", d
    for d in sorted((ROOT / "untitled").iterdir()):
        if d.is_dir():
            yield "untitled", d / "README.md", d


def drawings():
    for label, doc, work in works():
        solutions = solutions_in(work)
        if solutions:
            yield label, title_of(doc), solutions


def render() -> str:
    rows = []
    for number, title, solutions in drawings():
        for author, href in solutions:
            rows.append(
                f'<tr><td><a href="{html.escape(href)}">{html.escape(number)}</a></td>'
                f"<td>{html.escape(author)}</td>"
                f"<td>{html.escape(title)}</td></tr>"
            )
    body = "\n".join(rows)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Index of /solving-sol</title>
<style>
body {{ font-family: monospace; margin: 2em; max-width: 60em; }}
h1 {{ font-size: 1.2em; font-weight: normal; }}
hr {{ border: 0; border-top: 1px solid #000; }}
table {{ border-collapse: collapse; }}
td, th {{ padding: 0 2em 0 0; text-align: left; vertical-align: top; }}
a {{ color: #00e; }}
</style>
</head>
<body>
<h1>Index of /solving-sol</h1>
<p>Implementations of <a href="https://en.wikipedia.org/wiki/Sol_LeWitt">Sol LeWitt</a>'s
wall drawing instructions. Source on
<a href="https://github.com/llimllib/solving-sol">GitHub</a>. A fork of <a href="https://github.com/wholepixel/solving-sol">wholepixel/solving-sol</a>, by Brad Bouse</p>
<hr>
<table>
<tr><th>Drawing</th><th>By</th><th>Instructions</th></tr>
{body}
</table>
<hr>
</body>
</html>
"""


if __name__ == "__main__":
    (ROOT / "index.html").write_text(render(), encoding="utf-8")
