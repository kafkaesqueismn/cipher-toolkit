# Cipher Toolkit

A small Python command-line toolkit for three classical ciphers — **Caesar**,
**Vigenère** and **single-byte XOR** — together with the attacks that break
each one. It is meant for learning: the code is short and commented, and this
README explains how each cipher works and why it fails.

> ⚠️ None of these ciphers are secure. Never use them to protect real data.
> For real encryption use a vetted library (e.g. `cryptography`) and a modern
> algorithm such as AES-GCM or ChaCha20-Poly1305.

## Setup

The toolkit itself uses only the Python standard library (Python 3.10+).
`pytest` is only needed to run the tests.

```bash
python3 -m venv .venv
source .venv/bin/activate          # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
python -m pytest
```

## Usage

```
python -m cipher_toolkit <cipher> <action> [options] [text]
```

`<cipher>` is `caesar`, `vigenere` or `xor`; `<action>` is `encrypt`,
`decrypt` or `crack`. If `text` is left out, it is read from standard input.

```bash
# Caesar
python -m cipher_toolkit caesar encrypt -s 3 "Hello"            # Khoor
python -m cipher_toolkit caesar crack "Wkh vhfuhw phhwlqj lv dw gdzq"
python -m cipher_toolkit caesar crack --all "Khoor"             # show all 26

# Vigenère
python -m cipher_toolkit vigenere encrypt -k LEMON "Attack at dawn"
python -m cipher_toolkit vigenere crack -v < ciphertext.txt     # -v shows the IoC table
python -m cipher_toolkit vigenere crack --key-length 5 < ciphertext.txt

# Single-byte XOR (ciphertext is shown as hex)
python -m cipher_toolkit xor encrypt -k X "hello"               # key as char, 88, or 0x58
python -m cipher_toolkit xor decrypt -k 0x58 303d343437
python -m cipher_toolkit xor crack 303d343437
```

## Project layout

| File | Purpose |
|---|---|
| `cipher_toolkit/scoring.py` | Measures how English-like text is (chi-squared, byte scoring, index of coincidence) |
| `cipher_toolkit/caesar.py` | Caesar encrypt/decrypt and brute-force attack |
| `cipher_toolkit/vigenere.py` | Vigenère encrypt/decrypt, key-length detection, frequency-analysis attack |
| `cipher_toolkit/xor.py` | Single-byte XOR and brute-force attack |
| `cipher_toolkit/cli.py` | Command-line interface |
| `tests/` | pytest test suite |

---

## The common idea: "does this look like English?"

Each attack here tries candidate keys and keeps the one whose output looks
most like English. To decide what "looks like English" means, we use the fact
that letters in English are **not equally common**: about 12.7% of letters
are E and 9% are T, while Z is under 0.1%.

The **chi-squared statistic** measures how far a text's letter counts are from
those expected frequencies:

```
χ² = Σ (observed − expected)² / expected     (summed over A–Z)
```

Real English gives a small number. Wrongly decrypted gibberish gives a large
one. Encryption can change *which* letters appear, but it can't hide the fact
that the plaintext underneath is English, and that's the weakness every attack
here uses.

---

## Caesar cipher

### How it works
Shift every letter forward by a fixed amount, the **key**, wrapping from Z
back to A. With key 3:

```
plain:  A B C D E ... X Y Z
cipher: D E F G H ... A B C
```

Numbering A=0 … Z=25, encryption is `c = (p + k) mod 26` and decryption is
`p = (c − k) mod 26`. The `mod 26` does the wrap-around.

