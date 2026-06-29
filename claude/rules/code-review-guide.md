# コードレビューガイド

PR レビューの方針と、AI を活用したレビュー支援の手順をまとめた個人ルール。

---

## 0. 大原則

精度を上げるためにレバレッジが効くものからレビューする。

- 優先順位付け（セクション1）: レバレッジの高いPRから着手する
- レビューの進め方（セクション2）: 大きい粒度から評価し、リスクに応じて深さを調整する
- レビューコメント（セクション5）: 設計判断やアーキテクチャへの指摘を優先する

---

## 1. レビュー対象の優先順位付け

レビューリクエストが溜まった場合、以下の基準で優先度を判断する。

### 高優先度

- design doc、ADR、方針を決めるドキュメントのレビュー（設計が正しければ実装は自動生成可能。設計レビューが最もレバレッジが高い）
- 自分が既にコメントしていて議論が継続中のPR（返事待ちの相手をブロックしている）
- REVIEW_REQUIRED で人間の正式レビューがまだないPR
- 作成から日数が経過しているPR（目安: 1週間以上）
- 自分が mention されているPR/issue

### 中優先度

- CHANGES_REQUESTED 状態で修正が入った可能性があるPR
- 未レビューだが作成日が新しいPR
- サイズが大きく他の人がレビューを避けがちなPR

### 低優先度

- 既に他メンバーが APPROVED 済みで、追加の Approve が必要かどうか不明なPR

### 判断に必要な情報

PR一覧を出す際には以下を収集する。優先度の判断自体は LLM が行うが、判断材料となる情報を漏れなく取得するため、以下のコマンドを使う。

#### PR一覧と基本情報の取得

```bash
gh api graphql -f query='
{
  search(query: "is:pr is:open review-requested:<user> org:<org>", type: ISSUE, first: 30) {
    nodes {
      ... on PullRequest {
        repository { name }
        number
        title
        author { login }
        additions
        deletions
        changedFiles
        reviewDecision
        createdAt
        updatedAt
        isDraft
        latestReviews(first: 10) {
          nodes {
            author { login }
            state
          }
        }
      }
    }
  }
}'
```

取得できる情報:
- リポジトリ名、PR番号、タイトル、Author
- 変更サイズ（additions/deletions/changedFiles）
- reviewDecision（REVIEW_REQUIRED / APPROVED / CHANGES_REQUESTED）
- 既存レビューの状況（誰がどの state か）
- 作成日・最終更新日

注意: `latestReviews` は各ユーザーの最新レビューのみ返す。過去のレビュー履歴が必要な場合は REST API（`gh api repos/<org>/<repo>/pulls/<number>/reviews`）を使う。

個別PRの詳細確認や diff 取得のコマンドはセクション2を参照。

### レビュー中の一覧再取得

PR一覧は各PRのレビュー完了ごとに再取得し、優先順位を並び替える。時間経過で状態が変わったり差し込みが来たりするため、常に最新の優先順位で進める。

### 関連PRのまとめレビュー

同じ issue や同じ feature に紐づくPR（例: アプリ側 + IaC側）は、まとめてレビューする。個別に見ると全体の整合性を判断しにくい。

---

## 2. レビューの進め方

### リスク判定と深さの調整

大きい粒度の評価を行った上で、リスクに応じてレビューの深さを調整する。

- ユーザーや自分たちに対するリスクが低く、間違えても気づけて事後対処できる変更は、詳細レビューに入らず approve でよい
- 例: 新規リソースの追加のみ（既存への影響なし）、既存パターンの複製、検証済みコードの再適用

### 大きい粒度から始める

コードの細かい行単位の指摘より先に、以下の観点で全体を評価する:

1. 要件を満たしているか
   - 対応 issue の受け入れ条件との照合
   - design doc がある場合、実装との整合性
   - 要件の分類は正確か（機能要件と非機能要件の混同がないか）
2. 全体設計は妥当か
   - アーキテクチャ上の位置づけ
   - 関連PR群との依存関係とデプロイ順序
   - 既存システムへの影響範囲
   - design doc の場合: ドキュメントの位置付け・目的は適切か（設計書なのか実装計画書なのか）
3. 検証は十分か
   - テストがカバーしている範囲
   - STG/本番での検証計画
   - 監視・アラートの設計と実装の有無
4. design doc との乖離がないか
   - 設計判断が途中で変わった場合、doc が更新されているか
   - 数値（リトライ回数、タイムアウト値など）の不一致

### 細かい粒度のレビュー

大きい粒度の確認が終わってから、コードレベルの指摘に入る:

- 実装の正しさ（ロジックの誤り、エッジケース）
- エラーハンドリングの妥当性
- テストの品質（モック期待の強度、網羅性）
- 既存コードとの一貫性（命名規則、ヘルパー関数の再利用）

### 参照すべき情報と取得コマンド

レビュー時に以下を確認する。各情報の取得コマンドを示す。

#### PR 本文・メタデータ

```bash
gh pr view <number> -R <org>/<repo> --json title,body,baseRefName,url,reviewDecision
```

`baseRefName` が main でない場合は chain PR。依存先PRの状態も確認する。

#### 既存のレビューコメントと議論の経緯

PR レベルのレビュー状態:

```bash
gh pr view <number> -R <org>/<repo> --json reviews --jq '.reviews[] | {author: .author.login, state: .state, body: .body[:200]}'
```

