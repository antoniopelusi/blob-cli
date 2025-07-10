"""blob.py: Core functions for Shamir's Secret Sharing over bytes, with serialization and validation."""

import base64
import secrets
from typing import List, Tuple

# --- Global configuration ---
PRIME: int = 257  # Smallest prime > 256; used for byte-wise secret sharing (supports all byte values 0-255)

# --- Utility functions ---

# --- Secret sharing core ---
def modinv(a: int, p: int) -> int:
    """Modular inverse of a mod p."""
    return pow(a, -1, p)

def eval_poly(coeffs: List[int], x: int, p: int) -> int:
    """Evaluate a polynomial at x modulo p."""
    return sum(c * pow(x, i, p) for i, c in enumerate(coeffs)) % p

def lagrange_interp(xs: List[int], ys: List[int], p: int) -> int:
    """Lagrange interpolation at x=0 for given points (xs, ys) modulo p."""
    if len(set(xs)) != len(xs):
        raise ValueError("Duplicate x values in shares.")
    total = 0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        li = 1
        for j, xj in enumerate(xs):
            if i != j:
                li = li * (-xj) * modinv(xi - xj, p) % p
        total = (total + yi * li) % p
    return total

def split_secret(byte: int, n: int, k: int) -> List[Tuple[int, int]]:
    """Split a single byte into n shares with threshold k."""
    coeffs = [byte] + [secrets.randbelow(PRIME) for _ in range(k - 1)]
    return [(x, eval_poly(coeffs, x, PRIME)) for x in range(1, n + 1)]

def recover_secret(shares: List[Tuple[int, int]]) -> int:
    """Recover a single byte from shares using Lagrange interpolation."""
    xs, ys = zip(*shares)
    return lagrange_interp(list(xs), list(ys), PRIME)

def encode_secret(secret: str, n: int, k: int) -> List[List[Tuple[int, int]]]:
    """Encode an ASCII secret string into n shares with threshold k."""
    if not secret.isascii():
        raise ValueError("Only ASCII secrets supported.")
    shares = [[] for _ in range(n)]
    for b in secret.encode():
        for i, s in enumerate(split_secret(b, n, k)):
            shares[i].append(s)
    return shares

def decode_secret(shares: List[List[Tuple[int, int]]]) -> str:
    """Decode the secret string from a list of shares."""
    return bytes(recover_secret(list(byte_shares)) for byte_shares in zip(*shares)).decode()

# --- Share serialization ---
def share_to_str(share: List[Tuple[int, int]]) -> str:
    """Serialize a share (list of (x, y)) to string format x:base64string, using 2 bytes per y (to support y in 0..256)."""
    x = share[0][0]
    y_bytes = b''.join(y.to_bytes(2, 'big') for _, y in share)
    y_b64 = base64.b64encode(y_bytes).decode('ascii')
    return f"{x}:{y_b64}"

def str_to_share(s: str):
    """Deserialize a string to a share (list of (x, y)) from base64, using 2 bytes per y."""
    try:
        x_str, y_b64 = s.strip().split(":")
        x = int(x_str)
        y_bytes = base64.b64decode(y_b64)
        if len(y_bytes) % 2 != 0:
            raise ValueError("Corrupted share encoding.")
        y = [int.from_bytes(y_bytes[i:i+2], 'big') for i in range(0, len(y_bytes), 2)]
        if x <= 0 or any(not (0 <= v < PRIME) for v in y):
            raise ValueError
        return [(x, v) for v in y]
    except Exception:
        return None

# --- Share validation ---
def validate_shares(shares: List[List[Tuple[int, int]]]) -> Tuple[bool, str]:
    """
    Validate a list of shares for recovery.
    Checks: at least 2 shares, all same length, no duplicate x indices.
    """
    if len(shares) < 2:
        return False, "At least 2 shares needed."
    lengths = {len(s) for s in shares}
    if len(lengths) != 1:
        return False, "Shares length mismatch."
    indices = [s[0][0] for s in shares]
    if len(set(indices)) != len(indices):
        return False, "Duplicate share indices."
    return True, ""

if __name__ == "__main__":
    raise RuntimeError("This module is a library and should not be run directly.")
