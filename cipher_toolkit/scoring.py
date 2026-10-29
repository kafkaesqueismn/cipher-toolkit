"""Tools for measuring how "English-like" a piece of text is.

Every attack in this toolkit follows the same idea: try candidate keys,
decrypt with each one, and keep the result that looks most like English.
This module provides the "looks like English" part.
"""

import string

# Relative frequency of each letter in typical English text (sums to ~1.0).
# 'E' is the most common letter (~12.7%), 'Z' the rarest (~0.07%).
ENGLISH_FREQ = {
    "A": 0.08167, "B": 0.01492, "C": 0.02782, "D": 0.04253, "E": 0.12702,
    "F": 0.02228, "G": 0.02015, "H": 0.06094, "I": 0.06966, "J": 0.00153,
    "K": 0.00772, "L": 0.04025, "M": 0.02406, "N": 0.06749, "O": 0.07507,
    "P": 0.01929, "Q": 0.00095, "R": 0.05987, "S": 0.06327, "T": 0.09056,
    "U": 0.02758, "V": 0.00978, "W": 0.02360, "X": 0.00150, "Y": 0.01974,
    "Z": 0.00074,
}


def letters_only(text: str) -> str:
    """Return just the A-Z letters of `text`, uppercased."""
    return "".join(c for c in text.upper() if c in string.ascii_uppercase)


def chi_squared(text: str) -> float:
    """Chi-squared distance between `text`'s letter counts and English.

    For each letter we compare how many times it *actually* appears
    (observed) with how many times we'd *expect* it in English text of the
    same length (expected):

        sum over letters of (observed - expected)^2 / expected

    Lower is better: 0 would be a perfect match. Real English usually scores
    under ~100; gibberish scores in the hundreds or thousands.
    """
    letters = letters_only(text)
    n = len(letters)
    if n == 0:
        return float("inf")  # no letters at all: definitely not English

    counts = {c: 0 for c in string.ascii_uppercase}
    for c in letters:
        counts[c] += 1

    total = 0.0
    for letter, freq in ENGLISH_FREQ.items():
        expected = freq * n
        observed = counts[letter]
        total += (observed - expected) ** 2 / expected
    return total


def score_bytes(data: bytes) -> float:
    """Score raw bytes as English text. Higher is better.

    Used by the XOR cracker, where a wrong key often produces unprintable
    garbage bytes rather than just "wrong letters". We add up the English
    frequency of each letter, give spaces a bonus (English is ~15-20%
    spaces), and heavily penalise bytes that never appear in normal text.
    """
    score = 0.0
    for b in data:
        ch = chr(b)
        if ch.upper() in ENGLISH_FREQ:
            score += ENGLISH_FREQ[ch.upper()]
        elif ch == " ":
            score += 0.13
        elif ch in string.digits or ch in string.punctuation or ch in "\n\r\t":
            score += 0.0  # plausible, but not evidence for English
        else:
            score -= 1.0  # control characters / non-ASCII: very unlikely
    return score / max(len(data), 1)


def index_of_coincidence(text: str) -> float:
    """Probability that two randomly chosen letters of `text` are the same.

    English text has an IoC of about 0.066 because some letters (E, T, A)
    are very common. Uniformly random letters have an IoC of 1/26 ≈ 0.038.
    The Vigenère cracker uses this to detect the key length.
    """
    letters = letters_only(text)
    n = len(letters)
    if n < 2:
        return 0.0
    counts = {}
    for c in letters:
        counts[c] = counts.get(c, 0) + 1
    # Number of ways to pick two identical letters / ways to pick any two.
    same_pairs = sum(k * (k - 1) for k in counts.values())
    return same_pairs / (n * (n - 1))
