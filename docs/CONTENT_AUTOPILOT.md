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
- ~~記事への共感的な導入（読者の実感の言い直し）の追加~~
  （上記WRITING_RHYTHM適用時にバッチ1の6記事へは反映済み。2026-07-19に
  バッチ2の6記事（ai-citable-content / anticipating-ai-queries /
  faq-pages-ai-search / how-to-write-llms-txt / not-appearing-in-chatgpt /
  structured-data-aeo）の冒頭へ、読者の実感の言い直しをです・ます調で
  1文ずつ追加し完了）
- OpsOctopus実測データ・レポート画像の記事への挿入
  （Deep Scan本番稼働後、実調査データを引用素材化する）
- ~~バッチ2の6記事（not-appearing-in-chatgpt他）の
  です・ます調へのリライト~~（2026-07-18 完了。ai-citable-content /
  anticipating-ai-queries / faq-pages-ai-search / how-to-write-llms-txt /
  not-appearing-in-chatgpt / structured-data-aeo の本文をです・ます調へ統一）

## サンプルレポート生成

月次でQuick Scanサンプルレポートを自動生成し、マーケ素材(LP掲載・SNS転用)として蓄積する仕組み。

### 全体構成

- ブランドキュー:`data/SAMPLE_BRAND_QUEUE.md`(オーナーが対象ブランドを手動追加。AIは自動選定しない)
- テンプレート:`_templates/quick_scan_sample.html`(既存3サンプルの共通構造をプレースホルダ化したもの)
- 生成スクリプト:`scripts/generate_quick_sample.py`
  - Secret Manager(`GCP_SA_KEY`経由)からOpenAI/Claude/Geminiの各APIキーを取得
  - キュー先頭ブランド(または手動指定ブランド)について、質問文生成→3AI(GPT/Gemini/Claude)への同一質問送信→Claudeによるインサイト要約(共通見解・差分・想定ユーザー・注目ワード)を実施
  - `assets/sample_reports/` にレポートHTMLを出力し、`_src/samples.html` に一覧項目を追記、キューを「未実施」→「実施済み」へ移動、`data/SAMPLE_COST_LOG.md` に概算コストを記録
- 週次ループ(`weekly-content.yml`)とは独立した月次ワークフロー:`.github/workflows/sample-generator.yml`(毎月第1月曜起動 + 手動起動)
- サンプル追加をトリガーにSNS転用ドラフトを生成する:`.github/workflows/sample-to-sns.yml`(`assets/sample_reports/**` へのpushで起動)

### tier切替の考え方(`SAMPLE_TIER` Variable)

リポジトリVariable `SAMPLE_TIER` で `quick`(デフォルト)/`deep` を切り替える想定。現時点では `deep` を指定してもQuick Scan相当の処理にフォールバックするスタブのみが実装されており、実行ログに「Deep tier未実装。Quick実行にフォールバックしました」と出力される。将来Deep Scanが本番稼働した際は、このフォールバック部分をCloud Runの `/process` エンドポイント呼び出しに差し替える(スタブ箇所は`generate_quick_sample.py`内にTODOコメントで明記済み)。手動起動(`workflow_dispatch`)時はtier入力欄でも上書き指定できる。

### 承認フロー

- `sample-generator.yml` が作成するPRには `sample-review` ラベルを付与し、`autopilot` ラベルは付けない。そのため既存の48時間自動マージ(`auto-merge.yml`)の対象外となり、**必ず手動マージ**する(生成コストが発生する処理であり、レポート内容・掲載順・コストログを人が確認してからマージする運用のため)
- 一方、`sample-to-sns.yml` が生成するSNS転用ドラフトPRには `autopilot` ラベルを付与し、既存の48時間自動マージ対象に含める(ドラフトの追記のみで実際の投稿は行わないため、他の週次コンテンツ更新と同様の運用でよい)
- ブランドキューが空の場合は生成をスキップし、`sample-review` ラベル・`assignee: takazato3` 付きのIssueを作成して通知する

### コスト方針

- Quick Scan:3AI(GPT-4o-mini相当/Gemini Flash相当/Claude Sonnet)への1回ずつの問い合わせ + Claudeによる質問文生成・インサイト要約のみのため低コスト。実行のたびに `data/SAMPLE_COST_LOG.md` に概算USDを記録し、増加傾向を追跡できるようにする
- Deep Scan:将来実装。1回あたり3AI×複数質問×複数回の集計となるため、実行都度のコストはQuickより大きく増加する見込み。本番実装時はコストログのフォーマット・単価表を合わせて見直すこと

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
