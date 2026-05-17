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

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / '_src'
PARTIALS_DIR = ROOT / '_partials'

# ビルド対象ページ（quick-scan.html と preview.html はビルド管理対象外）
TARGET_PAGES = [
    'index.html',
    'detail.html',
    'samples.html',
    'legal.html',
    'faq.html',
    'privacy.html',
]

HEADER_MARKER = '<!-- HEADER -->'
FOOTER_MARKER = '<!-- FOOTER -->'

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
