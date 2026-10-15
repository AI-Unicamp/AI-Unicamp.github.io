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

### News navigation rollout

The new News pages link to `/news/`, `/news/positions/`, `/news/media/` and their PT equivalents. **Other site pages still contain the older News `#latest`, `#open-positions` and `#press-media` anchors.** Update their headers and `tools/check_navigation.py` together in a later, deliberate synchronization step; until then the existing navigation checker may report a mismatch. Do not publish the transition half-completed.

### Positions and media

`news/positions/`, `news/positions/archive/` and `news/media/` (and their PT equivalents) are currently **minimal static placeholders**, not generated from News Markdown. They should receive their own data contract only when actual records are ready. The public LinkedIn link is `https://www.linkedin.com/company/146693552/`, not the administrative analytics URL.

### Manual maintenance reminder

Document the full publishing workflow, RSS, image handling, URL stability, `--check`, global navigation synchronization and Python dependencies in the future AIMS homepage maintenance manual.
