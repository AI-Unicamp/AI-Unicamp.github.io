#!/usr/bin/env python3
"""Validate research/aims.bib without modifying it.

Usage (from any working directory):
    python3 tools/check_research.py

This is a structural and controlled-vocabulary check, NOT a LaTeX compilation
test, bibliographic fact-check, or institutional inclusion audit.
Only the Python standard library is required.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = ROOT / "research" / "aims.bib"

CATEGORIES = {"publication", "patent", "software", "data"}
PUBLICATION_SUBTYPES = {
    "conference-paper",
    "journal-article",
    "msc",
    "phd",
    "tcc",
}
TOPIC_TAGS = {
    "affective-computing",
    "climate-resilience",
    "cognitive-architectures",
    "data-visualization",
    "digital-cultural-heritage",
    "environmental-modeling",
    "facial-analysis",
    "facial-animation",
    "gesture-synthesis",
    "image-processing",
    "inertial-sensing",
    "natural-language-processing",
    "social-robotics",
    "spectral-imaging",
    "speech-processing",
    "stem-education",
    "time-series-analysis",
    "trustworthy-ai",
    "world-models",
}
TAG_FORMAT = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
YEAR_FORMAT = re.compile(r"^[0-9]{4}$")


class BibSyntaxError(ValueError):
    pass


class BibReader:
    """Read ordinary BibTeX entries, retaining the source unchanged.

    Handles nested braces, quoted strings, TeX escapes, numeric values,
    bare month macros and '#' concatenation. The checker never rewrites
    the bibliography. Advanced BibTeX constructs not encountered in the
    current catalogue should be tested before being added.
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def error(self, message: str) -> BibSyntaxError:
        line = self.text.count("\n", 0, self.pos) + 1
        return BibSyntaxError(f"line {line}: {message}")

    def skip_space(self) -> None:
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isspace():
                self.pos += 1
            elif ch == "%":
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end < 0 else end + 1
            else:
                break

    def expect(self, char: str) -> None:
        if self.pos >= len(self.text) or self.text[self.pos] != char:
            raise self.error(f"expected {char!r}")
        self.pos += 1

    def word(self) -> str:
        start = self.pos
        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] in "_-:"
        ):
            self.pos += 1
        if start == self.pos:
            raise self.error("expected identifier")
        return self.text[start:self.pos]

    def braced(self) -> str:
        self.expect("{")
        start = self.pos
        depth = 1
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == "\\":
                self.pos += 2  # escaped brace is not a delimiter
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    result = self.text[start:self.pos]
                    self.pos += 1
                    return result
            self.pos += 1
        raise self.error("unclosed braced value")

    def quoted(self) -> str:
        self.expect('"')
        start = self.pos
        depth = 0
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == "\\":
                self.pos += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    raise self.error("unbalanced braces in quoted value")
            elif ch == '"' and depth == 0:
                result = self.text[start:self.pos]
                self.pos += 1
                return result
            self.pos += 1
        raise self.error("unclosed quoted value")

    def value(self, closing: str) -> str:
        parts = []
        while True:
            self.skip_space()
            if self.pos >= len(self.text):
                raise self.error("missing field value")
            ch = self.text[self.pos]
            if ch == "{":
                parts.append(self.braced())
            elif ch == '"':
                parts.append(self.quoted())
            else:
                start = self.pos
                while self.pos < len(self.text) and (
                    not self.text[self.pos].isspace()
                    and self.text[self.pos] not in f",#{closing}"
                ):
                    self.pos += 1
                if self.pos == start:
                    raise self.error("missing or malformed field value")
                parts.append(self.text[start:self.pos])
            self.skip_space()
            if self.pos < len(self.text) and self.text[self.pos] == "#":
                self.pos += 1
                continue
            return "".join(parts).strip()

    def entries(self) -> list[tuple[str, str, dict[str, str]]]:
        found = []
        while True:
            self.skip_space()
            if self.pos >= len(self.text):
                return found
            self.expect("@")
            kind = self.word().lower()
            self.skip_space()
            if self.pos >= len(self.text) or self.text[self.pos] not in "{(":
                raise self.error("expected '{' or '(' after entry type")
            opener = self.text[self.pos]
            self.pos += 1
            closing = "}" if opener == "{" else ")"
            if kind in {"comment", "preamble", "string"}:
                raise self.error(
                    f"@{kind} requires explicit review; not used in the current catalogue"
                )
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos] != ",":
                if self.text[self.pos] == closing:
                    raise self.error("entry missing citation key separator ','")
                self.pos += 1
            key = self.text[start:self.pos].strip()
            if not key:
                raise self.error("empty citation key")
            self.expect(",")
            fields: dict[str, str] = {}
            while True:
                self.skip_space()
                if self.pos >= len(self.text):
                    raise self.error(f"unclosed entry {key}")
                if self.text[self.pos] == closing:
                    self.pos += 1
                    found.append((kind, key, fields))
                    break
                if self.text[self.pos] == ",":
                    self.pos += 1
                    continue
                name = self.word().lower()
                if name in fields:
                    raise self.error(f"{key}: duplicate field {name}")
                self.skip_space()
                self.expect("=")
                fields[name] = self.value(closing)
                self.skip_space()
                if self.pos < len(self.text) and self.text[self.pos] == ",":
                    self.pos += 1
                elif self.pos < len(self.text) and self.text[self.pos] == closing:
                    continue
                else:
                    raise self.error(f"{key}: expected ',' or {closing!r} after {name}")


