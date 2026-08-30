# AI 向けrule文書の編集

このルールはAI agentが指示として読み込むrule文書（CLAUDE.md、AGENTS.md、rule file等）に適用される。
ファイル名・置き場所は問わず、消費者がAI agentであることで判定する。

## 振り分け（どの仕組みに載せるか）

書きたい内容はまず以下の専用の仕組みへの振り分けを検討し、どの仕組みにも載らないものだけをruleに書く。
以降の節は、ruleに書く内容とその書き方を定める。

- 手順・チェックリスト・ワークフロー: skill
  - ruleは常時ロードされ、手順は使う時のみ必要となるため
  - skillの作成・改善にはskill-creator skillを使う
- 絶対に起きてはならない操作: hook / permissionによる強制
  - guardrailは決定論的である必要があり、指示は破られうるため
  - hookの作成にはhookify skillを使う
- モデルの弱点を補償するscaffolding（verification reminder、anti-rationalizationの言い換え反復、進捗報告の強制等）: invocation site（agent定義の本文、subagent呼び出し時のprompt等、そのモデルに仕事を渡す場所）
  - 必要なモデル・場面にだけ届け、常時ロードのcontextから外すため
- 上記のいずれにも該当しない事実と制約: rule

## 採用基準

- 常時成立する事実と制約だけを記述する
- 削除するとAIの挙動が変わる指示だけを記述する
- 以下は採用しない
  - セクション名・隣接bulletから導ける内容
  - モデルが既に知っている一般慣習
  - 特定のAI agent・モデル世代に依存した書き方（モデル名での条件分岐等）
  - 文書自身のロード状態に言及するmeta-statement（"already in context" 等）
  - 代替案との対比・経緯・ツール動作の解説
    - 制約に添えるwhyの1行は対象外
    - 本当に必要な時は1行括弧内に圧縮するか、References節にURLのみ残す

## 書き方

- 指示（何をする / いつする / どう分岐する）を本文の主成分に据える
- 具体的で検証可能に書く
  - o: 「2-space indentation」
  - x: 「適切にformatする」
- 制約には従う理由を1行添える
  - whyは遵守率を上げるため
- 肯定形で書く
  - 禁止を書く場合は望む行動の記述に言い換え、強制が必要ならhookにする
  - 採用可否・除外の判定リストは列挙形で書いてよい
- 強調マーカー（MUST / CRITICAL / 必ず / 絶対 等）はload-bearingなゲート（安全制約・不可逆操作・workflow契約等）に限定し、それ以外の指示は平叙形で書く
  - 濫用は強調の濃淡を壊すため

## 配置

- 置き場所はscopeで決める
  - 全プロジェクト・全作業に効く方針: user-levelのglobal rule
  - 特定プロジェクト固有の規約: そのprojectのCLAUDE.md / project rule
  - 特定の作業・手順に付随する制約: skill / agent定義
- 特定のファイル・作業でしか効かない制約は、`paths` frontmatterでpath-scoped rule化する
  - 無関係な作業のcontextから外すため
- 常時ロードのファイルは公式目安の200行/file以内に収める
  - 長いほど遵守率が落ちるため
- 行数の超過は、冗長さの削減か意味のある単位での分割で解消する
  - skill / path-scoped ruleへの切り出しは、振り分けの基準に該当する場合のみ行う
- 各rule fileは他のrule fileへのpath参照なしで完結させる
  - renameで壊れ、auto-load同士では情報追加もゼロで、相対パスはsymlink経由で解決しないため
  - 例外1: skill / workflow → ruleのframework名参照（"X defined in `file.md`" 等）は残す
    - skillが評価対象を名付けるためにload-bearing
  - 例外2: rule → skillの起動ポインタ（skill名のみ、pathなし）は残す
    - 常時ロードのruleから都度起動のskillへ誘導するため

## 変更手順

- 既存指示の適用を変える時は、影響を受ける指示文自体を書き換えて統合する
  - 隣への追記は矛盾した指示の併存を生むため
- 追加・変更時は、全rule fileから同じ決定を扱う既存文を列挙し、矛盾・重複が無いことを確認する
- 編集後、編集対象のファイルが本ルールに準拠していることを確認する
- 圧縮・簡素化では、元の全bullet・文との対応を突き合わせて指示の欠落が無いことを検証し、検証方法を成果物（PR本文等）に明記する
- scope（global / project）を把握し、変更時に明示する

## References

- https://code.claude.com/docs/en/memory.md
- https://code.claude.com/docs/en/best-practices.md
- https://code.claude.com/docs/en/skills.md
- https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- https://claude.com/blog/best-practices-for-prompt-engineering
