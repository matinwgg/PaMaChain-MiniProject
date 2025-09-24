import customtkinter as ctk
from pamachain.crypto import derive_key
from pamachain.keystore import load_salt

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Master Password").pack(pady=20)
        self.pw = ctk.CTkEntry(self, show="*")
        self.pw.pack()
        ctk.CTkButton(self, text="Unlock", command=self.unlock).pack(pady=20)

    def unlock(self):
        salt = load_salt()
        key, _ = derive_key(self.pw.get(), salt)
        # Key validation can be added
        self.master.show_vault()
        self.pw.delete(0, ctk.END)
# --- IGNORE ---