---
name: rule-edit
description: Changing or judging a rule document that an AI agent loads as instructions - CLAUDE.md, AGENTS.md, AIRULES.md, files under .claude/rules/, any file whose consumer is an agent rather than a person. Carries the criteria for what belongs in a rule (振り分け, 採用基準), how to word it (書き方), where to put it (配置), and the change procedure. Trigger whenever a task will add, reword, delete, compress, split, or relocate an instruction in such a file, including a one-line tweak, a "just add a rule so you stop doing X" request, and rule edits reached from /retro-review or a retrospective. Trigger equally when the user only asks about an existing rule rather than asking for an edit - whether it is worded well, whether it belongs where it sits, whether it duplicates another rule, whether it should be a rule at all or a skill or a hook - since answering that needs the same criteria.
---

# Rule Edit

`criteria.md`（このファイルの隣）が、何をruleに載せるか（振り分け）、何を残すか（採用基準）、どう書くか（書き方）、どこに置くか（配置）を定める。編集の前に読む。

## 変更手順

- scope（global / project）を把握し、変更時に明示する
- 追加・変更時は、同じ決定を扱う既存文を列挙し、矛盾・重複が無いことを確認する
  - 探索先は user-levelのrule setと対象プロジェクトのrule file
  - `~/.claude/rules/` は各エントリがsymlinkなので `grep -Rn` を使う（`-r` はsymlinkを辿らず、何も検索せずに0件を返す）
  - 矛盾が出た時はどちらを残すかをユーザーに確認する
- 振り分けで行き先を決めてから書く
  - 既にhookが強制している制約は、ruleに書くと拒否されるtool callを1回減らす価値で判断する
- 既存指示の適用を変える時は、影響を受ける指示文自体を書き換えて統合する
  - 隣への追記は矛盾した指示の併存を生むため
- 圧縮・簡素化・分割では、元の全bullet・文との対応を突き合わせて指示の欠落が無いことを検証し、その対応表を成果物（PR本文等）に載せる
  - 削除元と行き先が別ファイルに分かれる移動はrenameとして検出されず、対応がdiffから復元できないため
  - 受け皿の側が自分のscope文で当該ケースを除外していないかを、topicだけでなくscope文まで読んで確認する
- 編集後、編集対象のファイルが `criteria.md` に準拠していることを確認する

## 変更が大きい時に足す

常時ロード面の再編、複数ファイルにまたがる移動、削除を伴う圧縮では、上に加えて:

- 準拠確認を、編集意図を伝えない別contextのsubagent（`opus`）に投げる。編集したsessionは自分が意図した意味を文面に読み戻すため
- PR本文に貼るコマンド出力は、branchが最終的に落ち着いた文言で実行し直す。文言変更後に手で直した出力は再現しなくなるため
