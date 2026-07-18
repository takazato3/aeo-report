#!/usr/bin/env python3
"""
ビルドスクリプト
==============
使い方:
  python build.py          # _src/*.html → ルートの *.html を生成
  python build.py --init   # 現在のルート *.html から _src/*.html を初期生成（初回のみ）

ルール:
  - ページ内容は _src/*.html を編集する
  - ヘッダー・フッターは _partials/header.html / footer.html を編集する
  - 編集後は必ず python build.py を実行してルートHTMLに反映させる
  - ルートの *.html は build.py の出力物なので直接編集しない
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / '_src'
PARTIALS_DIR = ROOT / '_partials'
TEMPLATES_DIR = ROOT / '_templates'
BLOG_POSTS_DIR = ROOT / 'blog' / 'posts'
BLOG_OUT_DIR = ROOT / 'blog'
BLOG_INDEX_SRC = SRC_DIR / 'blog_index.html'
BLOG_POST_TEMPLATE = TEMPLATES_DIR / 'blog_post.html'
LLMS_TXT_SRC = SRC_DIR / 'llms.txt'

SITE_BASE_URL = 'https://app.ops-octopus.com'
ORGANIZATION_JSONLD = {'@type': 'Organization', 'name': 'Ops Octopus'}

# ビルド対象ページ（quick-scan.html と preview.html はビルド管理対象外）
TARGET_PAGES = [
    'index.html',
    'detail.html',
    'samples.html',
    'legal.html',
    'faq.html',
    'privacy.html',
    'terms.html',
]

HEADER_MARKER = '<!-- HEADER -->'
FOOTER_MARKER = '<!-- FOOTER -->'
POSTS_MARKER = '<!-- POSTS -->'
JSONLD_MARKER = '{{JSONLD}}'
LLMS_BLOG_POSTS_MARKER = '<!-- LLMS_BLOG_POSTS -->'

FRONT_MATTER_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*\n?(.*)\Z', re.DOTALL)
FAQ_SECTION_RE = re.compile(r'##\s*よくある質問\s*\n(.*)', re.DOTALL)
FAQ_QA_RE = re.compile(r'\*\*Q\.\s*(.+?)\*\*\s*<br>\s*\n\s*A\.\s*(.+?)\s*(?=\n\s*\n|\Z)', re.DOTALL)

# ルートHTMLからヘッダー・フッターブロックを抽出するパターン
# 直前のコメント行も含めて除去する
_HEADER_RE = re.compile(
    r'[ \t]*(?:<!--[^\n]*-->\n[ \t]*)?<header class="header">.*?</header>\n?',
    re.DOTALL,
)
_FOOTER_RE = re.compile(
    r'[ \t]*(?:<!--[^\n]*-->\n[ \t]*)?<footer class="footer">.*?</footer>\n?',
    re.DOTALL,
)


def build():
    """_src/*.html + パーシャルからルートHTMLを生成する"""
    header = (PARTIALS_DIR / 'header.html').read_text(encoding='utf-8')
    footer = (PARTIALS_DIR / 'footer.html').read_text(encoding='utf-8')

    built = []
    for name in TARGET_PAGES:
        src = SRC_DIR / name
        if not src.exists():
            print(f'  [SKIP] _src/{name} が存在しません。--init を先に実行してください。')
            continue

        content = src.read_text(encoding='utf-8')
        content = content.replace(HEADER_MARKER, header.rstrip('\n'))
        content = content.replace(FOOTER_MARKER, footer.rstrip('\n'))

        out = ROOT / name
        out.write_text(content, encoding='utf-8')
        built.append(name)
        print(f'  [OK]   {name}')

    print(f'\n{len(built)} ページをビルドしました。')


def _parse_markdown_post(path):
    """front matter付きMarkdown記事をパースする"""
    text = path.read_text(encoding='utf-8')
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f'{path.name}: front matterが見つかりません（---で囲んでください）')

    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()

    tags = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]

    return {
        'slug': path.stem,
        'title': meta.get('title', path.stem),
        'date': meta.get('date', ''),
        'description': meta.get('description', ''),
        'tags': tags,
        'body': m.group(2),
    }


def _format_date_jp(date_str):
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return date_str
    return f'{d.year}年{d.month}月{d.day}日'


def _render_tags_html(tags, css_class, indent='          '):
    return '\n'.join(f'{indent}<span class="{css_class}">{tag}</span>' for tag in tags)


def _extract_faq_pairs(body):
    """記事本文の「## よくある質問」セクションからQ&Aペアを抽出する"""
    section_match = FAQ_SECTION_RE.search(body)
    if not section_match:
        return []

    pairs = []
    for m in FAQ_QA_RE.finditer(section_match.group(1)):
        question = re.sub(r'\s+', ' ', m.group(1)).strip()
        answer = re.sub(r'\s+', ' ', m.group(2)).strip()
        if question and answer:
            pairs.append((question, answer))
    return pairs


def _jsonld_script(data):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    payload = payload.replace('</', '<\\/')
    return f'  <script type="application/ld+json">\n{payload}\n  </script>'


def _build_post_jsonld(post):
    """記事のArticle（＋FAQがあればFAQPage）構造化データをscriptタグとして生成する"""
    article = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': post['title'],
        'description': post['description'],
        'datePublished': post['date'],
        'inLanguage': 'ja',
        'author': ORGANIZATION_JSONLD,
        'publisher': ORGANIZATION_JSONLD,
    }
    scripts = [_jsonld_script(article)]

    faq_pairs = _extract_faq_pairs(post['body'])
    if faq_pairs:
        faqpage = {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': question,
                    'acceptedAnswer': {'@type': 'Answer', 'text': answer},
                }
                for question, answer in faq_pairs
            ],
        }
        scripts.append(_jsonld_script(faqpage))

    return '\n'.join(scripts)


def build_blog():
    """blog/posts/*.md を記事ページ・一覧ページにビルドする"""
    if not BLOG_POSTS_DIR.exists():
        print('  [SKIP] blog/posts/ が存在しません。')
        return

    try:
        import markdown
    except ImportError:
        print('  [ERROR] markdownライブラリが未インストールです。`pip install -r requirements.txt` を実行してください。')
        return

    header = (PARTIALS_DIR / 'header.html').read_text(encoding='utf-8')
    footer = (PARTIALS_DIR / 'footer.html').read_text(encoding='utf-8')
    post_template = BLOG_POST_TEMPLATE.read_text(encoding='utf-8')

    posts = [_parse_markdown_post(p) for p in sorted(BLOG_POSTS_DIR.glob('*.md'))]
    posts.sort(key=lambda p: p['date'], reverse=True)

    BLOG_OUT_DIR.mkdir(exist_ok=True)

    for post in posts:
        content_html = markdown.markdown(post['body'], extensions=['extra', 'sane_lists'])

        page = post_template
        page = page.replace(HEADER_MARKER, header.rstrip('\n'))
        page = page.replace(FOOTER_MARKER, footer.rstrip('\n'))
        page = page.replace('{{TITLE}}', post['title'])
        page = page.replace('{{DESCRIPTION}}', post['description'])
        page = page.replace('{{DATE_ISO}}', post['date'])
        page = page.replace('{{DATE}}', _format_date_jp(post['date']))
        page = page.replace('{{TAGS_HTML}}', _render_tags_html(post['tags'], 'article-tag'))
        page = page.replace('{{SLUG}}', post['slug'])
        page = page.replace('{{CONTENT}}', content_html)
        page = page.replace(JSONLD_MARKER, _build_post_jsonld(post))

        out_path = BLOG_OUT_DIR / f"{post['slug']}.html"
        out_path.write_text(page, encoding='utf-8')
        print(f"  [OK]   blog/{post['slug']}.html")

    if not BLOG_INDEX_SRC.exists():
        print('  [SKIP] _src/blog_index.html が存在しません。')
        return

    index_page = BLOG_INDEX_SRC.read_text(encoding='utf-8')
    index_page = index_page.replace(HEADER_MARKER, header.rstrip('\n'))
    index_page = index_page.replace(FOOTER_MARKER, footer.rstrip('\n'))

    if posts:
        cards = []
        for post in posts:
            tags_html = _render_tags_html(post['tags'], 'post-tag', indent='            ')
            cards.append(
                f'        <a class="post-card" href="/blog/{post["slug"]}.html">\n'
                f'          <div class="post-tags">\n{tags_html}\n          </div>\n'
                f'          <h2 class="post-title">{post["title"]}</h2>\n'
                f'          <p class="post-desc">{post["description"]}</p>\n'
                f'          <p class="post-date"><time datetime="{post["date"]}">{_format_date_jp(post["date"])}</time></p>\n'
                f'        </a>'
            )
        posts_html = '\n'.join(cards)
    else:
        posts_html = '        <p class="blog-empty">近日公開予定です。</p>'

    index_page = index_page.replace(POSTS_MARKER, posts_html)

    (BLOG_OUT_DIR / 'index.html').write_text(index_page, encoding='utf-8')
    print(f'  [OK]   blog/index.html（記事 {len(posts)} 件）')


def build_sitemap():
    """ルートの公開ページとブログ記事一覧からsitemap.xmlを生成する"""
    today = datetime.now().date().isoformat()
    urls = []

    for name in TARGET_PAGES:
        if (ROOT / name).exists():
            urls.append((f'{SITE_BASE_URL}/{name}', today))

    posts = []
    if BLOG_POSTS_DIR.exists():
        posts = [_parse_markdown_post(p) for p in sorted(BLOG_POSTS_DIR.glob('*.md'))]

    if posts or BLOG_INDEX_SRC.exists():
        urls.append((f'{SITE_BASE_URL}/blog/', today))

    for post in posts:
        urls.append((f'{SITE_BASE_URL}/blog/{post["slug"]}.html', post['date'] or today))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{loc}</loc>')
        lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append('  </url>')
    lines.append('</urlset>')

    (ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  [OK]   sitemap.xml（{len(urls)}件）')


def build_robots_txt():
    """robots.txtが存在しない場合のみ新規作成する（既存ファイルは上書きしない）"""
    robots_path = ROOT / 'robots.txt'
    if robots_path.exists():
        print('  [SKIP] robots.txt は既に存在します（内容は変更しません）。')
        return

    content = (
        'User-agent: *\n'
        'Allow: /\n'
        '\n'
        f'Sitemap: {SITE_BASE_URL}/sitemap.xml\n'
    )
    robots_path.write_text(content, encoding='utf-8')
    print('  [OK]   robots.txt を新規作成しました。')


def build_llms_txt():
    """_src/llms.txt のブログ記事一覧マーカーを埋めてルートにllms.txtを生成する"""
    if not LLMS_TXT_SRC.exists():
        print('  [SKIP] _src/llms.txt が存在しません。')
        return

    posts = []
    if BLOG_POSTS_DIR.exists():
        posts = [_parse_markdown_post(p) for p in sorted(BLOG_POSTS_DIR.glob('*.md'))]
        posts.sort(key=lambda p: p['date'], reverse=True)

    if posts:
        lines = [
            f'- [{post["title"]}]({SITE_BASE_URL}/blog/{post["slug"]}.html): {post["description"]}'
            for post in posts
        ]
        blog_list = '\n'.join(lines)
    else:
        blog_list = '（記事は準備中です）'

    content = LLMS_TXT_SRC.read_text(encoding='utf-8')
    content = content.replace(LLMS_BLOG_POSTS_MARKER, blog_list)

    (ROOT / 'llms.txt').write_text(content, encoding='utf-8')
    print(f'  [OK]   llms.txt（記事 {len(posts)} 件）')


def init():
    """現在のルートHTMLを解析して _src/*.html を初期生成する"""
    SRC_DIR.mkdir(exist_ok=True)

    created = []
    for name in TARGET_PAGES:
        src_path = ROOT / name
        if not src_path.exists():
            print(f'  [SKIP] {name} が存在しません。')
            continue

        content = src_path.read_text(encoding='utf-8')

        # <header> ブロックをマーカーに置換
        if _HEADER_RE.search(content):
            content = _HEADER_RE.sub(HEADER_MARKER + '\n', content, count=1)
        else:
            print(f'  [WARN] {name}: <header class="header"> が見つかりません。')

        # <footer> ブロックをマーカーに置換
        if _FOOTER_RE.search(content):
            content = _FOOTER_RE.sub(FOOTER_MARKER + '\n', content, count=1)
        else:
            print(f'  [WARN] {name}: <footer class="footer"> が見つかりません。')

        out = SRC_DIR / name
        out.write_text(content, encoding='utf-8')
        created.append(name)
        print(f'  [OK]   _src/{name}')

    print(f'\n{len(created)} ページの _src/ ファイルを生成しました。')
    print('内容を確認し、ヘッダー・フッター相当部分がマーカーに置き換わっているかチェックしてください。')


if __name__ == '__main__':
    if '--init' in sys.argv:
        print('--- init: _src/ ファイルを生成します ---')
        init()
    else:
        print('--- build: ルートHTMLを生成します ---')
        build()
        print('\n--- build: blog/ を生成します ---')
        build_blog()
        print('\n--- build: sitemap.xml / robots.txt / llms.txt を生成します ---')
        build_sitemap()
        build_robots_txt()
        build_llms_txt()
