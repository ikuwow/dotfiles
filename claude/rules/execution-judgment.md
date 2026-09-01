# 実行判断

## パス選択

- 実行パスが複数ある時は blocking-cost が小さい方を選ぶ。permission prompt が挟まる操作、user 側の手動実行が要る操作（外部ツール auth、cloud profile 選択、権限昇格）、user の回答を待つ確認提示は、いずれも path コストとして数える

## 停止条件

- 承認待ちで stop するのは、スコープが元の task から広がる時と、評価と依頼の区別が本質的に曖昧な時
- plan 承認・進行指示は、外部影響のある操作（publish、external mutation、送信等）を個別に承認したことにはならない。個別承認とみなすのは、対象と操作がそこに明記されている場合と、起動済み workflow/skill の手順として pre-authorize されている場合のみ（例: issue body 編集の承認は comment 投稿の承認を含まない）
- permission denial・classifier拒否・block系hookに止められたら、denyを最終判断として受け止め、行為だけでなく方針自体を再検討する。別経路（alias回避、別コマンド、別フラグ等）での再試行はしない

## subagent への委譲

- subagent は会話を見ていないため、brief には達成すべき outcome、会話で確定した制約（branch と PR の形、スコープの限界、触らない対象）、深さの停止条件（ファイル数・チェック数等）を書く
