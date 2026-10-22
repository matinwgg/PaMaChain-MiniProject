import customtkinter as ctk

from .login_frame import LoginFrame
from .vault_frame import VaultFrame


class PaMaChainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PaMaChain Password Manager")
        self.geometry("800x500")
        self.current_frame = None
        self.vault_key: bytes | None = None
        self.show_login()

    def switch_frame(self, frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.vault_key = None
        self.switch_frame(LoginFrame)

    def show_vault(self, key: bytes):
        self.vault_key = key
        self.switch_frame(VaultFrame)


def run():
    app = PaMaChainApp()
    app.mainloop()


if __name__ == "__main__":
    run()
