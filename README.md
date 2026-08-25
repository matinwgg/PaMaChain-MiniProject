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
- `cryptography`
- Argon2
- WebSockets
- pytest
- Desktop GUI tooling used by the application

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
│   ├── keystore.py   # Persistent cryptographic identity
│   ├── p2p_network.py# Experimental peer transport
│   └── ...
├── tests/            # Security and regression tests
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
pip install -r requirements.txt
pytest -q
python -m pamachain.cli --init
python -m pamachain.cli --add github myStrongPassword
```

## 💻 Usage

Use the CLI to initialize a local vault, add credentials, and inspect the ledger. Treat the local key material and vault files as sensitive state.

## 🔐 Security Model

The project separates confidentiality, integrity, identity, and transport concerns. The P2P layer remains a research prototype: resource validation is present, but a production network needs authenticated peer identities, signed network messages, replay protection, trust establishment, key rotation, and TLS/WSS.

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
- Durable concurrent storage
- Formal threat model and security review

## 🤝 Contributing

Security-sensitive changes must include negative tests and explain which security invariant they preserve.

## 📄 License

See repository license information.

## 👨‍💻 Author

**Matin Odoom**
