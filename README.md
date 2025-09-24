# PaMaChain – Decentralised, Trustless Password Manager

PaMaChain is a mini-project demonstrating a **decentralised, trustless password-management system** built on a simple blockchain ledger with peer-to-peer syncing.

### Features
- AES-256-GCM encryption with Argon2id key derivation
- Lightweight append-only blockchain ledger (`mock_chain`)
- Optional peer-to-peer networking stub (`p2p_network`)
- Command-line vault management
- Modern desktop GUI built with [customtkinter]

### Quick Start
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m pamachain.cli --init
python -m pamachain.cli --add github myStrongPassword
