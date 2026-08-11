#!/usr/bin/env python3
"""
Quick Scan サンプルレポート生成スクリプト
====================
data/SAMPLE_BRAND_QUEUE.md の「未実施」先頭ブランド(または引数指定ブランド)について、
質問文生成→ChatGPT/Gemini/Claudeへの同一質問送信→Claudeによるインサイト要約を行い、
_templates/quick_scan_sample.html に流し込んで assets/sample_reports/ 配下に
サンプルレポートHTMLを生成する。

使い方:
  python scripts/generate_quick_sample.py            # キューの未実施先頭1件を使用
  python scripts/generate_quick_sample.py "ブランド名"  # 手動指定(キュー未登録でも可)

環境変数:
  GCP_SA_KEY    Secret Manager接続用サービスアカウント認証情報(JSON文字列)
                openai-api-key / claude-api-key / gemini-api-key の3シークレットを取得する
  SAMPLE_TIER   "quick"(デフォルト)または "deep"。
                "deep" は現時点ではQuick実行にフォールバックするスタブ
                (将来Cloud Runの /process 呼び出しに差し替え予定)

このスクリプトが行わないこと(呼び出し側の責務):
  - python build.py の実行(_src/samples.html → samples.html への反映)
  - git commit / push・PR作成
  - キューが空の場合のIssue作成(呼び出し側のワークフローで判定する)
"""

import argparse
import html as html_lib
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / '_templates' / 'quick_scan_sample.html'
SAMPLE_REPORTS_DIR = ROOT / 'assets' / 'sample_reports'
SAMPLES_SRC_PATH = ROOT / '_src' / 'samples.html'
QUEUE_PATH = ROOT / 'data' / 'SAMPLE_BRAND_QUEUE.md'
COST_LOG_PATH = ROOT / 'data' / 'SAMPLE_COST_LOG.md'

# コスト予測性のため固定。変更する場合はこの値だけ書き換える。
CLAUDE_MODEL = os.environ.get('SAMPLE_CLAUDE_MODEL', 'claude-sonnet-5')
OPENAI_MODEL = os.environ.get('SAMPLE_OPENAI_MODEL', 'gpt-4o-mini')
GEMINI_MODEL = os.environ.get('SAMPLE_GEMINI_MODEL', 'gemini-2.5-flash')

# 1Mトークンあたりの概算USD単価。実際の請求額とは異なる場合がある(参考値。
# 料金改定があれば随時更新すること)。
PRICING = {
    'claude': {'input': 3.00, 'output': 15.00},
    'openai': {'input': 0.15, 'output': 0.60},
    'gemini': {'input': 0.30, 'output': 2.50},
}

TREND_WIDTH_MAP = {'低い': 30, '中程度': 60, '高い': 100}

QUESTION_EXAMPLES = """\
- Duolingoに興味があります。Duolingoのどんな点がユーザーに評価されていますか?特徴や強みも教えてください。
- 初めて観光バスツアーを利用する予定です。はとバスのツアーはどんな特徴がありますか?利用者の評判も知りたいです。
- 外資系企業への転職を考えています。JACリクルートメントの強みや評判について教えてください。"""

SYNTHESIS_SCHEMA = {
    'type': 'object',
    'properties': {
        'common': {'type': 'string'},
        'difference': {'type': 'string'},
        'persona': {'type': 'string'},
        'keywords': {'type': 'array', 'items': {'type': 'string'}},
        'industry_header': {'type': 'string'},
        'trend_level': {'type': 'string', 'enum': ['低い', '中程度', '高い']},
        'trend_comment': {'type': 'string'},
        'aeo_hint': {'type': 'string'},
    },
    'required': [
        'common', 'difference', 'persona', 'keywords',
        'industry_header', 'trend_level', 'trend_comment', 'aeo_hint',
    ],
    'additionalProperties': False,
}


# ─── Secret Manager ───

def load_gcp_credentials():
    key_json = os.environ.get('GCP_SA_KEY')
    if not key_json:
        print('[error] GCP_SA_KEY が未設定です。', file=sys.stderr)
        sys.exit(1)
    from google.oauth2 import service_account
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/cloud-platform'],
    )
    return creds, info['project_id']


def fetch_secret(client, project_id, secret_id):
    name = f'projects/{project_id}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(request={'name': name})
    return response.payload.data.decode('utf-8')


def load_api_keys():
    from google.cloud import secretmanager
    creds, project_id = load_gcp_credentials()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    return {
        'openai': fetch_secret(client, project_id, 'openai-api-key'),
        'claude': fetch_secret(client, project_id, 'claude-api-key'),
        'gemini': fetch_secret(client, project_id, 'gemini-api-key'),
    }


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


# ─── AI呼び出し ───

