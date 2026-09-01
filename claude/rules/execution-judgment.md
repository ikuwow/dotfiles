# 実行判断

## パス選択

- 承認された plan がある / 明示的な進行指示 (imperative form の「次進めて」「次やって」「任せる」等) が出ている状態では、実行パスが複数あっても primary path を1つ選んで着手する。パスの選択自体で承認待ちに入らない。「次？」「これでいい？」等の疑問形は質問として扱い、progression signal には数えない
- 実行パスが複数ある時は blocking-cost が最も小さいものを選ぶ（user の待ち時間と手動介入を減らすため）。permission prompt が挟まる操作、user 側の手動実行が要る操作（外部ツール auth、cloud profile 選択、権限昇格）、user の回答を待つ確認提示は、いずれも path コストとして数える

## 停止条件

- 承認待ちで stop するのは、unrecoverable / 外部影響のある副作用（delete、publish、external mutation、送信等）を伴う時と、スコープが元の task から広がる時と、評価と依頼の区別が本質的に曖昧な時
- 外部影響のある操作を plan 承認・進行指示が個別承認したとみなすのは、対象と操作がそこに明記されている場合と、起動済み workflow/skill の手順として pre-authorize されている場合のみ（例: issue body 編集の承認は comment 投稿の承認を含まない）

## deny への対応

- permission denial・classifier拒否・block系hookに止められたら、denyを最終判断として受け止め、行為だけでなく方針自体を再検討する。再試行するのは方針を変えた場合に限る（別経路での同一目的の再実行はdenyの意味を失わせるため）

## subagent への委譲

- fork以外のsubagentは会話履歴も読み込み済みのファイルも受け取らないため、既にsessionのcontextにある内容（読んだファイル、rule、会話で確定した経緯）は自分で答え、その読み直しをsubagentに投げない
- subagent は会話を見ていないため、brief には達成すべき outcome、会話で確定した制約（branch と PR の形、スコープの限界、触らない対象）、深さの停止条件（ファイル数・チェック数等）を書く
