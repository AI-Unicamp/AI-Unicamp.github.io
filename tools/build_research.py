#!/usr/bin/env python3
"""Build the AIMS Research EN/PT output sections from research/aims.bib.

No third-party packages. Uses the same BibTeX reader and validation rules
as tools/check_research.py. Only explicitly marked regions in the EN/PT
Research pages are modified. The source bibliography is NEVER written.

Usage (from repository root): python3 tools/build_research.py
"""

from __future__ import annotations

import html
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import quote

from check_research import BibReader, BibSyntaxError, check

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "research" / "aims.bib"
PAGES = {"en": ROOT / "research" / "index.html", "pt": ROOT / "pt" / "research" / "index.html"}
MARKERS = {
    name: (f"<!-- RESEARCH:{name.upper()}:START -->", f"<!-- RESEARCH:{name.upper()}:END -->")
    for name in ("publications", "patents", "software", "data")
}

LABELS = {
    "journal-article": "Journal article",
    "conference-paper": "Conference paper",
    "phd": "PhD thesis",
    "msc": "MSc dissertation",
    "tcc": "Undergraduate work",
}
LABELS_PT = {
    "journal-article": "Artigo de periódico",
    "conference-paper": "Artigo de conferência",
    "phd": "Tese de doutorado",
    "msc": "Dissertação de mestrado",
    "tcc": "Trabalho de graduação",
}

# Convert only the small set of LaTeX escapes present in this catalogue.
# Original .bib is not changed; this conversion affects HTML display only.
ACCENTS = {"'": "\u0301", "`": "\u0300", '"': "\u0308", "~": "\u0303", "^": "\u0302", "c": "\u0327"}
ACCENT_CMD = re.compile(r"\\([\'`\"~^c])\s*(?:\{([A-Za-z])\}|([A-Za-z]))")
OTHER_TEX = {r"\&": "&", r"\%": "%", r"\_": "_", r"\#": "#", r"\$": "$", r"\textendash": "–", r"\textemdash": "—", r"\LaTeX": "LaTeX", r"\TeX": "TeX"}


def display(value: str) -> str:
    for old, new in OTHER_TEX.items():
        value = value.replace(old, new)
    def accent(match: re.Match[str]) -> str:
        base = match.group(2) or match.group(3)
        return unicodedata.normalize("NFC", base + ACCENTS[match.group(1)])
    value = ACCENT_CMD.sub(accent, value)
    # Some entries use a TeX command with braces around its accented part,
    # e.g. Jos{\\'e}. Strip grouping braces after accent decoding.
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def author_list(value: str, lang: str = "en") -> str:
    authors = []
    for raw in re.split(r"\s+and\s+", value):
        raw = display(raw)
        if "," in raw:
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) == 2:
                raw = f"{parts[1]} {parts[0]}".strip()
            elif len(parts) == 3:
                raw = f"{parts[2]} {parts[0]} {parts[1]}".strip()
        authors.append(raw)
    conjunction = " e " if lang == "pt" else " and "
    return ", ".join(authors[:-1]) + conjunction + authors[-1] if len(authors) > 1 else (authors[0] if authors else "")


def safe_url(value: str) -> str:
    value = value.strip()
    if not re.match(r"^https?://", value, flags=re.I):
        return ""
    # Do not output dangerous HTML attributes; HTML escape happens at rendering.
    return value


def doi_url(doi: str) -> str:
    doi = doi.strip()
    if not doi:
        return ""
    if doi.lower().startswith(("https://doi.org/", "http://doi.org/")):
        return safe_url(doi)
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return "https://doi.org/" + quote(doi, safe="/._-;():")


def anchor(label: str, url: str, css: str = "") -> str:
    classes = f' class="{css}"' if css else ""
    return f'<a{classes} href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}<span aria-hidden="true"> ↗</span></a>'


def venue(fields: dict[str, str]) -> str:
    for field in ("journal", "booktitle", "school", "institution", "publisher"):
        if fields.get(field):
            return display(fields[field])
    return ""


def publication_item(kind: str, key: str, fields: dict[str, str], lang: str = "en") -> str:
    subtype = fields["subtype"].strip()
    title = html.escape(display(fields["title"]))
    authors = html.escape(author_list(fields["author"], lang))
    v = venue(fields)
    doi = doi_url(fields.get("doi", ""))
    url = safe_url(fields.get("url", ""))
    demo = safe_url(fields.get("demo", ""))
    primary = doi or url
    title_html = anchor(display(fields["title"]), primary, "publication-title-link") if primary else title
    links = []
    if doi:
        links.append(anchor("DOI", doi))
    if url and url.rstrip("/") != doi.rstrip("/"):
        links.append(anchor("Source", url))
    if demo:
        links.append(anchor("Demo", demo))
    links_label = "Links da publicação" if lang == "pt" else "Publication links"
    links_html = f'<div class="publication-links" aria-label="{links_label}">' + "".join(links) + "</div>" if links else ""
    venue_html = f'<p class="publication-venue">{html.escape(v)}</p>' if v else ""
    subtype_label = (LABELS_PT if lang == "pt" else LABELS)[subtype]
    return (
        f'<article class="publication-item" data-citation-key="{html.escape(key, quote=True)}">\n'
        f'  <h3 class="publication-title">{title_html}</h3>\n'
        f'  <p class="publication-authors">{authors}</p>\n'
        f'  {venue_html}\n'
        f'  <div class="publication-details"><span class="publication-type publication-type--{subtype}">{subtype_label}</span>'
        f'<span class="publication-item-year">{html.escape(fields["year"])}</span></div>\n'
        f'  {links_html}\n'
        f'</article>'
    )


