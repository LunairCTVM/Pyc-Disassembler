from textual.app import App
from src.ui.screens import MainScreen


class PycApp(App):
    """Application TUI Textual."""

    ENABLE_COMMAND_PALETTE = False
    COMMANDS = set()

    def __init__(self, filename: str, ver_str: str, disasm: str):
        super().__init__()
        self.filename = filename
        self.ver_str = ver_str
        self.disasm = disasm

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self.filename, self.ver_str, self.disasm))
