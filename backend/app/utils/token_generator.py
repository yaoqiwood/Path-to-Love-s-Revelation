# 参与者永久Token生成器
# 格式: {形容词}-{名词}-{4位随机数}
# 词库来源: 正面词汇，≤5 字母，易读好记
# 示例: grace-light-3847, glory-faith-9152

import random
import string

# 形容词词库（正面词汇，≤5字母）
_ADJECTIVES = [
    "pure",
    "true",
    "holy",
    "just",
    "good",
    "wise",
    "meek",
    "calm",
    "brave",
    "noble",
    "blest",
    "glad",
    "free",
    "kind",
    "warm",
    "bold",
    "dear",
    "fair",
    "keen",
    "mild",
    "royal",
    "vital",
    "new",
    "whole",
    "great",
    "sweet",
    "still",
    "prime",
    "grand",
    "clear",
    "rich",
    "firm",
    "deep",
    "safe",
    "sound",
    "sure",
    "loyal",
    "rare",
    "able",
    "alive",
]

# 名词词库（正面词汇，≤5字母）
_NOUNS = [
    "grace",
    "faith",
    "light",
    "peace",
    "glory",
    "hope",
    "love",
    "joy",
    "truth",
    "mercy",
    "bread",
    "lamb",
    "dove",
    "vine",
    "seed",
    "crown",
    "cross",
    "star",
    "river",
    "stone",
    "flame",
    "dawn",
    "palm",
    "cedar",
    "olive",
    "angel",
    "psalm",
    "altar",
    "lily",
    "rose",
    "rain",
    "manna",
    "path",
    "gate",
    "rock",
    "word",
    "song",
    "water",
    "fire",
    "sun",
]


def generate_participant_token() -> str:
    """
    生成参与者永久Token。
    格式: {adjective}-{noun}-{3位随机数字}
    组合数: ~40 × 40 × 1000 = 1,600,000 种

    示例: grace-light-3847, glory-faith-9152
    """
    adj = random.choice(_ADJECTIVES)
    noun = random.choice(_NOUNS)
    digits = "".join(random.choices(string.digits, k=3))
    return f"{adj}-{noun}-{digits}"
