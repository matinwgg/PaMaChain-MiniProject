"""
Minimal integration test for the p2p_network module.
Spins up a server and connects a client to ensure handshake works.
"""
import asyncio
import pytest

pytest.importorskip("websockets")

from pamachain.p2p_network import start_node

@pytest.mark.asyncio
async def test_p2p_node_start_and_connect():
    # Start server in background
    server_task = asyncio.create_task(start_node(port=8899))
    await asyncio.sleep(0.5)  # wait for server to be ready

    import websockets
    async with websockets.connect("ws://localhost:8899") as ws:
        await ws.send("ping")
        # The simple handler echoes to other peers; with one client no echo expected
        await asyncio.sleep(0.1)

    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
