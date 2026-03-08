"""
Plattform-Utilities für Mobile-Layout-Erkennung.
Bestimmt ob Smartphone-optimierte KV-Dateien geladen werden sollen.
"""

import json
import os
import sys
from pathlib import Path
from kivy.utils import platform
from kivy.logger import Logger

# Cache damit die Config-Datei nur einmal gelesen wird
_mobile_layout_cache = None


def _read_force_mobile_from_config():
    """
    Liest force_mobile_layout direkt aus der JSON-Config-Datei.
    Wird beim App-Start aufgerufen, bevor der ServiceContainer existiert.
    """
    try:
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path(__file__).parent.parent

        config_path = app_dir / "config" / "app_config.json"

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('force_mobile_layout', False)
    except Exception as e:
        Logger.warning(f"platform_utils: Fehler beim Lesen der Config: {e}")

    return False


def is_mobile_layout():
    """
    Prüft ob Mobile-KV-Dateien (Smartphone-Layout) geladen werden sollen.

    Entscheidungslogik:
    - Android mit Bildschirmbreite < 600dp → Mobile-Layout
    - Desktop mit force_mobile_layout in app_config.json → Mobile-Layout (für Tests)
    - Sonst → Desktop-Layout

    Returns:
        bool: True wenn Mobile-Layout verwendet werden soll
    """
    global _mobile_layout_cache

    # Cache verwenden falls bereits ermittelt
    if _mobile_layout_cache is not None:
        return _mobile_layout_cache

    if platform == 'android':
        # Android-Geräte nutzen immer Mobile-Layout.
        # Im Landscape-Modus kann Window.width > 600dp sein (z.B. Pixel 9: ~923dp),
        # aber Smartphones brauchen trotzdem das Mobile-Layout.
        _mobile_layout_cache = True
        Logger.info("platform_utils: Android erkannt → Mobile-Layout aktiviert")
        return True

    # Desktop-Override: Direkt aus JSON-Datei lesen (ServiceContainer existiert noch nicht)
    force_mobile = _read_force_mobile_from_config()
    if force_mobile:
        Logger.info("platform_utils: force_mobile_layout ist aktiviert (Desktop-Testmodus)")
        _mobile_layout_cache = True
        return True

    _mobile_layout_cache = False
    return False


def get_kv_filename(base_name):
    """
    Gibt den korrekten KV-Dateinamen zurück (Desktop oder Mobile).

    Args:
        base_name (str): Basis-Name der KV-Datei ohne Endung (z.B. 'profil_view')

    Returns:
        str: KV-Dateiname (z.B. 'profil_view_mobile.kv' oder 'profil_view.kv')
    """
    if is_mobile_layout():
        return f"{base_name}_mobile.kv"
    return f"{base_name}.kv"