def generate_question(client, model, brand, category_major, category_sub, direction_hint):
    prompt = f"""あなたはAIブランド調査サービス「Ops Octopus」の質問文生成担当です。
以下のブランドについて、実際のユーザーが生成AIに話しかけるときの自然な一人称の質問文を1つだけ作成してください。

ブランド名: {brand}
業種・大カテゴリ: {category_major or '(指定なし)'}
中カテゴリ: {category_sub or '(指定なし)'}
想定質問の方向性: {direction_hint or '(指定なし。ブランドの強み・評判を尋ねる一般的な質問でよい)'}

過去の質問文の例(トーンの参考。同じ文面は使わないこと):
{QUESTION_EXAMPLES}

出力ルール:
- 日本語の自然な一人称の会話文にすること(「〜を検討しています」「〜に興味があります」等)
- 1〜2文程度、120文字以内
- ブランド名を必ず含めること
- 質問文以外の説明・前置き・引用符は一切つけず、質問文そのものだけを出力すること"""

    resp = client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{'role': 'user', 'content': prompt}],
    )
    text = next((b.text for b in resp.content if b.type == 'text'), '').strip()
    return text.strip('「」"\''), resp.usage


def call_openai(client, model, question):
    resp = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': question}],
    )
    text = resp.choices[0].message.content or ''
    return text, resp.usage


def call_gemini(client, model, question):
    resp = client.models.generate_content(model=model, contents=question)
    text = resp.text or ''
    return text, resp.usage_metadata


def call_claude_answer(client, model, question):
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{'role': 'user', 'content': question}],
    )
    text = next((b.text for b in resp.content if b.type == 'text'), '')
    return text, resp.usage


def build_synthesis_prompt(brand, category_major, category_sub, chatgpt_text, gemini_text, claude_text):
    return f"""以下は、AIブランド調査サービス「Ops Octopus」がChatGPT・Gemini・Claudeの3AIに
同一の質問をした際の回答です。

ブランド名: {brand}
業種・大カテゴリ: {category_major or '(不明)'}
中カテゴリ: {category_sub or '(不明)'}

--- ChatGPTの回答 ---
{chatgpt_text}

--- Geminiの回答 ---
{gemini_text}

--- Claudeの回答 ---
{claude_text}

上記を踏まえ、以下をすべて日本語で作成してください。既存レポートのトーン
(実務者向け、断定しすぎず「〜傾向が見られます」等の柔らかい表現、煽らない)に合わせること。

- common: 3AIの回答に共通する見解を2〜3文で
- difference: 3AIの回答の間に見られる言及の差を2〜3文で
- persona: このキーワードを検索する想定ユーザー像を1〜2文で
- keywords: 3AIの回答に現れた注目ワードを8〜15個、単語または短い句で
- industry_header: 「{category_major or brand}」を業界名として短く言い換えたもの
- trend_level: この業界のAI検索利用傾向のレベル(「低い」「中程度」「高い」のいずれか)
- trend_comment: この業界でのAI検索利用傾向についての説明を2〜3文で
- aeo_hint: この業界向けのAEO改善のヒントを「・」始まりの行3項目程度、改行区切りのプレーンテキストで"""


def synthesize_insights(client, model, brand, category_major, category_sub, chatgpt_text, gemini_text, claude_text):
    prompt = build_synthesis_prompt(brand, category_major, category_sub, chatgpt_text, gemini_text, claude_text)
    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        output_config={'format': {'type': 'json_schema', 'schema': SYNTHESIS_SCHEMA}},
        messages=[{'role': 'user', 'content': prompt}],
    )
    text = next(b.text for b in resp.content if b.type == 'text')
    return json.loads(text), resp.usage


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
    rendered = markdown.markdown(esc(raw_text.strip()), extensions=['extra', 'sane_lists'])
    return highlight_keyword(rendered, brand)


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


# ─── コストログ ───

def estimate_cost(provider, input_tokens, output_tokens):
    pricing = PRICING[provider]
    return (input_tokens / 1_000_000 * pricing['input']) + (output_tokens / 1_000_000 * pricing['output'])


