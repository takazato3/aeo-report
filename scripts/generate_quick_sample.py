#!/usr/bin/env python3
"""
Quick Scan サンプルレポート生成スクリプト
====================
data/SAMPLE_BRAND_QUEUE.md の「未実施」先頭ブランド(または引数指定ブランド)について、
本番GAS Webアプリの action: "generateSampleReport" を呼び出し、画面②「調査開始」
確定時と同一のロジック(質問文生成→3AI実行→インサイト合成)で結果を取得したうえで、
_templates/quick_scan_sample.html に流し込んで assets/sample_reports/ 配下に
サンプルレポートHTMLを生成する。

独自にOpenAI/Claude/Geminiへ直接問い合わせることはしない。本番Quick Scanの
プロンプト・要約仕様が変わっても、GAS側の同一コードパスを経由するため
サンプル生成側の追従は不要になる。

使い方:
  python scripts/generate_quick_sample.py            # キューの未実施先頭1件を使用
  python scripts/generate_quick_sample.py "ブランド名"  # 手動指定(キュー未登録でも可)

環境変数:
  GAS_SAMPLE_SECRET  GAS Webアプリの generateSampleReport アクション認証用シークレット
                      (GASスクリプトプロパティ SAMPLE_GEN_SECRET と同じ値)
  GAS_WEBAPP_URL      GAS WebアプリのURL(省略時はCLAUDE.md記載の本番デプロイURLを使用)
  SAMPLE_TIER         "quick"(デフォルト)または "deep"。
                       "deep" は現時点ではQuick実行にフォールバックするスタブ
                       (将来Cloud Runの /process 呼び出しに差し替え予定)

このスクリプトが行わないこと(呼び出し側の責務):
  - python build.py の実行(_src/samples.html → samples.html への反映)
  - git commit / push・PR作成
  - キューが空の場合のIssue作成(呼び出し側のワークフローで判定する)
"""

import argparse
import html as html_lib
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import markdown
import requests

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / '_templates' / 'quick_scan_sample.html'
SAMPLE_REPORTS_DIR = ROOT / 'assets' / 'sample_reports'
SAMPLES_SRC_PATH = ROOT / '_src' / 'samples.html'
QUEUE_PATH = ROOT / 'data' / 'SAMPLE_BRAND_QUEUE.md'
COST_LOG_PATH = ROOT / 'data' / 'SAMPLE_COST_LOG.md'

# CLAUDE.md記載の本番GAS Webアプリ(既存デプロイ)。環境変数で上書き可能。
DEFAULT_GAS_WEBAPP_URL = (
    'https://script.google.com/macros/s/'
    'AKfycbzYeiBAv2CY5zqLjx2kbHTRegNRkdz2dAecGwa2MDH_c6_5NpIocr9xpVP3ItwT7m-0-Q/exec'
)
GAS_WEBAPP_URL = os.environ.get('GAS_WEBAPP_URL', DEFAULT_GAS_WEBAPP_URL)
GAS_REQUEST_TIMEOUT = 180  # 質問文生成+3AI+インサイト合成を直列実行するため長めに取る

TREND_WIDTH_MAP = {'低い': 30, '中程度': 60, '高い': 100}


# ─── GAS呼び出し ───

def call_gas_generate_sample_report(secret, brand, category_major, category_sub, direction_hint):
    """GASの action: "generateSampleReport" を呼び出す。

    GAS Webアプリのレスポンスはscript.google.com/.../execから
    script.googleusercontent.com/macros/echo?...への302リダイレクトで返る。
    リダイレクト先は一度しか読み出せない一時URLのため、requestsの自動
    リダイレクト追従（POSTのまま再送されうる）に頼らず、Locationヘッダーを
    手動で取得してGETで取得する。
    """
    payload = {
        'action': 'generateSampleReport',
        'secret': secret,
        'brand': brand,
        'category_major': category_major,
        'category_sub': category_sub,
        'direction_hint': direction_hint,
    }
    resp = requests.post(
        GAS_WEBAPP_URL, json=payload, allow_redirects=False, timeout=GAS_REQUEST_TIMEOUT,
    )
    if resp.status_code in (301, 302, 303) and 'Location' in resp.headers:
        resp = requests.get(resp.headers['Location'], timeout=GAS_REQUEST_TIMEOUT)
    resp.raise_for_status()
    body = resp.json()

    if not body.get('success'):
        raise RuntimeError(f'GAS generateSampleReport が失敗しました: {body.get("error")}')
    return body['data']


