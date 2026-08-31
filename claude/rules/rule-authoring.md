# AI 向けrule文書の編集

AI agentが指示として読み込む文書（CLAUDE.md、AGENTS.md、rule file、agent定義等。ファイル名・置き場所は問わず消費者がAI agentであることで判定する）に指示を追加・変更・削除・圧縮・移動する時と、「Xするルールを足して」等の依頼を受けた時は、着手前に `Skill(rule-edit)` を起動する。

- 採用基準・書き方・配置と、同じ決定が2箇所に載っていないかを検査する手順がskill側にあるため
- どの仕組み（rule / skill / hook / invocation site）に載せるかの判断がskillの最初の段にあり、rule前提で書き始めると振り分けを飛ばすため
