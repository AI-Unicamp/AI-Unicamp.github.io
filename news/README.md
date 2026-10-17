# AIMS News — maintenance contract (pilot)

News is published as static HTML generated from **one bilingual Markdown file per item**. No CMS, Jekyll or database is involved.

## Content model

Add `news/data/YYYY-MM-identifier.md` with YAML front matter followed by `## EN` and `## PT` Markdown sections:

```markdown
---
date: "2026-10-14"          # YYYY-MM-DD preferred; YYYY-MM accepted if day unknown
type: news
title_en: "Example news title"
title_pt: "Título de exemplo"
# image: /news/images/2026-10-example.jpg   # optional local image
# image_alt_en: "..."                      # describe the image
# image_alt_pt: "..."
# tldr_en: "..."                            # required for long posts
# tldr_pt: "..."
---

## EN

English body in Markdown.

## PT

Corpo em português, em Markdown.
```

- The filename (slug) is a permanent identifier. Do not rename a published item casually.
- `date` determines chronological order; month-only dates display as a month, **without inventing a day**. RSS omits `pubDate` for month-only entries.
- If the plain-text body in **either language** exceeds 1,000 characters, both languages require `tldr_en` and `tldr_pt`. The generator creates separate EN/PT article pages for the complete text. Short news is displayed in full on the listing.
- The same `type: news` source feeds News EN/PT and RSS EN/PT. Positions and Press & Media are separate sections, not part of this feed.
- Images are optional and local. If a referenced image is missing, the generator prints a note and omits it instead of showing a broken image. Images preserve their proportions and are height-limited by CSS; no automatic cropping.
- Review all titles, text, dates, alt text, links and rights to images before publishing. Existing SIBGRAPI and Interspeech entries were reconstructed from an earlier News HTML snapshot; the PT text is an editorial translation to review.

## Commands

From the repository root:

```bash
python3 tools/build_news.py
python3 tools/build_news.py --check
```

Dependencies: `PyYAML` and `Markdown`, documented in the root `requirements.txt`. The user environment may use APT packages instead of pip; no virtual environment is required by the project.

The builder updates only the `<!-- NEWS:START -->` / `<!-- NEWS:END -->` regions in `news/index.html` and `pt/news/index.html`, creates long-post pages when needed, and writes `news/feed.xml` and `pt/news/feed.xml`. Other pages and sources are not modified. `--check` returns exit code 1 when generated outputs are out of date and **never writes files**.

### Public domain

RSS currently uses `https://ai-unicamp.github.io` as the canonical origin. If the institutional domain is activated, use `--site-url https://aims.fee.unicamp.br` and update the documented deployment command. A consistent origin is essential for RSS links.

### Permanent links and the More button

Short news: `/news/#YYYY-MM-identifier` (or `/pt/news/#...`). Long news: `/news/posts/YYYY-MM-identifier/` (or PT equivalent). Each RSS item has a stable GUID based on the slug. The More button reveals five items per click; direct links to older short items reveal their batch automatically. Without JavaScript all news remains visible.

### About the initial two news items

The previous HTML contained image references:

- `/news/images/2026-09-sibgrapi.jpg`
- `/news/images/2026-09-interspeech.png`

**The image files themselves were not provided in this package.** Copy the actual images to `news/images/` when available, then rerun the generator. Until then, both news items remain readable without images.

### Navigation

News menu links are independent pages (`/news/`, `/news/positions/`, `/news/media/` and PT equivalents). Keep global navigation and `tools/check_navigation.py` synchronized when destinations change.

### Positions and media

`news/positions/` and `news/positions/archive/` (and PT equivalents) remain static placeholders. **Press & Media is now generated from one bilingual YAML file**, `news/media/media.yml`, by the same `tools/build_news.py`. The public LinkedIn link for positions is `https://www.linkedin.com/company/146693552/`, not the administrative analytics URL.

## Press & Media — bilingual editorial archive

`/news/media/` and `/pt/news/media/` are generated from **one** file:
`news/media/media.yml`. The **AIMS-authored** headline and summary follow the
selected language. The original publisher's title, outlet, link and language
are **never translated**. Only interface labels and date formatting vary.

Each item uses `id`, `date`, `outlet`, `kind`, `url`, `language`,
`headline_en`, `headline_pt`, `description_en`, `description_pt`, and `title`.
`date_display` is optional for original edition ranges. Example:

```yaml
- id: example-interview-2026
  date: '2026-10-16'
  outlet: Example Journal
  kind: expert-commentary
  language: pt
  url: https://example.org/interview
  headline_en: AIMS researcher discusses AI
  headline_pt: Pesquisadora do AIMS comenta inteligência artificial
  description_en: A short factual summary in English.
  description_pt: Um resumo factual e curto em português.
  title: Entrevista de exemplo
```

**Editorial policy:** lead with the documented AIMS connection, never exaggerate
participation, and limit each summary to **160 characters**. Use **Profa. Paula**
in PT editorial fields and **Prof. Paula** in EN editorial fields. The `title`
is always the original publication's title. See
`news/media/EDITORIAL_GUIDELINES.md` for the full policy and agent workflow.

**Dates:** `YYYY-MM-DD`, `YYYY-MM`, or `null` when unknown. Keep existing IDs
stable; they are permanent HTML anchors. The generator sorts newest first.

**To add a record:** append one item to the YAML, then run:

```bash
python3 tools/build_news.py
python3 tools/build_news.py --check
python3 tools/check_navigation.py
```

Only the regions between `<!-- MEDIA:START -->` and `<!-- MEDIA:END -->` are
updated in the two Press & Media pages. Latest News and RSS remain independent.
Review both languages before committing. Keep `.nojekyll` in the repo root.

The repository's `.nojekyll` file must remain at the root: GitHub Pages
should publish generated static HTML without Jekyll processing the data files.

### Manual maintenance reminder

Document the full publishing workflow, RSS, image handling, URL stability, `--check`, global navigation synchronization and Python dependencies in the future AIMS homepage maintenance manual.

**Future idea, not implemented:** consider a root `AGENTS.md` for repository-wide agent instructions when the broader maintenance manual is written. Do not create it as part of Press & Media.

**Press & Media editorial rule (Oct 2026):** Keep `description_en` and `description_pt` within 160 characters. Use **“Prof. Paula”** in EN and **“Profa. Paula”** in PT editorial fields. Never modify the original publisher `title`. The builder validates these conventions. See `news/media/EDITORIAL_GUIDELINES.md`.
