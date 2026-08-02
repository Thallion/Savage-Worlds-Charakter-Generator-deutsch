"""
Projektweite Standardwerte für Scrollbalken.

Kivys ScrollView hat als Default `bar_width = 2dp` — auf einem Smartphone
ist ein 2dp-Balken weder sichtbar noch mit dem Finger greifbar. Im Projekt
setzen zwar viele Views explizit dp(20) (mobil) bzw. dp(15) (Desktop),
aber rund 50 ScrollViews in `.py`- und `.kv`-Dateien tun das nicht und
bleiben dadurch beim 2dp-Default.

Statt jede einzelne Stelle anzufassen, wird hier der Default der
Kivy-Property angehoben. Explizit gesetzte Werte (im Konstruktor oder in
der KV-Datei) überschreiben den Default weiterhin — Views, die bewusst
einen schmalen Balken wollen (z.B. dp(6) in den Desktop-Listen), bleiben
also unverändert.

Muss vor dem Erzeugen der ersten Widgets aufgerufen werden.
"""

from kivy.metrics import dp
from kivy.logger import Logger
from kivy.uix.scrollview import ScrollView

from utils.platform_utils import is_mobile_layout

_applied = False


def apply_scrollbar_defaults():
    """Hebt den Default für bar_width/bar_margin aller ScrollViews an.

    Mobil zusätzlich `scroll_type = ['bars', 'content']`, damit der Balken
    auch gezogen werden kann — das ist der Standard, den die Mobile-KV-Dateien
    (z.B. `charakter_verwaltung_widget_mobile.kv`) bereits explizit setzen.

    Returns:
        bool: True wenn die Defaults gesetzt wurden
    """
    global _applied
    if _applied:
        return True

    try:
        mobile = is_mobile_layout()
        # MDScrollView und RecycleView erben dieselbe Property-Instanz,
        # ein Patch auf ScrollView wirkt daher für alle Varianten.
        ScrollView.bar_width.defaultvalue = dp(20) if mobile else dp(15)
        ScrollView.bar_margin.defaultvalue = dp(8) if mobile else dp(4)
        if mobile:
            ScrollView.scroll_type.defaultvalue = ['bars', 'content']
        _applied = True
        Logger.info(
            f"scrollbar_defaults: bar_width={ScrollView.bar_width.defaultvalue}px "
            f"(mobile={mobile}) als Default gesetzt"
        )
        return True
    except Exception as e:
        # Kivy-interne Änderung der Property-API — App darf davon nicht sterben
        Logger.warning(f"scrollbar_defaults: Defaults nicht gesetzt: {e}")
        return False
