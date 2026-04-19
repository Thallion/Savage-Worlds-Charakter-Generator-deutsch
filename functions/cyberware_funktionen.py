# functions/cyberware_funktionen.py
"""
Kernlogik für Cyberware-Verwaltung im SciFi Kompendium.
Verwaltet Installation, Deinstallation, Stressberechnung und Validierung
von kybernetischen Implantaten.
"""
import json
import os
import uuid
from datetime import datetime
from kivy.logger import Logger
from models.cyberware import CyberwareInstallation

# Settings die das Cyberware-System verwenden
CYBERWARE_SETTINGS = ["SciFi Kompendium"]

# Konfiguration laden
_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'cyberware_config.json')
_config = {}
try:
    with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
        _config = json.load(f)
    CYBERWARE_SETTINGS = _config.get('cyberware_settings', CYBERWARE_SETTINGS)
except (FileNotFoundError, json.JSONDecodeError):
    pass

DEINSTALLATIONS_KOSTEN_FAKTOR = _config.get('deinstallations_kosten_faktor', 0.25)


def ist_cyberware_setting(setting_name):
    """Prüft ob das Setting das Cyberware-System verwendet."""
    return setting_name in CYBERWARE_SETTINGS


def _get_wuerfel_wert(charakter, attribut_name):
    """Gibt den Würfelwert eines Attributs als int zurück (z.B. W6 → 6)."""
    attribut = charakter.attribute.get(attribut_name)
    if attribut:
        return attribut.wert
    return 4  # Standard W4


def berechne_stresslimit(charakter):
    """
    Berechnet das Stresslimit des Charakters.

    Stresslimit = Hälfte des niedrigeren Würfeltyps von Willenskraft/Konstitution
                  + Talent-Boni - Handicap-Mali

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Das berechnete Stresslimit
    """
    willenskraft = _get_wuerfel_wert(charakter, 'Willenskraft')
    konstitution = _get_wuerfel_wert(charakter, 'Konstitution')
    niedrigerer_wert = min(willenskraft, konstitution)

    stresslimit = niedrigerer_wert // 2

    # Talent-Boni
    stresslimit += _get_talent_stresslimit_bonus(charakter)

    # Handicap-Mali
    stresslimit -= _get_handicap_stresslimit_malus(charakter)

    return max(0, stresslimit)


def berechne_stress_maximum(charakter):
    """
    Berechnet das harte Stress-Maximum des Charakters.

    Maximum = niedrigerer Würfeltyp von Willenskraft/Konstitution + Talent-Boni

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Das berechnete Maximum
    """
    willenskraft = _get_wuerfel_wert(charakter, 'Willenskraft')
    konstitution = _get_wuerfel_wert(charakter, 'Konstitution')
    niedrigerer_wert = min(willenskraft, konstitution)

    maximum = niedrigerer_wert

    # Talent-Boni (nur stress_maximum_bonus)
    maximum += _get_talent_stress_maximum_bonus(charakter)

    return max(0, maximum)


def berechne_stress_aktuell(charakter):
    """
    Berechnet den aktuellen Gesamtstress aller installierten Cyberware.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Der aktuelle Gesamtstress
    """
    stress_gesamt = 0
    for inst in get_installierte_cyberware(charakter):
        stress_gesamt += inst.stress
    return stress_gesamt


def _get_talent_stresslimit_bonus(charakter):
    """Berechnet den Stresslimit-Bonus aus Talenten."""
    bonus = 0
    selected = getattr(charakter, 'selected_talente', [])
    talente = getattr(charakter, 'talente', {})

    for talent_name in selected:
        if talent_name in talente:
            talent = talente[talent_name]
            effekte = {}
            if hasattr(talent, 'cyberware_effekte'):
                effekte = talent.cyberware_effekte
            elif hasattr(talent, '__getitem__'):
                try:
                    effekte = talent.get('cyberware_effekte', {})
                except (AttributeError, TypeError):
                    pass
            # Auch aus dem Rohwörterbuch versuchen
            if not effekte and hasattr(talent, '__dict__'):
                effekte = getattr(talent, 'cyberware_effekte', {})
            if not effekte:
                # Fallback: bekannte Talente direkt abfragen
                effekte = _get_bekannte_talent_effekte(talent_name)
            bonus += effekte.get('stresslimit_bonus', 0)

    return bonus


