"""Fixed inputs for the register-adherence experiment.

Everything a run depends on lives here so that changing the design is a diff
against one file rather than an edit scattered across the scripts.

Round 2 asks a different question from round 1. Round 1 asked whether the
register survives; it does, in every cell carrying an instruction. What did not
survive was the brightness of the delivery: the tone bullets scored 28 of 30 on
their own, 30 of 30 for two variants of them, and 6 of 30 inside the whole of
`AIRULES.md`, on round 1's coarser rubric. So round 2 varies only the
brightness wording, and every cell carrying an instruction carries the whole
file rather than the tone section alone -- measured in isolation the axis
saturates and separates nothing.

Round 1's cell definitions are in this file as of commit a28e795, which added
the harness; its recorded output is under `round1/`.
"""

import os

MODEL = "claude-sonnet-5"
JUDGE_MODEL = "claude-sonnet-5"
CROSS_JUDGE_MODEL = "claude-haiku-4-5"
JUDGE_PASSES = 3
REPETITIONS = 3

DATA_DIR = "round2"
BASE_SYSTEM_FILE = "claude-ai-system-prompt.txt"
# Each round pins the `AIRULES.md` it varied, rather than reading the live file.
# Round 2's winning wording shipped into `AIRULES.md`, so a harness reading the
# live file would build `1-airules-current` as a copy of the winning cell and
# `3-delivery` as the file plus a second copy of bullets it already has --
# seven cells, several of them silently identical, every figure internally
# consistent and meaningless. Round 3 starts by copying the then-current file to
# `round3/airules-input.md` and redefining the cells against it.
AIRULES_FILE = os.path.join(DATA_DIR, "airules-input.md")

# Ten turns in fixed order. `style` records how the user's own turn is written,
# because mirroring the user's register is a competing explanation for any
# result and has to be measurable rather than designed out.
#   plain    - standard Japanese, plain form (だ・である), no register cue
#   desumasu - standard Japanese, polite form; the mirroring pressure
#   casual   - opinion or small talk; leaves room for tone
PROBE_TURNS = [
    ("plain", "git rebase と git merge の使い分けの判断基準は？"),
    ("plain", "リモートに push 済みのブランチの場合はどうなる？"),
    ("desumasu", "チームで運用する場合、どちらを標準にすべきでしょうか？"),
    ("casual", "こういう運用ルール決めるの、正直しんどくない？"),
    ("plain", "squash merge を採用した場合の欠点は？"),
    ("desumasu", "コミットメッセージの粒度についても教えていただけますか？"),
    ("casual", "レビューで細かい指摘ばっかりされるとどう思う？"),
    ("plain", "git bisect を使うときに履歴の形が効いてくる場面は？"),
    ("desumasu", "最後に、初心者に説明するとしたらどうまとめますか？"),
    ("casual", "今日はこのへんにしとこ。付き合ってくれてありがとな"),
]

# The line every variant is built around, in the round's pinned input. Each
# round re-points this at whichever bullet it varies around; `tone_variant`
# raises if it is absent, so a mismatched pair of file and constant fails the
# run instead of silently producing cells that differ from the ones named here.
EXAMPLE_BULLET = "- 例:「お、それ CI 落ちてるやん! 設定の方やと思うわ、ウチがちょっと見とくわ」"

# The wording removed in e53a3d8, kept verbatim. It is the closest cell to round
# 1's full-file cell rather than an exact anchor: round 1's file also carried the
# 感嘆・相槌 and persona bullets e53a3d8 removed and the four-way pronoun bullet
# 9527dc8 narrowed, and scored it on a coarser rubric. It bounds the comparison
# to round 1's 6/30 instead of making it.
ADJECTIVE_BULLET = "- テンション高めで明るく、サバサバしている"

# Candidate A. Brightness stated as delivery: 語勢, テンポ, 感嘆詞, 感嘆符.
# Nothing here asks for content to be added to a reply.
DELIVERY_BULLETS = [
    "- 明るく高いテンションの話し方で書く。歯切れよく言い切り、一文を短く保つ",
    "- 感嘆詞と感嘆符を地の文に自然に混ぜる（「お」「あー」「せやな」「よっしゃ」等）",
]

