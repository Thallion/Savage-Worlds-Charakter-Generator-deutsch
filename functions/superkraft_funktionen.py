# functions/superkraft_funktionen.py
"""
Kernlogik für Superkräfte-Verwaltung im Superkräfte-Kompendium.
Analog zu macht_funktionen.py, aber für das SKP-basierte Superkräfte-System.
"""
from kivy.logger import Logger
from models.superkraft import Superkraft

# Machtstufen-Daten (Defaults, werden aus Setting-JSON überschrieben)
MACHTSTUFEN_DEFAULTS = {
    "I": {"superkraftpunkte": 15, "kraftobergrenze": 5},
    "II": {"superkraftpunkte": 30, "kraftobergrenze": 10},
    "III": {"superkraftpunkte": 45, "kraftobergrenze": 15},
    "IV": {"superkraftpunkte": 60, "kraftobergrenze": 20},
    "V": {"superkraftpunkte": 75, "kraftobergrenze": 25},
}

# Settings die das Superkräfte-System verwenden
SUPERKRAEFTE_SETTINGS = ["Superkräfte Kompendium", "Superkräfte-Kompendium", "Superheroes"]


def ist_superkraefte_setting(setting_name):
    """Prüft ob das Setting das Superkräfte-System verwendet."""
    return setting_name in SUPERKRAEFTE_SETTINGS


def hat_superkraefte_talent(charakter):
    """Prüft ob der Charakter das Talent 'Superkräfte' besitzt.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        bool: True wenn das Talent vorhanden ist
    """
    selected = getattr(charakter, 'selected_talente', [])
    return "Superkräfte" in selected


def get_machtstufen_daten(charakter, stufe=None):
    """Gibt die Machtstufen-Daten zurück (aus Setting oder Defaults).

    Args:
        charakter: Das Charakterobjekt
        stufe: Optionale Machtstufe (z.B. "III"). Wenn None, wird charakter.machtstufe verwendet.

    Returns:
        dict: {"superkraftpunkte": int, "kraftobergrenze": int}
    """
    if stufe is None:
        stufe = getattr(charakter, 'machtstufe', 'III')

    # Versuche Daten aus dem Setting zu laden
    try:
        if hasattr(charakter, 'custom_element_manager'):
            setting_data = charakter.custom_element_manager.get_active_setting_data()
            if setting_data and 'machtstufen' in setting_data:
                machtstufen = setting_data['machtstufen']
                if stufe in machtstufen:
                    return {
                        'superkraftpunkte': machtstufen[stufe].get('superkraftpunkte', 0),
                        'kraftobergrenze': machtstufen[stufe].get('kraftobergrenze', 0),
                    }
    except Exception as e:
        Logger.warning(f"Fehler beim Laden der Machtstufen-Daten: {e}")

    # Fallback auf Defaults
    return MACHTSTUFEN_DEFAULTS.get(stufe, MACHTSTUFEN_DEFAULTS["III"])


def _berechne_kraftobergrenze(charakter):
    """Berechnet die Kraftobergrenze anhand Machtstufe und 'Der Beste'-Edge.

    Standard: 1/3 der maximalen SKP (aus Setting-JSON).
    Mit 'Der Beste'-Edge: 1/2 der maximalen SKP (gem. Edge-Beschreibung im Setting).

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Kraftobergrenze in SKP
    """
    stufe = getattr(charakter, 'machtstufe', 'III')
    daten = get_machtstufen_daten(charakter, stufe)
    max_skp = daten.get('superkraftpunkte', 0)
    default_og = daten.get('kraftobergrenze', 0)

    if 'Der Beste' in getattr(charakter, 'selected_talente', []):
        return max_skp // 2
    return default_og


def _aktualisiere_kraftobergrenze(charakter):
    """Aktualisiert die Kraftobergrenze. Wird als Listener auf selected_talente gebunden."""
    neuer_wert = _berechne_kraftobergrenze(charakter)
    if charakter.kraftobergrenze != neuer_wert:
        Logger.info(f"Kraftobergrenze neu berechnet: {charakter.kraftobergrenze} → {neuer_wert} SKP")
        charakter.kraftobergrenze = neuer_wert


def setze_machtstufe(charakter, stufe):
    """Setzt die Machtstufe und aktualisiert SKP-Budget und Kraftobergrenze.

    Bindet zudem einen Listener auf 'selected_talente', damit die Kraftobergrenze
    automatisch angepasst wird, sobald die 'Der Beste'-Edge hinzugefügt/entfernt wird.

    Args:
        charakter: Das Charakterobjekt
        stufe: Die Machtstufe ("I" bis "V")

    Returns:
        bool: True bei Erfolg
    """
    gueltige_stufen = ["I", "II", "III", "IV", "V"]
    if stufe not in gueltige_stufen:
        Logger.error(f"Ungültige Machtstufe: '{stufe}'. Gültig: {gueltige_stufen}")
        return False

    charakter.machtstufe = stufe
    daten = get_machtstufen_daten(charakter, stufe)
    charakter.superkraft_punkte_gesamt = daten['superkraftpunkte']
    charakter.kraftobergrenze = _berechne_kraftobergrenze(charakter)

    # Listener auf selected_talente nur einmal pro Charakter binden.
    # (Nur bei vollwertigen Kivy-Charakter-Objekten — Mocks haben kein .bind)
    if not getattr(charakter, '_superstufe_listener_aktiv', False) and callable(getattr(charakter, 'bind', None)):
        charakter.bind(selected_talente=lambda inst, val: _aktualisiere_kraftobergrenze(charakter))
        charakter._superstufe_listener_aktiv = True
        Logger.debug("Listener auf selected_talente für Kraftobergrenze gebunden")

    Logger.info(f"Machtstufe auf '{stufe}' gesetzt: {daten['superkraftpunkte']} SKP, "
                f"Kraftobergrenze {charakter.kraftobergrenze}")
    return True


