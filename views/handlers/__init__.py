# views/handlers/__init__.py
"""
Handler-Module für EinstellungenWidget
Aufgeteilte Funktionalitäten für bessere Code-Organisation
"""

from .theme_handler import ThemeHandler
from .character_handler import CharacterHandler
from .template_handler import TemplateHandler
from .game_elements_handler import GameElementsHandler

__all__ = [
    'ThemeHandler',
    'CharacterHandler', 
    'TemplateHandler',
    'GameElementsHandler'
]