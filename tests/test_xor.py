import pytest

from cipher_toolkit import xor


def test_xor_is_its_own_inverse(sample):
    data = sample.encode()
    assert xor.decrypt(xor.encrypt(data, 0x5A), 0x5A) == data


def test_known_answer():
    # 'A' is 0x41; 0x41 ^ 0x01 == 0x40 ('@').
    assert xor.encrypt(b"A", 0x01) == b"@"


def test_key_out_of_range():
    with pytest.raises(ValueError):
        xor.encrypt(b"hi", 256)


@pytest.mark.parametrize("key", [1, 42, 88, 127, 200, 255])
def test_brute_force_finds_key(sample, key):
    best_key, _, plaintext = xor.brute_force(xor.encrypt(sample.encode(), key))[0]
    assert best_key == key
    assert plaintext == sample.encode()


def test_brute_force_short_message():
    best_key, _, plaintext = xor.brute_force(xor.encrypt(b"Meet me at the bridge at noon", 77))[0]
    assert best_key == 77
