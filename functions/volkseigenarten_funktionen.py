# functions/volkseigenarten_funktionen.py
"""
Volkseigenarten-Funktionen für das Volkseigenarten-Punktesystem.
Enthält Lade-, Berechnungs- und Validierungslogik für die Erstellung
und Bearbeitung von benutzerdefinierten Völkern.
"""

import json
import logging
import time as time_mod
from pathlib import Path
from kivy.logger import Logger

_config_cache = None
_config_path = None
_custom_config_cache = None
_custom_config_path = None

START_PUNKTE = 2

# Verfügbare Effekttypen für benutzerdefinierte Eigenarten
EFFEKT_TYPEN = {
    'attribut_bonus': {
        'name': 'Attributserhöhung',
        'beschreibung': 'Erhöht ein Attribut um einen Würfeltyp',
        'kategorie': 'positive',
        'optionen_typ': 'attribut_auswahl',
        'effekt_schema': {'attribut_bonus': 2}
    },
    'attribut_malus': {
        'name': 'Attributsschwäche',
        'beschreibung': 'Senkt ein Attribut um einen Würfeltyp',
        'kategorie': 'negative',
        'optionen_typ': 'attribut_auswahl',
        'effekt_schema': {'attribut_malus': 2}
    },
    'fertigkeits_bonus_grund': {
        'name': 'Grundfertigkeitsbonus',
        'beschreibung': 'Eine Grundfertigkeit startet auf W6',
        'kategorie': 'positive',
        'optionen_typ': 'grundfertigkeit_auswahl',
        'effekt_schema': {'grundfertigkeit_bonus': 2}
    },
    'fertigkeits_bonus_nicht_grund': {
        'name': 'Fertigkeitsbonus',
        'beschreibung': 'Eine Nicht-Grundfertigkeit startet auf W4+0',
        'kategorie': 'positive',
        'optionen_typ': 'nicht_grundfertigkeit_auswahl',
        'effekt_schema': {'nicht_grundfertigkeit_bonus': 2}
    },
    'robustheit_bonus': {
        'name': 'Robustheit',
        'beschreibung': '+1 Robustheit',
        'kategorie': 'positive',
        'effekt_schema': {'robustheit_bonus': 1}
    },
    'robustheit_malus': {
        'name': 'Zerbrechlich',
        'beschreibung': '-1 Robustheit',
        'kategorie': 'negative',
        'effekt_schema': {'robustheit_bonus': -1}
    },
    'bewegungsweite_bonus': {
        'name': 'Beweglichkeit',
        'beschreibung': '+1 Bewegungsweite',
        'kategorie': 'positive',
        'effekt_schema': {'bewegungsweite_bonus': 1}
    },
    'bewegungsweite_malus': {
        'name': 'Langsam',
        'beschreibung': '-1 Bewegungsweite',
        'kategorie': 'negative',
        'effekt_schema': {'bewegungsweite_bonus': -1}
    },
    'nachtsicht': {
        'name': 'Nachtsicht',
        'beschreibung': 'Ignoriert Abzüge für Düstere und Dunkle Beleuchtung',
        'kategorie': 'positive',
        'effekt_schema': {'nachtsicht': True},
        'auto_talente': ['Nachtsicht']
    },
    'fliegen': {
        'name': 'Fliegen',
        'beschreibung': 'Das Volk kann fliegen (BW anpassbar)',
        'kategorie': 'positive',
        'effekt_schema': {'fliegen': True, 'bewegungsweite_flug': 6}
    },
    'natuerliche_waffe': {
        'name': 'Natürliche Waffe',
        'beschreibung': 'Eine natürliche Waffe (Hörner, Klauen, etc.)',
        'kategorie': 'positive',
        'effekt_schema': {}
    },
    'freies_talent': {
        'name': 'Freies Talent',
        'beschreibung': 'Ein freies Anfängertalent',
        'kategorie': 'positive',
        'effekt_schema': {'freies_talent': True},
        'optionen_typ': 'talent_auswahl'
    },
    'spezieller_effekt': {
        'name': 'Sonstiger Effekt',
        'beschreibung': 'Ein benutzerdefinierter Effekt (reine Beschreibung)',
        'kategorie': 'universal',
        'effekt_schema': {}
    }
}


def stufen_kosten_bereich(eigenart):
    """
    Gibt den (min, max) Kosten-Bereich der Stufen einer Eigenart zurück.
    Liefert None wenn die Eigenart keine Stufen hat.
    """
    stufen = eigenart.get('stufen')
    if not stufen:
        return None
    kosten_werte = [s.get('kosten', 0) for s in stufen if isinstance(s, dict)]
    if not kosten_werte:
        return None
    return min(kosten_werte), max(kosten_werte)


