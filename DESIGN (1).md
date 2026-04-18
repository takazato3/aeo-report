# DESIGN.md — AEOレポートサービス

> noteのデザイン言語をベースに、独自サービスとして成立するよう調整したデザイン仕様。
> noteから遷移したユーザーの違和感を最小化しつつ、別サービスであることを明確に示す。

---

## 1. Visual Theme & Atmosphere

- **デザイン方針**: 読みやすさを優先しながら、マーケター・SEOコンサルタントに刺さる、信頼感とポップさを両立したツール系デザイン
- **密度**: ゆったりとした余白。フォームとカードが主役
- **キーワード**: 信頼できる、わかりやすい、親しみやすい、スタートアップ、ツール感
- **noteとの差別化**: ブランドカラーを露草色（`#1B6CA8`）に変更。ヘッダーデザインで別サービスと明示

---

## 2. Color Palette & Roles

### Primary（ブランドカラー）

- **露草色** (`#1B6CA8`): ブランドアイデンティティカラー。ボタン、アクセント、リンクに使用
- **露草色ホバー** (`#155a8f`): ホバー・アクティブ状態

### Semantic（意味的な色）

- **Success** — surface: `#1e7b65`, text: `#1e7b65`, subdued: `#e6f6f2`
- **Danger** — surface: `#b22323`, text: `#b22323`, subdued: `#fdf3f3`
- **Caution** — surface: `#916626`, text: `#916626`, subdued: `#fefbea`

### Neutral — Gray Scale（noteと共通）

- **Gray 900** (`#08131a`): 本文テキスト（ほぼ黒）
- **Gray 800** (`#202a30`): 濃いテキスト
- **Gray 700** (`#363f42`): 強調テキスト
- **Gray 600** (`#5a656b`): セカンダリテキスト
- **Gray 500** (`#7e888f`): 薄いテキスト
- **Gray 400** (`#9ca7ad`): プレースホルダー
- **Gray 100** (`#dce0e3`): ボーダー
- **Gray 50** (`#f5f8fa`): セカンダリ背景

### Text（テキスト色）

- **Text Primary** (`#08131a`): 本文テキスト
- **Text Secondary** (`rgba(8,19,26,0.66)`): 補足テキスト
- **Text Disabled** (`rgba(8,19,26,0.50)`): 無効テキスト
- **Text Invert** (`#ffffff`): 反転テキスト（青背景上）
- **Text Placeholder** (`#9ca7ad`): プレースホルダー

### Surface & Borders

- **Background Primary** (`#fff`): ページ背景
- **Background Secondary** (`#f5f8fa`): セクション背景・カード背景
- **Border Default** (`rgba(8,19,26,0.14)`): 標準ボーダー
- **Border Strong** (`rgba(8,19,26,0.22)`): 強調ボーダー
- **Border Focus** (`#1B6CA8`): フォーカスリング（露草色）
- **Border Accent** (`#1B6CA8`): アクティブ状態のラジオカード等

### AI別カラー（結果表示用）

- **ChatGPT** (`#10a37f`): ドット・アクセント
- **Claude** (`#CC785C`): ドット・アクセント
- **Gemini** (`#4285F4`): ドット・アクセント

---

## 3. Typography Rules

### フォント

```css
/* デフォルト（ゴシック体） */
font-family: "Helvetica Neue", "Hiragino Sans", "Hiragino Kaku Gothic ProN",
  Arial, "Noto Sans JP", Meiryo, sans-serif;

/* 等幅（プロンプト表示用） */
font-family: SFMono-Regular, Consolas, Menlo, Courier, monospace;
```

### 文字サイズ・ウェイト階層

| Role | Size | Weight | Line Height | 備考 |
|------|------|--------|-------------|------|
| Page Title | 28px | 700 | 1.4 | サービス名・ページ見出し |
| Section Heading | 18px | 600 | 1.5 | セクション見出し |
| Body | 16px | 400 | 1.7 | 通常本文 |
| Label | 13px | 500 | 1.5 | フォームラベル |
| Caption | 12px | 400 | 1.5 | 注釈・補足 |
| Button | 15px | 500 | 1 | ボタンテキスト |
| Mono | 13px | 400 | 1.6 | プロンプト全文表示 |

### 文字間隔

- 見出し: `letter-spacing: 0.04em` + `font-feature-settings: "palt"`
- 本文・UI: `letter-spacing: normal`

---

## 4. Component Stylings

### Buttons

**Primary（CTA・実行ボタン）**
```css
background: #1B6CA8;
color: #ffffff;
border: none;
border-radius: 6px;
font-size: 15px;
font-weight: 500;
padding: 13px 24px;
width: 100%;
cursor: pointer;
transition: background 0.15s;

/* hover */
background: #155a8f;
```

