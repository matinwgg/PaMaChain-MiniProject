import customtkinter as ctk

from pamachain.crypto import derive_key, verify_key
from pamachain.keystore import load_keystore


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Master Password").pack(pady=20)
        self.pw = ctk.CTkEntry(self, show="*")
        self.pw.pack()
        self.pw.bind("<Return>", lambda _event: self.unlock())
        ctk.CTkButton(self, text="Unlock", command=self.unlock).pack(pady=20)
        self.error = ctk.CTkLabel(self, text="", text_color="#B00020")
        self.error.pack()

    def unlock(self):
        document = load_keystore()
        if document is None:
            self.error.configure(
                text="Vault not initialised. Run `pamachain --init` first."
            )
            return

        canary = document.get("verifier")
        if not isinstance(canary, str) or not canary:
            self.error.configure(
                text="This vault predates password verification. "
                "Run `pamachain --view` once to upgrade it."
            )
            return

        password = self.pw.get()
        try:
            key, _ = derive_key(password, document["salt"])
        except ValueError as exc:
            self.error.configure(text=str(exc))
            return

        if not verify_key(key, canary):
            self.error.configure(text="Incorrect master password.")
            self.pw.delete(0, ctk.END)
            return

        self.error.configure(text="")
        self.master.show_vault(key)
        self.pw.delete(0, ctk.END)
