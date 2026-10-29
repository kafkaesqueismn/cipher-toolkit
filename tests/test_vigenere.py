import pytest

from cipher_toolkit import vigenere


def test_known_answer():
    # The classic textbook example.
    assert vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"


def test_non_letters_pass_through_and_do_not_use_up_key():
    assert vigenere.encrypt("AT TA", "LE") == "LX EE"  # T+L=E, A+E=E: the space did not consume a key letter


def test_round_trip(sample):
    assert vigenere.decrypt(vigenere.encrypt(sample, "Secret"), "Secret") == sample


def test_empty_key_rejected():
    with pytest.raises(ValueError):
        vigenere.encrypt("hello", "123")


@pytest.mark.parametrize("key", ["LEMON", "CIPHER", "KEY", "CRYPTOGRAPHY"])
def test_guess_key_length(sample, key):
    assert vigenere.guess_key_length(vigenere.encrypt(sample, key)) == len(key)


@pytest.mark.parametrize("key", ["LEMON", "CIPHER", "KEY", "CRYPTOGRAPHY"])
def test_crack(sample, key):
    found_key, plaintext = vigenere.crack(vigenere.encrypt(sample, key))
    assert found_key == key
    assert plaintext == sample


def test_crack_with_given_key_length(sample):
    key, _ = vigenere.crack(vigenere.encrypt(sample, "LEMON"), key_length=5)
    assert key == "LEMON"
