"""Command-line interface.

Usage:  python -m cipher_toolkit <cipher> <action> [options] [text]

If text is omitted, it is read from standard input.
"""

import argparse
import sys

from . import caesar, vigenere, xor


def _read_text(args) -> str:
    if args.text is not None:
        return args.text
    return sys.stdin.read().rstrip("\n")


def _parse_hex(text: str) -> bytes:
    try:
        return bytes.fromhex(text.strip())
    except ValueError:
        sys.exit("error: XOR ciphertext must be hex, e.g. 1b37373331")


def _printable(data: bytes) -> str:
    # Show undecodable bytes as \xNN instead of crashing or garbling the terminal.
    return data.decode("ascii", errors="backslashreplace")


def run_caesar(args) -> None:
    text = _read_text(args)
    if args.action == "encrypt":
        print(caesar.encrypt(text, args.shift))
    elif args.action == "decrypt":
        print(caesar.decrypt(text, args.shift))
    else:  # crack
        results = caesar.brute_force(text)
        shown = results if args.all else results[: args.top]
        for shift, score, plain in shown:
            print(f"shift={shift:2d}  score={score:9.2f}  {plain}")


def run_vigenere(args) -> None:
    text = _read_text(args)
    if args.action == "encrypt":
        print(vigenere.encrypt(text, args.key))
    elif args.action == "decrypt":
        print(vigenere.decrypt(text, args.key))
    else:  # crack
        if args.verbose:
            print("Key length  avg IoC   (English ≈ 0.066, random ≈ 0.038)")
            for length, ioc in vigenere.key_length_scores(text, args.max_length):
                print(f"{length:10d}  {ioc:.4f}")
            print()
        key, plain = vigenere.crack(text, args.key_length, args.max_length)
        print(f"key: {key}")
        print(plain)


def run_xor(args) -> None:
    text = _read_text(args)
    if args.action == "encrypt":
        print(xor.encrypt(text.encode(), args.key).hex())
    elif args.action == "decrypt":
        print(_printable(xor.decrypt(_parse_hex(text), args.key)))
    else:  # crack
        results = xor.brute_force(_parse_hex(text))
        for key, score, plain in results[: args.top]:
            # Escape newlines/control bytes so each candidate stays on one line.
            shown = "".join(chr(b) if 32 <= b < 127 else f"\\x{b:02x}" for b in plain)
            print(f"key={key:3d} (0x{key:02x})  score={score:6.3f}  {shown}")


def _key_byte(value: str) -> int:
    """Accept XOR keys as decimal (88), hex (0x58) or a single character ('X')."""
    if len(value) == 1 and not value.isdigit():
        return ord(value)
    n = int(value, 0)  # base 0 lets Python understand 0x.. and 0b.. prefixes
    if not 0 <= n <= 255:
        raise argparse.ArgumentTypeError("key must be 0-255")
    return n


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cipher_toolkit",
        description="Encrypt, decrypt and break classical ciphers.",
    )
    ciphers = parser.add_subparsers(dest="cipher", required=True)

    def add_actions(cipher_parser, encrypt_opts, crack_opts):
        actions = cipher_parser.add_subparsers(dest="action", required=True)
        for name in ("encrypt", "decrypt", "crack"):
            p = actions.add_parser(name)
            (crack_opts if name == "crack" else encrypt_opts)(p)
            p.add_argument("text", nargs="?", help="input text (default: read stdin)")

    # Caesar
    c = ciphers.add_parser("caesar", help="Caesar shift cipher")
    c.set_defaults(func=run_caesar)

    def caesar_key(p):
        p.add_argument("-s", "--shift", type=int, required=True, help="shift amount (0-25)")

    def caesar_crack(p):
        p.add_argument("--top", type=int, default=5, help="how many candidates to show")
        p.add_argument("--all", action="store_true", help="show all 26 shifts")

    add_actions(c, caesar_key, caesar_crack)

    # Vigenère
    v = ciphers.add_parser("vigenere", help="Vigenère polyalphabetic cipher")
    v.set_defaults(func=run_vigenere)

    def vigenere_key(p):
        p.add_argument("-k", "--key", required=True, help="keyword, e.g. LEMON")

    def vigenere_crack(p):
        p.add_argument("--key-length", type=int, help="skip detection and use this key length")
        p.add_argument("--max-length", type=int, default=20, help="longest key length to try")
        p.add_argument("-v", "--verbose", action="store_true", help="show the IoC table")

    add_actions(v, vigenere_key, vigenere_crack)

    # XOR
    x = ciphers.add_parser("xor", help="single-byte XOR (ciphertext is hex)")
    x.set_defaults(func=run_xor)

    def xor_key(p):
        p.add_argument("-k", "--key", type=_key_byte, required=True,
                       help="key byte: decimal (88), hex (0x58) or a character (X)")

    def xor_crack(p):
        p.add_argument("--top", type=int, default=3, help="how many candidates to show")

    add_actions(x, xor_key, xor_crack)

    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValueError as e:
        sys.exit(f"error: {e}")
