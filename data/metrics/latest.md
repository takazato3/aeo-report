# 週次メトリクスレポート（2026-10-18）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-09-20 〜 2026-10-17、行数: 0）
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
- detail.html: セッション数 1、エンゲージメント率 0.0%

## 今週の実施アクション

- GSC行数0件・GA4もページ数6件（うちブログ関連は2件のみ）のため、CTR改善・リライト・
  クエリギャップいずれの判断材料もなし（データ欠損・分析不能）。
- 改善バックログ（docs/CONTENT_AUTOPILOT.md）を確認。未処理2件のうち、
  「OpsOctopus実測データ・レポート画像の記事への挿入」はDeep Scan本番稼働が前提条件で
  あり、`scripts/generate_quick_sample.py`の`SAMPLE_TIER=deep`は引き続きQuick実行への
  フォールバックのスタブのままのため今回も処理不可。もう一方の「KEYWORD_MAP.mdのP2候補
  プール枯渇」は、人間による新規クエリ候補の棚卸しが必要という前週の指摘に対し、今回は
  Claudeが競合ギャップの考え方（日本語・ロングテール・実務・非ブラックボックス）に沿って
  棚卸しを代行し解消した（最優先の1件として処理）。
  - クラスタ2（実務・ハウツー系）に新規クエリ候補6件を追加：採用ページAI検索／
    ホワイトペーパーAI引用／口コミサイトAI検索／多言語ページAI検索／
    セミナー・ウェビナーAI検索／社員インタビューAI検索。
- 上記P2候補のうち、既存P1記事（company-profile-page-ai／ai-citable-content／
  primary-source-ai-search／press-release-ai-search／case-study-ai-citation／
  not-appearing-in-chatgpt／structured-data-aeo）との内部リンクが張りやすい2件を選び、
  新規記事として生成しP1へ昇格（KEYWORD_MAP.mdに昇格日2026-10-18で記録）：
  - 採用ページ・求人情報はAIにどう読まれているのか（recruit-page-ai-search）
  - ホワイトペーパー・資料コンテンツはAIにどう使われうるのか（whitepaper-ai-citation）
  - 新規記事側から既存P1記事への内部リンクに加え、company-profile-page-ai.md・
    ai-citable-content.mdにも新規記事への参照リンクを1文ずつ追加し、相互リンク化した。
  - 残り4件のP2候補は未執筆のままプールに保持（次回以降の判断材料）。
- 変更した記事（新規2本・既存2本への軽微な追記）はWRITING_RHYTHM.mdの点検手順
  （話題テスト・漏出テスト・緊張台帳・拍の点検・境界の点検）を実施。本文自身を話題にする
  文・規範語彙の漏出・中盤での二人称依頼は検出されず、断定表現は1箇所
  （「唯一の手がかりになります」→「数少ない手がかりになります」）を修正した。
- `python build.py` 実行済み・ビルド成功（記事35件、sitemap 43件）。
- SNS転用：新規記事2本を生成したため、docs/SNS_REPURPOSE.mdのルールa.に従い各記事から
  X投稿ドラフト2案（計4案）をsns/x-queue.mdの未投稿セクション末尾に追記。新規記事が
  2本以上だったため、ルールb.に従いnote記事ドラフト1本
  （sns/note-drafts/2026-10-18-recruit-page-and-whitepaper.md）を生成。
  x-queue.mdに`[x]`済み項目はなく、sns/x-posted.mdへの移動は発生せず（ルールc.）。
  未投稿が34件で5件を下回っていないため補充も不要（ルールd.は新規記事ありのため非該当）。

