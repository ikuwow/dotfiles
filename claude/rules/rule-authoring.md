---
paths:
  - "**/CLAUDE.md"
  - "**/AGENTS.md"
  - "AIRULES.md"
  - "**/.claude/rules/**"
  - "claude/rules/**"
---
# AI 向けルール・規約ドキュメントの編集

## 振り分け（どの仕組みに載せるか）

書く前に内容を仕組みへ振り分ける。以下はruleに書かず、削除で挙動が変わるとしても適用する。

- 手順・チェックリスト・ワークフロー → skill（ruleは常時ロードされ、手順は使う時しか要らない）
- 絶対に起きてはならない操作 → hook / permissionで強制（guardrailは決定論的である必要があり、指示は破られうる）
- 特定のファイル・作業でしか効かない制約 → `paths` frontmatterでpath-scoped rule化（無関係な作業のcontextから外す）
- モデルの弱点を補償するscaffolding（verification reminder、言い換え反復、進捗報告の強制等）→ invocation site（agent定義本文・delegation brief）
- ruleに残るのは、常時成立する事実と制約だけ

## 採用基準

- 書いてよいのは、削除するとAIの挙動が変わる指示だけ
- 具体的で検証可能に書く（「適切にformatする」でなく「2-space indentation」）
- セクション名・隣接bulletから導ける内容と、モデルが既に知っている一般慣習は書かない
- 特定のAI agent・モデル世代に依存した書き方（モデル名での条件分岐等）をしない
- Loading mechanismについてのmeta-statement（"already in context" 等）はどこにも入れない（mechanism変更でdriftする）

## 書き方

- 制約には従う理由を1行添える（whyは遵守率を上げる。代替案との対比・経緯・ツール動作の解説はwhyではないので書かない）
- 肯定形で書く（禁止を書きたくなったら望む行動の記述に言い換え、強制が必要ならhookへ）
- 指示（何をする / いつする / どう分岐する）を本文の主成分に据える
- 強調マーカー（MUST / CRITICAL / 必ず / 絶対 等）は安全制約・不可逆操作・workflow契約に限定する（濫用は強調の濃淡を壊す）

## 配置

- 置き場所はscopeで決める（そのルールが適用される作業・場面を管轄するファイル・節に置く）
- 常時ロードのファイルは200行/file以内を目安にする（長いほど遵守率が落ちる。このrepoではpre-commit hookが強制）
- 行数を理由に別scopeへ置かない。超える時は削るか、path-scoped rule / skillへ切り出す
- Rule file間のcross-file path参照は入れない（renameで壊れ、auto-load同士なら情報追加ゼロ、相対パスがsymlink経由だと解決しない）
    - 例外1: skill / workflow → ruleのframework名参照は残す（skillが評価対象を名付けるためにload-bearing）
    - 例外2: rule → skillの起動ポインタ（skill名のみ、pathなし）は残す（常時ロードのruleから都度起動のskillへ誘導する）

## 変更手順

- 既存指示の適用を変える時は、隣に追記せず影響を受ける指示文自体を書き換えて統合する（矛盾した指示の併存を防ぐ）
- 追加・変更時は、全rule fileから同じ決定を扱う既存文を列挙し、矛盾・重複が無いことを確認する
- 圧縮・簡素化では元の全bullet・文との対応を突き合わせて政策落ちが無いことを検証し、検証方法をPR本文に明記する
- scope（global / project）を把握し、変更時に明示する

## References

- https://code.claude.com/docs/en/memory.md
- https://code.claude.com/docs/en/best-practices.md
- https://code.claude.com/docs/en/skills.md
- https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- https://claude.com/blog/best-practices-for-prompt-engineering
