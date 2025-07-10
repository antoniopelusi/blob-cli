# 🔐 Blob CLI – Secret Sharing Tool

A simple and secure command-line tool for splitting and recovering secrets using **Shamir's Secret Sharing** scheme.
Protect your secrets, share them safely, and recover them only with the right number of pieces! 🚀

---

## ✨ Features

- Split any ASCII secret into multiple shares
- Set a custom threshold for recovery
- Recover secrets from shares
- All operations performed locally (no network)
- Easy-to-use interactive CLI

---

## 📦 Installation

1. **Clone the repository:**
   ```sh
   git clone git@github.com:antoniopelusi/blob-cli.git
   cd blob-cli
   ```

2. **Run the CLI:**
   ```sh
   python3 blob-cli.py
   ```

> Is possible to use the `blob.py` module to develop another front-end.
---

## 🕹️ Usage

After launching the CLI, you'll see a menu like this:

```
[ Usage ]
split   : Generate shares from an ASCII secret
recover : Reconstruct a secret from shares
help    : Show this usage message
exit    : Quit the program

(Only ASCII secrets are supported)
```

### 🔸 Split a Secret

1. Type `split` and press Enter.
2. Enter the total number of shares (`n`).
3. Enter the threshold (`k`) – the minimum number of shares needed to recover the secret.
4. Enter your secret (input is hidden).
5. The CLI will output `n` shares in the format `x:base64`.

**Example:**
```
Mode (split/recover/help/exit): split

Total shares (n) (2-256): 5
Threshold (k) (2-5): 3
Secret (hidden): <your secret here>

Shares (x:base64):
1:AAECAwQFBgc=
2:AgMEBQYHCAk=
...
```

### 🔸 Recover a Secret

1. Type `recover` and press Enter.
2. Paste at least `k` valid shares (you can enter one per line, or paste several shares together). Leave an empty line to finish.
3. The CLI will reconstruct and display the secret.

**Example:**
```
Mode (split/recover/help/exit): recover

Enter shares (x:base64), empty line to finish:
1:AAECAwQFBgc=
2:AgMEBQYHCAk=
3:AwQFBgcICQo=

Recovered secret:
secretString_123
```

---

## 🧠 Theory: Shamir's Secret Sharing

Shamir's Secret Sharing is a cryptographic algorithm that allows you to split a secret into multiple pieces (shares), such that:
- **Any `k` out of `n` shares can reconstruct the secret.**
- **Fewer than `k` shares reveal nothing about the secret.**

### How it works (detailed explanation):

Shamir’s Secret Sharing (SSS) is a threshold cryptography scheme based on polynomial interpolation over a finite field. Here’s how the process works in detail:

#### 1. Secret Representation

- The secret (in this tool, an ASCII string) is first converted into a sequence of bytes.
- Each byte is treated as an integer in the range 0–255.
- The scheme operates over the finite field GF(257), i.e., integers modulo 257 (the smallest prime > 256, so every possible byte value is valid).

#### 2. Polynomial Generation

- For each byte of the secret, a random polynomial \( f(x) \) of degree \( k-1 \) is generated, where \( k \) is the threshold number of shares required to reconstruct the secret.
- The constant term \( a_0 \) of the polynomial is set to the secret byte value.
- The remaining coefficients \( a_1, a_2, ..., a_{k-1} \) are chosen uniformly at random from the field GF(257).
- The polynomial has the form:
  ```
  f(x) = a_0 + a_1 x + a_2 x^2 + ... + a_{k-1} x^{k-1} mod 257
  ```

#### 3. Share Generation

- For each share index \( x \) (where \( x \) ranges from 1 to \( n \), and \( n \) is the total number of shares), the value \( f(x) \) is computed.
- Each share for a given byte is the pair \( (x, f(x)) \).
- For a secret of length \( L \) bytes, each share is a list of \( L \) pairs, one for each byte.

#### 4. Distribution

- Each participant receives one share, which consists of their index \( x \) and the list of \( f(x) \) values for all bytes of the secret.
- Shares are serialized as `x:base64`, where the base64 string encodes all the \( f(x) \) values for that share.

#### 5. Secret Recovery

- To reconstruct the secret, at least \( k \) valid shares are required.
- For each byte position, the corresponding \( k \) pairs \( (x_i, y_i) \) are collected from the shares.
- Lagrange interpolation is used to reconstruct the original polynomial \( f(x) \) at \( x = 0 \), which yields the constant term \( a_0 \), i.e., the original secret byte.
- This process is repeated for every byte position to recover the full secret.

##### Lagrange Interpolation Formula

Given \( k \) points \( (x_1, y_1), ..., (x_k, y_k) \), the value at \( x = 0 \) is computed as:
```
f(0) = Σ_{j=1}^{k} y_j * Π_{m=1, m≠j}^{k} (-x_m) / (x_j - x_m) mod 257
```
- All arithmetic is performed modulo 257.
- The modular inverse is used for division in the field.

#### 6. Security Properties

- Any group of fewer than \( k \) shares has no information about the secret (information-theoretic security).
- The randomness of the coefficients ensures that all possible secrets are equally likely, given fewer than \( k \) shares.

#### 7. Implementation Notes

- The use of GF(257) allows all possible byte values (0–255) to be shared without ambiguity or overflow.
- Each share is independent; losing up to \( n-k \) shares does not affect the ability to recover the secret, as long as at least \( k \) valid shares remain.

**This tool uses a prime field of 257 to support all ASCII bytes (0-255).**

---

## ⚠️ Limitations & Security Notes

- **Only ASCII secrets are supported.** (No Unicode or binary data)
- **Keep your shares safe!** Anyone with `k` or more shares can recover the secret.
- Shares are output as `x:base64` strings; do not modify them.
- All operations are local; no data is sent over the network.
- For cryptographic applications, always use a secure environment.
