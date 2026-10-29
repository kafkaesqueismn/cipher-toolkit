"""Single-byte XOR cipher: XOR every byte of the message with one key byte.

XOR is its own inverse -- (m ^ k) ^ k == m -- so the same function both
encrypts and decrypts.
"""

from .scoring import score_bytes


def xor_bytes(data: bytes, key: int) -> bytes:
    if not 0 <= key <= 255:
        raise ValueError("single-byte XOR key must be between 0 and 255")
    return bytes(b ^ key for b in data)


# Encrypting and decrypting are literally the same operation.
encrypt = xor_bytes
decrypt = xor_bytes


def brute_force(ciphertext: bytes) -> list[tuple[int, float, bytes]]:
    """Try all 256 keys. Return (key, score, plaintext), best first.

    Higher score = more English-like.
    """
    results = []
    for key in range(256):
        candidate = xor_bytes(ciphertext, key)
        results.append((key, score_bytes(candidate), candidate))
    results.sort(key=lambda r: r[1], reverse=True)
    return results
