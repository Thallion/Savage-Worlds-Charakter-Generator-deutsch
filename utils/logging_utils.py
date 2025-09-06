# utils/logging_utils.py
"""
Logger-Handler Utilities extrahiert aus main.py
"""

import logging
from kivy.clock import Clock


class GUIHandler(logging.Handler):
    def __init__(self, logger_widget, **kwargs):
        super().__init__(**kwargs)
        self.logger_widget = logger_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        Clock.schedule_once(lambda dt: self.update_gui(msg), 0)

    def update_gui(self, msg):
        lines = self.logger_widget.text.splitlines()
        lines.append(msg)
        self.logger_widget.text = "\n".join(lines[-15:])  # Letzte 15 Zeilen anzeigen