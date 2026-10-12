---
name: pr-review
description: The user's own policy and procedure for reviewing pull requests written by other people together with the user - working through the queue of PRs that request the user's review, prioritizing it, sizing review depth to risk, judging the overall design before line-level comments, and leaving every post on the PR to the user. Use whenever the user asks to review someone else's PR, to go through review requests or the review queue, or to decide which PR to review next, even when they only paste a PR URL and say "レビューして". Not for the user's own PRs, which pr-selfcheck and the git-workflow review phases cover.
---

# PR Review

ユーザーと一緒に他人の PR をレビューする時の方針と手順。

## 方針

- レビューは早く返すことを、網羅することより優先する
    - レビュー待ちの PR は作者の作業を止めているため
    - 各 PR では、approve できそうかと主な論点を最初に出し、細部の確認はその後に回す
- 大枠から見る
    - 要件を満たしているか、設計がざっくり妥当か、検証は足りているかを先に判断し、行単位の指摘はその後にする
    - 設計が誤っていれば、行単位の指摘は書き直しで無駄になるため
- リスクで深さを変える
    - ユーザーやチームへの影響が小さく、誤っても気づけて後から直せる変更は、細部の確認に入らず approve を提案する
    - 例: 既存に影響しない新規リソースの追加、既存パターンの複製、検証済みのコードの再適用
- 機械的に検出できる問題を見つけたら、コメントでの指摘に加えて、lint rule や CI チェックの導入を提案する
    - 同じ種類の指摘を人間のレビューで繰り返さずに済むため
- design doc と実装が食い違っていたら、doc を直すか実装を直すかの2択として示す
    - どちらが正しいかは作者とチームが決めることのため
- 他人の PR へのコメント、返信、レビューの投稿はユーザーが行う
    - 投稿はユーザーのアカウントで他人の PR に書き込むことになるため
    - 相手が bot や AI agent のコメントでも同じで、AI が投稿した方がよいと判断した時は、投稿する前にユーザーに尋ねる

## キューの優先順位

レビュー依頼が複数ある時は、次の順に着手する。1つの PR が複数の段に当てはまる時は、上の段を採る。

1. design doc、ADR など方針を決める文書の PR
    - 設計が決まれば実装はそれに従うので、設計のレビューが最も多くの後続作業に効くため
1. ユーザーがレビュー済みで、その後に作者の返信か新しい commit がある PR
    - 議論の途中で作者がユーザーの返事を待っているため
1. 人間による APPROVED と CHANGES_REQUESTED がまだ無い PR と、ユーザーが mention されている PR
    - この段の中では作成日の古い順に着手し、作成から1週間以上の PR を特に先にする
1. 他のメンバーが CHANGES_REQUESTED を付けた後に、新しい commit が入った PR
1. 他のメンバーが既に approve しており、追加の approve が要るか分からない PR

ユーザーが approve 済みで、その後に新しい commit もコメントも無い PR は、キューから外す。

同じ issue や機能に紐づく PR（アプリ側と IaC 側など）は、続けてまとめてレビューする。個別に見ると全体の整合性を判断できないため。

## キューの取得

レビュー依頼の一覧は次の3つを合わせて作る。

```bash
gh search prs --review-requested=@me --state=open --sort updated --limit 100 --json repository,number,title,author,createdAt,updatedAt,isDraft,url -- -author:@me
gh search prs --reviewed-by=@me --state=open --sort updated --limit 100 --json repository,number,title,author,createdAt,updatedAt,isDraft,url -- -author:@me
gh search prs --mentions=@me --state=open --sort updated --limit 100 --json repository,number,title,author,createdAt,updatedAt,isDraft,url -- -author:@me
```

- `--reviewed-by` を足すのは、レビューを投稿した PR からはレビュー依頼が外れることがあり、議論中の PR が `--review-requested` から消えるため
- `-author:@me` でユーザー自身の PR を除く
    - ユーザー自身の PR にもユーザーの COMMENTED のレビューが付くことがあり、`--reviewed-by` に当てはまるため
- 結果が `--limit` の件数に届いた時は、取りこぼしがありうることをユーザーに伝える
- 組織を絞る時は `--owner <org>` を付ける
- 優先順位の判定に要る値は、PR ごとに取る
    - 文書の PR か、commit の日時: `gh pr view <number> -R <owner>/<repo> --json files,commits,reviewDecision`
    - レビューの履歴: `gh pr-review review view -R <owner>/<repo> <number>`（`latestReviews` はレビュアーごとに最新の1件しか持たず、前の CHANGES_REQUESTED が分からないため）

1件のレビューが終わるごとに一覧を取り直して並べ直す。レビュー中にも新しい依頼や状態の変化が入るため。

## 1件のレビューの流れ

1. PR の URL を最初に出す
    - ユーザーが並行して PR を開いて読み始められるため
1. 本文とメタデータを取得し、作者がユーザー自身でないことを確認する
    - `gh pr view <number> -R <owner>/<repo> --json author,title,body,baseRefName,url,reviewDecision,comments,closingIssuesReferences`
    - `author.login` を `gh api user --jq .login` と比べ、ユーザー自身の PR なら、この skill の手順ではなく pr-selfcheck を使う
1. レビューの状態と議論の経緯を要約する
    - レビューとインラインのスレッド: `gh pr-review review view -R <owner>/<repo> <number>`
    - `gh pr list -R <owner>/<repo> --head <baseRefName>` で base branch を head にする open な PR があれば chain PR なので、依存先の PR の状態も確認する
1. 対応する issue（`closingIssuesReferences`）を読み、ブロッカーや外部への依存が書かれていないか確認する
1. 大枠を評価して、approve できそうかと主な論点を出す
    - 要件：issue の受け入れ条件と照合する
    - 設計：関連 PR との依存関係とデプロイ順序、既存システムへの影響範囲を見る
    - 検証：検証環境と本番での確認計画、監視とアラートの有無を見る
    - design doc の PR では、文書の位置づけ（設計書か実装計画書か）が目的に合っているかを見る
    - リスクが低いと判断した時は approve を提案し、以降の手順はユーザーが求めた時に進める
1. design doc がある時は、実装との食い違いを探す
    - 途中で変わった設計判断が doc に反映されているか
    - リトライ回数、タイムアウト、バッチサイズ等の数値が一致しているか
1. diff を読み、気になる箇所を挙げる
    - 行番号はソースファイル上の行番号で示し、追加行と変更行は head 側、削除行は base 側の番号を使う（diff 出力上の行番号はユーザーがエディタで辿れないため）
    - PR ブランチのファイル全体を読む時は、`ghq list -p -e <owner>/<repo>` でローカルの clone を探し、`git -C <clone> fetch origin pull/<number>/head` の後に `git -C <clone> show FETCH_HEAD:<path>` で読む
    - clone が無い時は `gh pr diff <number> -R <owner>/<repo>` の範囲で読む
1. Revert の Revert（再適用）の PR では、元の PR の diff と比べる
    - 差分があれば（feature flag の除去など）、その差分を論点にする
1. ユーザーがコメントや approve を投稿したら、その内容を読み、指摘の網羅度、良かった点、改善できる点をフィードバックする
