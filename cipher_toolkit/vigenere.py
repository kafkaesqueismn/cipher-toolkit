"""Vigenère cipher: a Caesar cipher whose shift changes with each letter,
following a repeating keyword.

Only letters are encrypted, and only letters advance the key, so spaces and
punctuation pass through untouched.
"""

from .caesar import shift_char
from .scoring import chi_squared, index_of_coincidence, letters_only


def _key_shifts(key: str) -> list[int]:
    """Turn a keyword like 'LEMON' into shifts [11, 4, 12, 14, 13]."""
    key = letters_only(key)
    if not key:
        raise ValueError("Vigenère key must contain at least one letter")
    return [ord(c) - ord("A") for c in key]


def _apply(text: str, key: str, direction: int) -> str:
    shifts = _key_shifts(key)
    out = []
    i = 0  # position in the key; only advances on letters
    for ch in text:
        if ch.isascii() and ch.isalpha():
            out.append(shift_char(ch, direction * shifts[i % len(shifts)]))
            i += 1
        else:
            out.append(ch)
    return "".join(out)


def encrypt(plaintext: str, key: str) -> str:
    return _apply(plaintext, key, +1)


def decrypt(ciphertext: str, key: str) -> str:
    return _apply(ciphertext, key, -1)


def split_columns(letters: str, key_length: int) -> list[str]:
    """Split letters into `key_length` columns.

    Column i holds letters i, i+key_length, i+2*key_length, ... -- exactly
    the letters that were encrypted with key letter i.
    """
    return [letters[i::key_length] for i in range(key_length)]


def key_length_scores(ciphertext: str, max_length: int = 20) -> list[tuple[int, float]]:
    """Average index of coincidence of the columns for each key length.

    Returns [(length, avg_ioc), ...] in order of length. The true key length
    (and its multiples) will have an average IoC near English's ~0.066;
    wrong lengths sit closer to random's ~0.038.
    """
    letters = letters_only(ciphertext)
    # Need at least two letters per column for IoC to mean anything.
    max_length = max(1, min(max_length, len(letters) // 2))
    scores = []
    for length in range(1, max_length + 1):
        columns = split_columns(letters, length)
        avg = sum(index_of_coincidence(col) for col in columns) / length
        scores.append((length, avg))
    return scores


def guess_key_length(ciphertext: str, max_length: int = 20) -> int:
    """Pick the most likely key length.

    Multiples of the real length score just as well as the real length (a
    key of 'ABCABC' is the same as 'ABC'), so rather than taking the single
    highest score we take the *smallest* length that comes close to it.
    """
    scores = key_length_scores(ciphertext, max_length)
    best = max(ioc for _, ioc in scores)
    for length, ioc in scores:
        if ioc >= 0.9 * best:
            return length
    return scores[0][0]  # unreachable in practice; keeps type checkers happy


def crack_column(column: str) -> int:
    """Find the Caesar shift for one column via frequency analysis."""
    best_shift, best_score = 0, float("inf")
    for shift in range(26):
        candidate = "".join(shift_char(c, -shift) for c in column)
        score = chi_squared(candidate)
        if score < best_score:
            best_shift, best_score = shift, score
    return best_shift


def crack(ciphertext: str, key_length: int | None = None, max_length: int = 20) -> tuple[str, str]:
    """Recover (key, plaintext) from Vigenère ciphertext.

    If `key_length` is not given it is detected automatically. Works best
    with a few hundred letters or more -- with short texts the statistics
    are too noisy.
    """
    letters = letters_only(ciphertext)
    if not letters:
        raise ValueError("ciphertext contains no letters")
    if key_length is None:
        key_length = guess_key_length(ciphertext, max_length)

    columns = split_columns(letters, key_length)
    key = "".join(chr(crack_column(col) + ord("A")) for col in columns)
    return key, decrypt(ciphertext, key)
