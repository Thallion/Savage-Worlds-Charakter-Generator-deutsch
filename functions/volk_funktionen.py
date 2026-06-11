# functions/volk_funktionen.py
"""
Volk-Funktionen zur Trennung von Geschäftslogik und UI — Fassade.

Die Implementierung ist nach Domänen aufgeteilt:
  functions/volk_core.py              Kern (wählen/abwählen, Status, Helfer)
  functions/volk_wahlmoeglichkeiten.py  freie Talente/Attribute/Fertigkeiten, Magieaffin
  functions/volk_zusatzelemente.py    Zusatzelemente, Multi-Slot-Reconcile
  functions/volk_specials.py          Halbelf-/Mensch-Sonderfälle

Dieses Modul re-exportiert ALLE Namen (inkl. privater Helfer und
Konstanten), damit bestehende Importe und Tests unverändert weiterlaufen.
"""

from functions.volk_core import (
    DEFAULT_TALENT_TEXT,
    DEFAULT_ATTRIBUT_TEXT,
    DEFAULT_FERTIGKEIT_TEXT,
    NO_TALENT_AVAILABLE_TEXT,
    _ARKANE_FERTIGKEIT_PATTERN,
    _VORAUSSETZUNG_WUERFEL_PATTERN,
    _BEKANNTE_ARKANE_FERTIGKEITEN,
    _AH_FERTIGKEIT_FALLBACK,
    _ist_ah_talent,
    _fertigkeit_aus_voraussetzungen,
    extrahiere_arkane_fertigkeit_aus_ah,
    NO_ATTRIBUT_AVAILABLE_TEXT,
    NO_FERTIGKEIT_AVAILABLE_TEXT,
    waehle_volk,
    _cleanup_voelker_selected,
    abwaehlen_volk,
    get_selected_volk,
    hat_volk_wahlmoeglichkeit,
    initialisiere_voelker_system,
    get_voelker_status_info,
    _get_menschen_freies_attribut,
    _set_menschen_freies_attribut,
    _reset_menschen_freies_attribut,
    _get_menschen_freies_talent,
    _set_menschen_freies_talent,
    _reset_menschen_freies_talent,
    _get_halbelf_freies_talent,
    _set_halbelf_freies_talent,
    _get_halbelf_attribut_gewaehlt,
    _set_halbelf_attribut_gewaehlt,
    _reset_halbelf_auswahlen,
    _force_eigenschaften_update,
    _force_trigger_ui_refresh,
    _get_mensch_fertigkeitspunkte_gewaehlt,
    _set_mensch_fertigkeitspunkte_gewaehlt,
    _reset_mensch_fertigkeitspunkte,
)
from functions.volk_wahlmoeglichkeiten import (
    get_freie_talente,
    get_verfuegbare_attribute,
    get_absenkbare_attribute,
    get_staerkbare_attribute,
    get_verfuegbare_fertigkeiten,
    waehle_freies_talent,
    waehle_freies_attribut,
    waehle_freies_attribut_malus,
    waehle_freie_fertigkeit,
    waehle_magieaffin_fertigkeit,
    _reset_magieaffin,
    get_magieaffin_optionen,
    get_aktuelle_magieaffin_fertigkeit,
    get_aktuelles_magieaffin_ah,
    hat_volk_magieaffin,
)
from functions.volk_zusatzelemente import (
    get_volk_attribut_optionen,
    get_volk_zusatzelemente,
    reset_volk_auswahlen,
    reconcile_volk_auswahlen,
)
from functions.volk_specials import (
    waehle_halbelf_talent,
    waehle_halbelf_attribut,
    waehle_mensch_talent,
    waehle_mensch_fertigkeitspunkte,
)
