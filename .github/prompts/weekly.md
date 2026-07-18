CLAUDE.md、docs/CONTENT_AUTOPILOT.md、docs/WRITING_RHYTHM.md、
docs/KEYWORD_MAP.md、docs/SNS_REPURPOSE.md、data/metrics/latest.md
を読んでください。

以下を実施:
1. CONTENT_AUTOPILOT.mdの改善バックログに未処理項目があれば
   最優先で1件処理し、バックログから消し込む
2. latest.mdの分析結果に基づき、判断ロジック(CTR改善/リライト/
   新規生成)に従ってアクションを最大4件実施。新規記事は
   KEYWORD_MAP.mdのP2から選び、実施後P1に昇格させ記録する
3. データ欠損・分析不能の場合は、まず改善バックログに処理可能な
   項目がないか確認する。バックログにも処理可能な項目がない場合は、
   KEYWORD_MAP.mdのP2から新規記事を最大2本まで生成してよい
   (選定基準:既存P1記事との内部リンクが張りやすいものを優先する)。
   実施後はP2→P1への昇格をKEYWORD_MAP.mdに記録する
4. 変更した記事はWRITING_RHYTHM.mdの点検手順を実行してから確定
5. build.pyを実行しビルドが通ることを確認
6. 実施内容を data/metrics/latest.md の末尾に
   「## 今週の実施アクション」として追記
7. SNS転用(docs/SNS_REPURPOSE.mdのルール厳守):
   a. 今回の実行で新規生成・大幅改稿した記事があれば、
      各記事からX投稿ドラフトを2案生成し sns/x-queue.md の
      未投稿セクションに追記
   b. 新規記事が2本以上あった週は、note記事ドラフトを1本生成し
      sns/note-drafts/YYYY-MM-DD-<slug>.md に保存
      (複数記事を束ねた「今週の実験と観察」形式でもよい)
   c. x-queue.mdの[x]項目をsns/x-posted.mdへ移動
   d. 新規記事がない週はX投稿の生成をスキップしてよい。
      ただしx-queue.mdの未投稿が5件を下回っている場合は、
      既存記事(P1)から未転用のものを選び2案まで補充する

制約:
- 変更してよいのは blog/、docs/、data/、sns/ 配下のみ。
  それ以外(決済導線・LP・build.py等)は変更禁止
- 表現ルール(です・ます調、断定禁止、匿名性)を厳守
- sns/ 配下の生成はドラフトのみ。いかなる外部送信も行わない