def _get_talent_stress_maximum_bonus(charakter):
    """Berechnet den Stress-Maximum-Bonus aus Talenten."""
    bonus = 0
    selected = getattr(charakter, 'selected_talente', [])
    talente = getattr(charakter, 'talente', {})

    for talent_name in selected:
        if talent_name in talente:
            talent = talente[talent_name]
            effekte = {}
            if hasattr(talent, 'cyberware_effekte'):
                effekte = talent.cyberware_effekte
            elif hasattr(talent, '__getitem__'):
                try:
                    effekte = talent.get('cyberware_effekte', {})
                except (AttributeError, TypeError):
                    pass
            if not effekte and hasattr(talent, '__dict__'):
                effekte = getattr(talent, 'cyberware_effekte', {})
            if not effekte:
                effekte = _get_bekannte_talent_effekte(talent_name)
            bonus += effekte.get('stress_maximum_bonus', 0)

    return bonus


def _get_handicap_stresslimit_malus(charakter):
    """Berechnet den Stresslimit-Malus aus Handicaps."""
    malus = 0
    selected = getattr(charakter, 'selected_handicaps', [])
    handicaps = getattr(charakter, 'handicaps', {})

    for handicap_name in selected:
        if handicap_name in handicaps:
            handicap = handicaps[handicap_name]
            effekte = {}
            if hasattr(handicap, 'cyberware_effekte'):
                effekte = handicap.cyberware_effekte
            elif hasattr(handicap, '__getitem__'):
                try:
                    effekte = handicap.get('cyberware_effekte', {})
                except (AttributeError, TypeError):
                    pass
            if not effekte and hasattr(handicap, '__dict__'):
                effekte = getattr(handicap, 'cyberware_effekte', {})
            if not effekte:
                effekte = _get_bekannte_handicap_effekte(handicap_name)
            malus += effekte.get('stresslimit_malus', 0)

    return malus


def _get_bekannte_talent_effekte(talent_name):
    """Fallback für bekannte Cyberware-Talente ohne cyberware_effekte-Attribut."""
    bekannte = {
        'Kybernetische Toleranz': {'stresslimit_bonus': 2, 'stress_maximum_bonus': 2},
        'Cyber-Samurai': {'stresslimit_bonus': 2, 'stress_maximum_bonus': 2},
        'Cyborg': {'stresslimit_bonus': 4, 'stress_maximum_bonus': 4, 'cyberware_budget': 20000},
    }
    return bekannte.get(talent_name, {})


def _get_bekannte_handicap_effekte(handicap_name):
    """Fallback für bekannte Cyberware-Handicaps ohne cyberware_effekte-Attribut."""
    bekannte = {
        'Kybernetische Abstoßung': {'stresslimit_malus': 2},
        'Kybernetische Empfindlichkeit': {'installations_malus': 2},
        'Kybernetische Nebenwirkungen': {'cyberware_budget': 10000, 'permanente_nebenwirkung': True},
    }
    return bekannte.get(handicap_name, {})


