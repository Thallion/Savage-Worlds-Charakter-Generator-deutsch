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


def _read_layout_overrides_from_config():
    """
    Liest force_mobile_layout und tablet_layout direkt aus der JSON-Config-Datei.
    Wird beim App-Start aufgerufen, bevor der ServiceContainer existiert.

    Returns:
        tuple[bool, bool]: (force_mobile_layout, tablet_layout)
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
            return (
                data.get('force_mobile_layout', False),
                data.get('tablet_layout', False),
            )
    except Exception as e:
        Logger.warning(f"platform_utils: Fehler beim Lesen der Config: {e}")

    return False, False


def is_mobile_layout():
    """
    Prüft ob Mobile-KV-Dateien (Smartphone-Layout) geladen werden sollen.

    Entscheidungslogik:
    - Android mit aktivem tablet_layout → Desktop-Layout (für Tablets)
    - Android sonst → Mobile-Layout
    - Desktop mit force_mobile_layout in app_config.json → Mobile-Layout (für Tests)
    - Sonst → Desktop-Layout

    Returns:
        bool: True wenn Mobile-Layout verwendet werden soll
    """
    global _mobile_layout_cache

    # Cache verwenden falls bereits ermittelt
    if _mobile_layout_cache is not None:
        return _mobile_layout_cache

    force_mobile, tablet_layout = _read_layout_overrides_from_config()

    if platform == 'android':
        if tablet_layout:
            Logger.info("platform_utils: Android mit aktivem Tablet-Layout → Desktop-Layout")
            _mobile_layout_cache = False
            return False
        # Android-Geräte nutzen sonst immer Mobile-Layout.
        # Im Landscape-Modus kann Window.width > 600dp sein (z.B. Pixel 9: ~923dp),
        # aber Smartphones brauchen trotzdem das Mobile-Layout.
        _mobile_layout_cache = True
        Logger.info("platform_utils: Android erkannt → Mobile-Layout aktiviert")
        return True

    # Desktop-Override: Direkt aus JSON-Datei lesen (ServiceContainer existiert noch nicht)
    if force_mobile:
        if tablet_layout:
            # Tablet-Layout überschreibt force_mobile auch auf Desktop (für Tests)
            Logger.info(
                "platform_utils: force_mobile_layout + tablet_layout → Desktop-Layout (Tablet-Test)"
            )
            _mobile_layout_cache = False
            return False
        Logger.info("platform_utils: force_mobile_layout ist aktiviert (Desktop-Testmodus)")
        _mobile_layout_cache = True
        return True

    _mobile_layout_cache = False
    return False


def landscape_height(portrait_dp_value, landscape_fraction=0.7):
    """
    Gibt eine Hoehe zurueck, die im Landscape-Modus auf Mobile
    an die verfuegbare Bildschirmhoehe angepasst wird.

    Im Portrait-Modus oder auf Desktop wird der portrait_dp_value
    als dp()-Wert unveraendert zurueckgegeben.

    Args:
        portrait_dp_value: Hoehe in dp fuer den Portrait-Modus (ohne dp()-Aufruf)
        landscape_fraction: Anteil der Bildschirmhoehe im Landscape (Standard: 0.7)

    Returns:
        float: Berechnete Hoehe in Pixeln
    """
    from kivy.core.window import Window
    from kivy.metrics import dp

    if not is_mobile_layout():
        return dp(portrait_dp_value)

    # Landscape erkennen
    if Window.width > Window.height:
        return min(dp(portrait_dp_value), Window.height * landscape_fraction)

    return dp(portrait_dp_value)


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
