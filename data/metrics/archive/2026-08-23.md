# 週次メトリクスレポート（2026-08-23）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-07-26 〜 2026-08-22、行数: 0）
- GA4: 取得成功（ページ数: 8）

## a. ブログ記事別サマリー（GSC・直近28日）

該当データがありません。

## b. 機会クエリ（impressions >= 10 かつ 掲載順位 11〜20）

該当するクエリはありませんでした。

## c. CTR改善候補（impressions >= 20 かつ ctr < 2.0%）

該当するクエリはありませんでした。

## d. クエリギャップ（GSCに出るが対応記事がないクエリ／KEYWORD_MAP.mdのP2と突合）

簡易的な文字列一致による突合のため、参考情報として扱うこと（記事化の要否は人間またはClaudeの判断で最終確認する）。

該当するクエリはありませんでした。

## e. GA4データ（直近28日）

| ページ | セッション数 | エンゲージメント率 |
|---|---|---|
| /blog/ | 7 | 85.7% |
| /blog/aeo-score-transparency.html | 5 | 60.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.html: セッション数 1、エンゲージメント率 100.0%

## 今週の実施アクション

- GSCが行数0、機会クエリ・CTR改善候補・クエリギャップのいずれも該当なしのため、判断ロジック（CTR改善/リライト/新規生成）に基づくアクションは実施不可（データ欠損）
- 改善バックログ（docs/CONTENT_AUTOPILOT.md）を確認。未処理項目「OpsOctopus実測データ・レポート画像の記事への挿入」はDeep Scan本番稼働が前提条件であり、現時点では処理不可能なため見送り
- バックログにも処理可能な項目がなかったため、KEYWORD_MAP.mdのP2から新規記事を2本生成
  - `sge-ai-search-response`（生成AI検索（旧SGE）にどう対応すればいいのか）：ai-overviews-aeo / what-is-aeo / ai-search-strategy と内部リンク
  - `primary-source-ai-search`（AI検索時代に一次情報を出す意味を考える）：ai-citable-content / anticipating-ai-queries / structured-data-aeo / faq-pages-ai-search / not-appearing-in-chatgpt と内部リンク
  - KEYWORD_MAP.mdの該当2項目をP2→P1へ昇格し記録済み
- 上記2記事はWRITING_RHYTHM.mdの点検手順を実施済み（primary-source-ai-searchの1文を状況側の記述へ修正）
- `python build.py` 実行、ビルド成功（記事22件、sitemap 30件）
- SNS転用：新規記事2本それぞれからX投稿ドラフト2案（計4案）を`sns/x-queue.md`に追記。新規記事が2本以上だったため、note記事ドラフト1本（両記事を束ねた「今週の実験と観察」形式）を`sns/note-drafts/2026-08-23-sge-naming-and-primary-source.md`に保存。x-queue.mdに`[x]`項目はなく、x-posted.mdへの移動は無し

