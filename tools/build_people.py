from pathlib import Path
import html
import re

import yaml


ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "people" / "data"
PHOTO_DIR = ROOT / "assets" / "people"

EN_PAGE = ROOT / "people" / "index.html"
PT_PAGE = ROOT / "pt" / "people" / "index.html"

START_MARKER = "<!-- PEOPLE:START -->"
END_MARKER = "<!-- PEOPLE:END -->"

VALID_GROUPS = {
    "senior",
    "phd",
    "msc",
    "undergraduate",
    "alumni",
}

SENIOR_ORDER = {
    "head": 0,
    "postdoc": 1,
    "associate": 2,
}


def read_profile(path):
    text = path.read_text(encoding="utf-8")

    match = re.match(
        r"^---\s*\n(.*?)\n---(?:\s*\n)?",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(f"{path}: missing YAML front matter")

    data = yaml.safe_load(match.group(1))

    if not isinstance(data, dict):
        raise ValueError(f"{path}: invalid YAML front matter")

    data["_source"] = path.name
    validate_profile(data)

    return data


def validate_profile(person):
    source = person["_source"]

    for field in ("name", "group", "role_en", "role_pt"):
        if not person.get(field):
            raise ValueError(
                f"{source}: required field '{field}' is missing"
            )

    if person["group"] not in VALID_GROUPS:
        raise ValueError(
            f"{source}: invalid group '{person['group']}'"
        )

    photo = person.get("photo")

    if photo:
        photo_path = PHOTO_DIR / photo

        if not photo_path.is_file():
            raise ValueError(
                f"{source}: photo not found: {photo}"
            )


def load_people():
    return [
        read_profile(path)
        for path in sorted(DATA_DIR.glob("*.md"))
    ]


def sort_people(people):
    def key(person):
        if person["group"] == "senior":
            return (
                SENIOR_ORDER.get(person.get("role_key"), 99),
                person["name"].casefold(),
            )

        return person["name"].casefold()

    return sorted(people, key=key)


def render_photo(person, lang):
    name = html.escape(person["name"])
    photo = person.get("photo")

    if photo:
        prefix = "../" if lang == "en" else "../../"

        src = (
            prefix
            + "assets/people/"
            + html.escape(photo, quote=True)
        )

        return f"""
<div class="person-photo">
  <img src="{src}" alt="{name}">
</div>""".strip()

    initials = "".join(
        part[0]
        for part in person["name"].split()
        if part
    )[:2].upper()

    return f"""
<div class="person-photo person-photo-placeholder">
  <span>{html.escape(initials)}</span>
</div>""".strip()


def render_links(person):
    fields = (
        ("homepage", "Homepage"),
        ("orcid", "ORCID"),
        ("github", "GitHub"),
        ("scholar", "Scholar"),
        ("lattes", "Lattes"),
    )

    links = []

    for field, label in fields:
        url = person.get(field)

        if url:
            links.append(
                f'<a href="{html.escape(str(url), quote=True)}">'
                f"{label}</a>"
            )

    if not links:
        return ""

    return (
        '<p class="person-links">'
        + "\n".join(links)
        + "</p>"
    )


def render_keywords(person):
    keywords = person.get("keywords", [])

    if not keywords:
        return ""

    tags = "\n".join(
        '<span class="person-keyword">'
        + html.escape(str(keyword))
        + "</span>"
        for keyword in keywords
    )

    return f"""
<div class="person-keywords">
  {tags}
</div>
""".strip()


def render_person(person, lang):
    name = html.escape(person["name"])
    role = html.escape(person[f"role_{lang}"])

    return f"""
<article class="person-card">
  {render_photo(person, lang)}

  <h2 class="person-name">{name}</h2>

  <p class="person-role">{role}</p>

  {render_keywords(person)}

  {render_links(person)}
</article>
""".strip()


def render_group(title, people, lang, show_title=True):
    cards = "\n\n".join(
        render_person(person, lang)
        for person in people
    )

    label = ""

    if show_title:
        label = (
            f'<p class="section-label">'
            f"{html.escape(title)}"
            f"</p>"
        )

    featured_class = (
        " people-grid-featured"
        if not show_title
        else ""
    )

    return f"""
<section class="people-group">
  {label}

  <div class="people-grid{featured_class}">
    {cards}
  </div>
</section>
""".strip()


def render_people(people, lang):
    groups = {
        "senior": "AIMS",
        "phd": "PhD",
        "msc": "MSc",
        "undergraduate": (
            "Undergraduate Research"
            if lang == "en"
            else "Iniciação Científica"
        ),
        "alumni": "Alumni",
    }

    sections = []

    for group, title in groups.items():
        members = [
            person
            for person in people
            if person["group"] == group
        ]

        if not members:
            continue

        sections.append(
            render_group(
                title=title,
                people=sort_people(members),
                lang=lang,
                show_title=(group != "senior"),
            )
        )

    return "\n\n".join(sections)


def replace_generated_region(page, generated):
    text = page.read_text(encoding="utf-8")

    if START_MARKER not in text or END_MARKER not in text:
        raise ValueError(
            f"{page}: PEOPLE markers not found"
        )

    before, rest = text.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)

    result = (
        before
        + START_MARKER
        + "\n\n"
        + generated
        + "\n\n"
        + END_MARKER
        + after
    )

    page.write_text(result, encoding="utf-8")


def main():
    people = load_people()

    replace_generated_region(
        EN_PAGE,
        render_people(people, "en"),
    )

    replace_generated_region(
        PT_PAGE,
        render_people(people, "pt"),
    )

    print(
        f"Generated People pages for "
        f"{len(people)} profiles."
    )


if __name__ == "__main__":
    main()