def braucht_konfiguration(cyberware_name, charakter):
    """
    Prüft ob eine Cyberware User-Input (Konfiguration) braucht.

    Args:
        cyberware_name: Name der Cyberware
        charakter: Das Charakterobjekt

    Returns:
        dict oder None: Konfigurationsinfo oder None wenn keine Auswahl nötig.
              {"typ": "attribut"|"fertigkeit"|"talent", "optionen": [...], "label": "..."}
    """
    verfuegbar = getattr(charakter, 'cyberware_verfuegbar', {})
    vorlage = verfuegbar.get(cyberware_name)
    if not vorlage:
        return None

    effekte = vorlage.effekte

    # Attributerhöhung: Dropdown mit 5 Attributen
    if effekte.get('attribut_erhoehung'):
        return {
            "typ": "attribut",
            "optionen": ["Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"],
            "label": "Attribut wählen"
        }

    # Fertigkeit wählbar: Dropdown mit Charakter-Fertigkeiten
    fertigkeit_bonus = effekte.get('fertigkeit_bonus', {})
    if isinstance(fertigkeit_bonus, dict) and fertigkeit_bonus.get('fertigkeit') == 'waehlbar':
        fertigkeiten = list(getattr(charakter, 'fertigkeiten', {}).keys())
        if fertigkeiten:
            return {
                "typ": "fertigkeit",
                "optionen": sorted(fertigkeiten),
                "label": "Fertigkeit wählen"
            }

    # Fertigkeitschip: Dropdown mit allen Fertigkeiten
    if effekte.get('fertigkeitschip'):
        fertigkeiten = list(getattr(charakter, 'fertigkeiten', {}).keys())
        if fertigkeiten:
            return {
                "typ": "fertigkeit",
                "optionen": sorted(fertigkeiten),
                "label": "Fertigkeit wählen (wird auf W6 gesetzt)"
            }

    # Kampftalent wählbar: Dropdown mit Kampftalenten
    if effekte.get('kampftalent_gewaehrt'):
        kampftalente = _get_verfuegbare_kampftalente(charakter)
        if kampftalente:
            return {
                "typ": "talent",
                "optionen": sorted(kampftalente),
                "label": "Kampftalent wählen"
            }

    return None


def _get_verfuegbare_kampftalente(charakter):
    """Gibt eine Liste verfügbarer Kampftalente zurück."""
    talente = getattr(charakter, 'talente', {})
    kampftalente = []
    for name, talent in talente.items():
        # Prüfe ob es ein Kampftalent ist
        kategorie = ""
        if hasattr(talent, 'kategorie'):
            kategorie = talent.kategorie
        elif hasattr(talent, '__getitem__'):
            try:
                kategorie = talent.get('kategorie', '')
            except (AttributeError, TypeError):
                pass
        if kategorie in ('Kampf', 'Kampftalent', 'combat'):
            # Nicht bereits gewählt
            if name not in getattr(charakter, 'selected_talente', []):
                kampftalente.append(name)
    return kampftalente


