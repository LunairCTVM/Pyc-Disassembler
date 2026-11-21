import os
import sys

sys.dont_write_bytecode = True


from src.core.patch import apply_xdis_patches
from src.core.decompiler import disassemble_pyc
from src.ui.app import PycApp
from src.utils.console import init_windows_console


def main():
    init_windows_console()
    apply_xdis_patches()

    os.system("cls" if os.name == "nt" else "clear")

    while True:
        try:
            path_raw = input("Enter your path for pyc : ")
        except (KeyboardInterrupt, EOFError):
            print("\nSortie.")
            sys.exit(0)

        path = path_raw.strip().strip('"').strip("'").strip("& ").strip()
        if not path:
            continue

        if not os.path.exists(path):
            print(f"Erreur : Le fichier '{path}' est introuvable.\n")
            continue

        print(f"Analyse de {os.path.basename(path)}...")
        try:
            data = disassemble_pyc(path)
            app = PycApp(data["filename"], data["version_str"], data["disassembly"])
            app.run()
            break
        except Exception as e:
            print(f"Erreur lors de la decompilation : {e}\n")


if __name__ == "__main__":
    main()