def check(entries: list[tuple[str, str, dict[str, str]]]) -> list[str]:
    errors: list[str] = []
    seen_keys: set[str] = set()
    for kind, key, fields in entries:
        if key in seen_keys:
            errors.append(f"{key}: duplicate citation key")
        seen_keys.add(key)

        for name in ("author", "title", "year", "category", "tags"):
            if not fields.get(name, "").strip():
                errors.append(f"{key}: missing or empty {name}")

        year = fields.get("year", "")
        if year and not YEAR_FORMAT.fullmatch(year):
            errors.append(f"{key}: year must contain four digits (got {year!r})")

        category = fields.get("category", "").strip()
        if category and category not in CATEGORIES:
            errors.append(f"{key}: unknown category {category!r}")

        subtype = fields.get("subtype", "").strip()
        if category == "publication":
            if not subtype:
                errors.append(f"{key}: publication requires subtype")
            elif subtype not in PUBLICATION_SUBTYPES:
                errors.append(f"{key}: unknown publication subtype {subtype!r}")
        elif subtype:
            errors.append(f"{key}: subtype is only defined for publications")

        tags_raw = fields.get("tags", "")
        if tags_raw:
            tags = [t.strip() for t in tags_raw.split(",")]
            if len(tags) != len(set(tags)):
                errors.append(f"{key}: repeated topic tag")
            for tag in tags:
                if not TAG_FORMAT.fullmatch(tag):
                    errors.append(f"{key}: invalid topic tag format {tag!r}")
                elif tag not in TOPIC_TAGS:
                    errors.append(f"{key}: unknown topic tag {tag!r}")
    return errors


def main() -> int:
    print("Checking AIMS research catalogue...\n")
    if not BIB_PATH.is_file():
        print(f"ERROR: missing {BIB_PATH}")
        return 1
    try:
        entries = BibReader(BIB_PATH.read_text(encoding="utf-8")).entries()
    except (BibSyntaxError, UnicodeError) as exc:
        print(f"ERROR: could not parse {BIB_PATH.name}: {exc}")
        return 1
    errors = check(entries)
    if errors:
        print("Research check FAILED:\n")
        for error in errors:
            print(f"  - {error}")
        print(f"\n{len(errors)} problem(s) found.")
        return 1

    categories = Counter(fields["category"] for _, _, fields in entries)
    subtypes = Counter(fields.get("subtype", "") for _, _, fields in entries)
    print(f"PASS: {len(entries)} entries; unique citation keys.")
    print("Categories: " + ", ".join(f"{k}={v}" for k, v in sorted(categories.items())))
    print("Publication subtypes: " + ", ".join(
        f"{k}={v}" for k, v in sorted(subtypes.items()) if k
    ))
    print("PASS: required fields, controlled categories, subtypes and tags.")
    print("\nNo files modified. LaTeX compilation and bibliographic facts not checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
