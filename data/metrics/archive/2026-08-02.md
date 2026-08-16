# 週次メトリクスレポート（2026-08-02）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-07-05 〜 2026-08-01、行数: 0）
- GA4: 取得成功（ページ数: 11）

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
| /blog/ | 11 | 90.9% |
| /blog/aeo-tool-comparison-points.html | 1 | 100.0% |
| /blog/faq-pages-ai-search.html | 1 | 100.0% |
| /blog/how-to-write-llms-txt.html | 1 | 100.0% |
| /blog/not-appearing-in-chatgpt.html | 1 | 100.0% |
| /blog/what-is-aeo.html | 1 | 100.0% |
| /blog/what-is-llmo.html | 1 | 100.0% |

### detail.htmlの参考値

注記: GA4の標準Data APIでは「どのブログ記事からdetail.htmlへ遷移したか」というセッション内の経路（ファネル）は取得できない（BigQueryエクスポートまたはExploreのファネル探索が必要）。以下はdetail.html単体のセッション数・エンゲージメント率の参考値。
- detail.html: セッション数 1、エンゲージメント率 100.0%

## 今週の実施アクション

- **実施日**: 2026-08-02
- **判断**: GSCが今週も0行、GA4のセッション数も僅少（/blog/で11、各記事1件前後）で、
  機会クエリ・CTR改善候補・クエリギャップのいずれも算出できず、メトリクスに基づく
  CTR改善／リライト／新規生成の判断は不能でした。`docs/CONTENT_AUTOPILOT.md` の
  判断ロジック、およびタスク指示（3）に従い、まず改善バックログに処理可能な項目が
  ないかを確認しました。
- **バックログ確認**: 改善バックログの残項目は「OpsOctopus実測データ・レポート画像の
  記事への挿入（Deep Scan本番稼働後、実調査データを引用素材化する）」の1件のみでしたが、
  実際のDeep Scanレポート画像・実調査データが本ランでは取得できず、処理可能な項目では
  ないと判断しました。バックログは消し込まず据え置きです。
- **新規記事の生成（2本、指示（3）の代替ルートを適用）**: バックログに処理可能な項目が
  なかったため、`docs/KEYWORD_MAP.md` のP2から、既存P1記事との内部リンクが張りやすい
  ものを優先して2本を新規生成し、P1へ昇格しました。
  - 「指名検索でAIは何を答えるのか。ブランド名調査の考え方」
    （`blog/posts/brand-name-ai-search.md`）。not-appearing-in-chatgpt /
    anticipating-ai-queries / measuring-aeo-effectiveness /
    ai-search-ranking-measurement / aeo-tool-comparison-points と内部リンク。
  - 「AEOの独自スコアはなぜ分かりにくいのか。生データを見る意味」
    （`blog/posts/aeo-score-transparency.md`）。aeo-tool-comparison-points /
    measuring-aeo-effectiveness / ai-search-ranking-measurement /
    brand-name-ai-search（新規記事同士）と内部リンク。
- **KEYWORD_MAP.md更新**: 上記2件を「指名検索 AI」「AI検索 スコア ブラックボックス」の
  行でP2→P1（2026-08-02昇格）に更新し、P1タイトル一覧に追加しました。
- **点検**: `WRITING_RHYTHM.md` の点検手順（話題テスト・漏出テスト・緊張台帳・拍の点検・
  境界の点検）を両記事に適用済み。文体は「です・ます調」、AI挙動は「傾向が見られる」
  フレーミングを維持し、独自スコア・ブラックボックス指標をOps Octopus側が採用する
  表現は使用していません（新記事はむしろ独自スコアの不透明性を論じる内容）。
- **ビルド確認**: `python build.py` 実行済み。blog記事18件・sitemap 26件で
  ビルドエラーなしを確認しました。
- **SNS転用**: 新規記事2本からX投稿ドラフトを各2案（計4案）生成し
  `sns/x-queue.md` に追記。新規記事が2本以上のため、両記事を束ねたnote記事ドラフトを
  `sns/note-drafts/2026-08-02-brand-name-and-score-transparency.md` に生成しました。
  また、`sns/x-queue.md` の`[x]`済み項目（6件）を`sns/x-posted.md` へ移動しました。

