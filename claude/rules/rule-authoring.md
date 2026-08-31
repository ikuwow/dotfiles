# AI 向けrule文書の編集

rule文書（CLAUDE.md、AGENTS.md、rule file等。ファイル名・置き場所は問わず消費者がAI agentであることで判定する）について、指示を追加・変更・削除・圧縮・分割・移動する時と、既存の指示の書き方・置き場所・重複・そもそもruleにすべきかを問われた時は、着手前に `Skill(rule-edit)` を起動する。

- どの仕組み（rule / skill / hook / invocation site）に載せるかの判断と、採用基準・書き方・配置と、同じ決定が2箇所に載っていないかの検査がすべてskill側にあり、rule前提で答え始めると振り分けを飛ばすため
