#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent


PAGES = {
    "EN home": ROOT / "index.html",
    "EN people": ROOT / "people" / "index.html",
    "EN research": ROOT / "research" / "index.html",
    "EN news": ROOT / "news" / "index.html",

    "PT home": ROOT / "pt" / "index.html",
    "PT people": ROOT / "pt" / "people" / "index.html",
    "PT research": ROOT / "pt" / "research" / "index.html",
    "PT news": ROOT / "pt" / "news" / "index.html",
}


COMMON_MARKERS = {
    "AIMS logo": 'src="/assets/identity/aims-logo.png"',
    "desktop navigation": 'class="site-nav desktop-nav"',
    "desktop language selector": 'class="utility-nav desktop-utility"',
    "mobile language selector": 'class="mobile-utility"',
    "mobile menu": 'class="mobile-menu"',
    "mobile menu content": 'class="mobile-menu-content"',
}


EN_MARKERS = {
    "Research": 'href="/research/"',
    "Projects": 'href="/research/#projects"',
    "Publications": 'href="/research/#publications"',
    "Patents": 'href="/research/#patents"',
    "Software": 'href="/research/#software"',
    "Data": 'href="/research/#data"',

    "News": 'href="/news/"',
    "Latest": 'href="/news/#latest"',
    "Open Positions": 'href="/news/#open-positions"',
    "Press & Media": 'href="/news/#press-media"',

    "People": 'href="/people/"',
}


PT_MARKERS = {
    "Pesquisa": 'href="/pt/research/"',
    "Projetos": 'href="/pt/research/#projects"',
    "Publicações": 'href="/pt/research/#publications"',
    "Patentes": 'href="/pt/research/#patents"',
    "Software": 'href="/pt/research/#software"',
    "Dados": 'href="/pt/research/#data"',

    "Notícias": 'href="/pt/news/"',
    "Novidades": 'href="/pt/news/#latest"',
    "Oportunidades": 'href="/pt/news/#open-positions"',
    "Press & Media": 'href="/pt/news/#press-media"',

    "Pessoas": 'href="/pt/people/"',
}


FORBIDDEN_MARKERS = {
    "obsolete mobile language block": 'class="mobile-language"',
}


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_file_exists(label: str, path: Path) -> list[str]:
    if path.exists():
        return []

    return [
        f"{label}: missing file {relative(path)}"
    ]


def check_markers(
    label: str,
    text: str,
    markers: dict[str, str],
) -> list[str]:

    errors = []

    for description, marker in markers.items():
        if marker not in text:
            errors.append(
                f"{label}: missing {description}"
            )

    return errors


def check_forbidden_markers(
    label: str,
    text: str,
) -> list[str]:

    errors = []

    for description, marker in FORBIDDEN_MARKERS.items():
        if marker in text:
            errors.append(
                f"{label}: contains {description}"
            )

    return errors


def check_language_pair(
    label: str,
    text: str,
    path: Path,
) -> list[str]:

    errors = []

    relative_path = relative(path)

    if relative_path == "index.html":
        expected_en = 'href="/"'
        expected_pt = 'href="/pt/"'

    elif relative_path == "people/index.html":
        expected_en = 'href="/people/"'
        expected_pt = 'href="/pt/people/"'

    elif relative_path == "research/index.html":
        expected_en = 'href="/research/"'
        expected_pt = 'href="/pt/research/"'

    elif relative_path == "news/index.html":
        expected_en = 'href="/news/"'
        expected_pt = 'href="/pt/news/"'

    elif relative_path == "pt/index.html":
        expected_en = 'href="/"'
        expected_pt = 'href="/pt/"'

    elif relative_path == "pt/people/index.html":
        expected_en = 'href="/people/"'
        expected_pt = 'href="/pt/people/"'

    elif relative_path == "pt/research/index.html":
        expected_en = 'href="/research/"'
        expected_pt = 'href="/pt/research/"'

    elif relative_path == "pt/news/index.html":
        expected_en = 'href="/news/"'
        expected_pt = 'href="/pt/news/"'

    else:
        return errors

    if expected_en not in text:
        errors.append(
            f"{label}: missing corresponding EN link"
        )

    if expected_pt not in text:
        errors.append(
            f"{label}: missing corresponding PT link"
        )

    return errors


def check_page(
    label: str,
    path: Path,
) -> list[str]:

    errors = []

    errors.extend(
        check_file_exists(label, path)
    )

    if not path.exists():
        return errors

    text = path.read_text(encoding="utf-8")

    errors.extend(
        check_markers(
            label,
            text,
            COMMON_MARKERS,
        )
    )

    if label.startswith("EN"):
        errors.extend(
            check_markers(
                label,
                text,
                EN_MARKERS,
            )
        )

    if label.startswith("PT"):
        errors.extend(
            check_markers(
                label,
                text,
                PT_MARKERS,
            )
        )

    errors.extend(
        check_forbidden_markers(
            label,
            text,
        )
    )

    errors.extend(
        check_language_pair(
            label,
            text,
            path,
        )
    )

    return errors


def main() -> int:

    print("Checking AIMS navigation...\n")

    all_errors = []

    for label, path in PAGES.items():

        errors = check_page(label, path)

        if errors:
            print(f"✗ {label}")
            all_errors.extend(errors)
        else:
            print(f"✓ {label}")

    print()

    if all_errors:

        print("Navigation check failed:\n")

        for error in all_errors:
            print(f"  - {error}")

        print(
            f"\n{len(all_errors)} problem(s) found."
        )

        return 1

    print(
        "Navigation check passed. "
        "All pages are consistent."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())