インラインのレビューコメント:

```bash
gh api repos/<org>/<repo>/pulls/<number>/comments --jq '.[] | {author: .user.login, path: .path, body: .body[:300], created_at: .created_at}'
```

PR レベルのコメント:

```bash
gh pr view <number> -R <org>/<repo> --json comments --jq '.comments[] | {author: .author.login, body: .body[:300]}'
```

#### 対応 issue の内容

```bash
gh issue view <number> -R <org>/<repo> --json title,body,state,assignees
gh issue view <number> -R <org>/<repo> --comments
```

親 issue がある場合はその内容も確認する。sub issue の有無とステータスも把握する。
issue のコメントにはブロッカー情報（外部ベンダーの回答待ち等）が書かれていることがある。

#### diff の取得

変更ファイル一覧:

```bash
gh pr diff <number> -R <org>/<repo> --name-only
```

diff 全体:

```bash
gh pr diff <number> -R <org>/<repo>
```

#### PR ブランチのコードをローカルで読む

GitHub API でファイルを取得するよりローカルクローンの方が高速で確実。

```bash
git -C <local-repo-path> fetch origin <branch-name>
git -C <local-repo-path> show FETCH_HEAD:<file-path>
```

#### design doc

PR 本文にリンクがある場合、design doc の PR diff から取得する:

```bash
gh pr diff <design-doc-pr-number> -R <org>/<repo>
```

#### Revert / Revert^2 PR

Revert の Revert（再適用）PR の場合、元PRとの diff 比較を行い、変更内容が同一かどうかを確認する。差分がある場合（feature flag の除去など）はその差分がレビューの核心になる。

```bash
gh pr diff <original-pr-number> -R <org>/<repo>
```

#### 関連情報

- 関連する他の PR（同じ feature の分割PR群）
- 環境設定（manifests、IaC）との同期

---

## 3. 機械的に検知すべき観点

レビューで人間が気づいた問題のうち、以下は lint rule や CI チェックで自動検知・ブロックできる。レビュー中にこの類の問題を見つけたら、コメントで指摘するだけでなく、自動検知の仕組みの導入を提案する。

### 未使用リソースの検出

- 宣言されているが使われていない変数、import、依存関係、provider 等
- 各言語・ツールの linter にルールがあることが多い

### 設定値の整合性

- 同じ値が複数箇所（IaC、アプリ設定、manifests）に定義される場合の不一致
- 環境変数がアプリ側で required なのにデプロイ設定に存在しない

### PR間の依存関係

- base branch が main でないPR（chain の検出）
- 依存先PRがマージされていない状態での approve/merge 防止

### テストの品質

- モック期待の緩和（厳密な呼び出し回数の検証が外される変更）
- テスト内での固定時間 sleep（非決定的なテストの原因）

### design doc と実装の乖離

- 数値的な設定値（タイムアウト、リトライ回数、バッチサイズなど）が design doc の記述と異なる
- 完全な自動化は難しいが、design doc 内の設定値テーブルと IaC/コードの突き合わせは半自動化できる可能性がある

---

## 4. AI によるレビュー支援

### AI に依頼する流れ

1. PR一覧の取得と優先順位付け（セクション1のコマンドを使用）
2. 各PRについて以下を順に実行:
   a. PR の URL を先に提示する（ユーザーが並行して PR を見始められるようにする）
   b. PR 本文・レビュー状態・コメント経緯の取得と要約（セクション2のコマンドを使用）
   c. 対応 issue の確認（ブロッカーや外部依存の有無を含む）
   d. 大きい粒度の評価（要件充足、設計妥当性、検証計画）
   e. design doc がある場合、実装との整合性チェック
   f. コード diff の読み取りと気になるポイントの列挙
3. ユーザーが PR にコメント・approve した場合、その内容を確認する（approve に伴うコメントも含む）
4. 各PR完了時にユーザーのレビューコメントへのフィードバックを行う（カバレッジ、よかった点、改善点）
5. 優先度の区切りごとに、ガイドへの反映を提案する
6. レビューコメント投稿後、自分のコメント内容を AI に読ませてルールへのフィードバックを確認

### AI 活用時の注意点

- 行番号はソースファイル上の実際の行番号で示す（diff 出力上の行番号ではない）
- ローカルにクローン済みのリポジトリがあればそれを読む（GitHub API でファイル取得しない）
- PR ブランチのコードは `git fetch origin <branch>` → `git show FETCH_HEAD:<path>` で読む
- ライブラリやSDKの挙動は公式ドキュメントを参照する（ソースコードを clone して読みに行くのはやりすぎ）
- gh command でできることは gh command で行う（不要なサブエージェントを生成しない）

### コメント投稿の分担

- 人間が書いた PR コメントへの返信はユーザー自身が行う。AI は手を出さない
- bot / AI（Devin 等）のコメントや指摘への返信は AI が対応してよい

---

## 5. レビューコメントの方針

- 質問と指摘を区別する（「これは意図的？」vs「ここは変えるべき」）
- design doc との乖離は「doc を更新するか、実装を変えるか」の選択肢を示す
- 細かいスタイルの指摘は強制しない
- 全体OKなら Approve した上でインラインコメントを残す形でよい
- 機械的に防げる指摘を見つけたら、lint rule や CI チェックの導入を提案する
