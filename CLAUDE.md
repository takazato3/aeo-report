# CLAUDE.md — AEOレポートサービス 梅プラン

## このリポジトリについて

AEO（AI検索最適化）調査レポートサービスの「梅プラン（¥300）」フロントエンド。
購入者がトークンを使って、ChatGPT・Claude・Geminiの3AIに同じ質問を投げ、回答を横並びで確認できるWebアプリ。

## 作業ルール

- **必ずDESIGN.mdを読んでから作業を開始すること**
- シングルHTMLファイル（index.html）で完結させる
- 外部ライブラリはCDN経由のmarked.js（Markdownレンダリング）のみ
- GitHub Pagesで動作すること（静的ファイルのみ）
- バックエンドはGAS Webアプリで処理する

## GAS WebアプリURL

```
https://script.google.com/macros/s/AKfycbx_rsGMtxez4G17xEbcX46fk8GFs85lEd--eNdI1BZipoPpJf3nXkkxMfHQAOSaRUb3/exec
```

## 画面構成（シングルページ・3ステップ）

### 画面1：入力フォーム
- トークン入力（購入者に発行されたUUID）
- カテゴリ選択（6択ドロップダウン）
  1. BtoB SaaS / ITツール
  2. コンサルティング / 士業
  3. 人材サービス / HR Tech
  4. マーケティング支援・広告代理店
  5. スクール・資格・習い事
  6. D2Cブランド / EC
- キーワード入力（テキスト・1つ）
- 調査タイプ選択（2択ラジオボタン）
  - 市場での立ち位置を知りたい
  - このブランド・サービスの評判を知りたい
- 「次へ」ボタン → GASにgenerateQuestionリクエストを送信

### 画面2：質問文確認
- GASが生成した質問文を表示
- 「この質問で調査を実行する」ボタン
- 「質問を修正する」→ テキストエリアが開いて編集可能
- 「← 入力に戻る」ボタン
- GASにrunSurveyリクエストを送信

### 画面3：結果表示
- ChatGPT・Claude・Geminiの回答を3カラムで横並び表示
- 各回答はmarked.jsでMarkdownレンダリング
- 使用したプロンプト全文を表示（透明性のため）
- 「※ 回答は読みやすさのため140文字程度に要約しています」を明記
- 竹プランへのアップセル導線

## GAS APIの仕様

### リクエスト形式（全共通）
```json
POST https://script.google.com/macros/s/.../exec
Content-Type: application/json

{
  "action": "generateQuestion" | "runSurvey",
  "token": "uuid形式のトークン",
  ...
}
```

### generateQuestion
```json
// リクエスト
{
  "action": "generateQuestion",
  "token": "xxxx-xxxx-xxxx",
  "category": "人材サービス / HR Tech",
  "keyword": "JAC",
  "type": "brand" | "market"
}

// レスポンス
{
  "success": true,
  "data": { "question": "生成された質問文" },
  "error": null
}
```

### runSurvey
```json
// リクエスト
{
  "action": "runSurvey",
  "token": "xxxx-xxxx-xxxx",
  "question": "確定した質問文"
}

// レスポンス
{
  "success": true,
  "data": {
    "question": "質問文",
    "results": {
      "chatgpt": "回答テキスト",
      "claude": "回答テキスト（Markdown含む）",
      "gemini": "回答テキスト"
    },
    "errors": []
  },
  "error": null
}
```

## エラーハンドリング
- トークン無効・使用済み → エラーメッセージを画面1に表示
- API失敗 → 該当AIのカラムに「取得できませんでした」と表示
- ネットワークエラー → ユーザーへの再試行案内を表示

## 注意事項
- GASへのfetchはCORSエラーが出やすい。`mode: 'no-cors'`は使わず、GAS側がCORSヘッダーを返す設計になっている
- トークンは1回限り有効。runSurvey実行後は使用済みになる
- generateQuestionはトークンを消費しない（確認画面まで何度でも戻れる）
