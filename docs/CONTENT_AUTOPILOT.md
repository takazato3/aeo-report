# Content Autopilot 仕様書

サイト・SNS・noteのコンテンツを自律生成・計測・改善するシステム。

## 全体構成

- ブログ記事：blog/posts/*.md（front matter付きMarkdown）で管理
- build.py がmd→HTML変換・記事一覧生成を担当
- 週次でGitHub Actions cronがClaude Codeをヘッドレス起動し、
  GSC/GA4データを分析して記事の新規生成・改修PRを作成
- PRは48時間異議（holdラベル）がなければ自動マージ・公開
- X投稿・note記事はブログ記事から転用生成（自動送信はしない・
  ドラフト蓄積のみ）

## 判断ロジック（週次）

1. GSCでインプレッション有・CTR低 → タイトル/メタ改修
2. 順位11〜20位 → 加筆リライト
3. クエリギャップ（表示されるが該当記事なし）→ 新規記事生成

## 記事の表現ルール（厳守）

- AI挙動の断定表現禁止。「〜の傾向が見られた」フレーミング
- 独自スコア・ブラックボックス指標を使わない
- 運営者の個人情報・所属を推測させる記述禁止（匿名運営）
- 一人称は「Ops Octopus」または主語なし
- 文章の緩急はdocs/WRITING_RHYTHM.mdに従う（適用範囲注記あり）
- 文体は「です・ます調」を基本とする。WRITING_RHYTHM.mdの
  例文は「だ・である調」だが、これは拍・構造の参考であり、
  文体は模倣しない。断定の拍は「〜です」「〜でした」で作る
  - 例外：引用・箇条書き内の体言止め、FAQの質問文は自由

## 改善バックログ（SEOサイクルで回収）

- ~~既存記事（バッチ1の5本+what-is-aeo）へのWRITING_RHYTHM.md適用~~
  （2026-07-18 完了。aeo-llmo-geo-difference / ai-overviews-aeo /
  ai-search-strategy / geo-vs-seo / what-is-aeo / what-is-llmo の本文
  H2セクションに認知リズム〈観察→逡巡→断定→再観察〉を適用。冒頭結論
  サマリとFAQは適用除外。文体はです・ます調を維持し、点検手順〈話題・
  漏出テスト等〉を実施）
- 記事への共感的な導入（読者の実感の言い直し）の追加
  （上記WRITING_RHYTHM適用時にバッチ1の6記事へは反映済み。バッチ2の
  6記事は未対応のため項目として継続）
- OpsOctopus実測データ・レポート画像の記事への挿入
  （Deep Scan本番稼働後、実調査データを引用素材化する）
- ~~バッチ2の6記事（not-appearing-in-chatgpt他）の
  です・ます調へのリライト~~（2026-07-18 完了。ai-citable-content /
  anticipating-ai-queries / faq-pages-ai-search / how-to-write-llms-txt /
  not-appearing-in-chatgpt / structured-data-aeo の本文をです・ます調へ統一）

## 運用ナレッジ

- GA4接続403（`User does not have sufficient permissions`）の典型原因
  - GitHub SecretsのValueが空登録になっている
  - 測定ID（`G-`から始まる文字列）とプロパティID（数字のみ）を
    取り違えている。`GA4_PROPERTY_ID`には数字のプロパティIDを使う
  - サービスアカウントに権限を付与したGA4プロパティと、実際に
    参照しようとしているプロパティが異なっている
- GSC・GA4はいずれも、サービスアカウントへの権限付与だけでは
  不十分。GCPプロジェクト側で該当APIを有効化していないと
  `403 accessNotConfigured` になる（Search Console API /
  Google Analytics Data API をGCPコンソールで有効化しておくこと）
