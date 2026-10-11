# AIMS Research Catalogue — Data Contract

This directory holds the canonical, human-maintained bibliography for the AIMS (Artificial Intelligence and Multimodal Signal Processing) website at UNICAMP.

**Canonical file:** `research/aims.bib`

**Status:** This contract documents the recovered `aims.bib` catalogue (68 entries). It is a baseline for maintenance and future validation, **not** evidence that every bibliographic fact or the LaTeX workflow has already been verified.

## 1. Design principles

- **LaTeX first.** Preserve working BibTeX conventions, citation keys, TeX escapes, protected capitalization, and legitimate standard or custom bibliographic fields.
- **One source of truth.** Research website pages will be generated from `aims.bib`; do not maintain a second bibliography in HTML.
- **No invented metadata.** An absent or unverified DOI, URL, affiliation, or identifier stays absent until confirmed.
- **Minimal metadata.** The website uses a small number of explicit classification fields, without inferring scientific meaning from the BibTeX entry type.
- **Predictable builds.** Future Python scripts should validate or generate deterministically, and should not silently rewrite this source file.

## 2. Classification fields

All 68 entries in the recovered catalogue have `category` and `tags`. Publication entries also have `subtype`.

### `category` — output family

The current allowed values are:

| Value | Current entries | Public Research section |
| --- | ---: | --- |
| `publication` | 63 | Publications |
| `patent` | 3 | Patents |
| `software` | 1 | Software |
| `data` | 1 | Data |

**Projects** is a public Research section, but is **not** a `category` in this recovered BibTeX. Its data source remains to be decided; do not create project entries or a new category by assumption.

### `subtype` — publication type

`subtype` is required for `category = {publication}` under the recovered contract. Current values:

| Value | Meaning | Current entries |
| --- | --- | ---: |
| `conference-paper` | Conference contribution, including some proceedings chapters | 27 |
| `journal-article` | Journal article | 14 |
| `msc` | Master's dissertation | 16 |
| `phd` | Doctoral thesis | 4 |
| `tcc` | Undergraduate final project | 2 |

Do not infer `subtype` solely from `@article`, `@inproceedings`, `@misc`, etc. The source intentionally uses types such as `@misc` for some dissertations and patents. Entries in `patent`, `software`, and `data` currently have no `subtype`; do not require one for them.

Other academic outputs, such as selected undergraduate research reports, may need future decisions. Do not invent a new subtype without reviewing the vocabulary and the LaTeX implications.

### `tags` — scientific topics

`tags` contains one or more comma-separated **topic identifiers**. Identifiers are English, lowercase, and hyphen-separated, and are **not translated** between the English and Portuguese websites.

The recovered controlled vocabulary contains **19** values:

```text
affective-computing
climate-resilience
cognitive-architectures
data-visualization
digital-cultural-heritage
environmental-modeling
facial-analysis
facial-animation
gesture-synthesis
image-processing
inertial-sensing
natural-language-processing
social-robotics
spectral-imaging
speech-processing
stem-education
time-series-analysis
trustworthy-ai
world-models
```

Use the closest existing topic when it accurately describes the work. Propose new topic identifiers deliberately; avoid synonyms and using output types (`dataset`, `conference-paper`, etc.) as topic tags. Multiple tags are allowed.

The website may translate **display labels** for these identifiers, but should not alter the identifiers stored in the BibTeX.

## 3. Example records

These examples illustrate the classification fields; the full bibliographic fields of a real entry must be kept intact.

```bibtex
@article{example-journal,
  author   = {First Author and Second Author},
  title    = {An Example Article},
  journal  = {Example Journal},
  year     = {2026},
  category = {publication},
  subtype  = {journal-article},
  tags     = {affective-computing, speech-processing}
}

@misc{example-data,
  author   = {First Author},
  title    = {An Example Dataset},
  year     = {2026},
  category = {data},
  tags     = {natural-language-processing}
}
```

The `example-*` keys above are **illustrative only** and are not records to add to `aims.bib`.

## 4. DOI, URL and optional demo links

A publication can have **both** a persistent bibliographic identifier and a separate project or demo page. These are independent resources.

| Field | Purpose |
| --- | --- |
| `doi` | Persistent identifier of the output (DOI string). |
| `url` | Verified bibliographic landing page or repository URL. |
| `demo` | Optional, independent project, companion or demo page. |

Example (abbreviated; do not replace the real record with this snippet):

```bibtex
@inproceedings{ueda2025crossmodalser,
  ...
  doi      = {10.21437/Interspeech.2025-2014},
  demo     = {https://example.org/},
  category = {publication},
  subtype  = {conference-paper},
  tags     = {affective-computing, speech-processing}
}
```

### Website display rules

