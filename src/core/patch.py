def apply_xdis_patches():
    """Applique les correctifs de compatibilite pour xdis."""
    try:
        import xdis.bytecode
        orig_get_const = xdis.bytecode._get_const_info

        def safe_get_const(idx, lst):
            try:
                return orig_get_const(idx, lst)
            except (IndexError, TypeError):
                return idx, f"<const #{idx}>"

        xdis.bytecode._get_const_info = safe_get_const
    except ImportError:
        pass

    try:
        from textual.scrollbar import ScrollBarRender
        ScrollBarRender.VERTICAL_BARS = [" "] * 8
        ScrollBarRender.HORIZONTAL_BARS = [" "] * 8
        ScrollBarRender.BLANK_GLYPH = " "
    except Exception:
        pass
