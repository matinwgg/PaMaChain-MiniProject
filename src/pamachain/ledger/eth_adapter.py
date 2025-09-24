"""
Ethereum adapter for PaMaChain ledger.

This module provides a minimal wrapper around Web3.py to
store/retrieve encrypted password entries on an Ethereum-compatible chain.

It is optional—if Web3 is not installed or no node URL is set,
the functions will raise a RuntimeError so the rest of the system
can continue with the mock_chain backend.
"""

from typing import Any
from pathlib import Path
import json
import os

try:
    from web3 import Web3
except ImportError:  # Web3 not installed
    Web3 = None


class EthAdapter:
    """
    Lightweight helper to connect to an Ethereum node and
    store encrypted credential entries.
    """

    def __init__(self, provider_url: str | None = None, private_key: str | None = None):
        if Web3 is None:
            raise RuntimeError("web3 library not installed. `pip install web3`.")
        self.provider_url = provider_url or os.getenv("PAMACHAIN_ETH_URL", "http://127.0.0.1:8545")
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Cannot connect to Ethereum node at {self.provider_url}")
        self.private_key = private_key or os.getenv("PAMACHAIN_ETH_PRIVKEY")
        if not self.private_key:
            raise RuntimeError("No private key supplied or PAMACHAIN_ETH_PRIVKEY unset.")
        self.account = self.w3.eth.account.from_key(self.private_key)

    def send_entry(self, entry: dict[str, Any]) -> str:
        """
        Send an encrypted password entry as a transaction's data field.
        Returns the transaction hash.
        """
        data = json.dumps(entry).encode()
        tx = {
            "from": self.account.address,
            "to": self.account.address,  # self-send; just to put data on chain
            "value": 0,
            "data": data,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "gas": 100000,
            "gasPrice": self.w3.to_wei("5", "gwei"),
        }
        signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()

    def get_transactions(self, address: str | None = None, start_block: int = 0, end_block: int | str = "latest"):
        """
        Fetch transactions containing PaMaChain entries for a given address.
        """
        address = address or self.account.address
        end_block = self.w3.eth.block_number if end_block == "latest" else end_block
        entries = []
        for block_num in range(start_block, end_block + 1):
            block = self.w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx.to and tx.to.lower() == address.lower():
                    try:
                        payload = tx.input
                        if payload and payload != "0x":
                            raw = bytes.fromhex(payload[2:])
                            entries.append(json.loads(raw))
                    except Exception:
                        continue
        return entries


# Convenience function
def append_block(entry: dict[str, Any]) -> str:
    """
    Drop-in replacement for mock_chain.append_block().
    Requires environment variables:
      PAMACHAIN_ETH_URL   - Ethereum node endpoint
      PAMACHAIN_ETH_PRIVKEY - Hex private key
    """
    adapter = EthAdapter()
    return adapter.send_entry(entry)
