import subprocess


def copy_text(text: str) -> bool:
    """Copie le texte dans le presse-papier Windows avec gestion d'erreurs."""
    if not text:
        return False

    try:
        proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=False)
        proc.communicate(text.encode("utf-16le"))
        if proc.returncode == 0:
            return True
    except Exception:
        pass

    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    return False
