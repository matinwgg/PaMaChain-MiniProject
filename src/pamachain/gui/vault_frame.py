import customtkinter as ctk

from pamachain.crypto import decrypt_string
from pamachain.ledger.mock_chain import chain


class VaultFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Stored Entries").pack(pady=10)

        key = getattr(master, "vault_key", None)
        if not isinstance(key, bytes):
            ctk.CTkLabel(self, text="Vault is locked.").pack(pady=10)
            ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)
            return

        entries = ctk.CTkScrollableFrame(self)
        entries.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        try:
            blocks = chain()
        except ValueError as exc:
            ctk.CTkLabel(entries, text=f"Ledger error: {exc}").pack(pady=10)
            blocks = []

        for block in blocks:
            label = block.get("label", "(no label)")
            secret = block.get("secret")
            if isinstance(secret, str):
                try:
                    value = decrypt_string(secret, key)
                except ValueError:
                    value = "<could not decrypt>"
            else:
                value = "(no secret)"
            ctk.CTkLabel(
                entries, text=f"{label}: {value}", anchor="w", justify="left"
            ).pack(fill="x", pady=2)

        if not blocks:
            ctk.CTkLabel(entries, text="No entries yet.").pack(pady=10)

        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)

    def logout(self):
        """Switch back to the login screen and drop the derived key."""
        self.master.show_login()
