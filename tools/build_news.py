#!/usr/bin/env python3
"""Generate AIMS News EN/PT HTML and RSS from bilingual Markdown.

Usage: python3 tools/build_news.py [--check] [--site-url URL]

Only NEWS:START/END regions of News index pages are modified. Source
Markdown is never changed. Long articles have separate generated pages.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    import yaml
    import markdown
except ImportError as exc:
    sys.exit(f"Missing Python dependency ({exc}). Install PyYAML and Markdown; see news/README.md")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'news' / 'data'
START, END = '<!-- NEWS:START -->', '<!-- NEWS:END -->'
LONG_LIMIT = 1000
DEFAULT_SITE = 'https://ai-unicamp.github.io'
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}(?:-\d{2})?$')
SLUG_PATTERN = re.compile(r'^\d{4}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$')
LANG_SPLIT = re.compile(r'(?m)^## (EN|PT)\s*$')


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        return ' '.join(' '.join(self.parts).split())


def to_html(md):
    rendered = markdown.markdown(md, extensions=['extra', 'sane_lists'])
    return re.sub(r'<a href="(https?://[^"]+)"',
                  r'<a target="_blank" rel="noopener noreferrer" href="\1"', rendered)


def plain(md):
    parser = PlainText()
    parser.feed(to_html(md))
    return parser.text()


def read_post(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'{path.name}: missing YAML front matter')
    try:
        header, body = text[4:].split('\n---\n', 1)
    except ValueError:
        raise ValueError(f'{path.name}: missing closing YAML delimiter') from None
    meta = yaml.safe_load(header)
    if not isinstance(meta, dict):
        raise ValueError(f'{path.name}: front matter must be a mapping')
    slug = path.stem
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f'{path.name}: expected YYYY-MM-slug.md')
    for field in ('date', 'title_en', 'title_pt'):
        if not meta.get(field):
            raise ValueError(f'{path.name}: missing {field}')
    raw_date = meta['date']
    if isinstance(raw_date, (date, datetime)):
        raw_date = raw_date.isoformat()[:10]
    raw_date = str(raw_date)
    if not DATE_PATTERN.fullmatch(raw_date):
        raise ValueError(f'{path.name}: date must be YYYY-MM or YYYY-MM-DD')
    try:
        date.fromisoformat(raw_date if len(raw_date) == 10 else raw_date + '-01')
    except ValueError as exc:
        raise ValueError(f'{path.name}: invalid date') from exc
    if not raw_date.startswith(slug[:7]):
        raise ValueError(f'{path.name}: date month disagrees with filename')
    sections = list(LANG_SPLIT.finditer(body))
    if len(sections) != 2 or [m.group(1) for m in sections] != ['EN', 'PT']:
        raise ValueError(f"{path.name}: expected exactly '## EN' then '## PT'")
    if body[:sections[0].start()].strip():
        raise ValueError(f'{path.name}: unexpected text before ## EN')
    content = {
        'en': body[sections[0].end():sections[1].start()].strip(),
        'pt': body[sections[1].end():].strip(),
    }
    if not all(content.values()):
        raise ValueError(f'{path.name}: both languages need content')
    is_long = any(len(plain(content[lang])) > LONG_LIMIT for lang in ('en', 'pt'))
    if is_long and not all(meta.get(f'tldr_{lang}') for lang in ('en', 'pt')):
        raise ValueError(f'{path.name}: long post requires tldr_en and tldr_pt')
    if meta.get('type', 'news') != 'news':
        raise ValueError(f'{path.name}: only type=news is supported here')
    img = meta.get('image')
    if img is not None and (not isinstance(img, str) or not img.startswith('/news/images/') or '..' in img):
        raise ValueError(f'{path.name}: image must be a local /news/images/... path')
    return {'slug': slug, 'date': raw_date, 'meta': meta, 'content': content, 'long': is_long}


def date_label(value, lang):
    months_en = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    months_pt = ('janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro')
    y, m = int(value[:4]), int(value[5:7])
    if len(value) == 7:
        return f'{months_en[m-1]} {y}' if lang == 'en' else f'{months_pt[m-1]} de {y}'
    day = int(value[8:10])
    return f'{months_en[m-1]} {day}, {y}' if lang == 'en' else f'{day} de {months_pt[m-1]} de {y}'


def permalink(post, lang):
    prefix = '/news/' if lang == 'en' else '/pt/news/'
    return prefix + (f"posts/{post['slug']}/" if post['long'] else f"#{post['slug']}")


def image_html(post, lang):
    img = post['meta'].get('image')
    if not img or not (ROOT / img.lstrip('/')).is_file():
        return ''
    alt = post['meta'].get(f'image_alt_{lang}') or post['meta'][f'title_{lang}']
    return f'<figure class="news-figure"><img loading="lazy" src="{escape(img, quote=True)}" alt="{escape(str(alt), quote=True)}"></figure>'


def render_article(post, lang):
    title = escape(str(post['meta'][f'title_{lang}']))
    href = escape(permalink(post, lang), quote=True)
    label = escape(date_label(post['date'], lang))
    body = (f"<p>{escape(str(post['meta'][f'tldr_{lang}']))}</p>" if post['long']
            else to_html(post['content'][lang]))
    more = (f'<p class="news-links"><a href="{href}">'
            + ('Read more ↗' if lang == 'en' else 'Leia mais ↗')
            + '</a></p>') if post['long'] else ''
    return (f'<article class="news-entry" id="{post["slug"]}">\n'
            f'  <p class="news-meta">{label}</p>\n'
            f'  <h2 class="news-title"><a href="{href}">{title}</a></h2>\n'
            f'  <div class="news-body">{body}</div>\n'
            f'  {more}\n'
            f'  {image_html(post, lang)}\n'
            f'</article>')


def render_long_page(post, lang, template):
    title = escape(str(post['meta'][f'title_{lang}']))
    label = escape(date_label(post['date'], lang))
    back = '← Back to news' if lang == 'en' else '← Voltar às notícias'
    prefix = '/news/' if lang == 'en' else '/pt/news/'
    content = (f'<main>\n  <section class="hero page-hero news-page-hero">'
               f'<p class="eyebrow institutional-line">AIMS · '
               f'<a href="https://www.fee.unicamp.br/">FEEC</a> · '
               f'<a href="https://www.unicamp.br/">UNICAMP</a></p>'
               f'<h1>{title}</h1></section>\n'
               f'<article class="news-long-article">'
               f'<p class="news-meta">{label}</p>'
               f'<div class="news-body">{to_html(post["content"][lang])}</div>'
               f'{image_html(post, lang)}'
               f'<p class="news-links"><a href="{prefix}">{back}</a></p>'
               f'</article>\n</main>')
    result, count = re.subn(r'<main>.*?</main>', lambda _: content, template, count=1, flags=re.S)
    if count != 1:
        raise ValueError('News HTML template must contain exactly one <main>')
    result = result.replace('<!-- GENERATED: AIMS NEWS INDEX -->', '<!-- GENERATED: AIMS NEWS LONG POST -->')
    result = re.sub(r'<title>.*?</title>', f'<title>{title} · AIMS</title>', result, count=1)
    for language, path in [('en', '/news/'), ('pt-BR', '/pt/news/')]:
        link = path + f"posts/{post['slug']}/"
        result = re.sub(r'href="' + re.escape(path) + r'"(\s+lang="' + language + r'")',
                        lambda m: f'href="{link}"{m.group(1)}', result)
    return result


def replace_generated(html, entries):
    if html.count(START) != 1 or html.count(END) != 1:
        raise ValueError('Expected exactly one NEWS:START and NEWS:END marker in each News index')
    left, remainder = html.split(START, 1)
    _, right = remainder.split(END, 1)
    return left + START + '\n' + entries + '\n' + END + right


def rss(posts, lang, site_url):
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    root = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(root, 'channel')
    prefix = '/news/' if lang == 'en' else '/pt/news/'
    for name, value in (
        ('title', 'AIMS News' if lang == 'en' else 'AIMS Notícias'),
        ('link', site_url + prefix),
        ('description', 'Research news from AIMS at UNICAMP' if lang == 'en'
         else 'Notícias de pesquisa do AIMS na UNICAMP'),
        ('language', 'en-US' if lang == 'en' else 'pt-BR'),
    ):
        ET.SubElement(channel, name).text = value
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {
        'href': site_url + prefix + 'feed.xml', 'rel': 'self',
        'type': 'application/rss+xml',
    })
    for post in posts:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = str(post['meta'][f'title_{lang}'])
        ET.SubElement(item, 'link').text = site_url + permalink(post, lang)
        ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = 'urn:aims:news:' + post['slug']
        description = (str(post['meta'][f'tldr_{lang}']) if post['long']
                       else plain(post['content'][lang]))
        ET.SubElement(item, 'description').text = description
        ET.SubElement(item, 'category').text = 'News'
        if len(post['date']) == 10:
            d = date.fromisoformat(post['date'])
            timestamp = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            ET.SubElement(item, 'pubDate').text = format_datetime(timestamp, usegmt=True)
        # Month-only dates deliberately omit pubDate: no invented day.
    ET.indent(root, space='  ')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode') + '\n'


def sync(path, content, check, changes):
    previous = path.read_text(encoding='utf-8') if path.exists() else None
    if previous == content:
        return
    changes.append(path.relative_to(ROOT).as_posix())
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify outputs without writing')
    parser.add_argument('--site-url', default=DEFAULT_SITE, help='canonical public origin for RSS links')
    args = parser.parse_args()
    site_url = args.site_url.rstrip('/')
    if not site_url.startswith('https://'):
        parser.error('--site-url must begin with https://')
    try:
        posts = [read_post(path) for path in sorted(DATA.glob('*.md'))]
        if len(posts) != len({post['slug'] for post in posts}):
            raise ValueError('duplicate post slugs')
        posts.sort(key=lambda post: (post['date'], post['slug']), reverse=True)
        changes = []
        for lang in ('en', 'pt'):
            page = ROOT / ('news/index.html' if lang == 'en' else 'pt/news/index.html')
            template = page.read_text(encoding='utf-8')
            entries = '\n'.join(render_article(post, lang) for post in posts)
            sync(page, replace_generated(template, entries), args.check, changes)
            feed = ROOT / ('news/feed.xml' if lang == 'en' else 'pt/news/feed.xml')
            sync(feed, rss(posts, lang, site_url), args.check, changes)
            for post in posts:
                if post['long']:
                    long_path = ROOT / ('news/posts' if lang == 'en' else 'pt/news/posts') / post['slug'] / 'index.html'
                    if long_path.exists() and '<!-- GENERATED: AIMS NEWS LONG POST -->' not in long_path.read_text(encoding='utf-8'):
                        raise ValueError(f'Refusing to overwrite non-generated page: {long_path}')
                    sync(long_path, render_long_page(post, lang, template), args.check, changes)
        for post in posts:
            img = post['meta'].get('image')
            if img and not (ROOT / img.lstrip('/')).is_file():
                print(f'NOTE: optional image missing, omitted: {img}')
        if changes:
            for path in changes:
                print(('OUTDATED' if args.check else 'UPDATED') + ': ' + path)
            if args.check:
                print(f'FAIL: {len(changes)} output(s) need regeneration.')
                return 1
        print(f'PASS: {len(posts)} bilingual news item(s); EN/PT HTML and RSS up to date.')
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
