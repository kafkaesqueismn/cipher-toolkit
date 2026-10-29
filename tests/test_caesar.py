import pytest

from cipher_toolkit import caesar


def test_known_answer():
    assert caesar.encrypt("HELLO", 3) == "KHOOR"


def test_wraps_around_and_keeps_case_and_punctuation():
    assert caesar.encrypt("xyz, XYZ!", 3) == "abc, ABC!"


@pytest.mark.parametrize("shift", [0, 1, 13, 25, 26, -4])
def test_round_trip(sample, shift):
    assert caesar.decrypt(caesar.encrypt(sample, shift), shift) == sample


@pytest.mark.parametrize("shift", range(26))
def test_brute_force_finds_every_shift(sample, shift):
    best_shift, _, plaintext = caesar.brute_force(caesar.encrypt(sample, shift))[0]
    assert best_shift == shift
    assert plaintext == sample


def test_brute_force_returns_all_26():
    assert len(caesar.brute_force("abc")) == 26
