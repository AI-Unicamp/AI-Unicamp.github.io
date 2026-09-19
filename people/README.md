# AIMS People — Profile Guide

This document describes the standard format for AIMS member profiles.

The same profile structure is used regardless of how the files are submitted or stored. Keeping a consistent format allows member information to be incorporated automatically into the AIMS website and other internal workflows.

## Profile files

Each member profile consists of:

1. a Markdown file containing structured profile information;
2. an optional profile photograph.

Use a lowercase filename based on your name, with words separated by hyphens:

```text
firstname-lastname.md
```

For example:

```text
maria-silva.md
```

If you provide a photograph, use the same naming convention:

```text
maria-silva.jpg
```

JPG, JPEG, and PNG images are accepted.

The standard directory structure is:

```text
people/
└── data/
    └── maria-silva.md

assets/
└── people/
    └── maria-silva.jpg
```

---

## Profile format

Use the following template:

```yaml
---
name: Maria Silva
group: phd

role_en: PhD Researcher
role_pt: Doutoranda

photo: maria-silva.jpg

keywords:
  - speech
  - multimodal learning
  - generative models

homepage: https://...
orcid: https://...
github: https://...
scholar: https://...
lattes: https://...
---
```

Only include optional fields when they apply.

Do not include empty fields or placeholder URLs.

---

## Required fields

### `name`

Your preferred full name as it should appear publicly.

```yaml
name: Maria Silva
```

### `group`

Your current relationship with AIMS.

Currently supported values are:

```text
senior
phd
msc
undergraduate
alumni
```

Please use one of the existing values rather than creating a new group.

### `role_en` and `role_pt`

Your role as it should appear in the English and Portuguese versions of the AIMS website.

For example:

```yaml
role_en: PhD Researcher
role_pt: Doutoranda
```

or:

```yaml
role_en: MSc Researcher
role_pt: Mestrando
```

These fields describe your current academic role and are independent of your research interests.

---

## Photograph

Photographs are optional but encouraged.

Reference the photograph by filename:

```yaml
photo: maria-silva.jpg
```

Please provide:

- a JPG, JPEG, or PNG image;
- a reasonably high-resolution image;
- a photograph with some space around the face and head;
- an image you are comfortable having publicly displayed as part of your AIMS profile.

You do **not** need to crop the photograph to specific proportions. The website handles the visual crop automatically.

If no photograph is provided, the website can use a typographic placeholder.

---

## Research keywords

Keywords describe your current research interests.

For example:

```yaml
keywords:
  - speech
  - multimodal perception
  - representation learning
```

Please:

- use approximately 3–5 keywords;
- keep them concise;
- use English terms;
- reuse existing AIMS terminology whenever possible;
- avoid creating synonymous variants unless the distinction is scientifically meaningful.

For example, if `speech` is already used, avoid introducing `speech technologies` unless they represent meaningfully different concepts.

Keywords are structured information. They may be used to connect people with publications, theses, software, datasets, and other AIMS research outputs.

---

## Academic and professional links

The following fields are currently supported:

```yaml
homepage:
orcid:
github:
scholar:
lattes:
```

All are optional.

Only provide public profiles that you want associated with your AIMS profile.

For example:

```yaml
orcid: https://orcid.org/0000-0000-0000-0000
github: https://github.com/username
```

---

## Optional profile text

Additional Markdown content may be placed after the structured metadata:

```markdown
---
name: Maria Silva
...
---

Short profile text can appear here.
```

This section is optional and may not necessarily be displayed on the website.

---

## Updating a profile

The Markdown file is the canonical source for a member's public AIMS profile information.

When information changes, update the corresponding fields in the Markdown file.

If a photograph changes, replace the image while preserving the filename whenever practical.

Members should update **profile data**, not the generated website layout.

---

## How profiles are used

AIMS profile files are processed automatically to produce the public People pages.

Conceptually:

```text
member profile (.md)
        +
profile photograph
        ↓
AIMS profile processing
        ↓
English People page
Portuguese People page
```

The same structured profile information can also support future AIMS tools and research navigation.

---

## Design principle

Profile data and presentation are intentionally separated.

Members provide and maintain **their information**.

The AIMS infrastructure determines **how that information is presented**.

This keeps member profiles portable, consistent, and independent of any particular website, storage service, or external profile platform.