- When `doi` exists, the publication title links to `https://doi.org/<doi>`. Otherwise, the title links to `url` when available; otherwise, it is plain text.
- Show **DOI** and **Demo** as separate links when both are available. Do not replace one with the other.
- A `demo` link may exist without a DOI; the reverse is also valid.
- External links open in new tabs (`target="_blank" rel="noopener noreferrer"`).
- The generator must escape HTML and validate URL schemes; never invent links.
- The `demo` field is optional and website-specific. Traditional BibTeX styles such as `plain.bst` normally ignore unknown fields, but verify with the actual LaTeX workflow.

**Temporary test values:** `ueda2025crossmodalser` and `tonoli2023diffusiongesture` currently use `demo = {https://example.org/}`. This is a generic example page, **not a real demo**. Replace these URLs with verified project pages or remove the fields **before publishing**.

## 5. Bibliographic fields and compatibility

The recovered entries all have `author`, `title`, and `year`. Additional fields vary by publication type and may include `journal`, `booktitle`, `pages`, `school`, `publisher`, `doi`, `url`, `version`, `note`, and patent-specific fields such as `holder`, `institution`, `date`, or `number`.

- Preserve existing citation keys when correcting a record. Renaming a key may break LaTeX documents that cite it.
- Preserve TeX accent escapes and capitalization braces, such as `{SILFA}` and `Jos{\'e}`, unless a change has been explicitly tested.
- Do not replace existing date macros or formatting conventions automatically; the catalogue contains both braced values and bare macros such as `may` and `sep`.
- Do not add speculative URLs. Prefer verified DOI resolver URLs, repositories, or persistent identifiers when available.
- Custom classification fields are used by the website; their exact behavior with a given BibTeX or BibLaTeX style must be tested in the **actual** LaTeX toolchain. This README does not claim that compatibility has already been proven.
- BibTeX entry types are bibliographic syntax, **not** the authority for the website's `category` or `subtype`.

## 6. Scope and inclusion

The recovered file describes itself as an **initial migrated catalogue** of AIMS research outputs. However, the rule for including historical, pre-AIMS, or externally coauthored work has **not yet been formally settled in this project**.

For now:

1. Treat the recovered 68 records as the existing curated baseline, not as a definitive institutional eligibility ruling.
2. Confirm that a new output belongs in the AIMS catalogue before adding it.
3. Do not import all records from `pdpcosta.bib` automatically: that file also contains references cited in other documents.
4. Keep ambiguous candidate records outside the published catalogue until their identity and inclusion are resolved.

The source header mentions `pending.bib` and `migration-audit.json`, but those files were **not recovered with this copy**. Do not assume they exist locally or reconstruct their contents from guesswork.

## 7. How to add or correct an entry

1. Verify the output's identity and its eligibility for inclusion.
2. Choose a unique, stable citation key and a suitable BibTeX entry type.
3. Enter accurate bibliographic metadata; preserve the conventions already used in the file.
4. Set exactly one `category` from the approved values.
5. If `category = {publication}`, set one approved `subtype`.
6. Add one or more `tags` from the controlled topic vocabulary.
7. Add DOI, URL, repository links, and optional `demo` links **only when verified**. The two `example.org` demo URLs in this test version are temporary placeholders and must not be published as real demos.
8. Check for duplicate works and duplicate citation keys.
9. Validate the bibliography and test it with the lab's actual LaTeX compilation workflow before publishing.
10. Once the Research generator exists, regenerate EN/PT pages and review the output. Do not manually edit generated catalogue sections.

## 8. Website generation and maintenance

Planned pipeline:

```text
research/aims.bib
       |
       +--> tools/check_research.py  (implemented; validation only)
       |
       +--> tools/build_research.py  (planned; generated HTML only)
                         |
                         +--> research/index.html
                         +--> pt/research/index.html
```

`check_research.py` is implemented and has passed the current structural check; `build_research.py` remains planned. When implemented, the generator should update only explicitly delimited generated regions and preserve the surrounding manually maintained HTML.

The navigation validator already used by the site is separate:

```bash
python3 tools/check_navigation.py
```

It checks navigation structure, **not** bibliographic correctness.

## 9. Open decisions before the first Research build

- Define the institutional inclusion rule, especially for historical work.
- Confirm the exact LaTeX engine, bibliography backend, and styles that must remain compatible.
- Review the unresolved bibliographic uncertainties noted in comments within `aims.bib`.
- Decide the source and format for **Projects**.
- Decide how topic tags relate to People keywords and how public display labels will be translated.
- Publications: one chronological list, newest year first; show 10 initially and reveal 10 more per click (minimal JavaScript with all entries accessible without JavaScript). Use small colored subtype labels, without separate subtype sections. Patents, software, and data remain separate sections.

**Maintenance rule:** change the source data intentionally; never silently "clean up" the bibliography for presentation convenience.
