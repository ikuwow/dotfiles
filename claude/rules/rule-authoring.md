# AI 向けルール・規約ドキュメントの編集

このルールはAI agentが指示として読み込む規約・ルール文書すべて（CLAUDE.md、AGENTS.md、rule file、agent・skill定義の指示部等）に適用される。
ファイル名・置き場所は問わず、消費者がAI agentであることで判定する。

## 振り分け（どの仕組みに載せるか）

ルールには常時成立する事実と制約のみを記述する。
この振り分けは、削除で挙動が変わる内容にも適用する。

ルールに書かないものの例:

- 手順・チェックリスト・ワークフロー: skill
  - ruleは常時ロードされ、手順は使う時のみ必要となるため
- 絶対に起きてはならない操作: hook / permissionによる強制
  - guardrailは決定論的である必要があり、指示は破られうるため
- 特定のファイル・作業でしか効かない制約: `paths` frontmatterでpath-scoped rule化
  - 無関係な作業のcontextから外すため
- モデルの弱点を補償するscaffolding（verification reminder、言い換え反復、進捗報告の強制等）: invocation site（agent定義本文・delegation brief）

## 採用基準

- 削除するとAIの挙動が変わる指示だけを記述する
- 具体的で検証可能に書く
  - o: 「2-space indentation」
  - x: 「適切にformatする」
- 以下は採用しない
  - セクション名・隣接bulletから導ける内容
  - モデルが既に知っている一般慣習
  - 特定のAI agent・モデル世代に依存した書き方（モデル名での条件分岐等）
  - Loading mechanismについてのmeta-statement（"already in context" 等）
  - 代替案との対比・経緯・ツール動作の解説

## 書き方

- 指示（何をする / いつする / どう分岐する）を本文の主成分に据える
- 制約には従う理由を1行添える
  - whyは遵守率を上げるため
- 肯定形で書く
  - 禁止を書く場合は望む行動の記述に言い換え、強制が必要ならhookにする
- 強調マーカー（MUST / CRITICAL / 必ず / 絶対 等）は安全制約・不可逆操作・workflow契約に限定する
  - 濫用は強調の濃淡を壊すため

## 配置

- 置き場所はscopeで決める
  - そのルールが適用される作業・場面を管轄するファイル・節に置く
  - 行数の超過は、冗長さを削るかpath-scoped rule / skillへの切り出しで解消する（置き場所はscopeが決め続ける）
- 常時ロードのファイルは公式目安の200行/file以内に収める
  - 長いほど遵守率が落ちるため
  - このrepoのpre-commit hookはより厳しい独自上限を強制する
- 各rule fileは他のrule fileへのpath参照なしで完結させる
  - renameで壊れ、auto-load同士では情報追加もゼロで、相対パスはsymlink経由で解決しないため
  - 例外1: skill / workflow → ruleのframework名参照は残す
    - skillが評価対象を名付けるためにload-bearing
  - 例外2: rule → skillの起動ポインタ（skill名のみ、pathなし）は残す
    - 常時ロードのruleから都度起動のskillへ誘導するため

## 変更手順

- 既存指示の適用を変える時は、影響を受ける指示文自体を書き換えて統合する
  - 隣への追記は矛盾した指示の併存を生むため
- 追加・変更時は、全rule fileから同じ決定を扱う既存文を列挙し、矛盾・重複が無いことを確認する
- 圧縮・簡素化では、元の全bullet・文との対応を突き合わせて政策落ちが無いことを検証し、検証方法をPR本文に明記する
- scope（global / project）を把握し、変更時に明示する

## References

- https://code.claude.com/docs/en/memory.md
- https://code.claude.com/docs/en/best-practices.md
- https://code.claude.com/docs/en/skills.md
- https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- https://claude.com/blog/best-practices-for-prompt-engineering
