#!/usr/bin/env python3
"""Validate AIMS site navigation (EN/PT) without modifying files.

Usage: python3 tools/check_navigation.py

Checks all published index pages, desktop/mobile menus, language switchers,
local navigation destinations and section anchors. Standard library only.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT = Path(__file__).resolve().parent.parent

# Every page linked by the public site navigation, plus the positions archive.
PAGE_ROUTES = (
    "/", "/people/", "/research/", "/news/",
    "/news/positions/", "/news/positions/archive/", "/news/media/",
    "/pt/", "/pt/people/", "/pt/research/", "/pt/news/",
    "/pt/news/positions/", "/pt/news/positions/archive/", "/pt/news/media/",
)

RESEARCH_LINKS = (
    ("Research", "/research/"),
    ("Projects", "/research/#projects"),
    ("Publications", "/research/#publications"),
    ("Patents", "/research/#patents"),
    ("Software", "/research/#software"),
    ("Data", "/research/#data"),
)
NEWS_LINKS = (
    ("News", "/news/"),
    ("Latest News", "/news/"),
    ("Open Positions", "/news/positions/"),
    ("Press & Media", "/news/media/"),
)
PT_RESEARCH_LINKS = (
    ("Pesquisa", "/pt/research/"),
    ("Projetos", "/pt/research/#projects"),
    ("Publicações", "/pt/research/#publications"),
    ("Patentes", "/pt/research/#patents"),
    ("Software", "/pt/research/#software"),
    ("Dados", "/pt/research/#data"),
)
PT_NEWS_LINKS = (
    ("Notícias", "/pt/news/"),
    ("Novidades", "/pt/news/"),
    ("Oportunidades", "/pt/news/positions/"),
    ("Press & Media", "/pt/news/media/"),
)


def page_file(route: str) -> Path:
    return ROOT / route.lstrip("/") / "index.html"


def equivalent_routes(route: str) -> tuple[str, str]:
    if route.startswith("/pt/"):
        return "/" + route[4:], route
    if route == "/pt/":
        return "/", "/pt/"
    return route, "/pt" + route


class NavigationParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nav_stack: list[str | None] = []
        self.header_depth = 0
        self.anchors: list[dict] = []
        self.current_anchor: dict | None = None
        self.ids: set[str] = set()
        self.logo_link_found = False
        self.logo_image_found = False
        self.mobile_menu_found = False
        self.obsolete_mobile_language = False
        self.lang: str | None = None
        self.navs: dict[str, list[tuple[str, str]]] = {
            "desktop": [], "mobile": [], "desktop_language": [], "mobile_language": []
        }

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set(a.get("class", "").split())
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "header":
            self.header_depth += 1
        if self.header_depth:
            if "mobile-language" in classes:
                self.obsolete_mobile_language = True
            if tag == "details" and "mobile-menu" in classes:
                self.mobile_menu_found = True
            if tag == "a" and "site-logo" in classes and a.get("href") in ("/", "/pt/"):
                self.logo_link_found = True
            if tag == "img" and a.get("src") == "/assets/identity/aims-logo.png":
                self.logo_image_found = True
            if tag == "nav":
                kind = None
                if {"site-nav", "desktop-nav"} <= classes:
                    kind = "desktop"
                elif "mobile-menu-content" in classes:
                    kind = "mobile"
                elif {"utility-nav", "desktop-utility"} <= classes:
                    kind = "desktop_language"
                elif "mobile-utility" in classes:
                    kind = "mobile_language"
                self.nav_stack.append(kind)
            if tag == "a" and self.nav_stack and self.nav_stack[-1] is not None:
                self.current_anchor = {"nav": self.nav_stack[-1], "href": a.get("href", ""), "text": []}

    def handle_data(self, data):
        if self.current_anchor is not None:
            self.current_anchor["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_anchor is not None:
            a = self.current_anchor
            label = " ".join("".join(a["text"]).split())
            self.navs[a["nav"]].append((label, a["href"]))
            self.current_anchor = None
        if tag == "nav" and self.header_depth and self.nav_stack:
            self.nav_stack.pop()
        if tag == "header" and self.header_depth:
            self.header_depth -= 1


def check_navigation(route: str, cache: dict[str, NavigationParser]) -> list[str]:
    page = cache[route]
    errors = []
    pt = route.startswith("/pt/")
    en_route, pt_route = equivalent_routes(route)
    expected_main = list(PT_RESEARCH_LINKS + PT_NEWS_LINKS + (("Pessoas", "/pt/people/"),)) if pt else list(
        RESEARCH_LINKS + NEWS_LINKS + (("People", "/people/"),)
    )
    expected_lang = [("EN", en_route), ("PT", pt_route)]
    for name, expected in (("desktop", expected_main), ("mobile", expected_main),
                           ("desktop_language", expected_lang), ("mobile_language", expected_lang)):
        actual = page.navs[name]
        if actual != expected:
            # Show the first mismatch to keep diagnostics readable.
            from itertools import zip_longest
            for index, (found, want) in enumerate(zip_longest(actual, expected), 1):
                if found != want:
                    errors.append(f"{name} navigation link #{index}: expected {want!r}, got {found!r}")
                    break
    if page.lang != ("pt-BR" if pt else "en"):
        errors.append(f"incorrect HTML language: {page.lang!r}")
    if not page.logo_link_found or not page.logo_image_found:
        errors.append("missing AIMS home logo link or image")
    if not page.mobile_menu_found:
        errors.append("missing mobile + menu")
    if page.obsolete_mobile_language:
        errors.append("obsolete language selector inside mobile menu")

    # Every internal menu destination must exist; #fragment must identify a real element.
    for name in ("desktop", "mobile", "desktop_language", "mobile_language"):
        for label, href in page.navs[name]:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                errors.append(f"external URL in navigation: {href}")
                continue
            dest = unquote(parsed.path)
            if dest not in cache:
                errors.append(f"{label}: destination {dest!r} is missing")
            elif parsed.fragment and unquote(parsed.fragment) not in cache[dest].ids:
                errors.append(f"{label}: anchor #{parsed.fragment} missing at {dest}")
    return errors


def main() -> int:
    print("Checking AIMS navigation...\n")
    cache: dict[str, NavigationParser] = {}
    errors: dict[str, list[str]] = {}
    for route in PAGE_ROUTES:
        path = page_file(route)
        if not path.is_file():
            errors[route] = [f"missing {path.relative_to(ROOT)}"]
            continue
        try:
            parser = NavigationParser()
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
            cache[route] = parser
        except (OSError, UnicodeError, ValueError) as exc:
            errors[route] = [f"cannot read/parse HTML: {exc}"]

    for route in PAGE_ROUTES:
        if route in cache:
            problems = check_navigation(route, cache)
            if problems:
                errors[route] = problems
        if route in errors:
            print(f"✗ {route}")
        else:
            print(f"✓ {route}")

    if errors:
        print("\nNavigation check FAILED:\n")
        for route, problems in errors.items():
            for issue in problems:
                print(f"  - {route}: {issue}")
        print(f"\n{sum(len(x) for x in errors.values())} problem(s) found.")
        return 1

    print(f"\nNavigation check passed. All {len(PAGE_ROUTES)} pages are consistent.")
    print("No files modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
