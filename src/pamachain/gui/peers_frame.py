"""
Peer status frame for PaMaChain GUI.

Shows a live list of connected P2P peers using the pamachain.p2p_network module.
This is a lightweight example and polls the peer set every second.
"""

import customtkinter as ctk
import threading
import asyncio

from pamachain import p2p_network

class PeersFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Connected Peers", font=("Arial", 16, "bold")).pack(pady=10)
        self.listbox = ctk.CTkTextbox(self, width=400, height=200)
        self.listbox.pack(padx=20, pady=10, fill="both", expand=True)

        # Start background refresher
        self._running = True
        self._refresh_loop()

    def _refresh_loop(self):
        """
        Periodically refresh the peer list every 1 second.
        """
        if not self._running:
            return

        self.listbox.delete("0.0", "end")
        # p2p_network.PEERS is a set of websocket objects
        peers = [str(peer.remote_address) for peer in p2p_network.PEERS]
        if peers:
            for addr in peers:
                self.listbox.insert("end", f"{addr}\n")
        else:
            self.listbox.insert("end", "No peers connected.\n")

        # schedule next update
        self.after(1000, self._refresh_loop)

    def destroy(self):
        self._running = False
        super().destroy()


def launch_peer_node_in_background(port: int = 8765):
    """
    Convenience: start the P2P node in a background thread so the GUI remains responsive.
    """
    loop = asyncio.new_event_loop()

    def runner():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(p2p_network.start_node(port=port))

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return thread
# --- IGNORE ---