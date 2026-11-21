import io
import os
from xdis.load import load_module
from xdis.op_imports import get_opcode_module
import xdis.std


def disassemble_pyc(path: str) -> dict:
    """Charge et desassemble un fichier .pyc independamment de la version Python."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier '{path}' n'existe pas.")

    res = load_module(path)
    py_ver = res[0]
    co = res[3]
    impl = res[4]
    ver_str = f"Python {py_ver[0]}.{py_ver[1]}"

    opc = get_opcode_module(py_ver, impl)
    imported_modules = get_imported_modules(co, opc)

    api = xdis.std.make_std_api(py_ver)
    buf = io.StringIO()
    api.disassemble(co, file=buf)
    disasm = buf.getvalue()

    return {
        "filename": os.path.basename(path),
        "version_tuple": py_ver,
        "version_str": ver_str,
        "disassembly": disasm,
        "imports": imported_modules,
        "size": os.path.getsize(path),
    }


def get_imported_modules(co, opc) -> list[str]:
    """Recherche tous les modules importes dans le code object."""
    found = set()
    code = getattr(co, "co_code", b"")
    names = getattr(co, "co_names", ())
    consts = getattr(co, "co_consts", ())

    import_op = opc.opmap.get("IMPORT_NAME")
    if import_op is not None:
        for i in range(0, len(code), 2):
            op = code[i]
            arg = code[i + 1]
            if op == import_op and arg < len(names):
                found.add(names[arg])

    for c in consts:
        if hasattr(c, "co_code"):
            found.update(get_imported_modules(c, opc))

    return sorted(found)