def appliziere_cyberware_effekte(charakter, installation):
    """
    Wendet die mechanischen Effekte einer Cyberware-Installation auf den Charakter an.

    Effekte die abgeleitete Werte ändern (robustheit_bonus, panzerung_bonus,
    bewegungsweite_bonus, traglast_staerke_bonus) werden nicht hier direkt gesetzt,
    sondern über Helper-Funktionen in abgeleitete_werte.py bei der nächsten
    Neuberechnung berücksichtigt.

    Hier werden nur direkte Charakter-Modifikationen durchgeführt:
    - attribut_erhoehung → Attribut-Würfeltyp erhöhen
    - fertigkeit_bonus (wählbar/fest) → Fertigkeitswert erhöhen
    - fertigkeitschip → Fertigkeit auf W6 setzen
    - talent_gewaehrt → Talent zu selected_talente hinzufügen
    - kampftalent_gewaehrt → Kampftalent zu selected_talente hinzufügen
    - athletik_bonus / wahrnehmung_bonus → Feste Fertigkeit modifizieren

    Args:
        charakter: Das Charakterobjekt
        installation: Die CyberwareInstallation mit effekte und konfiguration
    """
    effekte = installation.effekte
    konfig = installation.konfiguration

    # --- Attributerhöhung ---
    if effekte.get('attribut_erhoehung') and konfig.get('attribut'):
        attr_name = konfig['attribut']
        attribut = charakter.attribute.get(attr_name)
        if attribut:
            attribut.wuerfel.value = min(attribut.wuerfel.value + 2, 12)
            Logger.info(f"Cyberware-Effekt: {attr_name} +1 Würfeltyp (jetzt W{attribut.wuerfel.value})")

    # --- Fertigkeit-Bonus (wählbar) ---
    fertigkeit_bonus = effekte.get('fertigkeit_bonus', {})
    if isinstance(fertigkeit_bonus, dict) and fertigkeit_bonus.get('fertigkeit') == 'waehlbar':
        if konfig.get('fertigkeit'):
            fert_name = konfig['fertigkeit']
            bonus = fertigkeit_bonus.get('bonus', 1)
            _modifiziere_fertigkeit(charakter, fert_name, bonus)

    # --- Fertigkeit-Bonus (fest, z.B. Attraktiv) ---
    if isinstance(fertigkeit_bonus, dict) and 'fertigkeiten' in fertigkeit_bonus:
        feste_fertigkeiten = fertigkeit_bonus['fertigkeiten']
        bonus = fertigkeit_bonus.get('bonus', 1)
        for fert_name in feste_fertigkeiten:
            _modifiziere_fertigkeit(charakter, fert_name, bonus)

    # --- Fertigkeitschip ---
    if effekte.get('fertigkeitschip') and konfig.get('fertigkeit'):
        fert_name = konfig['fertigkeit']
        fert = charakter.fertigkeiten.get(fert_name)
        if fert:
            ziel_wert = effekte.get('fertigkeit_wert', 6)
            # Speichere den alten Zustand in der Konfiguration für Rückgängig
            installation.konfiguration = dict(installation.konfiguration)
            installation.konfiguration['alter_fertigkeit_wert'] = fert.wuerfel.value
            installation.konfiguration['alter_fertigkeit_modifier'] = fert.wuerfel.modifier
            # Modifier auf 0 setzen (W4-2 → W4) und dann auf Zielwert erhöhen
            fert.wuerfel.modifier = 0
            fert.wuerfel.value = max(fert.wuerfel.value, ziel_wert)
            Logger.info(f"Cyberware-Effekt: {fert_name} auf W{fert.wuerfel.value} gesetzt")

    # --- Talent gewährt (fest) ---
    if effekte.get('talent_gewaehrt'):
        talent_name = effekte['talent_gewaehrt']
        _fuege_talent_hinzu(charakter, talent_name)

    # --- Kampftalent gewährt (wählbar) ---
    if effekte.get('kampftalent_gewaehrt') and konfig.get('talent'):
        talent_name = konfig['talent']
        _fuege_talent_hinzu(charakter, talent_name)

    # --- Athletik-Bonus ---
    if effekte.get('athletik_bonus'):
        _modifiziere_fertigkeit(charakter, 'Athletik', effekte['athletik_bonus'])

    # --- Wahrnehmung-Bonus ---
    if effekte.get('wahrnehmung_bonus'):
        _modifiziere_fertigkeit(charakter, 'Wahrnehmung', effekte['wahrnehmung_bonus'])

    # Abgeleitete Werte neu berechnen (Robustheit, Panzerung, BW etc.)
    charakter.berechne_abgeleitete_werte()


