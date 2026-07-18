#!/usr/bin/env python3
"""
週次メトリクス取得スクリプト
====================
GSC（Search Console API）とGA4（Analytics Data API）から直近28日分の
データを取得し、data/metrics/latest.md に人間可読なMarkdownレポートを
生成する。既存の latest.md は data/metrics/archive/YYYY-MM-DD.md に退避する。

使い方:
  python scripts/fetch_metrics.py

環境変数:
  GCP_SA_KEY       サービスアカウントの認証情報（JSON文字列）
  GA4_PROPERTY_ID  GA4プロパティID（数字のみ。例: 123456789）

設計方針:
  - GSC・GA4のいずれかが失敗しても、スクリプト全体は異常終了させない
    （エラーは欠損として latest.md に明記する）
  - 週次CIから呼ばれる想定のため、認証情報が無い/権限が無い場合も
    正常終了し、後続のClaude Codeステップに処理を渡せる状態にする
"""

import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS_DIR = ROOT / 'data' / 'metrics'
ARCHIVE_DIR = METRICS_DIR / 'archive'
LATEST_PATH = METRICS_DIR / 'latest.md'
KEYWORD_MAP_PATH = ROOT / 'docs' / 'KEYWORD_MAP.md'
BLOG_DIR = ROOT / 'blog'

GSC_SITE_PRIMARY = 'sc-domain:ops-octopus.com'
GSC_SITE_FALLBACK = 'https://app.ops-octopus.com/'
GSC_ROW_LIMIT = 500

OPPORTUNITY_MIN_IMPRESSIONS = 10
OPPORTUNITY_POSITION_MIN = 11
OPPORTUNITY_POSITION_MAX = 20

CTR_CANDIDATE_MIN_IMPRESSIONS = 20
CTR_CANDIDATE_MAX_CTR = 0.02  # 2%


# ─── 認証 ───

def load_credentials(scopes):
    """GCP_SA_KEY環境変数からサービスアカウント認証情報を生成する。"""
    key_json = os.environ.get('GCP_SA_KEY')
    if not key_json:
        return None, 'GCP_SA_KEY が未設定です'
    try:
        from google.oauth2 import service_account
        info = json.loads(key_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return creds, None
    except Exception as e:
        return None, f'サービスアカウント認証情報の読み込みに失敗しました: {e}'


# ─── GSC ───

def fetch_gsc_data():
    """GSCから直近28日のクエリ×ページ別データを取得する。

    プロパティ sc-domain:ops-octopus.com での取得を試み、
    権限エラー等で失敗した場合は https://app.ops-octopus.com/ にフォールバックする。
    """
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds, err = load_credentials(scopes)
    if creds is None:
        return None, err

    try:
        from googleapiclient.discovery import build
        service = build('searchconsole', 'v1', credentials=creds, cache_discovery=False)
    except Exception as e:
        return None, f'Search Console APIクライアントの初期化に失敗しました: {e}'

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=27)

    request_body = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query', 'page'],
        'rowLimit': GSC_ROW_LIMIT,
    }

    errors = []
    for site_url in (GSC_SITE_PRIMARY, GSC_SITE_FALLBACK):
        try:
            response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
            rows = []
            for row in response.get('rows', []):
                query, page = row['keys']
                rows.append({
                    'query': query,
                    'page': page,
                    'impressions': row.get('impressions', 0),
                    'clicks': row.get('clicks', 0),
                    'ctr': row.get('ctr', 0.0),
                    'position': row.get('position', 0.0),
                })
            return {
                'site_used': site_url,
                'start_date': start_date,
                'end_date': end_date,
                'rows': rows,
            }, None
        except Exception as e:
            errors.append(f'{site_url}: {e}')
            continue

    joined = ' / '.join(errors)
    return None, f'GSCデータの取得に失敗しました（{GSC_SITE_PRIMARY} → {GSC_SITE_FALLBACK} いずれも失敗）: {joined}'


# ─── GA4 ───

