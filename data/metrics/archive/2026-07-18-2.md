# 週次メトリクスレポート（2026-07-18）

## データ取得ステータス

- GSC: 取得成功（プロパティ: `https://app.ops-octopus.com/`、期間: 2026-06-20 〜 2026-07-17、行数: 0）
- GA4: 取得できませんでした（GA4ページ別レポートの取得に失敗しました: 403 User does not have sufficient permissions for this property. To learn more about Property ID, see https://developers.google.com/analytics/devguides/reporting/data/v1/property-id.）

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

GA4データが取得できなかったため、このセクションは空です。

## 今週の実施アクション

- **実施日**: 2026-07-18
- **判断**: GSCが0行、GA4が403で、CTR改善候補・機会クエリ・クエリギャップの
  いずれも算出できず、メトリクスに基づく判断は不能でした。
  `docs/CONTENT_AUTOPILOT.md` の判断ロジック（3）およびタスク指示（3）に従い、
  CTR改善／リライト／新規生成ではなく、記事品質改善（改善バックログ処理）へ
  切り替えました。
- **処理したバックログ項目（1件消し込み）**:
  「既存記事（バッチ1の5本+what-is-aeo）へのWRITING_RHYTHM.md適用」
- **対象記事（6本）**:
  what-is-aeo / what-is-llmo / geo-vs-seo / aeo-llmo-geo-difference /
  ai-search-strategy / ai-overviews-aeo
- **内容**: 各記事の本文H2セクションに認知リズム〈観察→逡巡→断定→再観察〉を
  適用し、節冒頭を読者の反問・違和感・共感的な言い直しで開く形へ改稿。
  文体は「です・ます調」を維持し、`WRITING_RHYTHM.md` の例文の文体（だ・である調）
  は模倣していません。冒頭の結論サマリと末尾のFAQは適用除外としました。
  front matter・内部リンク構造・FAQは保持しています。
- **点検**: `WRITING_RHYTHM.md` の点検手順（話題テスト・漏出テスト・緊張台帳・
  拍の点検・境界の点検）を実施。平叙終止2件（aeo-llmo-geo-difference）と
  進行予告の疑い1件（ai-search-strategy「次は」→「今度は」）を修正済み。
- **表現ルール**: AI挙動の断定を避け「傾向が見られる」フレーミングを維持。
  独自スコア不使用・匿名運営・一人称なし/Ops Octopusの各ルールを遵守。
- **ビルド**: `python build.py` 成功（ルート7ページ＋blog記事12本を再生成）。
- **KEYWORD_MAP更新**: 新規記事生成なし。データ欠損のため新規生成は見送り、
  P2→P1昇格は行っていません。
- **変更範囲**: `blog/`・`docs/`・`data/` 配下のみ（決済導線・LP・build.py等は不変更）。

