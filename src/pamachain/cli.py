"""Command-line interface to initialise the vault and add/view credentials."""

from __future__ import annotations

import argparse
import getpass
import sys

from .crypto import (
    decrypt_string,
    derive_key,
    encrypt_string,
    make_verifier,
    verify_key,
)
from .keystore import keystore_exists, load_keystore, save_keystore
from .ledger.mock_chain import append_block, chain, repair_anchor


def _load_vault() -> dict[str, object]:
    document = load_keystore()
    if document is None:
        raise SystemExit("Vault not initialised. Run `pamachain --init` first.")
    return document


def _unlock(document: dict[str, object]) -> bytes:
    """Derive the vault key and prove the password against the keystore."""
    password = getpass.getpass("Master password: ")
    try:
        key, _ = derive_key(password, document["salt"])  # type: ignore[arg-type]
    except ValueError as exc:
        raise SystemExit(f"Could not derive the vault key: {exc}") from exc

    verifier = document.get("verifier")
    if isinstance(verifier, str) and verifier:
        if not verify_key(key, verifier):
            raise SystemExit("Incorrect master password.")
        return key

    # Legacy keystore (salt only). Accept the password only if it actually
    # decrypts an existing entry, then upgrade the keystore with a verifier.
    for block in chain(verify=False):
        secret = block.get("secret")
        if not isinstance(secret, str):
            continue
        try:
            decrypt_string(secret, key)
        except ValueError:
            continue
        save_keystore(document["salt"], make_verifier(key))  # type: ignore[arg-type]
        print("Upgraded this vault with a password verifier.")
        return key
    raise SystemExit(
        "This legacy vault has no verifier and no entry could be decrypted. "
        "The master password is wrong, or the vault must be reinitialised."
    )


def init(force: bool = False) -> None:
    if keystore_exists() and not force:
        raise SystemExit(
            "Vault already initialised. Use --force to replace the master "
            "password; existing ledger entries will become unreadable."
        )
    password = getpass.getpass("Set master password: ")
    confirmation = getpass.getpass("Confirm master password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")
    key, salt = derive_key(password)
    save_keystore(salt, make_verifier(key))
    print("Vault initialised.")


def add(label: str, secret: str, key: bytes | None = None) -> None:
    if key is None:
        document = _load_vault()
        key = _unlock(document)
    entry = {"label": label, "secret": encrypt_string(secret, key)}
    append_block(entry)
    print("Secret stored on ledger.")


def view() -> None:
    document = _load_vault()
    key = _unlock(document)
    for block in chain():
        label = block.get("label", "(no label)")
        secret = block.get("secret")
        if not isinstance(secret, str):
            print(f"{label}: (no secret)")
            continue
        try:
            print(f"{label}: {decrypt_string(secret, key)}")
        except ValueError:
            print(f"{label}: <could not decrypt>")


def list_entries() -> None:
    for block in chain():
        print(f"{block.get('label', '(no label)')}  {block.get('timestamp', '')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pamachain")
    parser.add_argument("--init", action="store_true", help="create a new vault")
    parser.add_argument(
        "--force",
        action="store_true",
        help="with --init, replace an existing master password",
    )
    parser.add_argument("--add", metavar="LABEL", help="add a credential")
    parser.add_argument("--view", action="store_true", help="show credentials")
    parser.add_argument("--list", action="store_true", help="list labels only")
    parser.add_argument(
        "--repair-anchor",
        action="store_true",
        help="trust the current ledger and rewrite its head anchor",
    )
    args = parser.parse_args(argv)

    try:
        if args.init:
            init(force=args.force)
        elif args.add:
            # Authenticate before asking for the secret being stored.
            document = _load_vault()
            key = _unlock(document)
            secret = getpass.getpass("Secret: ")
            add(args.add, secret, key=key)
        elif args.view:
            view()
        elif args.list:
            list_entries()
        elif args.repair_anchor:
            head = repair_anchor()
            if head:
                print(f"Ledger anchor repaired at {head}.")
            else:
                print("Ledger is empty; anchor removed.")
        else:
            parser.print_help()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
