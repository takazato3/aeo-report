# CLAUDE.md — Ops Octopus AIブランド調査レポートサービス

## このリポジトリについて

**Ops Octopus** のWebサイト（LP・購入後ツール）のフロントエンド。
ChatGPT・Claude・Geminiの3AIに同じ質問を投げ、ブランドのAI上での評判・推奨傾向を調査するレポートサービス。

GitHub Pagesで静的配信。バックエンドはGoogle Apps Script（GAS）Webアプリ。

---

## 作業ルール

- **必ずDESIGN.mdを読んでから作業を開始すること**
- GitHub Pagesで動作すること（静的ファイルのみ）
- フロントエンドのページ編集は後述のビルドシステムに従うこと

---

## サイト構造

### ビルド管理対象ページ（LP・サポートページ群）

| ファイル | 役割 |
|---|---|
| `index.html` | LP（ヒーロー・サービス説明・料金プラン・購入導線） |
| `detail.html` | プラン詳細・調査フロー説明ページ |
| `samples.html` | サンプルレポートインデックスページ |
| `faq.html` | よくある質問ページ |
| `legal.html` | 特定商取引法に基づく表記 |
| `privacy.html` | プライバシーポリシー |

これらのページのヘッダー・フッターは後述のビルドシステムで一元管理している。

### ビルド管理対象外ページ（単体完結ファイル）

| ファイル | 役割 |
|---|---|
| `quick-scan.html` | Quick Scan購入後の調査ツール本体。外部ファイルへの依存なしでシングルHTMLファイルとして完結 |
| `preview.html` | レポートプレビュー用ページ（内部利用） |

---

## ビルドシステム（ヘッダー・フッターの一元管理）

### 仕組み

ヘッダー・フッターをパーシャルファイルとして管理し、Pythonスクリプトで各ページに注入する。

```
_partials/
  header.html    ← 全ページ共通ヘッダー（ここを編集）
  footer.html    ← 全ページ共通フッター（ここを編集）
_src/
  index.html     ← ページ本体（ヘッダー位置は <!-- HEADER -->、フッターは <!-- FOOTER --> マーカー）
  detail.html
  samples.html
  faq.html
  legal.html
  privacy.html
build.py         ← ビルドスクリプト
```

ルートの `*.html`（index.html 等）は `build.py` の出力物。直接編集しない。

### ページ本文を変更するとき

```bash
# 1. _src/ 配下の対象ファイルを編集する
# 2. ビルドを実行してルートHTMLに反映する
python build.py
# 3. コミット・プッシュ
git add -A && git commit -m "..." && git push
```

### ヘッダー・フッターを変更するとき

```bash
# 1. _partials/header.html または _partials/footer.html を編集する
# 2. ビルドを実行（全ページに自動反映される）
python build.py
# 3. コミット・プッシュ
git add -A && git commit -m "..." && git push
```

### 新しいページを追加するとき

1. `_src/newpage.html` を作成し、ヘッダー位置に `<!-- HEADER -->`・フッター位置に `<!-- FOOTER -->` を記述
2. `build.py` 内の `TARGET_PAGES` リストに `'newpage.html'` を追加
3. `python build.py` を実行

### ヘッダーのナビゲーションリンク構成

```
サービス概要 → index.html#about
プラン・料金 → detail.html
サンプル     → samples.html
よくある質問 → faq.html
[購入CTA]    → https://buy.stripe.com/6oU14ndhZcAR4XR1EKcwg00
```

### quick-scan.html はビルド管理対象外

`quick-scan.html` は購入後ツールのため独立したシングルHTMLで完結させる。
ビルドシステムには含まれない。編集する場合はファイルを直接変更する。

---

## デザイン・フォント

- CSS変数：`--navy-950`・`--amber-400`・`--text-dark`・`--border` 等（DESIGN.md参照）
- フォント：`DM Sans`（見出し・UI）・`Noto Sans JP`（本文・日本語）
- アイコン：Google Material Icons（CDN）
- ページ背景はライト系（`--white` または `--off-white`）。ヘッダーのみ `--navy-950` 系ダーク

---

## GAS Webアプリ（バックエンド）

quick-scan.html が呼び出すエンドポイント。

```
https://script.google.com/macros/s/AKfycbzYeiBAv2CY5zqLjx2kbHTRegNRkdz2dAecGwa2MDH_c6_5NpIocr9xpVP3ItwT7m-0-Q/exec
```

- `action: "generateQuestion"` → カテゴリ・キーワードから質問文を生成（トークンを消費しない）
- `action: "runSurvey"` → 3AIに質問し結果を返す（トークンを1回消費）
- GASへのfetchはCORSヘッダーをGAS側が返す設計。`mode: 'no-cors'` は使わない
- トークンは1回限り有効。runSurvey完了後は使用済みになる

---

## 計測・SEO

- 各ページにメタタグ・OGPを設定済み
- GA4トラッキングコード：未設置（測定ID確定後に追加予定）
- sitemap.xml：未作成
