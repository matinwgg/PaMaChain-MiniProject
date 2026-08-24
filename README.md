# PaMaChain — Decentralised Password Manager Research Prototype

PaMaChain is an educational security project exploring how password management, authenticated encryption, append-only ledgers, cryptographic identities, and peer-to-peer synchronization can be combined.

## What it demonstrates

- AES-256-GCM authenticated encryption
- Argon2id password-based key derivation
- Persistent cryptographic signing identity
- Append-only ledger with hash-chain integrity checks
- Signature verification and corruption detection
- Command-line vault management
- Desktop GUI
- Experimental WebSocket peer-to-peer transport

## Security model

The project treats the vault and ledger as security-sensitive state. Encryption provides confidentiality and integrity for vault data; the ledger provides tamper-evident history; signatures bind records to a signing identity.

The P2P layer is still a research/educational prototype. Transport validation and resource limits are implemented, but a production distributed system would additionally require authenticated peer identities, signed network messages, replay protection, key rotation, trust establishment, and TLS/WSS.

## Quick start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m pamachain.cli --init
python -m pamachain.cli --add github myStrongPassword
```

## Research themes

PaMaChain connects to applied cryptography, secure storage, distributed systems, integrity verification, key management, threat modelling, and trustworthy software engineering.

## Status

**Educational / research prototype.** It is intended for experimentation and learning, not as a production password manager or security boundary.
