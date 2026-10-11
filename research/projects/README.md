# AIMS Research Projects — content sources

This folder is the canonical source for the Projects section in **both** English and Portuguese. It describes AIMS contributions rather than all activities of partner centers.

## Record format

Each project has one `.md` file with a small metadata header followed by two plain-text sections, `## EN` and `## PT` (in this order). No external YAML/Markdown parser is needed.

```text
---
title: Project title in English
title_pt: Título do projeto em português
group: research
institutions: UNICAMP · Partner
institutions_pt: UNICAMP · Parceiro
url: https://example.org/
order: 10
featured: false
---

## EN

A short description of the AIMS contribution.

## PT

Uma descrição curta da contribuição do AIMS.
```

The example URL above illustrates syntax only; use a **real verified official URL** in records, or leave `url:` empty.

- `group`: `research`, `centers`, or `past`.
  - Display labels (EN / PT): `research` → **Ongoing / Em andamento**; `centers` → **Centers & Collaborations / Centros e colaborações**; `past` → **Completed / Concluídos**. These labels are presentation only; the stored group values do not change.
- `order`: nonnegative integer, smaller values appear first within a group.
- `featured`: `true` or `false`; use sparingly.
- `title`, `title_pt`: localized public titles. Keep official project acronyms.
- `institutions`, `institutions_pt`: short public institutional attribution.
- `url`: optional official link. The same link is used in both languages.
- `## EN`, `## PT`: one or more plain-text paragraphs, without Markdown links or HTML.

## Workflow

From the repository root:

```bash
python3 tools/build_projects.py
python3 tools/build_projects.py --check
python3 tools/check_navigation.py
```

The generator updates **only** the `<!-- PROJECTS:START -->` / `<!-- PROJECTS:END -->` region in `research/index.html` and `pt/research/index.html`. It does not modify the BibTeX catalogue, Publications, Patents, Software, Data, CSS, or JavaScript. The `--check` mode makes no changes and exits with a failure status if either page is stale.

## Editorial cautions

- The INSPIRE source documents describe a proposed UNICAMP–CPQD collaboration. Confirm its formal status before describing it as an ongoing, signed agreement.
- Verify participation and funding attributions before public release.
- Do not publish administrative plans, budgets, or internal agreements by default.
- Project and partner logos are not required.
