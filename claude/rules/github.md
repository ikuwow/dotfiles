# GitHub

## gh の使い分け

- GitHubの操作はコーディングタスクの場合 `gh` コマンドを使う
    - ghが使えない環境やghで実現できない操作の場合のみ `raw.githubusercontent.com` 等を使ってよい
- `gh` の中では高レベルサブコマンド（`gh pr view` / `gh pr diff` / `gh pr checks` / `gh issue view` / `gh run view` 等）を優先する
    - PRレビュー・レビューコメント・レビュースレッドの取得や操作は `gh pr-review` 拡張（`agynio/gh-pr-review`）を使う
    - sub-issue の list/add/remove は `gh sub-issue` 拡張を使う
    - `gh api`（特に `gh api graphql -f query=...`）はこれらで実現できない操作に限定する
- GitHub repositoryの内部詳細（source code・formula・configファイル等）を確認する時は個別ファイルから入らず上位から順に見る: README → 直近release tagとmain差分（`gh api repos/.../releases`）→ 既知issue/PR検索（`gh search issues/prs`）→ source code
    - CLIの使い方・挙動を `--help`・man page・実機実行で確認する段階では適用不要

## issue・PR の読み方と参照

- GitHub issueを読む際は以下を確認する
    - 親issueがある場合はその内容も読む
    - sub issueの有無を確認し、存在する場合はタイトルとステータスを把握する（詳細まで読む必要はない）
    - 本文とコメント全件を1コマンドで取得する（`gh issue view <number> --json title,body,state,comments`。`--comments` は出力先が端末でない時にコメントだけを出し本文を落とすため）
- GitHubのissue/PRを参照する時は、表示先に合わせて書く
    - GitHub上に載る文章（issue/PR本文・コメント・commit message）では `#123` 形式で書き、現在のリポジトリと異なるリポジトリのものは `orgname/reponame#123` 形式で書く
    - 会話応答では `[#123 タイトル](<issue/PRのURL>)` 形式のMarkdownリンクにする（ターミナル上の `#123` はリンクにならず、番号だけでは何のissueか分からないため）

## issue・PR の作成と書き込み

- PR・issueの作成前と、title・bodyを書く・編集する前に `Skill(pr-issue-writing)` を起動する（チャットに見せる下書きと、git workflow外で走らせる `gh pr edit` / `gh issue edit` を含む）
    - PR・issueの作成前と本文の書き換え前のチェックは、このskillを通した時だけ走るため
    - `implementer` subagentが作るplaceholder PRは対象外（親がdispatch前にskillのpreflightを済ませ、後でtitleとbodyを差し替えるため）
- issue・PR の状態変更と編集（close、reopen、merge、title・body・label・assignee の変更等）は、ユーザーが assignee の issue、ユーザーが author で assignee が空の issue、ユーザーが author の PR を除き、対象と操作を名指しした確認を取ってから実行する（他人の issue・PR は、作業の文脈で完了に見えても持ち主が判断するため）
    - この確認は plan 承認・進行指示・workflow/skill の pre-authorize では代えない
    - ユーザーかどうかは、その場で取った `gh issue view --json author,assignees` / `gh pr view --json author` を `gh api user --jq .login` と突き合わせて判定する
