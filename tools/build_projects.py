#!/usr/bin/env python3
"""Generate Projects in both EN and PT from research/projects/*.md.

Updates only the marked PROJECTS regions of research/index.html and
pt/research/index.html. No external dependencies; never edits the sources.

Usage:
    python3 tools/build_projects.py
    python3 tools/build_projects.py --check
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "research" / "projects"
PAGES = {"en": ROOT / "research" / "index.html", "pt": ROOT / "pt" / "research" / "index.html"}
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
GROUPS = {
    "en": (("research", "Ongoing"), ("centers", "Centers & Collaborations"), ("past", "Completed")),
    "pt": (("research", "Em andamento"), ("centers", "Centros e colaborações"), ("past", "Concluídos")),
}
REQUIRED = {"title", "title_pt", "group", "institutions", "institutions_pt", "url", "order", "featured"}


class ProjectError(ValueError):
    pass


def load_project(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ProjectError(f"{path.name}: missing metadata header")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ProjectError(f"{path.name}: missing closing ---") from exc
    meta = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ProjectError(f"{path.name}: malformed metadata line {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in REQUIRED or key in meta:
            raise ProjectError(f"{path.name}: unexpected/duplicate metadata field {key!r}")
        meta[key] = value.strip()
    missing = REQUIRED - set(meta)
    if missing:
        raise ProjectError(f"{path.name}: missing metadata: {', '.join(sorted(missing))}")
    if any(not meta[k] for k in ("title", "title_pt", "institutions", "institutions_pt")):
        raise ProjectError(f"{path.name}: titles and institutions cannot be empty")
    if meta["group"] not in {g for g, _ in GROUPS["en"]}:
        raise ProjectError(f"{path.name}: unknown group {meta['group']!r}")
    if meta["featured"] not in {"true", "false"} or not re.fullmatch(r"\d+", meta["order"]):
        raise ProjectError(f"{path.name}: invalid featured/order")
    if meta["url"]:
        url = urlsplit(meta["url"])
        if url.scheme not in {"http", "https"} or not url.netloc or any(c.isspace() for c in meta["url"]):
            raise ProjectError(f"{path.name}: URL must be absolute http(s)")
    body = "\n".join(lines[end + 1:]).strip()
    match = re.fullmatch(r"## EN\n(.*?)\n\s*## PT\n(.*)", body, re.S)
    if not match:
        raise ProjectError(f"{path.name}: expected ## EN and ## PT sections in that order")
    paragraphs = {}
    for lang, text in zip(("en", "pt"), match.groups()):
        text = text.strip()
        if not text or re.search(r"(?m)^##\s", text):
            raise ProjectError(f"{path.name}: invalid {lang} description")
        if re.search(r"(?m)^\s*[-*#>]\s", text) or re.search(r"\[[^\]]+\]\([^)]*\)", text) or "<" in text:
            raise ProjectError(f"{path.name}: descriptions must be plain text")
        paragraphs[lang] = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n", text)]
    return {"id": path.stem, **meta, "paragraphs": paragraphs}


def render_project(item: dict, lang: str) -> str:
    title = html.escape(item["title"] if lang == "en" else item["title_pt"])
    institutions = html.escape(item["institutions"] if lang == "en" else item["institutions_pt"])
    url = item["url"]
    if url:
        title = (f'<a class="project-title-link" href="{html.escape(url, quote=True)}" '
                 f'target="_blank" rel="noopener noreferrer">{title}'
                 '<span aria-hidden="true"> ↗</span></a>')
    css = "project-item project-item--featured" if item["featured"] == "true" else "project-item"
    result = [
        f'<article class="{css}" id="project-{html.escape(item["id"], quote=True)}">',
        f'  <h4 class="project-title">{title}</h4>',
        f'  <p class="project-institutions">{institutions}</p>',
    ]
    for paragraph in item["paragraphs"][lang]:
        result.append(f'  <p class="project-description">{html.escape(paragraph)}</p>')
    if url:
        label = (
            ("FAPESP record" if item["group"] == "past" else "Center website" if item["group"] == "centers" else "Project website")
            if lang == "en" else
            ("Registro FAPESP" if item["group"] == "past" else "Site do centro" if item["group"] == "centers" else "Site do projeto")
        )
        result.append(f'  <p class="project-links"><a href="{html.escape(url, quote=True)}" '
                      f'target="_blank" rel="noopener noreferrer">{label}'
                      '<span aria-hidden="true"> ↗</span></a></p>')
    result.append('</article>')
    return "\n".join(result)


def render(projects: list[dict], lang: str) -> str:
    out = []
    for group, label in GROUPS[lang]:
        items = sorted((p for p in projects if p["group"] == group),
                       key=lambda p: (int(p["order"]), p["id"]))
        if not items:
            continue
        out.extend([
            f'<section class="project-group" aria-labelledby="project-group-{group}">',
            f'  <h3 class="project-group-title" id="project-group-{group}">{html.escape(label)}</h3>',
        ])
        out.extend(render_project(item, lang) for item in items)
        out.append('</section>')
    return "\n".join(out)


def replace_region(source: str, content: str, page: Path) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ProjectError(f"{page.relative_to(ROOT)}: expected exactly one PROJECTS marker pair")
    start = source.index(START) + len(START)
    end = source.index(END)
    if end < start:
        raise ProjectError(f"{page.relative_to(ROOT)}: PROJECTS markers out of order")
    return source[:start] + "\n" + content + "\n" + source[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate both pages without writing")
    args = parser.parse_args()
    try:
        paths = sorted(p for p in DATA_DIR.glob("*.md") if p.name != "README.md")
        if not paths:
            raise ProjectError("no project data found")
        projects = [load_project(path) for path in paths]
        if len({p["id"] for p in projects}) != len(projects):
            raise ProjectError("duplicate project IDs")
        changes = {}
        for lang, page in PAGES.items():
            original = page.read_text(encoding="utf-8")
            updated = replace_region(original, render(projects, lang), page)
            changes[lang] = (page, original, updated)
    except (ProjectError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.check:
        stale = [lang.upper() for lang, (_, original, updated) in changes.items() if original != updated]
        if stale:
            print(f"FAIL: Projects pages out of date: {', '.join(stale)}; run python3 tools/build_projects.py")
            return 1
        print(f"PASS: Projects EN/PT up to date ({len(projects)} projects). No files modified.")
        return 0
    for lang, (page, original, updated) in changes.items():
        if original != updated:
            page.write_text(updated, encoding="utf-8")
            print(f"Updated {page.relative_to(ROOT)}: Projects {lang.upper()} ({len(projects)} projects).")
        else:
            print(f"Projects {lang.upper()} already up to date ({len(projects)} projects).")
    print("No BibTeX or other Research sections modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
