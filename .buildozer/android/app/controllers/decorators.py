# controllers/decorators.py

import logging
from functools import wraps

class Fehlerbehandlung:
    @staticmethod
    def handle_errors(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Fehler in {func.__name__}: {e}")
                # Optional: Popup anzeigen
                if hasattr(args[0], 'show_popup'):
                    args[0].show_popup("Fehler", f"Ein Fehler ist aufgetreten: {e}")
                return None
        return wrapper