def entferne_cyberware_effekte(charakter, installation):
    """
    Macht die mechanischen Effekte einer Cyberware-Installation rückgängig.
    Spiegelbild von appliziere_cyberware_effekte().

    Args:
        charakter: Das Charakterobjekt
        installation: Die CyberwareInstallation mit effekte und konfiguration
    """
    effekte = installation.effekte
    konfig = installation.konfiguration

    # --- Attributerhöhung rückgängig ---
    if effekte.get('attribut_erhoehung') and konfig.get('attribut'):
        attr_name = konfig['attribut']
        attribut = charakter.attribute.get(attr_name)
        if attribut:
            attribut.wuerfel.value = max(4, attribut.wuerfel.value - 2)
            Logger.info(f"Cyberware-Effekt entfernt: {attr_name} -1 Würfeltyp (jetzt W{attribut.wuerfel.value})")

    # --- Fertigkeit-Bonus (wählbar) rückgängig ---
    fertigkeit_bonus = effekte.get('fertigkeit_bonus', {})
    if isinstance(fertigkeit_bonus, dict) and fertigkeit_bonus.get('fertigkeit') == 'waehlbar':
        if konfig.get('fertigkeit'):
            fert_name = konfig['fertigkeit']
            bonus = fertigkeit_bonus.get('bonus', 1)
            _modifiziere_fertigkeit(charakter, fert_name, -bonus)

    # --- Fertigkeit-Bonus (fest) rückgängig ---
    if isinstance(fertigkeit_bonus, dict) and 'fertigkeiten' in fertigkeit_bonus:
        feste_fertigkeiten = fertigkeit_bonus['fertigkeiten']
        bonus = fertigkeit_bonus.get('bonus', 1)
        for fert_name in feste_fertigkeiten:
            _modifiziere_fertigkeit(charakter, fert_name, -bonus)

    # --- Fertigkeitschip rückgängig ---
    if effekte.get('fertigkeitschip') and konfig.get('fertigkeit'):
        fert_name = konfig['fertigkeit']
        fert = charakter.fertigkeiten.get(fert_name)
        if fert:
            alter_wert = konfig.get('alter_fertigkeit_wert', 4)
            alter_modifier = konfig.get('alter_fertigkeit_modifier', 0)
            fert.wuerfel.value = alter_wert
            fert.wuerfel.modifier = alter_modifier
            Logger.info(f"Cyberware-Effekt entfernt: {fert_name} zurück auf W{alter_wert}{alter_modifier:+d}" if alter_modifier else f"Cyberware-Effekt entfernt: {fert_name} zurück auf W{alter_wert}")

    # --- Talent gewährt (fest) rückgängig ---
    if effekte.get('talent_gewaehrt'):
        talent_name = effekte['talent_gewaehrt']
        _entferne_talent(charakter, talent_name)

    # --- Kampftalent gewährt (wählbar) rückgängig ---
    if effekte.get('kampftalent_gewaehrt') and konfig.get('talent'):
        talent_name = konfig['talent']
        _entferne_talent(charakter, talent_name)

    # --- Athletik-Bonus rückgängig ---
    if effekte.get('athletik_bonus'):
        _modifiziere_fertigkeit(charakter, 'Athletik', -effekte['athletik_bonus'])

    # --- Wahrnehmung-Bonus rückgängig ---
    if effekte.get('wahrnehmung_bonus'):
        _modifiziere_fertigkeit(charakter, 'Wahrnehmung', -effekte['wahrnehmung_bonus'])

    # Abgeleitete Werte neu berechnen
    charakter.berechne_abgeleitete_werte()


def _modifiziere_fertigkeit(charakter, fert_name, bonus):
    """
    Modifiziert den Würfelwert einer Fertigkeit um den gegebenen Bonus.
    Nutzt increase()/decrease() des Würfels, damit die W4-2 → W4 Transition
    (Modifier auf 0 setzen statt Würfeltyp erhöhen) korrekt funktioniert.
    """
    fert = charakter.fertigkeiten.get(fert_name)
    if fert:
        vorher = f"W{fert.wuerfel.value}" + (f"{fert.wuerfel.modifier:+d}" if fert.wuerfel.modifier else "")
        if bonus > 0:
            for _ in range(bonus):
                fert.wuerfel.increase()
        elif bonus < 0:
            for _ in range(abs(bonus)):
                fert.wuerfel.decrease()
        nachher = f"W{fert.wuerfel.value}" + (f"{fert.wuerfel.modifier:+d}" if fert.wuerfel.modifier else "")
        Logger.info(f"Cyberware-Effekt: {fert_name} {'+'if bonus > 0 else ''}{bonus} ({vorher} → {nachher})")
    else:
        Logger.warning(f"Cyberware-Effekt: Fertigkeit '{fert_name}' nicht gefunden")


def _fuege_talent_hinzu(charakter, talent_name):
    """Fügt ein Talent zu selected_talente hinzu."""
    selected = list(getattr(charakter, 'selected_talente', []))
    if talent_name not in selected:
        selected.append(talent_name)
        charakter.selected_talente = selected
        Logger.info(f"Cyberware-Effekt: Talent '{talent_name}' hinzugefügt")


def _entferne_talent(charakter, talent_name):
    """Entfernt ein Talent aus selected_talente."""
    selected = list(getattr(charakter, 'selected_talente', []))
    if talent_name in selected:
        selected.remove(talent_name)
        charakter.selected_talente = selected
        Logger.info(f"Cyberware-Effekt entfernt: Talent '{talent_name}'")