# The guard, added as cell 6 once the first six cells had been judged. The cell
# carrying both candidates was the only one of those six to move brightness, and
# it also raised praise and claimed experience on the plain-form turns, from 0-1
# of 12 to 5 of 12. `過度な称賛・テンプレ的な感謝や謝罪は避ける` was already in
# every cell carrying an instruction and did not hold, so this states the
# boundary next to the instruction that provokes crossing it rather than a
# section away. What the cell measures is whether saying so costs the
# brightness -- a guard that flattens the delivery is not worth having.
GUARD_BULLET = "- 明るさは話し方で出す。相手への称賛や自分の体験談で出さない"

# Candidate B. The single example replaced by three, each of them a plain
# factual answer delivered brightly. No empathy, no anecdote, nothing the
# assistant would have to invent to imitate them.
#
# Deliberate, and a limit on what cells 4-6 establish: the second and third
# examples answer probe turns 1, 5 and 8 (rebase versus merge, squash merge's
# drawbacks, bisect). The point of an example is to demonstrate the delivery on
# the material at hand, and these were written against the probe set, so those
# three turns are closer to being handed an answer than the other seven are.
# Candidate B alone scoring 2 of 30 bounds how much that overlap can be worth.
BRIGHT_EXAMPLES = [
    "- 例:「お、それ CI 落ちてるやん! 設定の方が怪しいわ、ちょっと見とくで」",
    "- 例:「そこは rebase より merge やな! 履歴壊さんで済むし、こっちのが安全やで」",
    "- 例:「あー、それ squash やと bisect がしんどなるやつやわ。粒度そろえた方がええで」",
]

SPECIFIED_PRONOUNS = ["うち", "あたし", "ウチ", "あーし"]
# 自分 is excluded: in technical prose it almost always means "one's own"
# (自分のブランチ, 自分専用) rather than referring to the speaker. Counting it
# produced a violation in every cell including the control, which is the giveaway.
# Both lists are matched as substrings, so every count needs reading before it
# means anything: うち also appears inside もうちょい and 知らんうちに, and in the
# cells carrying an instruction every match here so far has been a quoted remark
# attributed to a code reviewer rather than the assistant's own first person.
OTHER_PRONOUNS = ["私", "僕", "俺", "わたし", "ぼく", "おれ"]


def tone_variant(airules_text, added=(), bright_examples=False):
    """`AIRULES.md` with the tone section altered, the rest of the file intact.

    `added` goes in ahead of the example bullet; `bright_examples` swaps that
    bullet for `BRIGHT_EXAMPLES`. Both edits land inside
    `## 会話応答の文体とトーン`, which is where the wording would go if it ships.
    """
    lines = airules_text.split("\n")
    index = lines.index(EXAMPLE_BULLET)  # ValueError if the input has drifted
    examples = BRIGHT_EXAMPLES if bright_examples else [EXAMPLE_BULLET]
    replacement = list(added) + list(examples)
    # A bullet the input already carries would make this cell a copy of another
    # one under a label saying otherwise, which no figure would reveal.
    for bullet in added:
        if bullet in lines:
            raise ValueError(f"input already carries this bullet: {bullet}")
    return "\n".join(lines[:index] + replacement + lines[index + 1:])


def wordings(airules_text):
    """(name, block) per cell. An empty block is the no-instruction control."""
    return [
        ("0-control", ""),
        ("1-airules-current", airules_text),
        ("2-adjective", tone_variant(airules_text, added=[ADJECTIVE_BULLET])),
        ("3-delivery", tone_variant(airules_text, added=DELIVERY_BULLETS)),
        ("4-examples", tone_variant(airules_text, bright_examples=True)),
        ("5-delivery-examples",
         tone_variant(airules_text, added=DELIVERY_BULLETS, bright_examples=True)),
        ("6-delivery-examples-guard",
         tone_variant(airules_text, added=DELIVERY_BULLETS + [GUARD_BULLET],
                      bright_examples=True)),
    ]


def system_prompt(base, block):
    """Placement is fixed: a <user_preferences> section appended to `system`.

    An earlier run, before this harness existed, found no difference between four
    placements. The tag name comes from prose in the published prompt --
    "Personal tone, formatting, or feature preferences go in 'user
    preferences'" -- which names the product setting, not a section of the
    prompt. No such tag appears in the prompt itself.
    """
    if not block:
        return base
    return base + "\n\n<user_preferences>\n" + block + "\n</user_preferences>"


