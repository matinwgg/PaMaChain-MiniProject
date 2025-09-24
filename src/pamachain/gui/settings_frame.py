"""
SettingsFrame for PaMaChain GUI.

Lets the user configure appearance (light/dark), P2P node port,
and vault auto-lock timeout. Values are stored in-memory for now,
but can easily be saved to a config file.
"""

import customtkinter as ctk
from pamachain.gui.peers_frame import launch_peer_node_in_background

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Settings", font=("Arial", 16, "bold")).pack(pady=10)

        # Theme toggle
        ctk.CTkLabel(self, text="Theme:").pack(pady=(20, 0))
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkOptionMenu(
            self, values=["Light", "Dark"], variable=self.theme_var,
            command=self._change_theme
        ).pack()

        # P2P port entry
        ctk.CTkLabel(self, text="P2P Port:").pack(pady=(20, 0))
        self.port_var = ctk.StringVar(value="8765")
        ctk.CTkEntry(self, textvariable=self.port_var, width=100).pack()

        self.node_status = ctk.CTkLabel(self, text="Node not running")
        self.node_status.pack(pady=(5, 15))

        ctk.CTkButton(
            self,
            text="Launch Node",
            command=self._start_node
        ).pack()

        # Auto-lock timeout
        ctk.CTkLabel(self, text="Auto-Lock Timeout (minutes):").pack(pady=(20, 0))
        self.timeout_var = ctk.StringVar(value="5")
        ctk.CTkEntry(self, textvariable=self.timeout_var, width=100).pack()

        # Save button placeholder
        ctk.CTkButton(
            self,
            text="Save Settings",
            command=self._save_settings
        ).pack(pady=30)

    # ----------------- Callbacks -----------------

    def _change_theme(self, value: str):
        """Switch between light and dark mode."""
        ctk.set_appearance_mode(value)

    def _start_node(self):
        """Launch P2P node on chosen port in background."""
        try:
            port = int(self.port_var.get())
        except ValueError:
            self.node_status.configure(text="Invalid port number")
            return

        launch_peer_node_in_background(port=port)
        self.node_status.configure(text=f"Node running on port {port}")

    def _save_settings(self):
        """
        In a full implementation, persist settings to a file or secure storage.
        Here we just show a confirmation.
        """
        timeout = self.timeout_var.get()
        self.node_status.configure(text=f"Settings saved (timeout={timeout} min)")
        # In a real app, validate and save the timeout and other settings
# --- IGNORE ---