def initialisiere_superkraefte(charakter, krafte_daten):
    """Initialisiert die verfügbaren Superkräfte aus Setting-Daten.

    Args:
        charakter: Das Charakterobjekt
        krafte_daten: Dict mit Superkraft-Daten aus dem Setting-JSON
    """
    charakter.superkraefte = {}

    if not krafte_daten:
        Logger.info("Keine Superkraft-Daten vorhanden")
        return

    for name, kraft_data in krafte_daten.items():
        try:
            kraft = Superkraft.from_setting_dict(kraft_data)
            charakter.superkraefte[name] = kraft
        except Exception as e:
            Logger.warning(f"Fehler beim Laden der Superkraft '{name}': {e}")

    Logger.info(f"{len(charakter.superkraefte)} Superkräfte initialisiert")


def waehle_superkraft(charakter, kraft_name, kosten=None):
    """Wählt eine Superkraft aus.

    Args:
        charakter: Das Charakterobjekt
        kraft_name: Name der Superkraft
        kosten: Gewählte Basis-SKP (bei variablen Kosten erforderlich)

    Returns:
        str oder bool:
            True bei Erfolg,
            False bei Fehler,
            "needs_kosten" wenn Kosten noch festgelegt werden müssen,
            "ueber_obergrenze" wenn die Kraftobergrenze überschritten wird,
            "nicht_genug_skp" wenn nicht genug SKP verfügbar
    """
    if kraft_name not in charakter.superkraefte:
        Logger.warning(f"Superkraft '{kraft_name}' nicht gefunden")
        return False

    kraft = charakter.superkraefte[kraft_name]

    # Wiederholbare/gestufte Kräfte (Setting-Kosten im Format "X/Stufe", z.B. Superattribut,
    # Superfertigkeit, Supertalent, Panzerung) dürfen mehrfach gewählt werden — laut Kompendium
    # ("fünfmal Superattribut auswählen → 5 Stufen in dieser Kraft"). Jede zusätzliche Stufe wird
    # einzeln gegen die Kraftobergrenze geprüft und auf die Kraft aufaddiert. So lassen sich die
    # offiziellen PL-III-Archetypen mit Einzelkräften > Obergrenze (z.B. Super Attribute 20) bauen.
    ist_wiederholbar = '/stufe' in str(kraft.basis_kosten).lower()

    if kraft.ausgewaehlt and not ist_wiederholbar:
        Logger.warning(f"Superkraft '{kraft_name}' ist bereits ausgewählt")
        return False

    # Bei variablen Kosten müssen Kosten angegeben werden
    if kraft.hat_variable_kosten() and kosten is None:
        return "needs_kosten"

    # Kosten bestimmen
    effektive_kosten = kosten if kosten is not None else kraft.get_feste_kosten()

    # Kraftobergrenze prüfen (gilt pro Stufe/Wahl, nicht für die kumulierte wiederholbare Kraft)
    if effektive_kosten > charakter.kraftobergrenze:
        Logger.warning(f"Superkraft '{kraft_name}' ({effektive_kosten} SKP) überschreitet "
                      f"Kraftobergrenze ({charakter.kraftobergrenze} SKP)")
        return "ueber_obergrenze"

    # SKP-Budget prüfen
    verbleibend = charakter.superkraft_punkte_gesamt - charakter.superkraft_punkte_verbraucht
    if effektive_kosten > verbleibend:
        Logger.warning(f"Nicht genug SKP für '{kraft_name}': braucht {effektive_kosten}, "
                      f"verfügbar {verbleibend}")
        return "nicht_genug_skp"

    # Superkraft auswählen — bei wiederholbaren Kräften eine weitere Stufe aufaddieren
    if kraft.ausgewaehlt:
        kraft.gewaehlte_kosten += effektive_kosten
    else:
        kraft.auswaehlen(kosten=effektive_kosten)
        charakter.selected_superkraefte = list(charakter.selected_superkraefte) + [kraft_name]

    # SKP aktualisieren
    _aktualisiere_skp(charakter)

    Logger.info(f"Superkraft '{kraft_name}' ausgewählt ({kraft.gesamt_kosten} SKP)")
    return True


