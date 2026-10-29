from cipher_toolkit.scoring import chi_squared, index_of_coincidence, letters_only, score_bytes


def test_letters_only():
    assert letters_only("Hello, World! 123") == "HELLOWORLD"


def test_english_scores_better_than_gibberish(sample):
    assert chi_squared(sample) < chi_squared("QXZJ VKWQ ZZXJ QQPV XKZJ")


def test_chi_squared_with_no_letters_is_infinite():
    assert chi_squared("123 !!!") == float("inf")


def test_index_of_coincidence(sample):
    # English sits near 0.066; a flat alphabet sits at the random level.
    assert 0.055 < index_of_coincidence(sample) < 0.075
    assert index_of_coincidence("ABCDEFGHIJKLMNOPQRSTUVWXYZ") == 0.0


def test_score_bytes_prefers_text():
    assert score_bytes(b"hello there") > score_bytes(bytes([0x01, 0x9f, 0x03, 0xff]))
