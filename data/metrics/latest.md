# 週次メトリクスレポート（2026-08-09）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-07-12 〜 2026-08-08、行数: 0）
- GA4: 取得成功（ページ数: 14）

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
| /blog/ | 16 | 93.8% |
| /blog/aeo-score-transparency.html | 1 | 100.0% |
| /blog/aeo-tool-comparison-points.html | 1 | 100.0% |
| /blog/faq-pages-ai-search.html | 1 | 100.0% |
| /blog/how-to-write-llms-txt.html | 1 | 100.0% |
| /blog/not-appearing-in-chatgpt.html | 1 | 100.0% |
| /blog/what-is-aeo.html | 1 | 100.0% |
| /blog/what-is-llmo.html | 1 | 100.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.html: セッション数 2、エンゲージメント率 100.0%

## 今週の実施アクション

- GSCが行数0のため、機会クエリ・CTR改善候補・クエリギャップのいずれも分析不能（データ欠損）
- 改善バックログ（CONTENT_AUTOPILOT.md）を確認したが、処理可能な項目はなし
  - 「OpsOctopus実測データ・レポート画像の記事への挿入」は、Deep Scanが実データを蓄積する段階に至っていないため未着手のまま据え置き
- 上記により、判断ロジックに従いKEYWORD_MAP.mdのP2から新規記事を2本まで生成（内部リンクの張りやすさを優先し、既存P1記事群と接続しやすい2クラスタから選定）
  - 新規記事1：「AI検索とは何か。従来の検索行動との違いを整理する」（blog/posts/what-is-ai-search.md）
    - what-is-aeo / ai-search-strategy / chatgpt-search-mechanism / geo-vs-seo / aeo-llmo-geo-difference / ai-overviews-aeo と相互リンク
    - KEYWORD_MAP.md「AI検索 とは」をP2→P1に昇格（2026-08-09）
  - 新規記事2：「AIの『言及率』とは何か。数字の見方と注意点」（blog/posts/ai-mention-rate.md）
    - aeo-score-transparency / brand-name-ai-search / aeo-tool-comparison-points / ai-search-ranking-measurement / measuring-aeo-effectiveness と相互リンク
    - KEYWORD_MAP.md「AI 言及率 とは」をP2→P1に昇格（2026-08-09）
- 両記事ともWRITING_RHYTHM.mdの点検手順（話題テスト・漏出テスト・緊張台帳・拍の点検・境界の点検）を実施済み。冒頭結論サマリとFAQは適用除外を維持し、本文H2セクションのみ適用
- `python build.py` 実行、7ページ＋ブログ記事20件（新規2件含む）のビルドを確認
- SNS転用：新規記事2本それぞれからX投稿ドラフトを2案ずつ生成しsns/x-queue.mdへ追記（計4件）。新規記事が2本以上のため、noteドラフトを1本生成しsns/note-drafts/へ保存
- x-queue.mdに`[x]`済み項目はなかったため、x-posted.mdへのアーカイブ移動は該当なし
