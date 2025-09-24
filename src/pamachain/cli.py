"""
Simple command-line interface to initialise vault and add/view credentials.
"""
import argparse, getpass, json
from .crypto import derive_key, encrypt_string, decrypt_string
from .keystore import save_salt, load_salt
from .ledger.mock_chain import append_block, chain

def init():
    pwd = getpass.getpass("Set master password: ")
    key, salt = derive_key(pwd)
    save_salt(salt)
    print("Vault initialised.")

def add(label: str, secret: str):
    salt = load_salt()
    if not salt:
        raise SystemExit("Vault not initialised.")
    pwd = getpass.getpass("Master password: ")
    key, _ = derive_key(pwd, salt)
    entry = {"label": label, "secret": encrypt_string(secret, key)}
    append_block(entry)
    print("Secret stored on ledger.")

def view():
    salt = load_salt()
    pwd = getpass.getpass("Master password: ")
    key, _ = derive_key(pwd, salt)
    for b in chain():
        dec = decrypt_string(b["secret"], key)
        print(f"{b['label']}: {dec}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true")
    p.add_argument("--add")
    p.add_argument("--view", action="store_true")
    args = p.parse_args()

    if args.init: init()
    elif args.add:
        secret = getpass.getpass("Secret: ")
        add(args.add, secret)
    elif args.view: view()
    else: p.print_help()

if __name__ == "__main__":
    main()
# --- IGNORE ---