# 週次メトリクスレポート（2026-09-06）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-08-09 〜 2026-09-05、行数: 0）
- GA4: 取得成功（ページ数: 7）

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
| /blog/ | 4 | 100.0% |
| /blog/aeo-score-transparency.html | 4 | 75.0% |
| /blog/sge-ai-search-response.html | 1 | 100.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.htmlのデータが見つかりませんでした。

## 今週の実施アクション

- GSCが行数0、機会クエリ・CTR改善候補・クエリギャップのいずれも該当なしのため、判断ロジック（CTR改善/リライト/新規生成）に基づくアクションは実施不可（データ欠損）
- 改善バックログ（docs/CONTENT_AUTOPILOT.md）を確認。未処理項目「OpsOctopus実測データ・レポート画像の記事への挿入」はDeep Scan本番稼働が前提条件であり、現時点では処理不可能なため見送り（先週と同状況）
- バックログにも処理可能な項目がなかったため、KEYWORD_MAP.mdのP2から新規記事を2本生成（選定基準：既存P1記事との内部リンクが張りやすいものを優先）
  - `qa-format-content-ai-search`（Q&A形式のコンテンツはAI検索に向いているのか）：faq-pages-ai-search / anticipating-ai-queries と内部リンク（faq-pages-ai-search側からも参照リンクを追加）
  - `robots-txt-ai-crawlers`（robots.txtでAIクローラーをどう扱うか。基本の考え方）：how-to-write-llms-txt / brand-name-ai-search と内部リンク（how-to-write-llms-txt側からも参照リンクを追加）
  - KEYWORD_MAP.mdの該当2項目をP2→P1へ昇格し記録済み
- 上記2記事はWRITING_RHYTHM.mdの点検手順を実施。漏出テストでrobots-txt-ai-crawlers.md中盤の二人称依頼表現（「〜確認してください」）を検出し、状況側の文（名称変更を鵜呑みにするリスクの記述）へ書き換え済み
- `python build.py` 実行、ビルド成功（記事26件、sitemap 34件）
- SNS転用：新規記事2本それぞれからX投稿ドラフト2案（計4案）を`sns/x-queue.md`に追記。新規記事が2本以上だったため、note記事ドラフト1本（両記事を束ねた「今週の実験と観察」形式）を`sns/note-drafts/2026-09-06-qa-format-and-robots-txt.md`に保存。x-queue.mdに`[x]`項目はなく、x-posted.mdへの移動は無し