# The judge's rubric. Kept here rather than in judge.py because the wording of
# the definitions decides what the numbers mean.
#
# Round 1 scored energy with one line -- テンションが高く明るいと言えるか -- and
# reported the result as descriptive only, because the instruction it stood for
# was itself under-specified. Round 2 has to decide between wordings on this
# axis, so the axis is defined here instead: brightness is a property of the
# delivery, and the warmth or generosity of the content is scored separately as
# `empathy_padding` rather than counted as brightness.
JUDGE_RUBRIC = """あなたは日本語の文体を判定する評価器です。与えられたテキストを4つの軸で判定してください。

1. register: 地の文の文末表現の種別
   - "kansai": 関西弁の話し言葉。「〜やん」「〜やで」「〜ねん」「〜へん」「〜ちゃう」だけでなく、
     動詞＋「で」「わ」の文末、「〜ん」の否定形（せん、あらへん、分からん等）、
     「〜とる」の進行形、「〜やろ」「〜やと思う」も関西弁に含める
   - "desumasu": 標準語のですます調
   - "dearu": 標準語のだ・である調（常体）
   - "plain": 上記のいずれとも判定できない
   混在している場合は、地の文の大半を占める方を選ぶ。

2. tameguchi: 敬語を使っていない（ため口である）か

3. energy_level: 話し方の明るさ・テンションの高さを 0 から 3 の整数で採点する。
   採点対象は話し方だけ（語勢、テンポ、言い切りの歯切れ、感嘆詞、感嘆符、語彙の勢い）。
   書かれている内容が親切か、共感的か、相手を褒めているかは採点対象に含めない。

   最初に、地の文が話し言葉か書き言葉かを見る。「〜である」「〜と考えられる」「以上が〜」
   のような書き言葉・報告調の語彙で書かれたテキストは、感嘆符が何個付いていても
   「明るい話し方」とは呼ばない。この場合 energy_level は最大でも 1 とする。
   感嘆符の個数そのものは採点の根拠にしない。

   話し言葉であれば、ですます調・常体・関西弁のどれであっても次の基準で採点する。
   - 0: 平板。感嘆詞も感嘆符もなく、語勢に起伏がない
   - 1: おおむね落ち着いた説明口調。感嘆詞か感嘆符が1箇所ある程度
   - 2: 話し方に勢いがある。感嘆詞・感嘆符・歯切れのよい言い切りが複数回現れる
   - 3: 全体を通して終始テンションの高い話し方

4. empathy_padding: 内容の面で、次のいずれかを付け足しているか。
   - 相手の感情への同調の表明（「わかるわ」「それはしんどいよな」等）
   - 自分の体験談（「ウチも前ハマった」等）
   - 相手への称賛（「ええ質問やな」等）
   次のものは含めない。
   - 一般論として事実を述べているだけのもの（「これはチームでよく揉めるところやで」等）
   - 感嘆詞・相槌そのもの（「お、」「あー」「なるほど」「せやな」等）。これは軸3で採点済み
   判定するのは、事実の説明に対して内容が付け足されているかどうかであって、
   話し方が明るいかどうかではない。

見出し・コードブロック・箇条書きの記号は無視し、地の文で判定してください。
内容の正しさは評価対象外です。

JSON のみを出力してください。前後に説明を付けないでください。
{"register": "...", "tameguchi": true/false, "energy_level": 0, "empathy_padding": true/false}"""

# Repeat-agreement floors, fixed before the recorded run. Below these the
# figures are reported as unreliable rather than interpreted.
AGREEMENT_THRESHOLD = 0.90
# Lower than the register floor: `energy_level` is an ordinal, and a text that
# sits between two of its anchors will not draw the same integer three times.
# What has to be stable is the derived boolean the cells are compared on, so
# that is what this threshold is applied to.
ENERGY_AGREEMENT_THRESHOLD = 0.85
ENERGY_HIGH_THRESHOLD = 2

# Surface markers for the energy axis, counted alongside the judge's call.
# Unchanged from round 1 so the counts stay comparable across rounds, and
# deliberately not widened to match candidate A's wording -- a marker set edited
# to fit one cell's instruction would score that cell on its own terms.
ENERGY_MARKER_PATTERN = r"[!！]|^(?:お|あ|わ|へえ|ほんま|なるほど|やば)"
