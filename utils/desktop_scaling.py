"""
Desktop-Skalierung für HiDPI-Displays.

WICHTIG: Dieses Modul darf KEINE Kivy-Imports enthalten!
Es muss VOR allen Kivy-Imports aufgerufen werden, da KIVY_METRICS_DENSITY
als Environment-Variable gesetzt werden muss, bevor Kivy initialisiert wird.

Setzt KIVY_METRICS_DENSITY basierend auf:
1. Manuellem desktop_scale_factor aus app_config.json
2. Automatischer Erkennung der Bildschirmauflösung (Fallback)
"""

import json
import os
import sys
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard-Density auf Desktop: 1.0 (= 160 DPI Baseline)
DEFAULT_DENSITY = 1.0

# Auto-Detection Schwellwerte (Bildschirmbreite in Pixeln)
_RESOLUTION_THRESHOLDS = [
    (3840, 2.0),   # 4K → Density 2.0
    (2560, 1.5),   # QHD/WQHD → Density 1.5
    (1920, 1.0),   # Full HD → Density 1.0
]


def _get_app_root():
    """Ermittelt das App-Stammverzeichnis (ohne Kivy-Import)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def _read_scale_factor_from_config():
    """
    Liest desktop_scale_factor aus app_config.json.

    Returns:
        float oder str: Skalierungsfaktor (z.B. 1.5) oder "auto" für automatische Erkennung.
        None falls nicht gesetzt oder Fehler.
    """
    try:
        config_path = _get_app_root() / "config" / "app_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            value = data.get('desktop_scale_factor', 'auto')
            if isinstance(value, (int, float)) and value > 0:
                return float(value)
            if value == 'auto':
                return 'auto'
    except Exception as e:
        logger.debug(f"desktop_scaling: Config-Lesen fehlgeschlagen: {e}")
    return 'auto'


def _detect_screen_width_linux():
    """
    Erkennt die Bildschirmbreite unter Linux via xrandr.

    Returns:
        int: Bildschirmbreite in Pixeln oder 0 bei Fehler.
    """
    try:
        output = subprocess.check_output(
            ['xrandr', '--current'],
            stderr=subprocess.DEVNULL,
            timeout=3
        ).decode('utf-8', errors='replace')

        # Suche nach aktiven Ausgängen: z.B. "3840x2160+0+0"
        # Format: "HDMI-1 connected primary 3840x2160+0+0 ..."
        import re
        # Finde die höchste Auflösung eines verbundenen Monitors
        max_width = 0
        for line in output.splitlines():
            if ' connected' in line:
                match = re.search(r'(\d{3,5})x(\d{3,5})\+', line)
                if match:
                    width = int(match.group(1))
                    if width > max_width:
                        max_width = width
        return max_width
    except Exception:
        return 0


def _detect_screen_width_windows():
    """
    Erkennt die Bildschirmbreite unter Windows via ctypes.

    Returns:
        int: Bildschirmbreite in Pixeln oder 0 bei Fehler.
    """
    try:
        import ctypes
        # SM_CXSCREEN = 0, gibt die Breite des primären Monitors zurück
        user32 = ctypes.windll.user32
        # DPI-Awareness setzen für korrekte Auflösung
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
        return user32.GetSystemMetrics(0)
    except Exception:
        return 0


def _detect_screen_width_macos():
    """
    Erkennt die Bildschirmbreite unter macOS via system_profiler.

    Returns:
        int: Bildschirmbreite in Pixeln oder 0 bei Fehler.
    """
    try:
        output = subprocess.check_output(
            ['system_profiler', 'SPDisplaysDataType'],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode('utf-8', errors='replace')

        import re
        # Suche nach "Resolution: 3840 x 2160" oder ähnlich
        match = re.search(r'Resolution:\s*(\d{3,5})\s*x\s*\d{3,5}', output)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0


def _detect_screen_width():
    """Erkennt die Bildschirmbreite plattformübergreifend."""
    if sys.platform.startswith('linux'):
        return _detect_screen_width_linux()
    elif sys.platform == 'win32':
        return _detect_screen_width_windows()
    elif sys.platform == 'darwin':
        return _detect_screen_width_macos()
    return 0


def _auto_detect_density():
    """
    Erkennt automatisch eine passende Density basierend auf der Bildschirmauflösung.

    Returns:
        float: Empfohlene Density (1.0, 1.5 oder 2.0)
    """
    width = _detect_screen_width()
    if width > 0:
        for threshold, density in _RESOLUTION_THRESHOLDS:
            if width >= threshold:
                logger.info(
                    f"desktop_scaling: Bildschirmbreite {width}px erkannt → Density {density}"
                )
                return density

    # Fallback: Standard-Density
    return DEFAULT_DENSITY


def apply_desktop_scaling():
    """
    Setzt KIVY_METRICS_DENSITY basierend auf Konfiguration oder Auto-Erkennung.

    MUSS vor allen Kivy-Imports aufgerufen werden!

    Returns:
        float: Die angewandte Density.
    """
    # Auf Android/iOS nicht eingreifen - Kivy erkennt mobile DPI korrekt
    if hasattr(sys, '_ANDROID_API') or 'ANDROID_ARGUMENT' in os.environ:
        return DEFAULT_DENSITY

    # Wenn bereits gesetzt (z.B. durch Benutzer-Env), nicht überschreiben
    if 'KIVY_METRICS_DENSITY' in os.environ:
        try:
            existing = float(os.environ['KIVY_METRICS_DENSITY'])
            logger.info(f"desktop_scaling: KIVY_METRICS_DENSITY bereits gesetzt: {existing}")
            return existing
        except ValueError:
            pass

    scale_factor = _read_scale_factor_from_config()

    if scale_factor == 'auto' or scale_factor is None:
        density = _auto_detect_density()
    else:
        density = float(scale_factor)
        # Sicherheitsgrenzen
        density = max(0.5, min(3.0, density))

    os.environ['KIVY_METRICS_DENSITY'] = str(density)
    logger.info(f"desktop_scaling: KIVY_METRICS_DENSITY gesetzt auf {density}")

    return density
