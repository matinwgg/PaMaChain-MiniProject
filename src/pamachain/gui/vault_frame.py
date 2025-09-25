import customtkinter as ctk
from pamachain.ledger.mock_chain import chain
from pamachain.gui.login_frame import LoginFrame


class VaultFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # keep a reference to the app
        ctk.CTkLabel(self, text="Stored Entries").pack(pady=10)
        for b in chain():
            ctk.CTkLabel(self, text=b.get("label", "(no label)")).pack()
            ctk.CTkLabel(self, text=b.get("secret", "(no secret)")).pack()
        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)

    def logout(self):
        """Switch back to the login screen."""
        self.master.switch_frame(LoginFrame)