# ─── ブランドキュー ───

def parse_queue_pending(text):
    rows = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            in_section = stripped == '## 未実施'
            continue
        if not in_section or not stripped.startswith('|'):
            continue
        cells = [c.strip() for c in stripped.strip('|').split('|')]
        if len(cells) != 4:
            continue
        if cells[0] == 'ブランド名' or all(re.fullmatch(r'-+', c) for c in cells):
            continue
        rows.append({
            'brand': cells[0],
            'category_major': cells[1],
            'category_sub': cells[2],
            'direction_hint': cells[3],
        })
    return rows


def select_brand(queue_rows, manual_brand):
    if manual_brand:
        for row in queue_rows:
            if row['brand'] == manual_brand:
                return row, True
        print(
            f'[warn] "{manual_brand}" はキューの未実施リストに見つかりません。'
            'ブランド名のみで続行します(業種・カテゴリは空欄になります)。',
        )
        return {
            'brand': manual_brand, 'category_major': '',
            'category_sub': '', 'direction_hint': '',
        }, False
    if not queue_rows:
        print('[error] SAMPLE_BRAND_QUEUE.md の未実施リストが空です。', file=sys.stderr)
        sys.exit(1)
    return queue_rows[0], True


def update_queue_text(text, brand_row, output_filename, run_date):
    lines = text.splitlines()
    out_lines = []
    in_pending = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## '):
            in_pending = stripped == '## 未実施'
            out_lines.append(line)
            continue
        if in_pending and stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if cells and cells[0] == brand_row['brand']:
                continue
        out_lines.append(line)
    new_text = '\n'.join(out_lines).rstrip('\n') + '\n'
    new_row = f"| {brand_row['brand']} | {run_date.isoformat()} | {output_filename} |"
    return new_text + new_row + '\n'


# ─── HTML変換 ───

def esc(text):
    return html_lib.escape(text or '', quote=False)


def highlight_keyword(html_content, keyword):
    if not keyword:
        return html_content
    pattern = re.compile(f'({re.escape(keyword)})', re.IGNORECASE)
    parts = re.split(r'(<[^>]+>)', html_content)
    for i, part in enumerate(parts):
        if part.startswith('<'):
            continue
        parts[i] = pattern.sub(r'<span class="keyword-highlight">\1</span>', part)
    return ''.join(parts)


def to_card_html(raw_text, brand):
    """本番quick-scan.htmlのrenderResult()と同じ変換を行う:
    markdown変換→<em>/<mark>タグの除去(中身は残す)→キーワードハイライト。
    """
    if not raw_text:
        return '<p><span class="result-error">回答を取得できませんでした。</span></p>'
    rendered = markdown.markdown(esc(raw_text.strip()), extensions=['extra', 'sane_lists'])
    rendered = re.sub(r'</?mark>', '', rendered)
    rendered = re.sub(r'</?em>', '', rendered)
    return highlight_keyword(rendered, brand)


def parse_keywords(keywords_field):
    """GASのinsight.keywordsはカンマ区切りの文字列(quick-scan.htmlと同じ形式)。"""
    if not keywords_field:
        return []
    return [k.strip() for k in keywords_field.split(',') if k.strip()]


def render_template(template_text, mapping):
    text = template_text
    for key, value in mapping.items():
        text = text.replace('{{' + key + '}}', value)
    return text


