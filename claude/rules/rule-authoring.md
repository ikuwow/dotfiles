# AI 向けルール・規約ドキュメントの編集

## 採用基準（何を書くか）

- bulletを追加・温存するのは、削除するとAIの挙動が変わる場合のみ
- セクション名・隣接bulletから導ける内容は書かない
- 冗長な記述は省くのを基本とする
- 指示 (何をする / いつする / どう分岐する) を rule body の主成分に据え、tool/libraryの動作説明・選択の理由・対比や履歴は書かない
    - 本当に必要な時は1行括弧内に圧縮するか、References 節に URL のみ残す
- 次の禁止は、削除でAIの挙動が変わるとしても適用する
    - モデルの弱点を補償するscaffolding（verification reminder、anti-rationalizationの言い換え反復、進捗報告の強制等）をglobal ruleに書かない
        - 弱いモデルに必要な場合はinvocation site（agent定義本文・delegation brief）に置く
    - 特定のAI agent・モデル世代に依存した書き方（モデル名での条件分岐等）をしない
    - Loading mechanismについてのmeta-statement（"already in context"、"auto-loaded as global rule" 等）はどこにも入れない
        - mechanism変更でdriftし、ruleとしてはnoise

## 配置（どこに書くか）

- ルールの配置場所はscopeで決める（そのルールが適用される作業・場面を管轄するファイル・節に置く）
- 行数budgetを理由に別の場所へ置かない
    - budgetを超えそうな時は冗長さを削るか、意味のある単位で別ファイルへ切り出す
- Rule file間のcross-file path参照は基本入れない（auto-load同士なら情報追加ゼロ、renameで壊れる、相対パスがsymlink経由だと解決しない）
    - 例外1: skill / workflow → ruleのframework名参照（"X defined in `file.md`" 等）は残す。skillが評価対象を名付けるためにload-bearing
    - 例外2: rule → skillの起動ポインタ（"invoke the Y skill" 等、skill名参照でpathは指定しない）は残す。常時ロードのruleから都度起動のskillへ誘導するためload-bearing

## 書き方（どう書くか）

- 強調マーカー（MUST / CRITICAL / 必ず / 絶対 等）は安全制約・不可逆操作・workflow契約等のload-bearingなゲートに限定し、それ以外の指示は平叙形で書く（濫用は強調の濃淡を壊す）

## 変更手順

- 既存指示の適用を変える要件（例外・前処理等）は、隣に段落を追記せず影響を受ける指示文自体を書き換えて統合する（矛盾した指示の併存を防ぐ）
- 既存のrule文書を圧縮・簡素化する際は、元の全bullet・文との対応を突き合わせて政策落ちが無いことを検証し、検証方法を成果物（PR本文等）に明記する（記憶からの自由な書き直しで済ませない）
- scope（global / project）を把握し、変更時に明示する
