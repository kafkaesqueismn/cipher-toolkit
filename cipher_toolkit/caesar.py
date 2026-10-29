"""Caesar cipher: shift every letter by the same fixed amount."""

from .scoring import chi_squared


def shift_char(ch: str, shift: int) -> str:
    """Shift a single letter by `shift` places, wrapping Z around to A.

    Non-letters (spaces, digits, punctuation) are returned unchanged.
    Upper/lower case is preserved.
    """
    if "a" <= ch <= "z":
        base = ord("a")
    elif "A" <= ch <= "Z":
        base = ord("A")
    else:
        return ch
    # Convert to 0-25, shift, wrap with % 26, convert back to a character.
    return chr((ord(ch) - base + shift) % 26 + base)


def encrypt(plaintext: str, shift: int) -> str:
    return "".join(shift_char(c, shift) for c in plaintext)


def decrypt(ciphertext: str, shift: int) -> str:
    # Decrypting is just encrypting with the opposite shift.
    return encrypt(ciphertext, -shift)


def brute_force(ciphertext: str) -> list[tuple[int, float, str]]:
    """Try all 26 shifts. Return (shift, score, plaintext), best first.

    The score is chi-squared against English letter frequencies, so the
    lowest score is the most English-looking candidate.
    """
    results = []
    for shift in range(26):
        candidate = decrypt(ciphertext, shift)
        results.append((shift, chi_squared(candidate), candidate))
    results.sort(key=lambda r: r[1])
    return results
