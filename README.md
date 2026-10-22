# PaMaChain — Decentralised Password Manager Research Prototype

## 📖 About

PaMaChain is an educational security project exploring how password management, authenticated encryption, append-only ledgers, cryptographic identities, and peer-to-peer synchronization can be composed into a security-sensitive system.

### Why it exists

The project investigates a systems question: how can confidential vault data, tamper-evident history, cryptographic identity, and distributed communication interact without treating any one primitive as a complete security solution?

## ✨ Features

- AES-256-GCM authenticated encryption
- Argon2id password-based key derivation
- Persistent cryptographic signing identity
- Append-only ledger with hash-chain integrity checks
- Signature verification and corruption detection
- CLI vault management
- Desktop GUI
- Experimental WebSocket P2P transport
- P2P message-size and connection limits

## 🛠 Tech Stack

- Python
- PyCryptodome (AES-256-GCM)
- Argon2id
- ECDSA P-256
- WebSockets
- pytest
- customtkinter

## 🏗 Architecture

```text
User password
    ↓
Argon2id key derivation
    ↓
Vault encryption (AES-GCM)
    ↓
Ledger record
    ↓
Hash + signature
    ↓
Append-only local ledger
    ↓
Experimental P2P synchronization
```

The ledger provides tamper evidence; it does not replace authenticated storage, access control, or secure key management.

## 📁 Project Structure

```text
.
├── src/pamachain/
│   ├── ledger/       # Ledger and integrity logic
│   ├── tests/        # Security and regression tests
│   ├── keystore.py   # Salt + password-verifier metadata
│   ├── paths.py      # Overridable state-file locations
│   ├── p2p_network.py# Experimental peer transport
│   └── ...
├── requirements.txt
└── README.md
```

## 📋 Prerequisites

- Python 3.10+
- pip

## 🚀 Getting Started

```bash
git clone https://github.com/matinwgg/PaMaChain-MiniProject.git
cd PaMaChain-MiniProject
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
pamachain --init
pamachain --add github
pamachain --view
```

`pamachain --add LABEL` prompts for the secret instead of accepting it as an
argument, so it does not leak through shell history or the process list.

## 💻 Usage

Use the CLI to initialize a local vault, add credentials, and inspect the ledger. Treat the local key material and vault files as sensitive state.

Both the CLI and the GUI derive the master key from the password and verify it
against an authenticated verifier stored in `~/.pamachain_keystore.json`; a
wrong password is rejected before any entry is decrypted. The GUI displays
decrypted secrets and clears the derived key on logout.

State files are `~/.pamachain_ledger.jsonl` (ledger),
`~/.pamachain_ledger_signing_key.pem` (ECDSA identity),
`~/.pamachain_ledger.head.json` (anchored head), and
`~/.pamachain_keystore.json` (salt + verifier). The `PAMACHAIN_LEDGER`,
`PAMACHAIN_LEDGER_KEY`, `PAMACHAIN_LEDGER_ANCHOR`, and `PAMACHAIN_KEYSTORE`
environment variables override them, which is how the test suite isolates
itself.

## 🔐 Security Model

The project separates confidentiality, integrity, identity, and transport concerns. The ledger is tamper-evident: each block is signed, and the latest head is stored in a separate anchor file so truncation or deletion is detected. The head is still only anchored locally; an attacker who can rewrite both the ledger and the anchor can rewrite history. A production system needs an independent anchor (or a real chain).

The P2P layer remains a research prototype: resource validation is present, but a production network needs authenticated peer identities, signed network messages, replay protection, trust establishment, key rotation, and TLS/WSS.

If an older ledger predates the anchor file, `pamachain --repair-anchor` will verify the chain and write the current head. Run it only after reviewing the ledger, because it explicitly trusts whatever history is present.

## 🧪 Testing

```bash
pytest -q
```

Tests should cover tampering, corrupted records, invalid signatures, wrong keys, replayed network messages, and persistence across process restarts.

## 🚧 Limitations & Future Work

- Cryptographically authenticated P2P messages
- Peer trust/identity establishment
- Replay protection and sequence numbers
- Secure key rotation
- Remote/independent ledger anchoring (the local anchor detects accidental or
  naive tampering, not an attacker with full filesystem access)
- Encrypting the signing key at rest or storing it in an OS keychain (it is
  currently protected by `0600` filesystem permissions only)
- Encrypting ledger labels (only the secret values are encrypted)
- Formal threat model and security review

## 🤝 Contributing

Security-sensitive changes must include negative tests and explain which security invariant they preserve.

## 📄 License

See repository license information.

## 👨‍💻 Author

**Matin Odoom**