def append_cost_log(run_date, brand, tier, total_cost, breakdown):
    COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not COST_LOG_PATH.exists():
        header = (
            '# サンプルレポート生成コストログ\n\n'
            '日付順に追記する。トークン数は各AI SDKのusageレスポンスから取得した概算値。\n'
            '金額は概算(見積り)であり、実際の請求額とは異なる場合がある。\n\n'
            '| 実行日 | ブランド名 | ティア | 概算コスト(USD) | 内訳 |\n'
            '|---|---|---|---|---|\n'
        )
        COST_LOG_PATH.write_text(header, encoding='utf-8')
    row = f'| {run_date.isoformat()} | {brand} | {tier} | ${total_cost:.4f} | {breakdown} |\n'
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

    queue_text = QUEUE_PATH.read_text(encoding='utf-8')
    queue_rows = parse_queue_pending(queue_text)
    brand_row, from_queue = select_brand(queue_rows, args.brand)

    api_keys = load_api_keys()

    import anthropic
    import openai as openai_sdk
    from google import genai as genai_sdk

    claude_client = anthropic.Anthropic(api_key=api_keys['claude'])
    openai_client = openai_sdk.OpenAI(api_key=api_keys['openai'])
    gemini_client = genai_sdk.Client(api_key=api_keys['gemini'])

    brand = brand_row['brand']
    category_major = brand_row.get('category_major', '')
    category_sub = brand_row.get('category_sub', '')
    direction_hint = brand_row.get('direction_hint', '')

    question, q_usage = generate_question(
        claude_client, CLAUDE_MODEL, brand, category_major, category_sub, direction_hint,
    )
    print(f'[ok] 質問文を生成しました: {question}')

    chatgpt_text, chatgpt_usage = call_openai(openai_client, OPENAI_MODEL, question)
    gemini_text, gemini_usage = call_gemini(gemini_client, GEMINI_MODEL, question)
    claude_text, claude_usage = call_claude_answer(claude_client, CLAUDE_MODEL, question)
    print('[ok] 3AIへの質問を完了しました。')

    insight, synth_usage = synthesize_insights(
        claude_client, CLAUDE_MODEL, brand, category_major, category_sub,
        chatgpt_text, gemini_text, claude_text,
    )
    print('[ok] AIインサイトを生成しました。')

    run_date = date.today()
    now = datetime.now()
    slug = re.sub(r'[^A-Za-z0-9]+', '', _romanize(brand)) or f'brand{abs(hash(brand)) % 10000}'
    output_filename = f'OpsOctopus_QuickScan_{slug}_{run_date.strftime("%Y%m%d")}.html'
    output_path = SAMPLE_REPORTS_DIR / output_filename

    keywords_html = ''.join(f'<span class="keyword-tag">{esc(k)}</span>' for k in insight['keywords'])
    trend_level = insight['trend_level']
    mapping = {
        'BRAND_NAME': esc(brand),
        'DATE_YYYYMMDD': run_date.strftime('%Y%m%d'),
        'SURVEY_DATETIME': f'{now.year}/{now.month}/{now.day} {now.strftime("%H:%M:%S")}',
        'CATEGORY_MAJOR': esc(category_major or brand),
        'CATEGORY_SUB': esc(category_sub or brand),
        'PROMPT_TEXT': esc(question),
        'CHATGPT_ANSWER_HTML': to_card_html(chatgpt_text, brand),
        'GEMINI_ANSWER_HTML': to_card_html(gemini_text, brand),
        'CLAUDE_ANSWER_HTML': to_card_html(claude_text, brand),
        'INSIGHT_COMMON': esc(insight['common']),
        'INSIGHT_DIFFERENCE': esc(insight['difference']),
        'INSIGHT_PERSONA': esc(insight['persona']),
        'INSIGHT_KEYWORDS_HTML': keywords_html,
        'INDUSTRY_HEADER': esc(insight['industry_header']),
        'TREND_LEVEL': esc(trend_level),
        'TREND_WIDTH': str(TREND_WIDTH_MAP.get(trend_level, 60)),
        'TREND_COMMENT': esc(insight['trend_comment']),
        'AEO_HINT_HTML': esc(insight['aeo_hint']).replace('\n', '<br>'),
    }

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

    cost_items = [
        ('claude', q_usage.input_tokens, q_usage.output_tokens, '質問生成'),
        ('openai', getattr(chatgpt_usage, 'prompt_tokens', 0) or 0,
         getattr(chatgpt_usage, 'completion_tokens', 0) or 0, 'ChatGPT'),
        ('gemini', getattr(gemini_usage, 'prompt_token_count', 0) or 0,
         getattr(gemini_usage, 'candidates_token_count', 0) or 0, 'Gemini'),
        ('claude', claude_usage.input_tokens, claude_usage.output_tokens, 'Claude回答'),
        ('claude', synth_usage.input_tokens, synth_usage.output_tokens, 'Synthesize'),
    ]
    total_cost = 0.0
    breakdown_parts = []
    for provider, in_tok, out_tok, label in cost_items:
        total_cost += estimate_cost(provider, in_tok, out_tok)
        breakdown_parts.append(f'{label}={in_tok}+{out_tok}tok')
    append_cost_log(run_date, brand, tier, total_cost, ', '.join(breakdown_parts))
    print(f'[ok] data/SAMPLE_COST_LOG.md に概算コスト ${total_cost:.4f} を記録しました。')


def _romanize(text):
    try:
        from unidecode import unidecode
        return unidecode(text)
    except ImportError:
        return text


if __name__ == '__main__':
    main()