def wende_stufe_an(eigenart, stufe):
    """
    Übernimmt die Werte einer Stufe (kosten, effekt) in die Eigenart-Instanz und
    speichert die Stufe als 'ausgewaehlte_stufe', damit Anzeige/Reload sie kennen.

    Mutiert das übergebene eigenart-Dictionary in-place.

    Args:
        eigenart: Eigenart-Dictionary (wird modifiziert)
        stufe: Dictionary mit 'kosten', 'effekt' und optionalem 'label'
    """
    if not stufe or not isinstance(stufe, dict):
        return
    eigenart['kosten'] = stufe.get('kosten', eigenart.get('kosten', 0))
    if 'effekt' in stufe:
        eigenart['effekt'] = dict(stufe['effekt'])
    eigenart['ausgewaehlte_stufe'] = dict(stufe)


def lade_volkseigenarten_config():
    """
    Lädt die Volkseigenarten-Konfiguration aus der JSON-Datei.
    Cacht die geladenen Daten für nachfolgende Aufrufe.
    
    Returns:
        dict: Dictionary mit 'positive' und 'negative' Listen
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    global _config_path
    if _config_path is None:
        _config_path = Path(__file__).parent.parent / 'config' / 'volkseigenarten_config.json'
    
    try:
        if _config_path.exists():
            with open(_config_path, 'r', encoding='utf-8') as f:
                _config_cache = json.load(f)
                Logger.info(f"Volkseigenarten-Konfiguration geladen von {_config_path}")
                return _config_cache
        else:
            Logger.error(f"Volkseigenarten-Konfigurationsdatei nicht gefunden: {_config_path}")
            return _get_default_config()
    except Exception as e:
        Logger.error(f"Fehler beim Laden der Volkseigenarten-Konfiguration: {e}")
        return _get_default_config()


def _get_default_config():
    """
    Gibt eine Standard-Konfiguration zurück (Fallback).
    
    Returns:
        dict: Minimale Standard-Konfiguration
    """
    return {
        "beschreibung": "Volkseigenarten nach Savage Worlds Punktesystem.",
        "attribute": ["Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"],
        "positive": [],
        "negative": []
    }


def berechne_punktestand(ausgewaehlte_eigenarten):
    """
    Berechnet den aktuellen Punktestand basierend auf ausgewählten Eigenarten.
    Start: 2 Punkte (für positive Eigenarten)
    Positive Eigenarten kosten Punkte, negative geben Punkte zurück.
    
    Args:
        ausgewaehlte_eigenarten: Liste von dicts mit 'id', 'kosten', optional 'optionen'
        
    Returns:
        dict: {
            'start_punkte': 2,
            'positive_kosten': int,
            'negative_punkte': int,
            'aktuelle_punkte': int (verbleibend für neue positive),
            'differenz': int (positive - negative, sollte >= 0 sein)
        }
    """
    config = lade_volkseigenarten_config()
    
    positive_kosten = 0
    negative_punkte = 0
    
    for eigenart in ausgewaehlte_eigenarten:
        kosten = eigenart.get('kosten', 0)
        if kosten > 0:
            positive_kosten += kosten
        else:
            negative_punkte += abs(kosten)
    
    differenz = positive_kosten - negative_punkte
    aktuelle_punkte = START_PUNKTE - differenz
    
    return {
        'start_punkte': START_PUNKTE,
        'positive_kosten': positive_kosten,
        'negative_punkte': negative_punkte,
        'aktuelle_punkte': max(0, aktuelle_punkte),
        'differenz': differenz,
        'ist_ausgeglichen': differenz >= 0
    }


def ist_punktestand_gueltig(ausgewaehlte_eigenarten):
    """
    Prüft ob der aktuelle Punktestand gültig ist.
    Gültig bedeutet: positive_kosten - negative_punkte <= start_punkte
    (d.h. man hat nicht mehr positive als verfügbare Punkte)
    
    Args:
        ausgewaehlte_eigenarten: Liste von ausgewählten Eigenarten
        
    Returns:
        bool: True wenn gültig
    """
    status = berechne_punktestand(ausgewaehlte_eigenarten)
    return status['ist_ausgeglichen']


def get_eigenart_by_id(eigenart_id, eigenart_typ='positive'):
    """
    Sucht eine Eigenart anhand ihrer ID (durchsucht Basis + Custom).

    Args:
        eigenart_id: Die ID der Eigenart
        eigenart_typ: 'positive' oder 'negative'

    Returns:
        dict oder None: Die Eigenart oder None wenn nicht gefunden
    """
    config = get_merged_eigenarten_config()
    eigenarten_liste = config.get(eigenart_typ, [])

    for eigenart in eigenarten_liste:
        if eigenart.get('id') == eigenart_id:
            return eigenart
    return None


def validiere_eigenart_auswahl(eigenart_id, eigenart_typ, aktuelle_auswahlen):
    """
    Prüft ob eine Eigenart noch wählbar ist.
    
    Args:
        eigenart_id: Die ID der zu prüfenden Eigenart
        eigenart_typ: 'positive' oder 'negative'
        aktuelle_auswahlen: Liste der aktuell ausgewählten Eigenarten-IDs
        
    Returns:
        dict: {
            'ist_wählbar': bool,
            'grund': str oder None,
            'max_auswahl': int,
            'aktuelle_anzahl': int
        }
    """
    eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
    
    if eigenart is None:
        return {
            'ist_wählbar': False,
            'grund': f"Eigenart '{eigenart_id}' nicht gefunden",
            'max_auswahl': 0,
            'aktuelle_anzahl': 0
        }
    
    max_auswahl = eigenart.get('max_auswahl', 1)
    aktuelle_anzahl = aktuelle_auswahlen.count(eigenart_id)
    
    if max_auswahl == 0:
        return {
            'ist_wählbar': True,
            'grund': None,
            'max_auswahl': max_auswahl,
            'aktuelle_anzahl': aktuelle_anzahl
        }
    
    if aktuelle_anzahl >= max_auswahl:
        return {
            'ist_wählbar': False,
            'grund': f"Bereits {aktuelle_anzahl}/{max_auswahl} ausgewählt",
            'max_auswahl': max_auswahl,
            'aktuelle_anzahl': aktuelle_anzahl
        }
    
    return {
        'ist_wählbar': True,
        'grund': None,
        'max_auswahl': max_auswahl,
        'aktuelle_anzahl': aktuelle_anzahl
    }


def eigenart_zu_effekte(positive_eigenarten, negative_eigenarten):
    """
    Konvertiert ausgewählte Eigenarten in das Volk.effects-Dictionary.

    Args:
        positive_eigenarten: Liste von Eigenarten mit Auswahloptionen
        negative_eigenarten: Liste von Eigenarten mit Auswahloptionen

    Returns:
        dict: Das effects-Dictionary für das Volk-Objekt
    """
    effects = {
        'eigenarten': [],
        'wahlmoeglichkeiten': {},
        'attribute_bonuses': {},
        'fertigkeits_startboni': {},
        'spezielle_effekte': [],
        'handicaps': [],
        'auto_talente': []
    }

    alle_eigenarten = []
    for e in positive_eigenarten:
        e_copy = dict(e)
        e_copy['typ'] = 'positiv'
        alle_eigenarten.append(e_copy)
    for e in negative_eigenarten:
        e_copy = dict(e)
        e_copy['typ'] = 'negativ'
        alle_eigenarten.append(e_copy)

    Logger.debug(f"[EIGENART_ZU_EFFEKTE] Start - {len(alle_eigenarten)} Eigenarten")
    for eigenart in alle_eigenarten:
        Logger.debug(f"[EIGENART_ZU_EFFEKTE] Bearbeite: {eigenart.get('id')} (effekt_typ={eigenart.get('effekt_typ')})")
        effekt_typ = eigenart.get('effekt_typ', 'spezieller_effekt')
        effekt = eigenart.get('effekt', {})
        optionen = eigenart.get('optionen', None)

        eintrag = {
            'id': eigenart.get('id'),
            'name': eigenart.get('name'),
            'typ': eigenart.get('typ'),
            'kosten': eigenart.get('kosten'),
            'beschreibung': eigenart.get('beschreibung'),
        }
        # Stufen-Auswahl persistieren, damit die Stufe nach Reload erhalten bleibt
        if eigenart.get('ausgewaehlte_stufe'):
            eintrag['ausgewaehlte_stufe'] = eigenart['ausgewaehlte_stufe']
        effects['eigenarten'].append(eintrag)
        
        if effekt_typ == 'attribut_bonus':
            attribut = None
            if optionen and optionen.get('typ') == 'attribut_auswahl':
                attribut = optionen.get('ausgewaehlt')
            if effekt.get('attribut_wahl') or (optionen and optionen.get('auswahl_verzoegert')):
                if attribut:
                    effects['wahlmoeglichkeiten']['freies_attribut'] = attribut
                else:
                    effects['wahlmoeglichkeiten']['freies_attribut'] = True
            if attribut:
                effects['attribute_bonuses'][attribut] = effekt.get('attribut_bonus', 2)

        elif effekt_typ == 'fertigkeits_bonus':
            if effekt.get('grundfertigkeit_bonus'):
                if optionen and optionen.get('typ') == 'grundfertigkeit_auswahl':
                    fertigkeit = optionen.get('ausgewaehlt')
                    if fertigkeit:
                        effects['fertigkeits_startboni'][fertigkeit] = effekt.get('grundfertigkeit_bonus', 2)
                    elif optionen.get('auswahl_verzoegert'):
                        effects['wahlmoeglichkeiten']['freie_grundfertigkeit'] = True
            elif effekt.get('nicht_grundfertigkeit_bonus'):
                if optionen and optionen.get('typ') == 'nicht_grundfertigkeit_auswahl':
                    fertigkeit = optionen.get('ausgewaehlt')
                    if fertigkeit:
                        effects['fertigkeits_startboni'][fertigkeit] = effekt.get('nicht_grundfertigkeit_bonus', 2)
                    elif optionen.get('auswahl_verzoegert'):
                        effects['wahlmoeglichkeiten']['freie_nicht_grundfertigkeit'] = True
            elif effekt.get('geschaeftssinn'):
                effects['fertigkeits_startboni']['Überzeugen/Schätzen'] = 2

        elif effekt_typ == 'wahlmoeglichkeit':
            for key, value in effekt.items():
                if key == 'freies_talent':
                    if optionen and optionen.get('auswahl_verzoegert'):
                        effects['wahlmoeglichkeiten']['freies_talent'] = True
                    else:
                        effects['wahlmoeglichkeiten']['freies_talent'] = value
        
        elif effekt_typ == 'spezieller_effekt':
            for key, value in effekt.items():
                if key in ['fliegen', 'nachtsicht', 'nachtsicht_einfach', 'untot', 'konstrukt',
                          'wasserwesen', 'baumfoermig', 'magieaffin', 'steingaenger',
                          'aussenseiter', 'abhaengigkeit', 'pazifist', 'nichtschwimmer',
                          'gesichtslos', 'niedrig', 'angeblich', 'minderwertig', 'uebergross',
                          'schwer_zu_heilen', 'leichtes_ziel', 'lahm', 'blind', 'sprachbehindert',
                          'geringe_lebenserwartung', 'kann_nicht_ertrinken', 'atmet_nicht',
                          'immun_gifte_krankheiten', 'immun_angst', 'keine_natuerliche_heilung',
                          'horn_waffe', 'klauen', 'panzerbrechend', 'giftige_beruehrung',
                          'regeneration']:
                    effects['spezielle_effekte'].append({'typ': key, 'wert': value})
                elif key in ['bewegungsweite_bonus', 'robustheit_bonus', 'bewegungsweite_flug',
                             'sozialer_malus', 'athletik_malus', 'ueberreden_malus',
                             'koerpersprache_malus', 'verstand_malus', 'erholung_malus',
                             'treffer_bonus_gegner', 'bewegung_malus', 'sicht_malus',
                             'erholungsbonus', 'erholungsbonus_angeschlagen', 'lebenserwartung_mult']:
                    if key == 'bewegungsweite_bonus':
                        effects.setdefault('bewegungsweite_bonus', 0)
                        effects['bewegungsweite_bonus'] += value
                    elif key == 'robustheit_bonus':
                        effects.setdefault('robustheit_bonus', 0)
                        effects['robustheit_bonus'] += value
                    else:
                        effects[key] = value

        elif effekt_typ == 'natuerliche_waffe':
            for key, value in effekt.items():
                if key in ['horn_waffe', 'klauen', 'panzerbrechend']:
                    effects['spezielle_effekte'].append({'typ': key, 'wert': value})
        
        elif effekt_typ == 'attribut_malus':
            attribut = None
            if optionen and optionen.get('typ') == 'attribut_auswahl':
                attribut = optionen.get('ausgewaehlt')
            if optionen and optionen.get('auswahl_verzoegert'):
                if attribut:
                    effects['wahlmoeglichkeiten']['freies_attribut_malus'] = attribut
                else:
                    effects['wahlmoeglichkeiten']['freies_attribut_malus'] = True
            if attribut:
                malus = effekt.get('attribut_malus', 2)
                effects['attribute_bonuses'][attribut] = effects['attribute_bonuses'].get(attribut, 0) - malus

        elif effekt_typ == 'robustheit_bonus':
            effects.setdefault('robustheit_bonus', 0)
            effects['robustheit_bonus'] += effekt.get('robustheit_bonus', 0)

        elif effekt_typ == 'robustheit_malus':
            effects.setdefault('robustheit_bonus', 0)
            effects['robustheit_bonus'] += effekt.get('robustheit_bonus', 0)

        elif effekt_typ == 'bewegungsweite_bonus':
            effects.setdefault('bewegungsweite_bonus', 0)
            effects['bewegungsweite_bonus'] += effekt.get('bewegungsweite_bonus', 0)

        elif effekt_typ == 'bewegungsweite_malus':
            effects.setdefault('bewegungsweite_bonus', 0)
            effects['bewegungsweite_bonus'] += effekt.get('bewegungsweite_bonus', 0)

        elif effekt_typ == 'kombinierter_effekt':
            for key, value in effekt.items():
                if key == 'bewegungsweite_bonus':
                    effects.setdefault('bewegungsweite_bonus', 0)
                    effects['bewegungsweite_bonus'] += value
                elif key == 'robustheit_bonus':
                    effects.setdefault('robustheit_bonus', 0)
                    effects['robustheit_bonus'] += value
        
        if eigenart.get('auto_talente'):
            effects['auto_talente'].extend(eigenart['auto_talente'])
        
        if eigenart.get('handicaps'):
            effects['handicaps'].extend(eigenart['handicaps'])
    
    if not effects['attribute_bonuses']:
        del effects['attribute_bonuses']
    if not effects['fertigkeits_startboni']:
        del effects['fertigkeits_startboni']
    if not effects['spezielle_effekte']:
        del effects['spezielle_effekte']
    if not effects['auto_talente']:
        del effects['auto_talente']
    if not effects['handicaps']:
        del effects['handicaps']

    Logger.debug(f"[EIGENART_ZU_EFFEKTE] Finale effects: {effects}")
    return effects


def eigenart_zu_besonderheiten(positive_eigenarten, negative_eigenarten):
    """
    Generiert die besonderheiten-Liste (Beschreibungstexte) für das Volk.
    
    Args:
        positive_eigenarten: Liste von Eigenarten
        negative_eigenarten: Liste von Eigenarten
        
    Returns:
        list: Liste von Beschreibungstexten
    """
    besonderheiten = []
    
    for eigenart in positive_eigenarten:
        text_parts = [eigenart.get('name', '')]

        # Stufen-Eigenart: zeige das Label der gewählten Stufe
        ausgewaehlte_stufe = eigenart.get('ausgewaehlte_stufe')
        if ausgewaehlte_stufe and ausgewaehlte_stufe.get('label'):
            text_parts.append(f": {ausgewaehlte_stufe['label']}")

        elif eigenart.get('effekt_typ') == 'attribut_bonus':
            optionen = eigenart.get('optionen', {})
            if optionen.get('typ') == 'attribut_auswahl':
                ausgewaehlt = optionen.get('ausgewaehlt', optionen.get('standard', 'einem Attribut'))
                text_parts.append(f": +1 auf {ausgewaehlt}")

        elif eigenart.get('effekt_typ') == 'fertigkeits_bonus':
            optionen = eigenart.get('optionen', {})
            if optionen.get('typ') == 'grundfertigkeit_auswahl':
                ausgewaehlt = optionen.get('ausgewaehlt', optionen.get('standard', 'einer Fertigkeit'))
                text_parts.append(f": W6 in {ausgewaehlt}")
            elif optionen.get('typ') == 'nicht_grundfertigkeit_auswahl':
                ausgewaehlt = optionen.get('ausgewaehlt', 'einer Fertigkeit')
                text_parts.append(f": W6 in {ausgewaehlt}")

        elif eigenart.get('effekt', {}).get('fliegen'):
            bewegung = eigenart.get('effekt', {}).get('bewegungsweite_flug', 6)
            text_parts.append(f": Flug {bewegung}\"")

        elif eigenart.get('effekt', {}).get('nachtsicht'):
            text_parts.append(": Nachtsicht")

        elif eigenart.get('effekt', {}).get('untot'):
            text_parts.append(": Untot")

        elif eigenart.get('effekt', {}).get('konstrukt'):
            text_parts.append(": Konstrukt")
        
        beschreibung = eigenart.get('beschreibung', '')
        if beschreibung:
            text_parts.append(f" ({beschreibung})")
        
        besonderheiten.append(''.join(text_parts))
    
    for eigenart in negative_eigenarten:
        text_parts = [f"[{eigenart.get('kosten')} EP] ", eigenart.get('name', '')]

        ausgewaehlte_stufe = eigenart.get('ausgewaehlte_stufe')
        if ausgewaehlte_stufe and ausgewaehlte_stufe.get('label'):
            text_parts.append(f": {ausgewaehlte_stufe['label']}")

        optionen = eigenart.get('optionen', {})
        if optionen.get('typ') == 'text_eingabe' and optionen.get('ausgewaehlt'):
            text_parts.append(f": {optionen.get('ausgewaehlt')}")

        beschreibung = eigenart.get('beschreibung', '')
        if beschreibung:
            text_parts.append(f" ({beschreibung})")

        besonderheiten.append(''.join(text_parts))
    
    return besonderheiten


def generiere_volk_name(volk_name, positive_eigenarten, negative_eigenarten):
    """
    Generiert einen angepassten Volkennamen basierend auf Eigenarten.
    Optional: Fügt Suffix hinzu (z.B. "Wald-Elf" aus "Elf" + "Waldbewohner").
    
    Args:
        volk_name: Basisname des Volkes
        positive_eigenarten: Liste positiver Eigenarten
        negative_eigenarten: Liste negativer Eigenarten
        
    Returns:
        str: Der Name (optional mit Suffix)
    """
    return volk_name


def validiere_volk_erstellung(volk_name, positive_eigenarten, negative_eigenarten):
    """
    Validiert alle Eingaben für die Völker-Erstellung.
    
    Args:
        volk_name: Name des Volkes
        positive_eigenarten: Liste positiver Eigenarten
        negative_eigenarten: Liste negativer Eigenarten
        
    Returns:
        dict: {
            'ist_gueltig': bool,
            'fehler': list von Fehlermeldungen,
            'warnungen': list von Warnungen
        }
    """
    fehler = []
    warnungen = []
    
    if not volk_name or not volk_name.strip():
        fehler.append("Volk benötigt einen Namen")
    elif len(volk_name) < 2:
        fehler.append("Volkname muss mindestens 2 Zeichen haben")
    elif len(volk_name) > 50:
        fehler.append("Volkname darf maximal 50 Zeichen haben")
    
    if not positive_eigenarten and not negative_eigenarten:
        warnungen.append("Keine Volkseigenarten ausgewählt")
    
    punktestand = berechne_punktestand(positive_eigenarten + negative_eigenarten)
    
    if not punktestand['ist_ausgeglichen']:
        fehler.append(f"Nicht genug Punkte! Positive Eigenarten kosten {punktestand['positive_kosten']} Punkte, "
                     f"aber es sind nur {START_PUNKTE} + {punktestand['negative_punkte']} = "
                     f"{START_PUNKTE + punktestand['negative_punkte']} Punkte verfügbar")

    alle_eigenarten = positive_eigenarten + negative_eigenarten

    id_counts = {}
    for e in alle_eigenarten:
        eid = e.get('id')
        if eid:
            id_counts[eid] = id_counts.get(eid, 0) + 1

    checked_ids = set()
    for eigenart in alle_eigenarten:
        eid = eigenart.get('id')
        if eid and eid not in checked_ids:
            checked_ids.add(eid)
            volle = get_eigenart_by_id(eid, 'positive') or get_eigenart_by_id(eid, 'negative')
            if volle:
                max_aus = volle.get('max_auswahl', 1)
                if max_aus != 0:
                    akt_count = id_counts.get(eid, 0)
                    if akt_count > max_aus:
                        fehler.append(f"Eigenart '{volle.get('name', eid)}' ist {akt_count}x ausgewählt, maximal {max_aus}x erlaubt")

    for eigenart in alle_eigenarten:
        if eigenart.get('stufen') and not eigenart.get('ausgewaehlte_stufe'):
            fehler.append(f"Eigenart '{eigenart.get('name')}' erfordert die Wahl einer Stufe")

        if eigenart.get('optionen'):
            optionen = eigenart['optionen']
            if optionen.get('typ') in ['attribut_auswahl', 'grundfertigkeit_auswahl',
                                       'nicht_grundfertigkeit_auswahl']:
                if not optionen.get('ausgewaehlt') and not optionen.get('auswahl_verzoegert'):
                    fehler.append(f"Eigenart '{eigenart.get('name')}' erfordert eine Auswahl")
            elif optionen.get('typ') == 'text_eingabe':
                if not optionen.get('ausgewaehlt'):
                    warnungen.append(f"Eigenart '{eigenart.get('name')}' hat keine Beschreibung")

    return {
        'ist_gueltig': len(fehler) == 0,
        'fehler': fehler,
        'warnungen': warnungen
    }


def lade_eigenarten_fuer_bearbeitung(volk_dict):
    """
    Lädt die Eigenarten aus einem gespeicherten Volk-Dictionary.
    Rekonstruiert die positive/negative Listen für den Wizard.
    
    Args:
        volk_dict: Das Dictionary des gespeicherten Volkes
        
    Returns:
        tuple: (positive_eigenarten, negative_eigenarten)
    """
    positive_eigenarten = []
    negative_eigenarten = []
    
    eigenarten = volk_dict.get('eigenarten', [])
    
    for eigenart in eigenarten:
        eigenart_typ = eigenart.get('typ', 'positiv')
        eigenart_id = eigenart.get('id')
        
        if eigenart_id:
            volle_eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
            if volle_eigenart:
                eigenart_data = dict(volle_eigenart)
            else:
                eigenart_data = {
                    'id': eigenart_id,
                    'name': eigenart.get('name', eigenart_id),
                    'kosten': eigenart.get('kosten', 2 if eigenart_typ == 'positiv' else -2),
                    'beschreibung': eigenart.get('beschreibung', ''),
                    'effekt_typ': 'spezieller_effekt',
                    'effekt': {},
                    'optionen': None
                }
        else:
            eigenart_data = {
                'id': eigenart.get('id', f"custom_{len(eigenarten)}"),
                'name': eigenart.get('name', 'Unbekannte Eigenart'),
                'kosten': eigenart.get('kosten', 2 if eigenart_typ == 'positiv' else -2),
                'beschreibung': eigenart.get('beschreibung', ''),
                'effekt_typ': 'spezieller_effekt',
                'effekt': {},
                'optionen': None
            }

        # Persistierte Stufen-Auswahl wiederherstellen (sowohl kosten als auch effekt)
        gespeicherte_stufe = eigenart.get('ausgewaehlte_stufe')
        if gespeicherte_stufe and eigenart_data.get('stufen'):
            wende_stufe_an(eigenart_data, gespeicherte_stufe)

        if eigenart_typ == 'positiv':
            positive_eigenarten.append(eigenart_data)
        else:
            negative_eigenarten.append(eigenart_data)
    
    return positive_eigenarten, negative_eigenarten


def lade_custom_eigenarten_config():
    """
    Lädt die benutzerdefinierten Volkseigenarten aus der Custom-JSON-Datei.
    Cacht die geladenen Daten für nachfolgende Aufrufe.

    Returns:
        dict: Dictionary mit 'positive' und 'negative' Listen
    """
    global _custom_config_cache

    if _custom_config_cache is not None:
        return _custom_config_cache

    global _custom_config_path
    if _custom_config_path is None:
        _custom_config_path = Path(__file__).parent.parent / 'config' / 'custom_volkseigenarten_config.json'

    try:
        if _custom_config_path.exists():
            with open(_custom_config_path, 'r', encoding='utf-8') as f:
                _custom_config_cache = json.load(f)
                Logger.info(f"Benutzerdefinierte Volkseigenarten geladen von {_custom_config_path}")
                return _custom_config_cache
        else:
            Logger.info("Keine benutzerdefinierten Volkseigenarten gefunden, leere Konfiguration erstellt")
            _custom_config_cache = {'positive': [], 'negative': []}
            return _custom_config_cache
    except Exception as e:
        Logger.error(f"Fehler beim Laden der benutzerdefinierten Volkseigenarten: {e}")
        _custom_config_cache = {'positive': [], 'negative': []}
        return _custom_config_cache


def get_merged_eigenarten_config():
    """
    Gibt die zusammengeführte Konfiguration aus Basis- und Custom-Datei zurück.

    Returns:
        dict: Dictionary mit 'positive' und 'negative' Listen (gemerged)
    """
    basis = lade_volkseigenarten_config()
    custom = lade_custom_eigenarten_config()

    merged = {
        'beschreibung': basis.get('beschreibung', ''),
        'attribute': basis.get('attribute', ['Stärke', 'Geschicklichkeit', 'Konstitution', 'Verstand', 'Willenskraft']),
        'positive': basis.get('positive', []) + custom.get('positive', []),
        'negative': basis.get('negative', []) + custom.get('negative', [])
    }
    return merged


def speichere_custom_eigenart(eigenart_data, eigenart_typ):
    """
    Speichert eine neue benutzerdefinierte Eigenart in der Custom-JSON-Datei.

    Args:
        eigenart_data: Dictionary mit den Eigenart-Daten (name, kosten, effekt_typ, etc.)
        eigenart_typ: 'positive' oder 'negative'

    Returns:
        bool: True wenn erfolgreich gespeichert
    """
    global _custom_config_cache, _custom_config_path

    if _custom_config_cache is None:
        lade_custom_eigenarten_config()
    if _custom_config_path is None:
        _custom_config_path = Path(__file__).parent.parent / 'config' / 'custom_volkseigenarten_config.json'

    if _custom_config_cache is None:
        _custom_config_cache = {'positive': [], 'negative': []}

    # Stelle sicher, dass die Eigenart eine eindeutige ID hat
    if 'id' not in eigenart_data:
        timestamp = int(time_mod.time() * 1000)
        eigenart_data['id'] = f"custom_{eigenart_typ}_{timestamp}_{len(_custom_config_cache.get(eigenart_typ, []))}"

    eigenart_data['custom'] = True

    _custom_config_cache.setdefault(eigenart_typ, []).append(eigenart_data)

    try:
        _custom_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(_custom_config_path, 'w', encoding='utf-8') as f:
            json.dump(_custom_config_cache, f, ensure_ascii=False, indent=4)
        Logger.info(f"Benutzerdefinierte Eigenart '{eigenart_data.get('name')}' gespeichert")
        return True
    except Exception as e:
        Logger.error(f"Fehler beim Speichern der benutzerdefinierten Eigenart: {e}")
        return False


def loesche_custom_eigenart(eigenart_id, eigenart_typ):
    """
    Löscht eine benutzerdefinierte Eigenart aus der Custom-JSON-Datei.

    Args:
        eigenart_id: Die ID der zu löschenden Eigenart
        eigenart_typ: 'positive' oder 'negative'

    Returns:
        bool: True wenn erfolgreich gelöscht
    """
    global _custom_config_cache, _custom_config_path

    if _custom_config_cache is None:
        lade_custom_eigenarten_config()
    if _custom_config_path is None:
        _custom_config_path = Path(__file__).parent.parent / 'config' / 'custom_volkseigenarten_config.json'

    if _custom_config_cache is None:
        return False

    liste = _custom_config_cache.get(eigenart_typ, [])
    for i, e in enumerate(liste):
        if e.get('id') == eigenart_id:
            geloescht = liste.pop(i)
            try:
                with open(_custom_config_path, 'w', encoding='utf-8') as f:
                    json.dump(_custom_config_cache, f, ensure_ascii=False, indent=4)
                Logger.info(f"Benutzerdefinierte Eigenart '{geloescht.get('name')}' gelöscht")
                return True
            except Exception as e:
                Logger.error(f"Fehler beim Löschen der benutzerdefinierten Eigenart: {e}")
                return False
    return False


def ist_eigenart_custom(eigenart_id, eigenart_typ='positive'):
    """
    Prüft ob eine Eigenart benutzerdefiniert ist.

    Args:
        eigenart_id: Die ID der Eigenart
        eigenart_typ: 'positive' oder 'negative'

    Returns:
        bool: True wenn benutzerdefiniert
    """
    # Zuerst in Basis-Konfiguration suchen
    basis = lade_volkseigenarten_config()
    for e in basis.get(eigenart_typ, []):
        if e.get('id') == eigenart_id:
            return False

    # Dann in Custom-Konfiguration
    custom = lade_custom_eigenarten_config()
    for e in custom.get(eigenart_typ, []):
        if e.get('id') == eigenart_id:
            return e.get('custom', True)
    return False


def generiere_eigenart_id(name, eigenart_typ):
    """
    Generiert eine eindeutige ID für eine neue Eigenart.

    Args:
        name: Der Name der Eigenart
        eigenart_typ: 'positive' oder 'negative'

    Returns:
        str: Eindeutige ID
    """
    timestamp = int(time_mod.time() * 1000)
    return f"custom_{eigenart_typ}_{timestamp}"


def erstelle_eigenart_dict(name, kosten, effekt_typ, beschreibung='', optionen=None,
                           effekt=None, auto_talente=None, handicaps=None, max_auswahl=1):
    """
    Erstellt ein vollständiges Eigenart-Dictionary aus den Benutzereingaben.

    Args:
        name: Name der Eigenart
        kosten: EP-Kosten (positiv für Vorteile, negativ für Nachteile)
        effekt_typ: Der Effekttyp (Schlüssel aus EFFEKT_TYPEN)
        beschreibung: Beschreibungstext
        optionen: Optionen-Dictionary oder None
        effekt: Effekt-Dictionary (überschreibt Schema)
        auto_talente: Liste automatischer Talente
        handicaps: Liste automatischer Handicaps
        max_auswahl: Maximale Auswahl

    Returns:
        dict: Vollständiges Eigenart-Dictionary
    """
    eigenart_typ = 'positive' if kosten > 0 else 'negative'

    effekt_typ_info = EFFEKT_TYPEN.get(effekt_typ, {})
    eigenart_id = generiere_eigenart_id(name, eigenart_typ)

    eigenart = {
        'id': eigenart_id,
        'name': name,
        'kosten': kosten,
        'max_auswahl': max_auswahl,
        'beschreibung': beschreibung,
        'effekt_typ': effekt_typ,
        'effekt': effekt if effekt is not None else effekt_typ_info.get('effekt_schema', {}),
        'custom': True
    }

    if optionen:
        eigenart['optionen'] = optionen
    if auto_talente:
        eigenart['auto_talente'] = auto_talente
    if handicaps:
        eigenart['handicaps'] = handicaps

    return eigenart


def formatiere_punkte_anzeige(ausgewaehlte_eigenarten):
    """
    Formatiert die Punkteanzeige für die UI.
    
    Args:
        ausgewaehlte_eigenarten: Liste von Eigenarten
        
    Returns:
        str: Formatierter String wie "4 / 2 (2 negative benötigt)"
    """
    status = berechne_punktestand(ausgewaehlte_eigenarten)
    
    if status['aktuelle_punkte'] > 0:
        if status['negative_punkte'] > 0:
            return f"{status['positive_kosten']} / {START_PUNKTE} (+{status['negative_punkte']} durch negative)"
        else:
            return f"{status['positive_kosten']} / {START_PUNKTE}"
    else:
        return f"{status['positive_kosten']} / {START_PUNKTE} + {status['negative_punkte']} = {START_PUNKTE + status['negative_punkte']}"