def fetch_ga4_data():
    """GA4から直近28日のページ別セッション・エンゲージメント率と、
    detail.html関連の簡易集計を取得する。

    注記: GA4の標準Data APIでは「セッション内でどのページからdetail.htmlへ
    遷移したか」という真の経路（ファネル）情報は取得できない（BigQuery
    エクスポートかExploreのファネル探索が必要）。そのため、ここでは
    「ブログ各ページのセッション数」と「detail.htmlのセッション数・
    エンゲージメント率」を並べて見せる簡易的な代替集計にとどめる。
    """
    property_id = os.environ.get('GA4_PROPERTY_ID')
    if not property_id:
        return None, 'GA4_PROPERTY_ID が未設定です'

    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    creds, err = load_credentials(scopes)
    if creds is None:
        return None, err

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
    except Exception as e:
        return None, f'GA4クライアントライブラリの読み込みに失敗しました: {e}'

    try:
        client = BetaAnalyticsDataClient(credentials=creds)
    except Exception as e:
        return None, f'GA4クライアントの初期化に失敗しました: {e}'

    try:
        request = RunReportRequest(
            property=f'properties/{property_id}',
            dimensions=[Dimension(name='pagePath')],
            metrics=[Metric(name='sessions'), Metric(name='engagementRate')],
            date_ranges=[DateRange(start_date='28daysAgo', end_date='yesterday')],
            limit=500,
        )
        response = client.run_report(request)
    except Exception as e:
        return None, f'GA4ページ別レポートの取得に失敗しました: {e}'

    pages = []
    for row in response.rows:
        page_path = row.dimension_values[0].value
        sessions = int(float(row.metric_values[0].value))
        engagement_rate = float(row.metric_values[1].value)
        pages.append({
            'page_path': page_path,
            'sessions': sessions,
            'engagement_rate': engagement_rate,
        })

    detail_rows = [p for p in pages if p['page_path'].rstrip('/') == '/detail.html']
    blog_rows = sorted(
        (p for p in pages if p['page_path'].startswith('/blog/')),
        key=lambda p: p['sessions'],
        reverse=True,
    )

    return {
        'pages': pages,
        'blog_pages': blog_rows,
        'detail_page': detail_rows[0] if detail_rows else None,
    }, None


# ─── KEYWORD_MAP.md のP2抽出 ───

def parse_keyword_map_p2():
    """KEYWORD_MAP.mdの表からP2行（クエリ・タイトル案）を抽出する。"""
    if not KEYWORD_MAP_PATH.exists():
        return []

    text = KEYWORD_MAP_PATH.read_text(encoding='utf-8')
    p2_rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) != 5:
            continue
        query, intent, title, priority, existing = cells
        if priority == 'P2':
            p2_rows.append({'query': query, 'title': title})
    return p2_rows


def normalize_for_match(text):
    return re.sub(r'\s+', '', text).lower()


def find_query_gaps(gsc_rows, p2_rows):
    """GSCのクエリのうち、P2キーワードと重なりそうなものを抽出する（簡易ヒューリスティック）。"""
    if not gsc_rows or not p2_rows:
        return []

    gaps = []
    seen_queries = {}
    for row in gsc_rows:
        q = row['query']
        seen_queries.setdefault(q, {'impressions': 0, 'clicks': 0})
        seen_queries[q]['impressions'] += row['impressions']
        seen_queries[q]['clicks'] += row['clicks']

    for gsc_query, agg in seen_queries.items():
        normalized_gsc = normalize_for_match(gsc_query)
        for p2 in p2_rows:
            p2_tokens = [t for t in re.split(r'\s+', p2['query']) if t]
            # 短いトークン（2文字未満、"AI"等）は偶然の部分一致を招きやすいため対象外にする
            meaningful_tokens = [t for t in p2_tokens if len(t) >= 2]
            if not meaningful_tokens:
                continue
            hit_count = sum(1 for t in meaningful_tokens if normalize_for_match(t) in normalized_gsc)
            if hit_count == len(meaningful_tokens):
                gaps.append({
                    'gsc_query': gsc_query,
                    'impressions': agg['impressions'],
                    'p2_query': p2['query'],
                    'p2_title': p2['title'],
                })
                break

    gaps.sort(key=lambda g: g['impressions'], reverse=True)
    return gaps


# ─── レポート生成 ───

def aggregate_by_page(gsc_rows):
    pages = {}
    for row in gsc_rows:
        p = pages.setdefault(row['page'], {
            'query_count': 0, 'impressions': 0, 'clicks': 0,
            'ctr_sum': 0.0, 'position_sum': 0.0,
        })
        p['query_count'] += 1
        p['impressions'] += row['impressions']
        p['clicks'] += row['clicks']
        p['ctr_sum'] += row['ctr']
        p['position_sum'] += row['position']

    summary = []
    for page, agg in pages.items():
        n = agg['query_count']
        summary.append({
            'page': page,
            'query_count': n,
            'impressions': agg['impressions'],
            'clicks': agg['clicks'],
            'avg_ctr': agg['ctr_sum'] / n if n else 0.0,
            'avg_position': agg['position_sum'] / n if n else 0.0,
        })
    summary.sort(key=lambda p: p['impressions'], reverse=True)
    return summary


