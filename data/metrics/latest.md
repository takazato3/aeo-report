# 週次メトリクスレポート（2026-07-18）

## データ取得ステータス

- GSC: 取得できませんでした（GSCデータの取得に失敗しました（sc-domain:ops-octopus.com → https://app.ops-octopus.com/ いずれも失敗）: sc-domain:ops-octopus.com: <HttpError 403 when requesting https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3Aops-octopus.com/searchAnalytics/query?alt=json returned "Google Search Console API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.". Details: "[{'message': 'Google Search Console API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.', 'domain': 'usageLimits', 'reason': 'accessNotConfigured', 'extendedHelp': 'https://console.developers.google.com'}]"> / https://app.ops-octopus.com/: <HttpError 403 when requesting https://searchconsole.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fapp.ops-octopus.com%2F/searchAnalytics/query?alt=json returned "Google Search Console API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.". Details: "[{'message': 'Google Search Console API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.', 'domain': 'usageLimits', 'reason': 'accessNotConfigured', 'extendedHelp': 'https://console.developers.google.com'}]">）
- GA4: 取得できませんでした（GA4ページ別レポートの取得に失敗しました: 403 Google Analytics Data API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry. [reason: "SERVICE_DISABLED"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "analyticsdata.googleapis.com"
}
metadata {
  key: "serviceTitle"
  value: "Google Analytics Data API"
}
metadata {
  key: "containerInfo"
  value: "153846392272"
}
metadata {
  key: "consumer"
  value: "projects/153846392272"
}
metadata {
  key: "activationUrl"
  value: "https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=153846392272"
}
, locale: "en-US"
message: "Google Analytics Data API has not been used in project 153846392272 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=153846392272 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry."
, links {
  description: "Google developers console API activation"
  url: "https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=153846392272"
}
]）

## a. ブログ記事別サマリー（GSC・直近28日）

GSCデータが取得できなかったため、このセクションは空です。

## b. 機会クエリ（impressions >= 10 かつ 掲載順位 11〜20）

GSCデータが取得できなかったため、このセクションは空です。

## c. CTR改善候補（impressions >= 20 かつ ctr < 2.0%）

GSCデータが取得できなかったため、このセクションは空です。

## d. クエリギャップ（GSCに出るが対応記事がないクエリ／KEYWORD_MAP.mdのP2と突合）

簡易的な文字列一致による突合のため、参考情報として扱うこと（記事化の要否は人間またはClaudeの判断で最終確認する）。

GSCデータが取得できなかったため、このセクションは空です。

## e. GA4データ（直近28日）

GA4データが取得できなかったため、このセクションは空です。

## 今週の実施アクション

### 判断の前提

- GSC・GA4ともにAPIが無効化されており（project 153846392272 で
  Search Console API / Analytics Data API が未有効化）、
  a〜eの分析データがすべて欠損しました。
- データ欠損のため、判断ロジック（CTR改善／リライト／新規記事生成）は
  実行不能と判断しました。`docs/CONTENT_AUTOPILOT.md` の運用に従い、
  記事品質改善（改善バックログの処理）に切り替えています。
- 新規記事生成は、KEYWORD_MAP.md のP2からデータ駆動で選定する設計のため、
  クエリギャップ実績が得られない今週は見送りました（P2→P1昇格なし）。

### 実施内容（バックログ処理・1件）

- **バッチ2の6記事のです・ます調リライト**（改善バックログの最優先項目・
  「優先度高・計測ループ初回で実施」を消し込み）
  - 対象：`ai-citable-content` / `anticipating-ai-queries` /
    `faq-pages-ai-search` / `how-to-write-llms-txt` /
    `not-appearing-in-chatgpt` / `structured-data-aeo`
  - 本文（導入サマリ・H2セクション群）の文末を「だ・である調」から
    「です・ます調」へ統一。断定の拍は「〜です／〜でしょう」で作り、
    逡巡の拍（〜かもしれません／〜でしょうか）を保持して認知リズムを維持。
  - 表現ルール順守：AI挙動の断定回避（「〜とされています」「〜傾向」）、
    独自スコア不使用、匿名運営（一人称なし）を確認。
  - WRITING_RHYTHM.md の点検手順を実行：話題テスト（導入は適用除外）・
    漏出テスト（規範語彙・節末進行予告ともに検出なし）・拍の点検を通過。
    残存していたプレーン文末2件（`言葉を選ぶ。`／`また試す。`）を修正。
  - `python build.py` 実行済み。全12記事・LP群のビルド成功を確認。

### 次回への申し送り

- **最優先**：GSC / GA4 のAPI有効化。有効化されるまで新規記事の
  データ駆動生成（P2→P1昇格）は保留となります。
- データ復旧後、残る改善バックログ（バッチ1へのWRITING_RHYTHM適用、
  共感的導入の追加、Deep Scan実測データの挿入）を順次処理予定です。