def initialisiere_cyberware(charakter, ausruestung_daten):
    """
    Initialisiert verfügbare Cyberware aus den Ausrüstungsdaten.
    Filtert alle Items mit kategorie == "Cyberware".

    Args:
        charakter: Das Charakterobjekt
        ausruestung_daten: Dict mit Ausrüstungsdaten aus dem Setting
    """
    charakter.cyberware_verfuegbar = {}
    for name, item_data in ausruestung_daten.items():
        if item_data.get('kategorie') == 'Cyberware':
            try:
                installation = CyberwareInstallation.from_setting_dict(item_data)
                charakter.cyberware_verfuegbar[name] = installation
            except Exception as e:
                Logger.warning(f"Fehler beim Laden von Cyberware '{name}': {e}")

    Logger.info(f"Cyberware initialisiert: {len(charakter.cyberware_verfuegbar)} Items verfügbar")


def validiere_installation(charakter, cyberware_name):
    """
    Prüft ob eine Cyberware installiert werden kann.

    Args:
        charakter: Das Charakterobjekt
        cyberware_name: Name der zu installierenden Cyberware

    Returns:
        tuple: (bool, str) - (Kann installiert werden?, Fehlermeldung oder "")
    """
    verfuegbar = getattr(charakter, 'cyberware_verfuegbar', {})
    if cyberware_name not in verfuegbar:
        return False, f"Cyberware '{cyberware_name}' nicht verfügbar"

    vorlage = verfuegbar[cyberware_name]

    # Max-Installationen prüfen
    if vorlage.max_installationen != -1:
        aktuelle_anzahl = _zaehle_installationen(charakter, cyberware_name)
        if aktuelle_anzahl >= vorlage.max_installationen:
            return False, f"Maximum von {vorlage.max_installationen} Installationen erreicht"

    # Stress-Maximum prüfen
    aktueller_stress = berechne_stress_aktuell(charakter)
    maximum = berechne_stress_maximum(charakter)
    if aktueller_stress + vorlage.stress > maximum:
        return False, f"Stress-Maximum überschritten ({aktueller_stress + vorlage.stress} > {maximum})"

    return True, ""


def installiere_cyberware(charakter, cyberware_name, konfiguration=None):
    """
    Installiert eine Cyberware beim Charakter.

    Args:
        charakter: Das Charakterobjekt
        cyberware_name: Name der zu installierenden Cyberware
        konfiguration: Optionale Konfiguration (z.B. {"attribut": "Stärke"})

    Returns:
        tuple: (bool, str) - (Erfolgreich?, Nachricht)
    """
    kann_installiert, fehler = validiere_installation(charakter, cyberware_name)
    if not kann_installiert:
        return False, fehler

    vorlage = charakter.cyberware_verfuegbar[cyberware_name]

    # Neue Installation erstellen
    installation = CyberwareInstallation(
        name=vorlage.name,
        beschreibung=vorlage.beschreibung,
        unterkategorie=vorlage.unterkategorie,
        stress=vorlage.stress,
        max_installationen=vorlage.max_installationen,
        kosten=vorlage.kosten,
        effekte=dict(vorlage.effekte),
    )
    installation.installiert = True
    installation.installations_id = str(uuid.uuid4())
    installation.installations_datum = datetime.now().strftime('%Y-%m-%d')
    if konfiguration:
        installation.konfiguration = konfiguration

    # Installation speichern
    installationen = dict(getattr(charakter, 'cyberware_installationen', {}))
    installationen[installation.installations_id] = installation
    charakter.cyberware_installationen = installationen

    # selected_cyberware aktualisieren
    selected = list(getattr(charakter, 'selected_cyberware', []))
    if cyberware_name not in selected:
        selected.append(cyberware_name)
    charakter.selected_cyberware = selected

    # Stress aktualisieren
    _aktualisiere_stress(charakter)

    # Effekte anwenden
    appliziere_cyberware_effekte(charakter, installation)

    # Nebenwirkungen prüfen
    nebenwirkungen_info = ""
    stresslimit = berechne_stresslimit(charakter)
    if charakter.cyberware_stress_aktuell > stresslimit:
        nebenwirkungen_info = " WARNUNG: Stresslimit überschritten - Nebenwirkung erforderlich!"

    Logger.info(f"Cyberware '{cyberware_name}' installiert (ID: {installation.installations_id})")
    return True, f"'{cyberware_name}' erfolgreich installiert.{nebenwirkungen_info}"


