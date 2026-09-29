# 週次メトリクスレポート（2026-09-20）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-08-23 〜 2026-09-19、行数: 0）
- GA4: 取得成功（ページ数: 6）

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
| /blog/ | 2 | 100.0% |
| /blog/sge-ai-search-response.html | 1 | 100.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.htmlのデータが見つかりませんでした。

## 今週の実施アクション

- GSCが行数0、機会クエリ・CTR改善候補・クエリギャップのいずれも該当なしのため、判断ロジック（CTR改善/リライト/新規生成）に基づくアクションは実施不可（データ欠損。先週2026-09-13・先々週2026-09-06と同状況）
- 改善バックログ（docs/CONTENT_AUTOPILOT.md）を確認。未処理項目「OpsOctopus実測データ・レポート画像の記事への挿入」はDeep Scan本番稼働が前提条件であり、現時点では処理不可能なため見送り（scripts/generate_quick_sample.pyのDeep tierは引き続き未実装のフォールバックスタブのままであることを確認済み。先週と同状況）
- バックログにも処理可能な項目がなかったため、KEYWORD_MAP.mdのP2から新規記事を2本生成（選定基準：既存P1記事との内部リンクが張りやすいものを優先）
  - `perplexity-ai-visibility`（Perplexityで自社が見られるためにできること）：chatgpt-search-mechanism / robots-txt-ai-crawlers / ai-citable-content / primary-source-ai-search / brand-name-ai-search / anticipating-ai-queries / competitor-ai-search-comparison / measuring-aeo-effectiveness / ai-search-report-guide と内部リンク（chatgpt-search-mechanism側からも参照リンクを追加）
  - `aeo-effect-timing`（AEO施策の効果はいつ頃見え始めるのか）：structured-data-aeo / robots-txt-ai-crawlers / measuring-aeo-effectiveness / case-study-ai-citation / ai-search-strategy / ai-mention-rate と内部リンク（measuring-aeo-effectiveness側からも参照リンクを追加）
  - KEYWORD_MAP.mdの該当2項目をP2→P1へ昇格し記録済み（クラスタ1「概念理解系」・クラスタ3「検証・比較系」それぞれの追加分として反映）
- 上記2記事はWRITING_RHYTHM.mdの点検手順（漏出テスト・二人称の境界確認・だ/である調混入確認）をgrepで機械的に実施。規範語彙の漏出、中盤での二人称呼びかけ、文体の混在はいずれも検出されず、修正なしで確定
- `python build.py` 実行、ビルド成功（記事30件、sitemap 38件）
- SNS転用：新規記事2本それぞれからX投稿ドラフト2案（計4案）を`sns/x-queue.md`に追記。新規記事が2本以上だったため、note記事ドラフト1本（両記事を束ねた「今週の実験と観察」形式）を`sns/note-drafts/2026-09-20-perplexity-and-effect-timing.md`に保存。x-queue.mdに実際の`[x]`項目はなく、x-posted.mdへの移動は無し（未投稿24件のため補充も不要）

