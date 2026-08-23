"""Defensive stub peer-to-peer networking using websockets/asyncio.

This module intentionally remains a transport prototype. It validates message
shape and bounds resource usage, but it does NOT provide authenticated peer
identity; production use requires signed messages and WSS/TLS.
"""
import asyncio
import json

import websockets

PEERS = set()
MAX_MESSAGE_BYTES = 64 * 1024
MAX_PEERS = 32


async def handler(ws):
    if len(PEERS) >= MAX_PEERS:
        await ws.close(code=1013, reason="peer limit reached")
        return

    PEERS.add(ws)
    try:
        async for msg in ws:
            if not isinstance(msg, str) or len(msg.encode("utf-8")) > MAX_MESSAGE_BYTES:
                await ws.close(code=1009, reason="message too large")
                break

            try:
                payload = json.loads(msg)
            except json.JSONDecodeError:
                await ws.close(code=1003, reason="invalid JSON")
                break

            if not isinstance(payload, dict) or not isinstance(payload.get("type"), str):
                await ws.close(code=1003, reason="invalid message schema")
                break

            outbound = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            for peer in tuple(PEERS):
                if peer is ws:
                    continue
                try:
                    await peer.send(outbound)
                except websockets.exceptions.ConnectionClosed:
                    PEERS.discard(peer)
    finally:
        PEERS.discard(ws)


async def start_node(port=8765):
    async with websockets.serve(handler, "0.0.0.0", port, max_size=MAX_MESSAGE_BYTES):
        print(f"P2P node listening on {port}")
        await asyncio.Future()


def run_node(port=8765):
    asyncio.run(start_node(port))
