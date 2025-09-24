"""
Stub peer-to-peer networking using websockets/asyncio.
"""
import asyncio, websockets, json

PEERS = set()

async def handler(ws):
    PEERS.add(ws)
    try:
        async for msg in ws:
            for peer in PEERS:
                if peer is not ws:
                    await peer.send(msg)
    finally:
        PEERS.remove(ws)

async def start_node(port=8765):
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"P2P node listening on {port}")
        await asyncio.Future()

def run_node(port=8765):
    asyncio.run(start_node(port))
# --- IGNORE ---