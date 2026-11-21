from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from src.ui.viewer import BytecodeViewer
from src.utils.clipboard import copy_text
from src.config import DEFAULT_OUTPUT_FILE


class MainScreen(Screen):
    """Ecran principal affichant le bytecode, les controles et la recherche."""

    CSS = """
    MainScreen {
        background: #090d13;
        scrollbar-background: #161b22;
        scrollbar-color: #238636;
        scrollbar-color-hover: #2ea043;
        scrollbar-color-active: #3fb950;
        scrollbar-size-vertical: 1;
        scrollbar-size-horizontal: 1;
    }

    Header {
        background: #161b22;
        color: #58a6ff;
    }

    Footer {
        background: #161b22;
    }

    #top_info_bar {
        dock: top;
        height: 3;
        background: #161b22;
        border-bottom: heavy #30363d;
        padding: 0 1;
    }

    #file_label {
        width: 1fr;
        height: 1;
        color: #58a6ff;
        text-style: bold;
        margin-top: 1;
    }

    #search_bar {
        dock: top;
        height: 3;
        background: #1f242c;
        border-bottom: solid #58a6ff;
        padding: 0 1;
        display: none;
    }

    #search_prompt {
        width: 14;
        height: 1;
        color: #f2cc60;
        text-style: bold;
        margin-top: 1;
    }

    #search_input {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
        color: #f0f6fc;
        padding: 0;
        margin-top: 1;
    }

    #search_input:focus {
        border: none;
    }

    #btn_copy {
        width: auto;
        height: 1;
        min-width: 10;
        margin-top: 1;
        margin-right: 1;
        background: #238636;
        color: white;
        border: none;
    }

    #status_pill, #search_status {
        width: auto;
        height: 1;
        margin-top: 1;
        color: #8b949e;
    }

    #code_viewer {
        width: 100%;
        height: 100%;
        background: #090d13;
        border: none;
        scrollbar-background: #161b22;
        scrollbar-color: #388bfd;
        scrollbar-color-hover: #58a6ff;
        scrollbar-color-active: #79c0ff;
        scrollbar-size-vertical: 1;
        scrollbar-size-horizontal: 1;
    }

    #code_viewer:focus {
        border: none;
    }
    """

    BINDINGS = [
        ("f", "open_search", "Rechercher"),
        ("c", "copy_code", "Copier"),
        ("a", "select_all", "Tout select"),
        ("s", "save_output", "Sauvegarder"),
        ("q", "quit", "Quitter"),
        ("ctrl+f", "open_search", "Rechercher"),
        ("ctrl+c", "copy_code", "Copier"),
        ("ctrl+a", "select_all", "Tout select"),
        ("escape", "close_search", "Fermer"),
    ]

    def __init__(self, filename: str, ver_str: str, disasm: str):
        super().__init__()
        self.filename = filename
        self.ver_str = ver_str
        self.disasm_raw = disasm
        self.search_matches = []
        self.current_match_idx = -1
        self.last_query = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="top_info_bar"):
            yield Static(f"Fichier : {self.filename} ({self.ver_str})", id="file_label")
            yield Button("Copier", id="btn_copy")
            yield Static(f"[ OK - {self.ver_str} ]", id="status_pill")

        with Horizontal(id="search_bar"):
            yield Static("Rechercher  >", id="search_prompt")
            yield Input(placeholder="Tapez un mot ou opcode (Entree: suivant, Echap: fermer)...", id="search_input")
            yield Static("[ 0/0 ]", id="search_status")

        viewer = BytecodeViewer(
            read_only=True,
            show_line_numbers=True,
            id="code_viewer"
        )
        viewer.text = self.disasm_raw
        yield viewer
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_copy":
            self.action_copy_code()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search_input":
            query = event.value.strip()
            if query:
                if query != self.last_query:
                    self._perform_search(query)
                else:
                    self._navigate_match(1)

    def _perform_search(self, query: str) -> None:
        self.last_query = query
        self.search_matches.clear()
        self.current_match_idx = -1

        viewer = self.query_one("#code_viewer", BytecodeViewer)
        lines = viewer.text.splitlines()
        q_lower = query.lower()

        for row_idx, line in enumerate(lines):
            line_lower = line.lower()
            start = 0
            while True:
                pos = line_lower.find(q_lower, start)
                if pos == -1:
                    break
                self.search_matches.append((row_idx, pos, pos + len(query)))
                start = pos + len(query)

        status = self.query_one("#search_status", Static)
        total = len(self.search_matches)
        if total > 0:
            self.current_match_idx = 0
            status.update(f"[bold green][ 1/{total} ][/bold green]")
            self._jump_to_current_match()
        else:
            status.update("[bold red][ 0 resultat ][/bold red]")

    def _navigate_match(self, direction: int) -> None:
        total = len(self.search_matches)
        if total == 0:
            return
        self.current_match_idx = (self.current_match_idx + direction) % total
        status = self.query_one("#search_status", Static)
        status.update(f"[bold green][ {self.current_match_idx + 1}/{total} ][/bold green]")
        self._jump_to_current_match()

    def _jump_to_current_match(self) -> None:
        if 0 <= self.current_match_idx < len(self.search_matches):
            row, start_col, end_col = self.search_matches[self.current_match_idx]
            viewer = self.query_one("#code_viewer", BytecodeViewer)
            viewer.selection = ((row, start_col), (row, end_col))
            viewer.cursor_location = (row, end_col)
            viewer.scroll_cursor_visible()

    def action_open_search(self) -> None:
        search_bar = self.query_one("#search_bar", Horizontal)
        search_input = self.query_one("#search_input", Input)
        search_bar.styles.display = "block"
        search_input.focus()

    def action_close_search(self) -> None:
        search_bar = self.query_one("#search_bar", Horizontal)
        if search_bar.styles.display == "block":
            search_bar.styles.display = "none"
            viewer = self.query_one("#code_viewer", BytecodeViewer)
            viewer.focus()

    def action_copy_code(self) -> None:
        viewer = self.query_one("#code_viewer", BytecodeViewer)
        target = viewer.selected_text or self.disasm_raw
        if target:
            if copy_text(target):
                self.notify(f"Copie dans le presse-papier ({len(target.splitlines())} lignes)")
            else:
                self.notify("Erreur lors de la copie", severity="error")

    def action_select_all(self) -> None:
        viewer = self.query_one("#code_viewer", BytecodeViewer)
        viewer.select_all()
        viewer.focus()
        self.notify("Tout est selectionne. Appuyez sur [c] pour copier.")

    def action_save_output(self) -> None:
        if not self.disasm_raw:
            return
        with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(self.disasm_raw)
        self.notify(f"Exporte dans {DEFAULT_OUTPUT_FILE}")
