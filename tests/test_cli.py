from cipher_toolkit.cli import main


def run(capsys, *argv):
    main(list(argv))
    return capsys.readouterr().out.strip()


def test_caesar_cli(capsys):
    assert run(capsys, "caesar", "encrypt", "-s", "3", "HELLO") == "KHOOR"
    assert run(capsys, "caesar", "decrypt", "-s", "3", "KHOOR") == "HELLO"


def test_vigenere_cli(capsys, sample):
    ct = run(capsys, "vigenere", "encrypt", "-k", "LEMON", sample)
    out = run(capsys, "vigenere", "crack", ct)
    assert out.splitlines()[0] == "key: LEMON"


def test_xor_cli(capsys):
    ct = run(capsys, "xor", "encrypt", "-k", "0x58", "hello world")
    assert run(capsys, "xor", "decrypt", "-k", "88", ct) == "hello world"
    assert "key= 88" in run(capsys, "xor", "crack", ct)


def test_cli_reads_stdin(capsys, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("KHOOR\n"))
    assert run(capsys, "caesar", "decrypt", "-s", "3") == "HELLO"