def build_sample_log_entry(brand, category_major, category_sub, run_date, question, output_filename):
    label = category_sub or category_major or ''
    title = f'{esc(label)}｜{esc(brand)}' if label else esc(brand)
    date_label = f'{run_date.year}年{run_date.month}月'
    summary = f'「{esc(question)}」と直接たずねた際の、3AIの回答を記録。'
    return f'''
        <li class="sample-log-item">
          <div class="sample-log-body">
            <div class="sample-log-title-row">
              <p class="sample-log-title">{title}</p>
              <div class="sample-log-meta-inline">
                <span class="sample-log-date">{date_label}</span>
                <span class="sample-log-plan">Quick Scan(n=1)</span>
              </div>
            </div>
            <p class="sample-log-summary">{summary}</p>
          </div>
          <a class="sample-log-link" href="assets/sample_reports/{output_filename}" target="_blank">AIの回答結果を確認 →</a>
        </li>
'''


def update_samples_src(text, entry_html):
    marker = '<ul class="sample-log">'
    start = text.index(marker) + len(marker)
    end = text.index('</ul>', start)
    return text[:end] + entry_html + text[end:]


def build_industry_trend_fields(category_major, category_data):
    """業界傾向(02セクション下段)のプレースホルダ値を組み立てる。

    categoryDataはGAS側のcategoriesシートに該当行が無ければnullになる
    (新規カテゴリをキューに追加した直後などに起こりうる)。その場合は
    生成自体は失敗させず、「未登録」であることが分かる表示にフォールバックする。
    """
    industry_header = esc(category_major)
    if not category_data:
        print(f'[warn] categoriesシートに一致する行が見つかりませんでした（業種・大カテゴリ: "{category_major}"）。'
              '業界傾向パネルは「未登録」表示になります。')
        return {
            'INDUSTRY_HEADER': industry_header,
            'TREND_LEVEL': 'データ未登録',
            'TREND_WIDTH': '0',
            'TREND_COMMENT': 'この業種・カテゴリのAI検索利用傾向データは、まだcategoriesシートに登録されていません。',
            'AEO_HINT_HTML': 'この業種・カテゴリのAEO改善ヒントは、まだcategoriesシートに登録されていません。',
        }

    trend_level = category_data.get('ai_usage_trend') or '中程度'
    # 本番quick-scan.htmlと同じく、コメント・ヒントはcategoriesシートの内容を
    # そのまま(エスケープせず)改行→<br>変換のみで埋め込む。
    trend_comment = (category_data.get('ai_usage_comment_quick') or '').replace('\n', '<br>')
    aeo_hint = (category_data.get('aeo_hint_quick') or '').replace('\n', '<br>')
    return {
        'INDUSTRY_HEADER': industry_header,
        'TREND_LEVEL': esc(trend_level),
        'TREND_WIDTH': str(TREND_WIDTH_MAP.get(trend_level, 60)),
        'TREND_COMMENT': trend_comment,
        'AEO_HINT_HTML': aeo_hint,
    }


# ─── コストログ ───

def append_cost_log(run_date, brand, tier):
    COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not COST_LOG_PATH.exists():
        header = (
            '# サンプルレポート生成コストログ\n\n'
            '本番GAS(generateSampleReportアクション)経由で生成しており、本番Quick Scan/Deep Scan\n'
            'と同一のAPI利用枠を使うため、このスクリプト単体での個別コスト算出は行わない。\n'
            '実行履歴の記録のみを目的とする。\n\n'
            '| 実行日 | ブランド名 | ティア | 備考 |\n'
            '|---|---|---|---|\n'
        )
        COST_LOG_PATH.write_text(header, encoding='utf-8')
    row = f'| {run_date.isoformat()} | {brand} | {tier} | GAS経由・本番同一ロジック(個別コスト算出なし) |\n'
    with COST_LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(row)


# ─── メイン ───

