# utils.py
def char_limit_ticks(event, limit: int):
    entry_widget = event.widget
    texto_actual = entry_widget.get()
    if len(texto_actual) > limit:
        entry_widget.delete(limit, 'end')


# share/utils.py
def char_limit_validator(limit: int):
    """
    Devuelve una función validadora para usar con validatecommand en Entries.
    """
    def _validator(P):
        return len(P) <= limit
    print(_validator)
    return _validator