### Why it's weak
- **There are only 26 keys** (shift 0 doesn't even change anything). The
  attack in `caesar.brute_force` tries all 26 and ranks the results with
  chi-squared. A computer does this instantly, and a person could do it by hand.
- **Letter frequencies survive.** Every E turns into the same ciphertext
  letter, so the most common ciphertext letter is probably E. That alone
  often gives away the key.

---

## Vigenère cipher

### How it works
Vigenère is a Caesar cipher whose shift changes on every letter, following a
repeating **keyword**:

```
plain:  A T T A C K A T D A W N
key:    L E M O N L E M O N L E
cipher: L X F O P V E F R N H R
```

The shifts come from the key letters (L=11, E=4, M=12, …). One plaintext letter
now encrypts to different ciphertext letters depending on its position, so a
simple frequency count of the whole message looks almost flat. For 300 years
it was called *le chiffre indéchiffrable*, "the indecipherable cipher".

### Why it's weak
The key **repeats**. If the key has length *n*, then letters 0, *n*, 2*n*, …
were all encrypted with the same key letter, so that group of letters is just
an ordinary Caesar cipher. The attack has two stages:

**1. Find the key length using the index of coincidence (IoC).**
The IoC is the chance that two randomly chosen letters from a text are the
same. English has an uneven letter distribution, so its IoC is about
**0.066**. Uniformly random letters have an IoC of 1/26 ≈ **0.038**.

For each candidate length *n*, we split the ciphertext into *n* columns and
average their IoC:
- If *n* is right, each column is a Caesar-shifted slice of English. Shifting
  doesn't change how uneven the distribution is, so the IoC is about 0.066.
- If *n* is wrong, each column mixes several different shifts, the
  distribution flattens, and the IoC falls toward 0.038.

Here's a real run against a key of `LEMON` (`crack -v`):

```
Key length  avg IoC
         4  0.0424
         5  0.0687   ← jump: key length is 5
         6  0.0411
        ...
        10  0.0695   ← multiples of 5 score well too
```

Multiples of the true length also score highly (a key of `LEMONLEMON` is the
same as `LEMON`), so `guess_key_length` chooses the **smallest** length whose
IoC is within 90% of the best.

**2. Crack each column as a Caesar cipher.** For each column, try all 26
shifts and keep the one with the lowest chi-squared. The column shifts, read
as letters, spell out the key.

So the cipher's apparent strength is really just *n* separate Caesar ciphers,
and each of those is trivial to break. The attack needs enough text, though.
With only a few dozen letters per column the statistics get noisy. If
detection guesses wrong, give `--key-length` yourself. A Vigenère key that is
truly random and as long as the message never repeats, and that turns it into
the one-time pad, which *is* unbreakable.

---

## Single-byte XOR

### How it works
XOR (`^` in Python) compares two bits and outputs 1 if they differ and 0 if
they match:

```
0 ^ 0 = 0    0 ^ 1 = 1    1 ^ 0 = 1    1 ^ 1 = 0
```

Every byte of the message is XORed with the same one-byte key. XOR is its own
inverse, `(m ^ k) ^ k = m`, so the same operation both encrypts and decrypts.
The result is arbitrary bytes, which the CLI shows as hex.

### Why it's weak
- **There are only 256 keys** (one byte = 8 bits = 2⁸ values). The attack in
  `xor.brute_force` tries all of them.
- **Picking the right one is easy.** With a wrong key, the "plaintext" is
  usually full of unprintable control bytes. `score_bytes` rewards common
  letters and spaces and heavily penalises unprintable bytes, so the real
  message comes out clearly on top.
- **It's really a substitution cipher.** The same plaintext byte always
  becomes the same ciphertext byte, so frequency patterns survive, the same
  way they do in Caesar.

XOR itself isn't the problem. Modern stream ciphers XOR data with a key
stream. What breaks this cipher is that the key is **tiny and repeated**.
XOR with a truly random key that is as long as the message is again the
one-time pad.

---

## Lessons

1. **A small keyspace dies to brute force.** 26 or 256 keys is nothing. Modern
   ciphers use 2¹²⁸ or more possible keys.
2. **Any surviving structure is a leak.** Letter frequencies, repeated keys and
   one-to-one substitution all let statistics see through the encryption.
3. **Good ciphers make ciphertext look random.** Their output should be
   impossible to tell apart from random bytes, with nothing to measure.
