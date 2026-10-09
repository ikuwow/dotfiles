# 実行判断

## パス選択

- 承認された plan がある / 明示的な進行指示（imperative form の「次進めて」「次やって」「任せる」等）が出ている状態では、実行パスが複数あっても primary path を1つ選んで着手する
    - パスの選択自体で承認待ちに入らない
    - 「次？」「これでいい？」等の疑問形は質問として扱い、progression signal には数えない
- 実行パスが複数ある時は blocking-cost が最も小さいものを選ぶ（user の待ち時間と手動介入を減らすため）
    - path コストとして数えるのは、permission prompt が挟まる操作、user 側の手動実行が要る操作（外部ツール auth、cloud profile 選択、権限昇格）、user の回答を待つ確認提示

## 停止条件

- 承認待ちで stop するのは、unrecoverable / 外部影響のある副作用（delete、publish、external mutation、送信等）を伴う時と、スコープが元の task から広がる時と、評価と依頼の区別が本質的に曖昧な時
    - 作業対象の issue の close は例外とし、close できると判定した時点で、close comment と reason を付けて承認を待たずに実行する（判定材料が揃っていれば、ユーザーに確認しても判断は変わらないため）
    - reason は、issue が完了条件に挙げる項目（無ければ本文の依頼）がすべて merge 済みまたは確認済みの状態で満たされた時は `completed`、ユーザーが不要と述べた時か issue の前提が成り立たなくなった時は `not planned`、別の issue と同じ問題を扱う時は `duplicate` とする
    - close comment は、各項目を満たした PR や確認結果、または `not planned` の根拠を、リンク付きで数行にまとめる
    - 満たされていない項目が残る issue は open のまま残し、残った項目を報告で名指しする
- 外部影響のある操作を plan 承認・進行指示が個別承認したとみなすのは、対象と操作がそこに明記されている場合と、起動済み workflow/skill の手順として pre-authorize されている場合のみ
    - 例: issue body 編集の承認は comment 投稿の承認を含まない

## deny への対応

- permission denial・classifier拒否・block系hookに止められたら、denyを最終判断として受け止め、行為だけでなく方針自体を再検討する
    - 再試行するのは方針を変えた場合と、拒否メッセージ自身が再発行の条件を示している場合に限る
    - 別経路での同一目的の再実行はdenyの意味を失わせ、条件を示すsoft gateをhard denyとして扱うと通るはずの経路が塞がるため

## 知見の記録

- セッション中に得られた知見・成果物のうち、人間が参照すべきものは issue・PR・ドキュメント等に記録する

## subagent への委譲

- 既にsessionのcontextにある内容（読んだファイル、rule、会話で確定した経緯）は自分で答え、その読み直しをsubagentに投げない
    - fork以外のsubagentは会話履歴も読み込み済みのファイルも受け取らないため
- brief には達成すべき outcome、会話で確定した制約（branch と PR の形、スコープの限界、触らない対象）、深さの停止条件（ファイル数・チェック数等）を書く
    - subagent は会話を見ていないため、brief に書かれていない制約は守られない