def entferne_superkraft(charakter, kraft_name):
    """Entfernt eine ausgewählte Superkraft.

    Args:
        charakter: Das Charakterobjekt
        kraft_name: Name der Superkraft

    Returns:
        bool: True bei Erfolg
    """
    if kraft_name not in charakter.superkraefte:
        Logger.warning(f"Superkraft '{kraft_name}' nicht gefunden")
        return False

    kraft = charakter.superkraefte[kraft_name]
    if not kraft.ausgewaehlt:
        Logger.warning(f"Superkraft '{kraft_name}' ist nicht ausgewählt")
        return False

    kraft.abwaehlen()
    neue_liste = [n for n in charakter.selected_superkraefte if n != kraft_name]
    charakter.selected_superkraefte = neue_liste

    # SKP aktualisieren
    _aktualisiere_skp(charakter)

    Logger.info(f"Superkraft '{kraft_name}' entfernt")
    return True


def waehle_modifikator(charakter, kraft_name, mod_name):
    """Fügt einen Modifikator zu einer ausgewählten Superkraft hinzu.

    Args:
        charakter: Das Charakterobjekt
        kraft_name: Name der Superkraft
        mod_name: Name des Modifikators

    Returns:
        str oder bool:
            True bei Erfolg,
            False bei Fehler,
            "ueber_obergrenze" bei Überschreitung der Kraftobergrenze,
            "nicht_genug_skp" bei unzureichenden SKP
    """
    if kraft_name not in charakter.superkraefte:
        return False

    kraft = charakter.superkraefte[kraft_name]
    if not kraft.ausgewaehlt:
        Logger.warning(f"Superkraft '{kraft_name}' muss erst ausgewählt werden")
        return False

    if mod_name not in kraft.verfuegbare_modifikatoren:
        Logger.warning(f"Modifikator '{mod_name}' nicht verfügbar für '{kraft_name}'")
        return False

    # Prüfe ob Modifikator die Kraftobergrenze überschreiten würde
    mod_data = kraft.verfuegbare_modifikatoren[mod_name]
    mod_kosten = mod_data.get('kosten', 0)

    # Versuche mod_kosten als int zu interpretieren
    if isinstance(mod_kosten, str):
        try:
            mod_kosten_int = int(mod_kosten.split('/')[0].strip().lstrip('-'))
            if mod_kosten.strip().startswith('-'):
                mod_kosten_int = -mod_kosten_int
        except ValueError:
            mod_kosten_int = 0
    else:
        mod_kosten_int = int(mod_kosten)

    neue_gesamt = kraft.gesamt_kosten + mod_kosten_int

    if neue_gesamt > charakter.kraftobergrenze:
        return "ueber_obergrenze"

    # SKP-Budget prüfen (nur bei positiven Kosten)
    if mod_kosten_int > 0:
        verbleibend = charakter.superkraft_punkte_gesamt - charakter.superkraft_punkte_verbraucht
        if mod_kosten_int > verbleibend:
            return "nicht_genug_skp"

    kraft.waehle_modifikator(mod_name)

    # SKP aktualisieren
    _aktualisiere_skp(charakter)

    return True


def entferne_modifikator(charakter, kraft_name, mod_name):
    """Entfernt einen Modifikator von einer Superkraft.

    Returns:
        bool: True bei Erfolg
    """
    if kraft_name not in charakter.superkraefte:
        return False

    kraft = charakter.superkraefte[kraft_name]
    erfolg = kraft.entferne_modifikator(mod_name)
    if erfolg:
        _aktualisiere_skp(charakter)
    return erfolg


def ausgewaehlte_superkraefte(charakter):
    """Gibt eine Liste der ausgewählten Superkräfte zurück.

    Returns:
        list: Liste von Superkraft-Objekten
    """
    return [kraft for kraft in charakter.superkraefte.values() if kraft.ausgewaehlt]


def berechne_gesamt_kosten(charakter):
    """Berechnet die gesamten SKP-Kosten aller ausgewählten Superkräfte.

    Returns:
        int: Gesamtkosten in SKP
    """
    gesamt = 0
    for kraft in charakter.superkraefte.values():
        if kraft.ausgewaehlt:
            gesamt += kraft.gesamt_kosten
    return gesamt


def validiere_kraftobergrenze(charakter, kraft_name, kosten):
    """Prüft ob eine Kraft die Kraftobergrenze überschreitet.

    Args:
        charakter: Das Charakterobjekt
        kraft_name: Name der Superkraft
        kosten: Zu prüfende Kosten

    Returns:
        bool: True wenn innerhalb der Obergrenze
    """
    return kosten <= charakter.kraftobergrenze


def get_verbleibende_skp(charakter):
    """Gibt die verbleibenden SKP zurück.

    Returns:
        int: Verbleibende Superkraftpunkte
    """
    return charakter.superkraft_punkte_gesamt - charakter.superkraft_punkte_verbraucht


def _aktualisiere_skp(charakter):
    """Aktualisiert die verbrauchten SKP basierend auf ausgewählten Superkräften."""
    charakter.superkraft_punkte_verbraucht = berechne_gesamt_kosten(charakter)