**Secondary（戻るボタン等）**
```css
background: transparent;
color: #5a656b;
border: 1px solid rgba(8,19,26,0.22);
border-radius: 6px;
font-size: 14px;
padding: 11px 24px;
width: 100%;
cursor: pointer;

/* hover */
background: #f5f8fa;
```

### Radio Cards（調査タイプ選択）

```css
/* 通常 */
border: 1px solid rgba(8,19,26,0.14);
border-radius: 8px;
padding: 12px 14px;
cursor: pointer;

/* 選択済み */
border: 2px solid #1B6CA8;
background: rgba(27,108,168,0.05);
```

### Cards（結果表示・確認ボックス）

```css
background: #ffffff;
border: 1px solid rgba(8,19,26,0.14);
border-radius: 12px;
padding: 16px 20px;
box-shadow: 0px 1px 3px 1px rgba(0,0,0,0.08), 0px 1px 2px 0px rgba(0,0,0,0.12);
```

### Prompt Box（プロンプト全文表示）

```css
background: #f5f8fa;
border-radius: 8px;
padding: 12px 16px;
font-family: SFMono-Regular, Consolas, Menlo, Courier, monospace;
font-size: 13px;
color: #5a656b;
line-height: 1.6;
```

### Stepper（ステップ進捗）

```css
/* 完了ステップ */
background: #1B6CA8;
color: #ffffff;

/* 現在のステップ */
background: rgba(27,108,168,0.1);
color: #1B6CA8;
border: 2px solid #1B6CA8;

/* 未到達ステップ */
background: #f5f8fa;
color: #9ca7ad;
```

### Header

```css
background: #ffffff;
border-bottom: 1px solid rgba(8,19,26,0.14);
height: 56px;
padding: 0 24px;
display: flex;
align-items: center;
justify-content: space-between;
```

ロゴ・サービス名は露草色（`#1B6CA8`）で表示。noteのナビゲーションとは異なるレイアウトにする。

### Upsell Banner（竹プランへの導線）

```css
background: rgba(27,108,168,0.08);
border: 1px solid rgba(27,108,168,0.2);
border-radius: 12px;
padding: 16px 20px;
```

---

## 5. Layout Principles

### Content Width

| Area | Width | 用途 |
|------|-------|------|
| Main Content | 640px | フォーム・確認画面 |
| Result Grid | 100% (3カラム) | AI回答横並び表示 |
| Max Width | 960px | 結果画面の最大幅 |

### Spacing

- セクション間: `2rem`
- コンポーネント間: `1.25rem`
- コンポーネント内: `8px〜16px`

---

## 6. Do's and Don'ts

### Do（推奨）

- テキスト色は `#08131a` を使い、純粋な `#000000` を避ける
- セカンダリテキストは `rgba(8,19,26,0.66)` で表現する
- ブランドカラー `#1B6CA8` をCTA・フォーカス・アクセントに一貫して使う
- プロンプト表示は必ずmonospaceフォントで表示する
- 3AIの結果カラムは均等幅で横並びにする
- 注釈・透明性の説明文はcaptionサイズ（12px）でグレーで表示する

### Don't（禁止）

- 純粋な `#000000` をテキストに使わない
- noteのブランドカラー `#5ac8b8` を使わない
- グラデーション・派手なアニメーションを多用しない（ツール感を損なう）
- AI回答カードの高さを揃えようとしない（内容量が違うため自然な高さでよい）

---

## 7. Responsive Behavior

### Breakpoints

| Name | Width | 対応 |
|------|-------|------|
| Mobile | < 640px | 結果カラムを縦積みに変更 |
| Tablet | 640px〜 | 2カラム |
| Desktop | 960px〜 | 3カラム横並び |

### タッチターゲット

- ボタン・ラジオカードの最小高さ: 44px

---

## 8. Agent Prompt Guide

### クイックリファレンス

```
Brand Color: #1B6CA8（露草色・CTA・アクセント）
Brand Hover: #155a8f
Text Primary: #08131a
Text Secondary: rgba(8,19,26,0.66)
Background: #ffffff
Background Secondary: #f5f8fa
Border: rgba(8,19,26,0.14)
Focus Ring: #1B6CA8

AI Colors:
  ChatGPT: #10a37f
  Claude: #CC785C
  Gemini: #4285F4

Font: "Helvetica Neue", "Hiragino Sans", "Hiragino Kaku Gothic ProN",
  Arial, "Noto Sans JP", Meiryo, sans-serif
Mono Font: SFMono-Regular, Consolas, Menlo, Courier, monospace

Body: 16px / line-height: 1.7 / letter-spacing: normal
Heading: letter-spacing: 0.04em + font-feature-settings: "palt"
Content Width (form): 640px
Content Width (result): 960px
```