def deinstalliere_cyberware(charakter, installations_id):
    """
    Entfernt eine installierte Cyberware.

    Args:
        charakter: Das Charakterobjekt
        installations_id: Die UUID der Installation

    Returns:
        tuple: (bool, str, int) - (Erfolgreich?, Nachricht, Deinstallationskosten)
    """
    installationen = dict(getattr(charakter, 'cyberware_installationen', {}))
    if installations_id not in installationen:
        return False, f"Installation '{installations_id}' nicht gefunden", 0

    installation = installationen[installations_id]
    deinstallations_kosten = int(installation.kosten * DEINSTALLATIONS_KOSTEN_FAKTOR)

    # Effekte entfernen VOR dem Löschen der Installation
    entferne_cyberware_effekte(charakter, installation)

    name = installation.name
    del installationen[installations_id]
    charakter.cyberware_installationen = installationen

    # selected_cyberware aktualisieren
    _aktualisiere_selected_cyberware(charakter)

    # Stress aktualisieren
    _aktualisiere_stress(charakter)

    Logger.info(f"Cyberware '{name}' deinstalliert (Kosten: {deinstallations_kosten})")
    return True, f"'{name}' deinstalliert.", deinstallations_kosten


def aktiviere_cyberware(charakter, installations_id):
    """Aktiviert eine installierte Cyberware."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    if installations_id in installationen:
        installationen[installations_id].aktiv = True
        charakter.cyberware_installationen = dict(installationen)
        _aktualisiere_stress(charakter)
        return True
    return False


def deaktiviere_cyberware(charakter, installations_id):
    """Deaktiviert eine installierte Cyberware (Stress bleibt)."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    if installations_id in installationen:
        installationen[installations_id].aktiv = False
        charakter.cyberware_installationen = dict(installationen)
        return True
    return False


def get_installierte_cyberware(charakter):
    """Gibt eine Liste aller installierten Cyberware zurück."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    return [inst for inst in installationen.values() if inst.installiert]


def get_aktive_cyberware(charakter):
    """Gibt eine Liste aller aktiven (installierten + aktivierten) Cyberware zurück."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    return [inst for inst in installationen.values() if inst.installiert and inst.aktiv]


def berechne_nebenwirkungen(charakter):
    """
    Prüft ob der Charakter Nebenwirkungen durch Cyberware hat.

    Returns:
        dict: {"hat_nebenwirkungen": bool, "ueber_limit": int, "ueber_maximum": bool}
    """
    stresslimit = berechne_stresslimit(charakter)
    maximum = berechne_stress_maximum(charakter)
    aktuell = berechne_stress_aktuell(charakter)

    return {
        'hat_nebenwirkungen': aktuell > stresslimit,
        'ueber_limit': max(0, aktuell - stresslimit),
        'ueber_maximum': aktuell > maximum,
    }


def _zaehle_installationen(charakter, cyberware_name):
    """Zählt wie oft eine bestimmte Cyberware installiert ist."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    return sum(1 for inst in installationen.values()
               if inst.name == cyberware_name and inst.installiert)


def _aktualisiere_stress(charakter):
    """Aktualisiert die Stress-Werte des Charakters."""
    charakter.cyberware_stress_aktuell = berechne_stress_aktuell(charakter)
    charakter.cyberware_stresslimit = berechne_stresslimit(charakter)
    charakter.cyberware_stress_maximum = berechne_stress_maximum(charakter)


def _aktualisiere_selected_cyberware(charakter):
    """Aktualisiert die selected_cyberware-Liste basierend auf Installationen."""
    installationen = getattr(charakter, 'cyberware_installationen', {})
    namen = set()
    for inst in installationen.values():
        if inst.installiert:
            namen.add(inst.name)
    charakter.selected_cyberware = list(namen)
