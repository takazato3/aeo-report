# 週次メトリクスレポート（2026-11-16）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-10-19 〜 2026-11-15、行数: 0）
- GA4: 取得成功（ページ数: 5）

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

ブログページ（/blog/配下）のデータがありませんでした。

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.htmlのデータが見つかりませんでした。

## 今週の実施アクション

- GSC（行数0）・GA4（ブログページ該当なし）とも分析可能なデータが引き続き得られず、判断ロジック（CTR改善/リライト/クエリギャップ）に基づくアクションは今回も実施不可
- 改善バックログ（docs/CONTENT_AUTOPILOT.md）を確認。唯一の未処理項目「OpsOctopus実測データ・レポート画像の記事への挿入」はDeep Scan本番稼働が前提条件であり、Deep Scanは引き続きComing Soon（スタブ実装のまま）のため今回も処理不可
- 上記によりデータ欠損・バックログ双方とも処理可能な項目がなかったため、KEYWORD_MAP.mdのP2プールから、既存P1記事との内部リンクが特に張りやすい2件を選定し新規記事化
  - IR情報・決算ページはAIにどう参照されているのか（`blog/posts/ir-page-ai-search.md`）：[会社概要ページ](/blog/company-profile-page-ai.html)・[プレスリリース](/blog/press-release-ai-search.html)・[一次情報](/blog/primary-source-ai-search.html)・[ホワイトペーパー](/blog/whitepaper-ai-citation.html)・[構造化データ](/blog/structured-data-aeo.html)へリンク
  - 商品ページの仕様表記はAIにどう読まれるのか（`blog/posts/product-spec-table-ai-search.md`）：[AIに引用されやすいコンテンツ](/blog/ai-citable-content.html)・[構造化データ](/blog/structured-data-aeo.html)・[FAQページ](/blog/faq-pages-ai-search.html)・[導入事例](/blog/case-study-ai-citation.html)・[競合比較](/blog/competitor-ai-search-comparison.html)へリンク
  - 両記事とも執筆後にWRITING_RHYTHM.mdの点検手順（話題テスト・漏出テスト・緊張台帳・拍の点検・境界の点検）を実施済み
  - KEYWORD_MAP.mdで両クエリをP2→P1（2026-11-16昇格）へ更新し、P1初期15本リストに41・42として追記。P2プールには「動画 YouTube AI検索」のみ残留
- `python build.py`を実行し、新規2記事のビルド（blog/index.html・sitemap.xml・llms.txt反映含む）がエラーなく通ることを確認
- SNS転用：新規記事2本それぞれからX投稿ドラフト2案（計4案）を生成し`sns/x-queue.md`の未投稿セクション末尾に追記。新規記事が2本以上だったため、両記事を束ねたnote記事ドラフト1本を`sns/note-drafts/2026-11-16-ir-page-and-product-spec.md`として生成
- `sns/x-queue.md`に`[x]`済みの項目はなかったため、`sns/x-posted.md`への移動作業は対象なし

