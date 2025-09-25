"""
Basic headless tests for the customtkinter GUI.
These tests only verify that frames can be created and destroyed without errors.
"""
import os
import pytest

pytest.importorskip("customtkinter")

from pamachain.gui.main_app import PaMaChainApp
from pamachain.gui.login_frame import LoginFrame
from pamachain.gui.vault_frame import VaultFrame

# Skip GUI tests if DISPLAY is not available (headless environments like CI)
skip_headless = pytest.mark.skipif(
    os.environ.get("DISPLAY", "") == "",
    reason="No display available for Tkinter"
)

@skip_headless
def test_app_starts_and_switches_frames():
    # Do not call .mainloop() to avoid blocking
    app = PaMaChainApp()
    
    # Ensure login frame is default
    assert isinstance(app.current_frame, LoginFrame)
    
    # Switch to vault frame
    app.switch_frame(VaultFrame)
    assert isinstance(app.current_frame, VaultFrame)
    
    # Destroy safely
    app.destroy()