def render_publications(entries: list[tuple[str, str, dict[str, str]]], lang: str = "en") -> str:
    publications = [(kind, key, fields) for kind, key, fields in entries if fields.get("category") == "publication"]
    publications.sort(key=lambda e: (-int(e[2]["year"]), display(e[2]["title"]).casefold(), e[1]))
    grouped: dict[str, list[str]] = {}
    for kind, key, fields in publications:
        grouped.setdefault(fields["year"], []).append(publication_item(kind, key, fields, lang))
    output = [f'<div class="publications-list" data-publications-list data-page-size="10" data-total="{len(publications)}">']
    for year, items in grouped.items():
        year_label = "Publicações de" if lang == "pt" else "Publications from"
        output.append(f'  <section class="publication-year-group" aria-label="{year_label} {year}">')
        output.append(f'    <h3 class="publication-year-heading">{year}</h3>')
        output.extend('    ' + item for item in items)
        output.append('  </section>')
    output.append('</div>')
    more_label = "Mais publicações" if lang == "pt" else "More publications"
    output.append(f'<button class="publications-more" type="button" data-publications-more hidden>{more_label} <span aria-hidden="true">+</span></button>')
    return "\n".join(output)



def research_output_item(key: str, fields: dict[str, str], category: str, lang: str = "en") -> str:
    """A simple output entry, reusing the existing Publications typography."""
    title = display(fields["title"])
    authors = html.escape(author_list(fields["author"], lang))
    doi = doi_url(fields.get("doi", ""))
    url = safe_url(fields.get("url", ""))
    demo = safe_url(fields.get("demo", ""))
    primary = doi or url
    title_html = anchor(title, primary, "publication-title-link") if primary else html.escape(title)

    if category == "patent":
        institution = display(fields.get("holder", "") or fields.get("institution", ""))
        patent_label = "Patente nº" if lang == "pt" else "Patent no."
        extras = [f"{patent_label} {display(fields['number'])}"] if fields.get("number") else []
    else:
        institution = display(fields.get("publisher", "") or fields.get("institution", ""))
        version_label = "Versão" if lang == "pt" else "Version"
        extras = [f"{version_label} {display(fields['version'])}"] if fields.get("version") else []

    extras.append(fields["year"])
    institution_html = f'<p class="publication-venue">{html.escape(institution)}</p>' if institution else ""
    details_html = " · ".join(html.escape(v) for v in extras)
    links = []
    if doi:
        links.append(anchor("DOI", doi))
    if url and url.rstrip("/") != doi.rstrip("/"):
        links.append(anchor("Source", url))
    if demo:
        links.append(anchor("Demo", demo))
    links_html = (
        ('<div class="publication-links" aria-label="Links do resultado de pesquisa">' if lang == "pt" else '<div class="publication-links" aria-label="Research output links">')
        + "".join(links) + "</div>"
        if links else ""
    )
    return (
        f'<article class="publication-item" data-citation-key="{html.escape(key, quote=True)}">\n'
        f'  <h3 class="publication-title">{title_html}</h3>\n'
        f'  <p class="publication-authors">{authors}</p>\n'
        f'  {institution_html}\n'
        f'  <p class="publication-item-year">{details_html}</p>\n'
        f'  {links_html}\n'
        f'</article>'
    )


def render_outputs(entries: list[tuple[str, str, dict[str, str]]], category: str, lang: str = "en") -> str:
    chosen = [(key, fields) for _, key, fields in entries if fields.get("category") == category]
    chosen.sort(key=lambda e: (-int(e[1]["year"]), display(e[1]["title"]).casefold(), e[0]))
    return "\n".join(
        research_output_item(key, fields, category, lang) for key, fields in chosen
    )


def replace_region(source: str, name: str, content: str) -> str:
    start, end = MARKERS[name]
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"missing or repeated {name.upper()} markers")
    if source.index(start) > source.index(end):
        raise ValueError(f"out-of-order {name.upper()} markers")
    begin = source.index(start) + len(start)
    finish = source.index(end)
    return source[:begin] + "\n" + content + "\n" + source[finish:]


def main() -> int:
    if not BIB.is_file() or any(not page.is_file() for page in PAGES.values()):
        print("ERROR: missing research/aims.bib or EN/PT Research page", file=sys.stderr)
        return 1
    try:
        entries = BibReader(BIB.read_text(encoding="utf-8")).entries()
    except (BibSyntaxError, UnicodeError) as exc:
        print(f"ERROR parsing bibliography: {exc}", file=sys.stderr)
        return 1
    errors = check(entries)
    if errors:
        print("ERROR: research bibliography did not pass validation:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    # Render and validate BOTH files before writing EITHER one.
    # This avoids partial updates if a page is missing a marker.
    changes = {}
    try:
        for lang, page in PAGES.items():
            source = page.read_text(encoding="utf-8")
            rendered = {
                "publications": render_publications(entries, lang),
                "patents": render_outputs(entries, "patent", lang),
                "software": render_outputs(entries, "software", lang),
                "data": render_outputs(entries, "data", lang),
            }
            result = source
            for name, content in rendered.items():
                result = replace_region(result, name, content)
            changes[page] = (source, result)
    except (ValueError, UnicodeError) as exc:
        print(f"ERROR: cannot update EN/PT Research pages: {exc}", file=sys.stderr)
        return 1

    for page, (source, result) in changes.items():
        label = page.relative_to(ROOT)
        if result == source:
            print(f"{label}: already up to date; no file changed.")
        else:
            page.write_text(result, encoding="utf-8")
            print(f"Updated {label} (marked regions only).")

    for category in ("publication", "patent", "software", "data"):
        count = sum(f.get("category") == category for _, _, f in entries)
        print(f"{category}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
