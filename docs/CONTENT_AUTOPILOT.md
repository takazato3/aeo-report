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
  - 独自にOpenAI/Claude/Geminiへ直接問い合わせることはしない。本番GAS Webアプリ(gas-opsoctopus、CLAUDE.md記載のデプロイURL)の `action: "generateSampleReport"` を呼び出す(認証は環境変数`GAS_SAMPLE_SECRET`、GAS側スクリプトプロパティ`SAMPLE_GEN_SECRET`と照合)
  - このアクションは画面②「調査開始」確定時(`runSurvey`)と同一のコードパスを、人間による質問確認・編集をスキップして実行する。本番のプロンプト・要約仕様が変わってもサンプル生成側の追従が不要になる設計
  - キュー先頭ブランド(または手動指定ブランド)のbrand/category_major/category_sub/direction_hintを送信し、質問文・3AI回答・インサイト(共通見解・言及の差・想定ユーザー・注目ワード)・業界傾向データ(categoriesシート由来)をJSONで受け取る
  - 業界傾向データがcategoriesシート未登録(該当行なし)の場合は生成を失敗させず、「データ未登録」であることが分かる表示にフォールバックする
  - `assets/sample_reports/` にレポートHTMLを出力し、`_src/samples.html` に一覧項目を追記、キューを「未実施」→「実施済み」へ移動、`data/SAMPLE_COST_LOG.md` に実行履歴を記録(本番Quick Scanと同一API枠のため個別コスト算出は行わない)
- 週次ループ(`weekly-content.yml`)とは独立した月次ワークフロー:`.github/workflows/sample-generator.yml`(毎月第1月曜起動 + 手動起動)
- サンプル追加をトリガーにSNS転用ドラフト・ブログ事例記事を生成する:`.github/workflows/sample-to-content.yml`(`assets/sample_reports/**` へのpushで起動。詳細は「サンプル→コンテンツ連携」参照)

### tier切替の考え方(`SAMPLE_TIER` Variable)

リポジトリVariable `SAMPLE_TIER` で `quick`(デフォルト)/`deep` を切り替える想定。現時点では `deep` を指定してもQuick Scan相当の処理にフォールバックするスタブのみが実装されており、実行ログに「Deep tier未実装。Quick実行にフォールバックしました」と出力される。将来Deep Scanが本番稼働した際は、このフォールバック部分をCloud Runの `/process` エンドポイント呼び出しに差し替える(スタブ箇所は`generate_quick_sample.py`内にTODOコメントで明記済み)。手動起動(`workflow_dispatch`)時はtier入力欄でも上書き指定できる。

### 承認フロー

- `sample-generator.yml` が作成するPRには `sample-review` ラベルを付与し、`autopilot` ラベルは付けない。そのため既存の48時間自動マージ(`auto-merge.yml`)の対象外となり、**必ず手動マージ**する(本番と同一のAI API利用枠を消費する処理であり、レポート内容・掲載順を人が確認してからマージする運用のため)
- 一方、`sample-to-content.yml` が生成するSNS転用ドラフト・ブログ事例記事のPRには `autopilot` ラベルを付与し、既存の48時間自動マージ対象に含める(ドラフトの追記・記事の新規追加のみで実際の投稿は行わないため、他の週次コンテンツ更新と同様の運用でよい)
- ブランドキューが空の場合は生成をスキップし、`sample-review` ラベル・`assignee: takazato3` 付きのIssueを作成して通知する

### コスト方針

- Quick Scan:本番GASの`generateSampleReport`アクション経由で3AI(GPT/Claude/Gemini)への1回ずつの問い合わせ+Claudeによる質問文生成・インサイト要約を行う。本番Quick Scanの購入者が消費するのと同一のAPI利用枠(APIキー)を使うため、サンプル生成側で個別にコストを見積もる必要はない。`data/SAMPLE_COST_LOG.md`には実行日・ブランド名・tierの履歴のみを記録する
- Deep Scan:将来実装。1回あたり3AI×複数質問×複数回の集計となるため、実行都度のAPI利用量はQuickより大きく増加する見込み。本番実装時はGAS側のDeep Scan相当アクション追加とあわせて、コストへの影響を確認すること

## サンプル→コンテンツ連携

サンプルレポート(`sample-generator.yml`のPRがマージされ`assets/sample_reports/**`に新規ファイルが追加されたタイミング)をトリガーに、`.github/workflows/sample-to-content.yml`がSNS転用ドラフトとブログ事例記事の両方を1回のワークフロー実行で生成する。

### 仕組み

- トリガー・生成方法とも`weekly-content.yml`と同じくClaude Codeヘッドレス起動(プロンプトは`.github/prompts/sample-to-content.md`)。モデルはコスト予測性のため`sonnet`固定
- X投稿ドラフト2案:既存どおりdocs/SNS_REPURPOSE.mdのルールに従い`sns/x-queue.md`に追記。サンプルレポートの中身(ブランド名・AI回答)には言及しない一般的なサービス紹介文にする
- ブログ事例記事1本:サンプルレポートHTMLの「01 3AIの回答」「02 AIインサイト」セクションの内容のみを根拠に生成し、`blog/posts/<slug>-case-study.md`として保存(front matterの`tags`に"事例"を含める)。記事構成は「結論ファースト→共通点・差分→AEO視点での示唆→サンプルレポート本体へのリンク→自社ブランド確認のCTA(detail.html)」の順で固定。1000〜1500字程度
- docs/WRITING_RHYTHM.mdは記事中間部(共通点・差分、AEO視点での示唆)にのみ適用し、結論部と末尾CTAは適用除外とする(WRITING_RHYTHM.md自体の「適用範囲」注記と同じ考え方)
- 生成後`python build.py`を実行し、`blog/<slug>-case-study.html`・`blog/index.html`・`sitemap.xml`等に反映してからコミットする
- SNS転用ドラフトとブログ事例記事は同一コミット・同一PRにまとめ、`autopilot`ラベルを付与して既存の48時間自動マージフローに乗せる(別立てのPRフローは作らない)

### 承認済みデータのみ使用する制約(厳守)

- ブログ事例記事の執筆にあたり、対象ブランドへ新たにAIへ質問を投げ直したり、Web検索等で追加情報を集めたりすることを禁止する。サンプルレポート(人がレビューし`sample-review`ラベルのPRを手動マージして承認済みの内容)に書かれている情報だけを根拠にする
- この制約により、ブログ記事の内容は必ず「人が確認済みのサンプルレポート」の範囲に収まる。サンプルレポート生成時点(`sample-generator.yml`、必ず手動マージ)での品質管理が、そのままブログ記事側の品質担保にもなる設計

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
