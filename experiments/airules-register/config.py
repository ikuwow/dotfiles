"""Fixed inputs for the register-adherence experiment.

Everything a run depends on lives here so that changing the design is a diff
against one file rather than an edit scattered across the scripts.
"""

MODEL = "claude-sonnet-5"
JUDGE_MODEL = "claude-sonnet-5"
CROSS_JUDGE_MODEL = "claude-haiku-4-5"
JUDGE_PASSES = 3
REPETITIONS = 3

BASE_SYSTEM_FILE = "claude-ai-system-prompt.txt"
AIRULES_FILE = "../../AIRULES.md"

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

REGISTER_BULLETS = [
    "- 応答は日本語で書き、必要に応じて英語を混ぜてよい",
    "- 関西弁のカジュアルな話し言葉で書く（文末は「〜やん」「〜やで」「〜ちゃう?」等）",
    "- 一人称は「うち」「あたし」「ウチ」「あーし」から選ぶ",
    "- 「ですます」を使わず、常にため口で書く",
    "- 感嘆・相槌を自然に混ぜ、時には愚痴や感情のこもったリアクションも交える",
    "- テンション高めで明るく、サバサバしている",
    "- 例:「お、それ CI 落ちてるやん! 設定の方やと思うわ、うちがちょっと見とくわ」",
    "- 兵庫県出身の27歳の賢いギャルの女性の人格として振る舞う",
]

DESUMASU_BAN = "- 「ですます」を使わず、常にため口で書く"
ONE_EXAMPLE = "- 例:「お、それ CI 落ちてるやん! 設定の方やと思うわ、うちがちょっと見とくわ」"
THREE_EXAMPLES = [
    "- 例:「お、それ CI 落ちてるやん! 設定の方やと思うわ、うちがちょっと見とくわ」",
    "- 例:「あーそれ、うちも前ハマったやつやわ。設定ファイルの方見た方が早いんちゃう?」",
    "- 例:「なるほどな、それやったら rebase より merge の方が安全やと思うで」",
]

SPECIFIED_PRONOUNS = ["うち", "あたし", "ウチ", "あーし"]
# 自分 is excluded: in technical prose it almost always means "one's own"
# (自分のブランチ, 自分専用) rather than referring to the speaker. Counting it
# produced a violation in every cell including the control, which is the giveaway.
# Both lists are matched as substrings, so every count needs reading before it
# means anything: うち also appears inside もうちょい and 知らんうちに, and the
# earlier run's two matches here were both quoted remarks attributed to a code
# reviewer rather than the assistant's own first person.
OTHER_PRONOUNS = ["私", "僕", "俺", "わたし", "ぼく", "おれ"]


def register_section(bullets):
    return "\n".join(["## 会話応答の文体とトーン", ""] + bullets)


def wordings(airules_text):
    """(name, block) per cell. An empty block is the no-instruction control."""
    only = list(REGISTER_BULLETS)
    no_ban = [b for b in only if b != DESUMASU_BAN]
    more_examples = []
    for b in only:
        if b == ONE_EXAMPLE:
            more_examples.extend(THREE_EXAMPLES)
        else:
            more_examples.append(b)

    return [
        ("0-control", ""),
        ("1-airules-full", airules_text),
        ("2-register-only", register_section(only)),
        ("3-three-examples", register_section(more_examples)),
        ("4-no-desumasu-ban", register_section(no_ban)),
    ]


def system_prompt(base, block):
    """Placement is fixed: a <user_preferences> section appended to `system`.

    An earlier round of the investigation found no difference between four
    placements. The tag name comes from prose in the published prompt --
    "Personal tone, formatting, or feature preferences go in 'user
    preferences'" -- which names the product setting, not a section of the
    prompt. No such tag appears in the prompt itself.
    """
    if not block:
        return base
    return base + "\n\n<user_preferences>\n" + block + "\n</user_preferences>"


# The judge's rubric. Kept here rather than in judge.py because the wording of
# the register definition decides what the numbers mean.
JUDGE_RUBRIC = """あなたは日本語の文体を判定する評価器です。与えられたテキストを3つの軸で判定してください。

1. register: 地の文の文末表現の種別
   - "kansai": 関西弁の話し言葉。「〜やん」「〜やで」「〜ねん」「〜へん」「〜ちゃう」だけでなく、
     動詞＋「で」「わ」の文末、「〜ん」の否定形（せん、あらへん、分からん等）、
     「〜とる」の進行形、「〜やろ」「〜やと思う」も関西弁に含める
   - "desumasu": 標準語のですます調
   - "dearu": 標準語のだ・である調（常体）
   - "plain": 上記のいずれとも判定できない
   混在している場合は、地の文の大半を占める方を選ぶ。
2. tameguchi: 敬語を使っていない（ため口である）か
3. high_energy: テンションが高く明るいと言えるか。落ち着いた説明口調なら false

見出し・コードブロック・箇条書きの記号は無視し、地の文で判定してください。
内容の正しさは評価対象外です。

JSON のみを出力してください。前後に説明を付けないでください。
{"register": "...", "tameguchi": true/false, "high_energy": true/false}"""

# Repeat-agreement floor for the register axis, fixed before the recorded run.
# Below this the figures are reported as unreliable rather than interpreted.
AGREEMENT_THRESHOLD = 0.90

# Surface markers for the energy axis, counted alongside the judge's call. The
# instruction this stands for is under-specified, so both are descriptive.
ENERGY_MARKER_PATTERN = r"[!！]|^(?:お|あ|わ|へえ|ほんま|なるほど|やば)"
