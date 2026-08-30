# PaMaChain Threat Model

## Scope

The model covers peer discovery, WebSocket transport, message parsing, ledger mutation, and persistence.

## Assets

- Ledger integrity and ordering
- Peer identity
- Transaction authenticity
- Node availability
- Local private keys

## Adversaries

Assume an attacker can connect as an untrusted peer, send malformed or replayed messages, drop connections, and attempt to submit unauthorized state transitions. Do not assume network transport alone authenticates a peer.

## Required invariants

1. Unauthenticated input must never mutate trusted ledger state.
2. Every accepted state-changing message must authenticate its sender.
3. Replayed messages must be rejected.
4. Invalid transactions must fail closed.
5. Ledger persistence must preserve integrity across restart.

## Planned controls

- Ed25519 peer identities and signatures
- Monotonic sequence numbers/nonces
- WSS/TLS transport
- Peer authorization policy
- Persistent integrity checks
- Property-based protocol testing
- Fault-injection and recovery tests

## Current boundary

The current implementation provides input/resource validation but is not a production-secure consensus network. These planned controls must be implemented and tested before production claims are made.