def find_opportunity_queries(gsc_rows):
    return sorted(
        (r for r in gsc_rows
         if r['impressions'] >= OPPORTUNITY_MIN_IMPRESSIONS
         and OPPORTUNITY_POSITION_MIN <= r['position'] <= OPPORTUNITY_POSITION_MAX),
        key=lambda r: r['impressions'], reverse=True,
    )


def find_ctr_candidates(gsc_rows):
    return sorted(
        (r for r in gsc_rows
         if r['impressions'] >= CTR_CANDIDATE_MIN_IMPRESSIONS
         and r['ctr'] < CTR_CANDIDATE_MAX_CTR),
        key=lambda r: r['impressions'], reverse=True,
    )


def fmt_pct(v):
    return f'{v * 100:.1f}%'


def fmt_pos(v):
    return f'{v:.1f}'


def build_report_markdown(run_date, gsc_result, gsc_error, ga4_result, ga4_error, gap_rows):
    lines = []
    lines.append(f'# 週次メトリクスレポート（{run_date.isoformat()}）')
    lines.append('')

    lines.append('## データ取得ステータス')
    lines.append('')
    if gsc_result:
        lines.append(
            f'- GSC: 取得成功（プロパティ: `{gsc_result["site_used"]}`、'
            f'期間: {gsc_result["start_date"].isoformat()} 〜 {gsc_result["end_date"].isoformat()}、'
            f'行数: {len(gsc_result["rows"])}）'
        )
    else:
        lines.append(f'- GSC: 取得できませんでした（{gsc_error}）')

    if ga4_result:
        lines.append(f'- GA4: 取得成功（ページ数: {len(ga4_result["pages"])}）')
    else:
        lines.append(f'- GA4: 取得できませんでした（{ga4_error}）')
    lines.append('')

    gsc_rows = gsc_result['rows'] if gsc_result else []

    # a. ブログ記事別サマリー
    lines.append('## a. ブログ記事別サマリー（GSC・直近28日）')
    lines.append('')
    if not gsc_result:
        lines.append('GSCデータが取得できなかったため、このセクションは空です。')
    else:
        page_summary = aggregate_by_page(gsc_rows)
        blog_summary = [p for p in page_summary if '/blog/' in p['page']]
        target = blog_summary if blog_summary else page_summary
        if not target:
            lines.append('該当データがありません。')
        else:
            lines.append('| ページ | クエリ数 | impressions | clicks | 平均CTR | 平均掲載順位 |')
            lines.append('|---|---|---|---|---|---|')
            for p in target:
                lines.append(
                    f'| {p["page"]} | {p["query_count"]} | {p["impressions"]} | '
                    f'{p["clicks"]} | {fmt_pct(p["avg_ctr"])} | {fmt_pos(p["avg_position"])} |'
                )
    lines.append('')

    # b. 機会クエリ
    lines.append(
        f'## b. 機会クエリ（impressions >= {OPPORTUNITY_MIN_IMPRESSIONS} かつ '
        f'掲載順位 {OPPORTUNITY_POSITION_MIN}〜{OPPORTUNITY_POSITION_MAX}）'
    )
    lines.append('')
    if not gsc_result:
        lines.append('GSCデータが取得できなかったため、このセクションは空です。')
    else:
        opportunities = find_opportunity_queries(gsc_rows)
        if not opportunities:
            lines.append('該当するクエリはありませんでした。')
        else:
            lines.append('| クエリ | ページ | impressions | clicks | ctr | position |')
            lines.append('|---|---|---|---|---|---|')
            for r in opportunities:
                lines.append(
                    f'| {r["query"]} | {r["page"]} | {r["impressions"]} | '
                    f'{r["clicks"]} | {fmt_pct(r["ctr"])} | {fmt_pos(r["position"])} |'
                )
    lines.append('')

    # c. CTR改善候補
    lines.append(
        f'## c. CTR改善候補（impressions >= {CTR_CANDIDATE_MIN_IMPRESSIONS} かつ '
        f'ctr < {fmt_pct(CTR_CANDIDATE_MAX_CTR)}）'
    )
    lines.append('')
    if not gsc_result:
        lines.append('GSCデータが取得できなかったため、このセクションは空です。')
    else:
        candidates = find_ctr_candidates(gsc_rows)
        if not candidates:
            lines.append('該当するクエリはありませんでした。')
        else:
            lines.append('| クエリ | ページ | impressions | clicks | ctr | position |')
            lines.append('|---|---|---|---|---|---|')
            for r in candidates:
                lines.append(
                    f'| {r["query"]} | {r["page"]} | {r["impressions"]} | '
                    f'{r["clicks"]} | {fmt_pct(r["ctr"])} | {fmt_pos(r["position"])} |'
                )
    lines.append('')

    # d. クエリギャップ
    lines.append('## d. クエリギャップ（GSCに出るが対応記事がないクエリ／KEYWORD_MAP.mdのP2と突合）')
    lines.append('')
    lines.append(
        '簡易的な文字列一致による突合のため、参考情報として扱うこと（記事化の要否は人間またはClaudeの判断で最終確認する）。'
    )
    lines.append('')
    if not gsc_result:
        lines.append('GSCデータが取得できなかったため、このセクションは空です。')
    elif not gap_rows:
        lines.append('該当するクエリはありませんでした。')
    else:
        lines.append('| GSCクエリ | impressions | 近いP2候補 | 記事タイトル案 |')
        lines.append('|---|---|---|---|')
        for g in gap_rows:
            lines.append(
                f'| {g["gsc_query"]} | {g["impressions"]} | {g["p2_query"]} | {g["p2_title"]} |'
            )
    lines.append('')

    # e. GA4データ
    lines.append('## e. GA4データ（直近28日）')
    lines.append('')
    if not ga4_result:
        lines.append('GA4データが取得できなかったため、このセクションは空です。')
    else:
        blog_pages = ga4_result['blog_pages']
        if not blog_pages:
            lines.append('ブログページ（/blog/配下）のデータがありませんでした。')
        else:
            lines.append('| ページ | セッション数 | エンゲージメント率 |')
            lines.append('|---|---|---|')
            for p in blog_pages:
                lines.append(
                    f'| {p["page_path"]} | {p["sessions"]} | {fmt_pct(p["engagement_rate"])} |'
                )
        lines.append('')
        lines.append('### detail.htmlの参考値')
        lines.append('')
        lines.append(
            '注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」という'
            'セッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreの'
            'ファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。'
        )
        if ga4_result['detail_page']:
            dp = ga4_result['detail_page']
            lines.append(
                f'- detail.html: セッション数 {dp["sessions"]}、'
                f'エンゲージメント率 {fmt_pct(dp["engagement_rate"])}'
            )
        else:
            lines.append('- detail.htmlのデータが見つかりませんでした。')
    lines.append('')

    return '\n'.join(lines) + '\n'


