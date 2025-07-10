"""blob-cli.py: Command-line interface for splitting and recovering ASCII secrets using Shamir's Secret Sharing."""

import sys
import getpass
from typing import List, Tuple
from blob import (
    encode_secret, decode_secret, share_to_str, str_to_share, validate_shares
)

LENGTH: int = 80  # Separator length for CLI output

class BlobCLI:
    """Command-line interface"""
    SEP = "=" * LENGTH
    SEP_MINUS = "-" * LENGTH

    _last_secret = None  # For secure secret variable handling

    def _wipe_secret(self):
        """Overwrite and delete the secret variable from memory."""
        if hasattr(self, "_last_secret") and self._last_secret:
            try:
                self._last_secret = "x" * len(self._last_secret)
            except Exception:
                pass
            try:
                del self._last_secret
            except Exception:
                pass

    def secure_exit(self):
        """Overwrite and delete the secret variable before exiting."""
        self._wipe_secret()
        print("\nExiting...")
        print(self.SEP)
        sys.exit(0)

    def print_usage(self) -> None:
        """Print usage instructions for the CLI."""
        print(f"{self.SEP}")
        print("[ Usage ]")
        print(self.SEP)
        print(
            "\nsplit   : Generate shares from an ASCII secret\n"
            "recover : Reconstruct a secret from shares\n"
            "help    : Show this usage message\n"
            "exit    : Quit the program\n"
            "\n(Only ASCII secrets are supported)\n"
        )
        print(self.SEP)

    def input_int_in_range(self, prompt: str, min_value: int, max_value: int) -> int:
        """
        Prompt the user for an integer within a specified range.
        """
        while True:
            v = input(f"{prompt} ({min_value}-{max_value}): ").strip()
            if v.isdigit():
                n = int(v)
                if min_value <= n <= max_value:
                    return n
                print(f"[!] Value must be between {min_value} and {max_value}.")
            else:
                print("[!] Enter an integer.")

    def input_n(self) -> int:
        """Prompt for the total number of shares (n)."""
        from blob import PRIME
        return self.input_int_in_range("\nTotal shares (n)", 2, PRIME-1)

    def input_k(self, n: int) -> int:
        """Prompt for the threshold number of shares (k)."""
        return self.input_int_in_range("Threshold (k)", 2, n)

    def input_nonempty(self, prompt: str, hidden: bool = False) -> str:
        """
        Prompt for a non-empty string (optionally hidden).
        """
        while True:
            v = getpass.getpass(prompt) if hidden else input(prompt)
            if v:
                return v
            print("[!] Input cannot be empty.")

    def handle_split(self) -> None:
        """
        Handle the 'split' command: generate shares from an ASCII secret.
        """
        print(f"{self.SEP}\n[ Secret Splitting ]\n{self.SEP}")
        n = self.input_n()
        k = self.input_k(n)
        secret = self.input_nonempty("Secret (hidden): ", hidden=True)
        try:
            shares = encode_secret(secret, n, k)
        except Exception:
            print("\n[!] Error: could not encode secret.")
            print(self.SEP)
            self._last_secret = secret
            self._wipe_secret()
            return
        print("\nShares (x:base64):")
        print(self.SEP_MINUS)
        for s in shares:
            print(share_to_str(s))
        print(self.SEP_MINUS)
        print(self.SEP)
        self._last_secret = secret
        self._wipe_secret()

    def handle_recover(self) -> None:
        """
        Handle the 'recover' command: reconstruct a secret from shares.
        """
        print(f"{self.SEP}\n[ Secret Recovery ]\n{self.SEP}")
        print("\nEnter shares (x:base64), empty line to finish:")
        shares: List[List[Tuple[int, int]]] = []
        while True:
            try:
                line = input().strip()
            except EOFError:
                print("\n[!] Input terminated (EOF).")
                self.secure_exit()
            if not line:
                break
            share = str_to_share(line)
            if not share:
                print("[!] Invalid share format.")
                print(self.SEP)
                return
            shares.append(share)
        valid, msg = validate_shares(shares)
        if not valid:
            print(f"[!] Share validation error: {msg}")
            print(self.SEP)
            return
        try:
            secret = decode_secret(shares)
            if not secret.isascii():
                raise ValueError
            print("Recovered secret:")
            print(self.SEP_MINUS)
            print(secret)
            print(self.SEP_MINUS)
            print(self.SEP)
            self._last_secret = secret
            self._wipe_secret()
        except Exception:
            print("[!] Error: could not recover secret. (Check that you provided at least k valid, matching shares.)")
            print(self.SEP)
            # Defensive: only wipe if secret was successfully assigned
            secret_to_wipe = locals().get("secret", None)
            if secret_to_wipe is not None:
                self._last_secret = secret_to_wipe
                self._wipe_secret()

    def main(self) -> None:
        """
        Main CLI loop.
        """
        print(f"\n{self.SEP}")
        print("Blob CLI")
        self.print_usage()
        actions = {
            "split": self.handle_split,
            "recover": self.handle_recover,
            "help": self.print_usage,
            "exit": self.secure_exit
        }
        while True:
            try:
                print()
                cmd = input("Mode (split/recover/help/exit): ").strip().lower()
                print()
                actions.get(cmd, lambda: print("  [!] Unknown command. Type 'help'.\n" + self.SEP))()
            except (KeyboardInterrupt, EOFError):
                self.secure_exit()

if __name__ == "__main__":
    BlobCLI().main()