def main():
    tier = os.environ.get('SAMPLE_TIER', 'quick').strip().lower()
    if tier == 'deep':
        print('[info] Deep tier未実装。Quick実行にフォールバックしました。')
        # TODO: Deep Scan本実装後、ここをCloud Runの /process エンドポイント呼び出しに差し替える
        tier = 'quick'

    parser = argparse.ArgumentParser(description='Quick Scanサンプルレポートを1件生成する')
    parser.add_argument('brand', nargs='?', default=None, help='手動指定するブランド名(省略時はキュー先頭)')
    args = parser.parse_args()

    secret = os.environ.get('GAS_SAMPLE_SECRET')
    if not secret:
        print('[error] GAS_SAMPLE_SECRET が未設定です。', file=sys.stderr)
        sys.exit(1)

    queue_text = QUEUE_PATH.read_text(encoding='utf-8')
    queue_rows = parse_queue_pending(queue_text)
    brand_row, from_queue = select_brand(queue_rows, args.brand)

    brand = brand_row['brand']
    category_major = brand_row.get('category_major', '')
    category_sub = brand_row.get('category_sub', '')
    direction_hint = brand_row.get('direction_hint', '')

    if not category_major:
        print('[error] category_major が空です。SAMPLE_BRAND_QUEUE.md を確認してください。', file=sys.stderr)
        sys.exit(1)

    print(f'[ok] GAS generateSampleReport を呼び出します（ブランド: {brand}）...')
    data = call_gas_generate_sample_report(secret, brand, category_major, category_sub, direction_hint)

    question = data.get('question') or ''
    results = data.get('results') or {}
    insight = data.get('insight') or {}
    errors = data.get('errors') or []
    category_data = data.get('categoryData')

    print(f'[ok] 質問文: {question}')
    if errors:
        print(f'[warn] GAS側で一部エラーが発生しました: {errors}')

    run_date = date.today()
    now = datetime.now()
    slug = re.sub(r'[^A-Za-z0-9]+', '', _romanize(brand)) or f'brand{abs(hash(brand)) % 10000}'
    output_filename = f'OpsOctopus_QuickScan_{slug}_{run_date.strftime("%Y%m%d")}.html'
    output_path = SAMPLE_REPORTS_DIR / output_filename

    keywords_html = ''.join(f'<span class="keyword-tag">{esc(k)}</span>' for k in parse_keywords(insight.get('keywords')))

    mapping = {
        'BRAND_NAME': esc(brand),
        'DATE_YYYYMMDD': run_date.strftime('%Y%m%d'),
        'SURVEY_DATETIME': f'{now.year}/{now.month}/{now.day} {now.strftime("%H:%M:%S")}',
        'CATEGORY_MAJOR': esc(category_major),
        'CATEGORY_SUB': esc(category_sub or category_major),
        'PROMPT_TEXT': esc(question),
        'CHATGPT_ANSWER_HTML': to_card_html(results.get('chatgpt'), brand),
        'GEMINI_ANSWER_HTML': to_card_html(results.get('gemini'), brand),
        'CLAUDE_ANSWER_HTML': to_card_html(results.get('claude'), brand),
        'INSIGHT_COMMON': esc(insight.get('common')),
        'INSIGHT_DIFFERENCE': esc(insight.get('difference')),
        'INSIGHT_PERSONA': esc(insight.get('persona')),
        'INSIGHT_KEYWORDS_HTML': keywords_html,
    }
    mapping.update(build_industry_trend_fields(category_major, category_data))

    template_text = TEMPLATE_PATH.read_text(encoding='utf-8')
    SAMPLE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_template(template_text, mapping), encoding='utf-8')
    print(f'[ok] {output_path} を生成しました。')

    entry_html = build_sample_log_entry(brand, category_major, category_sub, run_date, question, output_filename)
    samples_src_text = SAMPLES_SRC_PATH.read_text(encoding='utf-8')
    SAMPLES_SRC_PATH.write_text(update_samples_src(samples_src_text, entry_html), encoding='utf-8')
    print('[ok] _src/samples.html にエントリを追加しました(python build.py の実行で反映されます)。')

    if from_queue:
        QUEUE_PATH.write_text(update_queue_text(queue_text, brand_row, output_filename, run_date), encoding='utf-8')
        print('[ok] SAMPLE_BRAND_QUEUE.md を更新しました(未実施→実施済み)。')
    else:
        print('[warn] キュー未登録のブランドのため、SAMPLE_BRAND_QUEUE.md は更新していません。')

    append_cost_log(run_date, brand, tier)
    print('[ok] data/SAMPLE_COST_LOG.md に実行履歴を記録しました。')


def _romanize(text):
    try:
        from unidecode import unidecode
        return unidecode(text)
    except ImportError:
        return text


if __name__ == '__main__':
    main()
