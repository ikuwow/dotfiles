# 実行判断

## primary path の選択と進行

- 承認された plan がある / 明示的な進行指示 (imperative form の「次進めて」「次やって」「任せる」等) が出ている状態では、実行パスが複数あっても primary path を1つ選んで着手する。パスの選択自体で承認待ちに入らない。「次？」「これでいい？」等の疑問形は progression signal に該当しない (質問として回答し、修正方針が自明なら提案・着手してよい)
- パス選択時は blocking-cost を最小化する。以下は path コストとして扱い、他に選択肢があるパスを優先する
  - Claude Code の permission prompt が挟まる操作 (`--force*`, `git reset --hard`, `git branch -D`, `rm -rf` 等)
  - user 側で手動実行が必要な操作 (外部ツール auth、cloud profile 選択、sudo 等の権限昇格、手動 shell コマンド実行)
  - user への回答を待つ確認提示 (A/B 選択の丸投げ、方針レビュー要求)

## 停止条件

- 承認待ちで stop するのは以下の場合のみ
  - unrecoverable / 外部影響のある副作用 (delete、publish、external mutation、send message 等)。上の cat 1 destructive で他に代替パスが無い場合もこの stop に落ちる。plan 承認・進行指示がこれらを個別承認するのは、対象と操作がそこに明記されている場合と、起動済み workflow/skill の手順として pre-authorize されている場合のみ (例: issue body 編集の承認は comment 投稿の承認を含まない)
  - スコープが元の task から広がる
  - 評価／依頼の区別が本質的に曖昧
- 承認待ちのsafety mechanism（hook拒否、permission denial、classifier拒否等）に一度止められたら、別経路（alias回避、別コマンド、別フラグ等）で同じ行為を再試行しない。denyを最終判断として受け止め、行為だけでなく方針自体も再検討する

## プランの自己完結と知見の記録

- プランを作成・出力する前に、会話の中にある制約・前提（ブランチ・PR構成、スコープの限定等）を漏らさずプランに含めること。プラン承認後にcontextがクリアされても実装に支障がないよう、プランを唯一の情報源として完結させること
- セッション中に得られた知見・成果物のうち、人間が参照すべきものは issue・PR・ドキュメント等に記録する。AI が次回以降の会話で参照すべき行動指針や事実は user rule (`AIRULES.md` / `~/.claude/rules/`) または project rule (`CLAUDE.md` / 各リポの `.claude/rules/`) に直接書く

## セッション終了時

- ユーザーがタスク完了・セッション終了を宣言したら（「終わり」「done」「これで完了」等）、確認せず自動的に `/retro-note` skill を invoke する
  - 深い分析が必要な時のみ明示的に `/retrospective` を呼ぶ