def archive_existing_latest():
    if not LATEST_PATH.exists():
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    archive_date = None
    try:
        first_line = LATEST_PATH.read_text(encoding='utf-8').splitlines()[0]
        m = re.search(r'(\d{4}-\d{2}-\d{2})', first_line)
        if m:
            archive_date = m.group(1)
    except Exception:
        pass

    if not archive_date:
        mtime = datetime.fromtimestamp(LATEST_PATH.stat().st_mtime)
        archive_date = mtime.date().isoformat()

    dest = ARCHIVE_DIR / f'{archive_date}.md'
    if dest.exists():
        # 同日に複数回実行された場合は上書きせず連番を振る
        i = 2
        while (ARCHIVE_DIR / f'{archive_date}-{i}.md').exists():
            i += 1
        dest = ARCHIVE_DIR / f'{archive_date}-{i}.md'

    dest.write_text(LATEST_PATH.read_text(encoding='utf-8'), encoding='utf-8')


def main():
    run_date = date.today()

    gsc_result, gsc_error = None, None
    try:
        gsc_result, gsc_error = fetch_gsc_data()
    except Exception as e:
        gsc_error = f'GSC取得処理で想定外のエラーが発生しました: {e}'

    ga4_result, ga4_error = None, None
    try:
        ga4_result, ga4_error = fetch_ga4_data()
    except Exception as e:
        ga4_error = f'GA4取得処理で想定外のエラーが発生しました: {e}'

    gap_rows = []
    if gsc_result:
        try:
            p2_rows = parse_keyword_map_p2()
            gap_rows = find_query_gaps(gsc_result['rows'], p2_rows)
        except Exception as e:
            print(f'[warn] クエリギャップ分析でエラーが発生しました: {e}', file=sys.stderr)

    report = build_report_markdown(run_date, gsc_result, gsc_error, ga4_result, ga4_error, gap_rows)

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        archive_existing_latest()
    except Exception as e:
        print(f'[warn] 既存latest.mdの退避に失敗しました: {e}', file=sys.stderr)

    LATEST_PATH.write_text(report, encoding='utf-8')
    print(f'[ok] {LATEST_PATH} を生成しました。')


if __name__ == '__main__':
    main()
