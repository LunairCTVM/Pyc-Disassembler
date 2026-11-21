from textual.widgets import TextArea
from rich.style import Style
from src.utils.clipboard import copy_text


class BytecodeViewer(TextArea):
    """Widget de visionnage du bytecode avec coloration btop et raccourcis."""

    BINDINGS = [
        ("c", "copy_text", "Copier"),
        ("ctrl+c", "copy_text", "Copier"),
        ("a", "select_all_text", "Tout select"),
        ("ctrl+a", "select_all_text", "Tout select"),
        ("f", "trigger_search", "Rechercher"),
        ("ctrl+f", "trigger_search", "Rechercher"),
    ]

    def action_copy_text(self) -> None:
        target = self.selected_text or self.text
        if target:
            if copy_text(target):
                self.app.notify(f"Copie dans le presse-papier ({len(target.splitlines())} lignes)")
            else:
                self.app.notify("Erreur lors de la copie", severity="error")
        else:
            self.app.notify("Rien a copier", severity="warning")

    def action_select_all_text(self) -> None:
        self.select_all()
        self.app.notify("Selection complete. Appuyez sur [c] pour copier.")

    def action_trigger_search(self) -> None:
        self.screen.action_open_search()

    def get_line(self, index: int):
        t = super().get_line(index)
        line = t.plain
        if not line or not line.strip():
            return t

        if line.startswith("#"):
            t.stylize(Style(color="#484f58"))
            return t

        if line.startswith("Method Name:") or line.startswith("Filename:") or "Disassembly of" in line:
            t.stylize(Style(color="#58a6ff", bold=True))
            return t

        tokens = line.split()
        for tok in tokens:
            pos = line.find(tok)
            if pos == -1:
                continue
            end = pos + len(tok)

            if tok == ">>":
                t.stylize(Style(color="#ff7b72", bold=True), pos, end)
            elif tok.isdigit():
                t.stylize(Style(color="#79c0ff"), pos, end)
            elif "JUMP" in tok:
                t.stylize(Style(color="#ff7b72", bold=True), pos, end)
            elif tok.startswith("IMPORT"):
                t.stylize(Style(color="#f2cc60", bold=True), pos, end)
            elif tok.startswith("LOAD_FAST") or tok.startswith("STORE_FAST"):
                t.stylize(Style(color="#7ee787", bold=True), pos, end)
            elif tok.startswith("LOAD_GLOBAL") or tok.startswith("LOAD_NAME") or tok.startswith("STORE_NAME"):
                t.stylize(Style(color="#79c0ff", bold=True), pos, end)
            elif tok.startswith("LOAD_CONST"):
                t.stylize(Style(color="#ffa657", bold=True), pos, end)
            elif "CALL" in tok or tok.startswith("PRECALL"):
                t.stylize(Style(color="#d2a8ff", bold=True), pos, end)
            elif tok.startswith("COMPARE") or tok.startswith("BINARY_") or tok.startswith("UNARY_"):
                t.stylize(Style(color="#f0883e", bold=True), pos, end)
            elif tok.startswith("RETURN_") or tok.startswith("POP_"):
                t.stylize(Style(color="#6e7681"), pos, end)

        if "(" in line and ")" in line:
            start_p = line.find("(")
            end_p = line.rfind(")") + 1
            inner = line[start_p:end_p]
            if "'" in inner or '"' in inner:
                t.stylize(Style(color="#a5d6ff"), start_p, end_p)
            elif any(c.isdigit() for c in inner):
                t.stylize(Style(color="#ffa657"), start_p, end_p)
            else:
                t.stylize(Style(color="#3fb950"), start_p, end_p)

        return t
