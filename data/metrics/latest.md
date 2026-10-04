# 週次メトリクスレポート（2026-10-04）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-09-06 〜 2026-10-03、行数: 0）
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
| /blog/ | 1 | 100.0% |
| /blog/press-release-ai-search.html | 1 | 100.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.htmlのデータが見つかりませんでした。

## 今週の実施アクション

- GSC行数0件のためCTR改善・リライト・クエリギャップの判断材料なし（データ欠損・分析不能）。
- 改善バックログを確認したが、唯一の未処理項目（OpsOctopus実測データ・レポート画像の記事への挿入）はDeep Scan本番稼働が前提条件のため、現時点では処理不可（スタブ実装のまま）。
- バックログに処理可能な項目がなかったため、KEYWORD_MAP.mdのP2から新規記事を生成（P2該当は1件のみだったため1本）。
  - 新規記事：`blog/posts/generative-ai-seo.md`（生成AI時代の検索エンジン最適化とは何をすればいいか）
  - 選定理由：既存P1記事（ai-search-strategy / aeo-llmo-geo-difference / geo-vs-seo / ai-search-ranking-measurement / faq-pages-ai-search / anticipating-ai-queries / structured-data-aeo / aeo-effect-timing）との内部リンクが張りやすく、「生成AI向けSEO」という検索意図と概念理解系クラスタの既存記事群が直接つながる内容だったため
  - KEYWORD_MAP.mdでP2→P1へ昇格済み（2026-10-04昇格、概念理解系・項目32として追記）
- WRITING_RHYTHM.mdの点検手順（話題テスト・漏出テスト・緊張台帳・拍の点検・境界の点検）を実行し、本文H2セクションに適用（冒頭結論サマリ・FAQは適用除外）。
- `python build.py` 実行済み・ビルド成功（記事33件、sitemap 41件）。
- SNS転用：新規記事1本のため、docs/SNS_REPURPOSE.mdのルールに従いX投稿ドラフト2案を`sns/x-queue.md`の未投稿末尾へ追記。新規記事が2本未満のためnote記事ドラフトは今回生成せず。x-queue.mdに`[x]`済み項目はなかったため、`sns/x-posted.md`への移動は発生せず。

