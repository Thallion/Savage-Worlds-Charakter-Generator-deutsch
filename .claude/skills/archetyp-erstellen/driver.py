#driver.py
"""
Headless-Treiber für den Archetyp-Erstellen-Skill.

Zweck: Den CharakterController genauso ansteuern wie die GUI es tut – aber
ohne Fenster, schnell und reproduzierbar. Jede Aktion wird mit Vorher/Nachher-
Zustand protokolliert, damit jeder Schritt einzeln geprüft werden kann.

Wird vom Agenten (SKILL.md) interaktiv über inline-Python genutzt, z.B.:

    import sys; sys.path.insert(0, '.claude/skills/archetyp-erstellen')
    import driver as d
    sitz = d.Sitzung('Savage Pathfinder', 'Amiri', protokoll='logs/amiri.log')
    print(sitz.handicap('Jähzornig'))      # ein Schritt, prüfbarer Return
    print(sitz.attribut('Stärke'))
    sitz.diff(soll)                         # Soll/Ist-Vergleich am Ende
    sitz.speichern('chars/Archetypen/...json')

WICHTIG: Aus dem Repo-Root ausführen und headless-Umgebung setzen
(passiert hier automatisch beim Import).
"""

import os
# Headless BEVOR Kivy importiert wird:
# WICHTIG: KEIN KIVY_WINDOW=mock setzen! Der Mock-Provider erfüllt
# EventLoop.ensure_window() nicht -> kivymd.font_definitions (sp(24) beim Import)
# löst sys.exit(1) aus. Der Standard-sdl2-Provider mit SDL_VIDEODRIVER=dummy
# erzeugt dagegen ein Offscreen-Fenster und funktioniert headless.
os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ.setdefault('KIVY_NO_CONSOLELOG', '1')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import sys
import json
import time
import datetime
import traceback

# Repo-Root importierbar machen, egal von wo das Skript gestartet wird.
# driver.py liegt in <root>/.claude/skills/archetyp-erstellen/
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from controllers.charakter_controller import CharakterController
import functions.volk_funktionen as vf


# --------------------------------------------------------------------------
# Setting-Name aus Dateiname ableiten
# --------------------------------------------------------------------------
def setting_aus_dateiname(name):
    """
    Ermittelt den offiziellen Setting-Namen (= settings/<Name>.json) aus einem
    beliebigen Dateinamen, indem Unterstriche/Leerzeichen normalisiert und gegen
    die vorhandenen Settings gematcht werden. Längster Treffer gewinnt.
    """
    import glob
    basis = os.path.basename(name)
    norm = basis.replace('_', ' ').replace('-', ' ').lower()
    settings = [os.path.splitext(os.path.basename(p))[0]
                for p in glob.glob('settings/*.json')]
    treffer = [s for s in settings if s.lower() in norm]
    if not treffer:
        return None
    return max(treffer, key=len)


# --------------------------------------------------------------------------
# Zustands-Snapshot
# --------------------------------------------------------------------------
def snap(ch):
    """Liest den kompletten relevanten Charakterzustand als reines dict aus."""
    attribute = {
        name: {'wert': a.wuerfel.value, 'modifier': a.wuerfel.modifier}
        for name, a in ch.attribute.items()
    }
    fertigkeiten = {
        name: {
            'wert': f.wuerfel.value,
            'modifier': f.wuerfel.modifier,
            'grundfertigkeit': f.grundfertigkeit,
            'ausgewaehlt': getattr(f, 'ausgewaehlt', False),
        }
        for name, f in ch.fertigkeiten.items()
        # Eine Fertigkeit gilt als "auf dem Bogen", wenn sie Grundfertigkeit ist,
        # über W4 liegt ODER trainiert wurde (modifier != -2). Untrainierte
        # Nicht-Grundfertigkeiten (value 4, modifier -2 = effektiv W0) fliegen raus.
        if (f.grundfertigkeit or f.wuerfel.value > 4
            or f.wuerfel.modifier != -2 or getattr(f, 'ausgewaehlt', False))
    }
    return {
        'attribute': attribute,
        'fertigkeiten': fertigkeiten,
        'handicaps': list(ch.selected_handicaps),
        'talente': list(ch.selected_talente),
        'maechte': list(ch.selected_maechte),
        'ausruestung': {n: getattr(i, 'anzahl', 1)
                        for n, i in ch.ausruestung.items()
                        if getattr(i, 'anzahl', 0)},
        'punkte': {
            'attribut': ch.verbleibende_attributsteigerungen,
            'fertigkeit': ch.verbleibende_fertigkeitssteigerungen,
            'handicap': ch.verbleibende_handicap_punkte,
            'handicap_gesamt': ch.gesamt_handicap_punkte,
            'aufstiege': ch.verbleibende_aufstiege,
        },
        'machtpunkte': ch.machtpunkte,
        'vermoegen': ch.vermoegen,
        'rang': ch.rang,
        'volk': _volk_name(ch),
    }


def _volk_name(ch):
    """Name des gewählten Volks als String (JSON-serialisierbar)."""
    try:
        v = vf.get_selected_volk(ch)
    except Exception:
        return None
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return getattr(v, 'name', None) or getattr(v, 'volk_name', None) or str(v)


def _punkte(ch):
    return (ch.verbleibende_attributsteigerungen,
            ch.verbleibende_fertigkeitssteigerungen,
            ch.verbleibende_handicap_punkte,
            ch.vermoegen)


# --------------------------------------------------------------------------
# Sitzung: kapselt Controller + Protokoll
# --------------------------------------------------------------------------
class Sitzung:
    """Eine Archetyp-Erstellungssitzung. Jede Aktion gibt ein Ergebnis-dict
    zurück: {ok, aktion, vorher, nachher, kosten, kostenart, warnung}."""

    def __init__(self, setting, name='Archetyp', protokoll=None):
        self.setting = setting
        self.name = name
        self.protokoll_pfad = protokoll
        self.schritte = []          # alle Aktionen
        self.anomalien = []         # nur Auffälligkeiten -> Logdatei
        self.controller = CharakterController()
        self.controller.neuer_charakter(name, setting)
        self.ch = self.controller.charakter
        self._log_kopf()

    # ---- internes Protokoll -------------------------------------------------
    def _log_kopf(self):
        s = snap(self.ch)
        self.schritte.append({'aktion': f'neuer_charakter({self.name}, {self.setting})',
                              'ok': True, 'nachher_punkte': s['punkte'],
                              'vermoegen': s['vermoegen']})

    def _erfasse(self, aktion, ok, vorher, warnung=None, hart=False):
        """Erfasst eine Aktion. hart=True => immer Anomalie (z.B. Exception)."""
        a0, f0, h0, v0 = vorher
        a1, f1, h1, v1 = _punkte(self.ch)
        # Welche Punktart wurde verbraucht?
        kostenart, kosten = None, 0
        if a0 != a1:
            kostenart, kosten = 'Attributpunkte', a0 - a1
        elif f0 != f1:
            kostenart, kosten = 'Fertigkeitspunkte', f0 - f1
        elif h0 != h1:
            kostenart, kosten = 'Handicap-Punkte', h0 - h1
        elif v0 != v1:
            kostenart, kosten = 'Vermögen', v0 - v1
        eintrag = {
            'aktion': aktion, 'ok': ok,
            'kosten': kosten, 'kostenart': kostenart,
            'punkte': {'attribut': a1, 'fertigkeit': f1, 'handicap': h1},
            'vermoegen': v1, 'warnung': warnung,
        }
        self.schritte.append(eintrag)
        if warnung or hart or (not ok):
            self.anomalien.append(eintrag)
            self._schreibe_log()
        return eintrag

    def _schreibe_log(self):
        """Schreibt eine Logdatei, sobald eine Anomalie auftritt."""
        if not self.protokoll_pfad:
            return
        os.makedirs(os.path.dirname(self.protokoll_pfad) or '.', exist_ok=True)
        with open(self.protokoll_pfad, 'w', encoding='utf-8') as fh:
            fh.write(f"# Archetyp-Erstellung: {self.name} ({self.setting})\n")
            fh.write(f"# Stand: {datetime.datetime.now().isoformat(timespec='seconds')}\n")
            fh.write(f"# {len(self.anomalien)} Anomalie(n) von {len(self.schritte)} Schritten\n\n")
            fh.write("## ANOMALIEN\n")
            for e in self.anomalien:
                fh.write(f"  [!] {e['aktion']}: ok={e['ok']} "
                         f"warnung={e.get('warnung')} kosten={e['kosten']} {e['kostenart']}\n")
            fh.write("\n## ALLE SCHRITTE\n")
            for e in self.schritte:
                fh.write(f"  - {e['aktion']}: ok={e.get('ok')} "
                         f"kosten={e.get('kosten')} {e.get('kostenart') or ''} "
                         f"| Pkt={e.get('punkte')} Geld={e.get('vermoegen')}\n")

    def notiz(self, text):
        """Manuelle Notiz in die Logdatei (z.B. 'keine Ausrüstung im Setting')."""
        self.anomalien.append({'aktion': f'NOTIZ: {text}', 'ok': True,
                               'warnung': text, 'kosten': 0, 'kostenart': None,
                               'punkte': {}, 'vermoegen': self.ch.vermoegen})
        self._schreibe_log()

    def _try(self, aktion, fn, warn_wenn_false=True):
        vorher = _punkte(self.ch)
        try:
            res = fn()
            ok = bool(res) if res is not None else True
            warnung = None if (ok or not warn_wenn_false) else 'Aktion lieferte False/None'
            return self._erfasse(aktion, ok, vorher, warnung)
        except Exception as e:
            return self._erfasse(aktion, False, vorher,
                                 warnung=f'EXCEPTION: {e}\n{traceback.format_exc()}',
                                 hart=True)

    # ---- Schritt 1: Pathfinder-Klassentalent --------------------------------
    def pathfinder_klassentalent(self, talent_name, ignore_voraussetzungen=False):
        return self._try(
            f'pathfinder_klassentalent({talent_name})',
            lambda: self.controller.waehle_pathfinder_kostenloses_talent(
                talent_name, ignore_voraussetzungen=ignore_voraussetzungen))

    def ist_pathfinder(self):
        return self.controller.ist_savage_pathfinder_setting()

    # ---- Schritt 2: Handicaps ----------------------------------------------
    def handicap(self, name):
        return self._try(f'handicap({name})',
                         lambda: self.controller.waehle_handicap(name))

    # ---- Schritt 3: Volk ----------------------------------------------------
    def volk(self, name):
        return self._try(f'volk({name})', lambda: vf.waehle_volk(self.ch, name))

    # ---- Schritt 4: Volkseigenarten / freie Wahlen --------------------------
    def volk_freies_talent(self, volk, talent, ignore_voraussetzungen=False):
        return self._try(f'volk_freies_talent({volk},{talent})',
                         lambda: vf.waehle_freies_talent(self.ch, volk, talent,
                                                         ignore_voraussetzungen))

    def volk_freies_attribut(self, volk, attribut):
        return self._try(f'volk_freies_attribut({volk},{attribut})',
                         lambda: vf.waehle_freies_attribut(self.ch, volk, attribut))

    def volk_attribut_malus(self, volk, attribut):
        return self._try(f'volk_attribut_malus({volk},{attribut})',
                         lambda: vf.waehle_freies_attribut_malus(self.ch, volk, attribut))

    def volk_freie_fertigkeit(self, volk, fertigkeit):
        return self._try(f'volk_freie_fertigkeit({volk},{fertigkeit})',
                         lambda: vf.waehle_freie_fertigkeit(self.ch, volk, fertigkeit))

    def volk_magieaffin(self, volk, fertigkeit, ah_talent):
        return self._try(f'volk_magieaffin({volk},{fertigkeit},{ah_talent})',
                         lambda: vf.waehle_magieaffin_fertigkeit(self.ch, volk,
                                                                fertigkeit, ah_talent))

    def volk_wahlmoeglichkeiten(self, volk):
        """Hilfs-Inspektion: was bietet das Volk an Wahlen? (nur lesen)"""
        info = {}
        for typ in ('freies_talent', 'freies_attribut', 'freie_fertigkeit',
                    'magieaffin', 'attribut_malus'):
            try:
                info[typ] = vf.hat_volk_wahlmoeglichkeit(self.ch, volk, typ)
            except Exception:
                info[typ] = '?'
        try:
            info['attribut_optionen'] = vf.get_volk_attribut_optionen(self.ch, volk)
        except Exception:
            pass
        try:
            info['zusatzelemente'] = vf.get_volk_zusatzelemente(self.ch, volk)
        except Exception:
            pass
        return info

    # ---- Schritt 4/5: Attribute & Fertigkeiten ------------------------------
    def attribut(self, name, nur_freie_punkte=True):
        """Steigert ein Attribut. nur_freie_punkte=True bricht ab, wenn keine
        regulären Attributpunkte mehr da sind (verhindert vorzeitigen
        Handicap-Punkte-Verbrauch – siehe Schritt 9)."""
        if nur_freie_punkte and self.ch.verbleibende_attributsteigerungen <= 0:
            return self._erfasse(f'attribut({name}) ÜBERSPRUNGEN (keine Attr-Punkte)',
                                 True, _punkte(self.ch))
        return self._try(f'attribut({name})',
                         lambda: self.controller.steigere_attribut(name))

    def fertigkeit(self, name, nur_freie_punkte=True, confirm_double_cost=True):
        if nur_freie_punkte and self.ch.verbleibende_fertigkeitssteigerungen <= 0:
            return self._erfasse(f'fertigkeit({name}) ÜBERSPRUNGEN (keine Fert-Punkte)',
                                 True, _punkte(self.ch))
        return self._try(f'fertigkeit({name})',
                         lambda: self.controller.steigere_fertigkeit(
                             name, confirm_double_cost=confirm_double_cost))

    def _fortschritt(self, w):
        """Fortschritts-Signatur eines Würfels + Restpunkte. Erkennt auch die
        Aktivierung einer untrainierten Fertigkeit (modifier -2 -> 0 bei
        gleichbleibendem value) als Fortschritt."""
        return (w.value, w.modifier, _punkte(self.ch))

    def attribut_auf(self, name, zielwert, **kw):
        """Steigert ein Attribut bis zum Zielwürfel (4/6/8/10/12)."""
        ergebnisse = []
        while self.ch.attribute[name].wuerfel.value < zielwert:
            vor = self._fortschritt(self.ch.attribute[name].wuerfel)
            r = self.attribut(name, **kw)
            ergebnisse.append(r)
            if self._fortschritt(self.ch.attribute[name].wuerfel) == vor:
                break  # kein Fortschritt -> Endlosschleife vermeiden
        return ergebnisse

    def fertigkeit_auf(self, name, zielwert, **kw):
        """Steigert eine Fertigkeit bis zum Zielwürfel. Beachtet, dass die erste
        Steigerung einer untrainierten Fertigkeit nur den -2-Modifier entfernt
        (value bleibt 4) – das zählt als Fortschritt."""
        ergebnisse = []
        w = self.ch.fertigkeiten[name].wuerfel
        # Weiter steigern, solange der Würfel unter dem Ziel liegt ODER die
        # Fertigkeit noch untrainiert ist (modifier < 0 = d4-2). So wird auch
        # eine Nicht-Grundfertigkeit mit Ziel W4 zunächst aktiviert.
        while w.value < zielwert or w.modifier < 0:
            vor = self._fortschritt(w)
            r = self.fertigkeit(name, **kw)
            ergebnisse.append(r)
            if self._fortschritt(w) == vor:
                break
        return ergebnisse

    def fertigkeit_auf_mit_attr_steigerung(self, name, zielwert, attr_name=None):
        """Steigert eine Fertigkeit und erhöht vorher das Attribut wenn nötig,
        um Doppelkosten zu vermeiden. Nutzt Attributpunkte + Handicap-Punkte
        für die Attributsteigerung."""
        ergebnisse = []
        fert = self.ch.fertigkeiten.get(name)
        if not fert:
            return ergebnisse

        if attr_name is None:
            attr_name = fert.attribut

        attr = self.ch.attribute.get(attr_name)
        if not attr:
            return ergebnisse

        # Solange Fertigkeit über Attributniveau steigen würde -> Attribut zuerst
        while True:
            fert_w = fert.wuerfel
            attr_w = attr.wuerfel
            fert_eff = fert_w.value + fert_w.modifier
            attr_eff = attr_w.value + attr_w.modifier

            if fert_eff >= attr_eff and attr_w.value < 12:
                # Zuerst Attr-Punkte versuchen, dann HC-Punkte
                if self.ch.verbleibende_attributsteigerungen > 0:
                    vor = self._fortschritt(attr_w)
                    r = self.attribut(attr_name)
                    ergebnisse.append(r)
                    if self._fortschritt(attr_w) == vor:
                        break
                    continue
                elif self.ch.verbleibende_handicap_punkte >= 1:
                    vor = self._fortschritt(attr_w)
                    r = self.steigere_mit_handicap_attribut(attr_name)
                    ergebnisse.append(r)
                    if self._fortschritt(attr_w) == vor:
                        break
                    continue
            break

        w = fert.wuerfel
        while w.value < zielwert or w.modifier < 0:
            vor = self._fortschritt(w)
            r = self.fertigkeit(name, confirm_double_cost=True)
            ergebnisse.append(r)
            if self._fortschritt(w) == vor:
                break
        return ergebnisse

    # ---- Schritt 6: Talente -------------------------------------------------
    def talent(self, name, ignore_rang_check=False, ignore_voraussetzungen=False):
        r = self._try(
            f'talent({name})',
            lambda: self.controller.waehle_talent(
                name, ignore_rang_check=ignore_rang_check,
                ignore_voraussetzungen=ignore_voraussetzungen),
            warn_wenn_false=True)
        return r

    # ---- Schritt 7: Mächte --------------------------------------------------
    def macht(self, name, ignore_rang_check=False):
        return self._try(f'macht({name})',
                         lambda: self.controller.waehle_macht(
                             name, ignore_rang_check=ignore_rang_check))

    # ---- Schritt 8: Ausrüstung ---------------------------------------------
    def kaufen(self, name, anzahl=1, force_bei_geldmangel=True):
        """Kauft Ausrüstung. Bei Geldmangel und force=True wird vermoegen=0
        gesetzt und der Rest zum Preis 0 gekauft (Wunsch des Users)."""
        vorher = _punkte(self.ch)
        ok = self.controller.kaufen_ausruestung(name, anzahl=anzahl)
        if not ok and force_bei_geldmangel:
            self.ch.vermoegen = 0
            time.sleep(0.6)  # Android-Double-Touch-Schutz (500ms) umgehen
            ok = self.controller.kaufen_ausruestung(name, anzahl=anzahl,
                                                    preis_pro_stueck=0)
            warn = f'Geld reichte nicht – auf 0 gesetzt und {name} zum Preis 0 gekauft'
            return self._erfasse(f'kaufen({name}x{anzahl}) FORCE', ok, vorher, warn)
        warn = None if ok else 'Kauf fehlgeschlagen'
        return self._erfasse(f'kaufen({name}x{anzahl})', ok, vorher, warn)

    # ---- Schritt 9: Handicap-Punkte zum Steigern / Startkapital ------------
    def steigere_mit_handicap_attribut(self, name):
        """Steigert ein Attribut bewusst mit Handicap-Punkten (Attr-Punkte = 0)."""
        return self._try(f'attribut_mit_hc({name})',
                         lambda: self.controller.steigere_attribut(name))

    def steigere_mit_handicap_fertigkeit(self, name, confirm_double_cost=True):
        return self._try(f'fertigkeit_mit_hc({name})',
                         lambda: self.controller.steigere_fertigkeit(
                             name, confirm_double_cost=confirm_double_cost))

    def startkapital_mit_handicap(self):
        return self._try('startkapital_mit_handicap',
                         lambda: self.controller.erhoehe_startkapital_mit_handicap())

    # ---- Inspektion / Vergleich / Speichern --------------------------------
    def zustand(self):
        return snap(self.ch)

    def zeige_auto_eintraege(self, vor_snap):
        """Vergleicht den aktuellen Zustand mit einem früheren Snapshot und gibt
        zurück, was neu hinzukam (Talente, Handicaps, Mächte). Nützlich nach
        pathfinder_klassentalent(), volk() oder talent('AH ...') um Auto-Einträge
        für das SOLL-Dict zu ermitteln.

        Beispiel:
            vor = s.zustand()
            s.pathfinder_klassentalent('Mönch', ignore_voraussetzungen=True)
            m(str(s.zeige_auto_eintraege(vor)))
            # → {'talente_neu': ['Waffenloser Schlag', ...], 'handicaps_neu': ['Rüstungsbeschränkung_jede']}
        """
        jetzt = snap(self.ch)
        return {
            'talente_neu':   [t for t in jetzt['talente']   if t not in vor_snap.get('talente', [])],
            'handicaps_neu': [h for h in jetzt['handicaps'] if h not in vor_snap.get('handicaps', [])],
            'maechte_neu':   [m for m in jetzt['maechte']   if m not in vor_snap.get('maechte', [])],
        }

    def punktestand(self):
        s = snap(self.ch)
        return {**s['punkte'], 'vermoegen': s['vermoegen'], 'machtpunkte': s['machtpunkte']}

    def historie(self, limit=200):
        """Liest die Event-Historie (das was der Historie-View anzeigt)."""
        try:
            from services.service_container import service_container
            es = service_container.get_event_service()
            return [(e.event_type, e.data) for e in es.get_event_history(limit=limit)]
        except Exception as e:
            return [('FEHLER', str(e))]

    def diff(self, soll):
        """Vergleicht den Ist-Zustand mit den Soll-Werten aus dem Screenshot.
        soll = {'attribute': {...}, 'fertigkeiten': {...}, 'handicaps': [...],
                'talente': [...], 'maechte': [...]}"""
        ist = snap(self.ch)
        ab = []

        def vgl_dict_wert(kat, sollmap):
            for k, v in (sollmap or {}).items():
                istwert = ist[kat].get(k, {}).get('wert')
                if istwert != v:
                    ab.append(f'{kat}: {k} soll W{v}, ist {("W"+str(istwert)) if istwert else "FEHLT"}')

        def vgl_liste(kat, sollliste):
            istset = set(ist[kat])
            for x in (sollliste or []):
                if x not in istset and not any(x in y or y in x for y in istset):
                    ab.append(f'{kat}: "{x}" FEHLT')
            for y in istset:
                if y not in set(sollliste or []) and not any(y in x or x in y for x in (sollliste or [])):
                    ab.append(f'{kat}: "{y}" ZUVIEL')

        vgl_dict_wert('attribute', soll.get('attribute'))
        vgl_dict_wert('fertigkeiten', soll.get('fertigkeiten'))
        vgl_liste('handicaps', soll.get('handicaps'))
        vgl_liste('talente', soll.get('talente'))
        vgl_liste('maechte', soll.get('maechte'))

        ergebnis = {
            'abweichungen': ab,
            'restpunkte': ist['punkte'],
            'vermoegen': ist['vermoegen'],
        }
        if ab:
            self.anomalien.append({'aktion': 'SOLL/IST-DIFF', 'ok': False,
                                   'warnung': '; '.join(ab), 'kosten': 0,
                                   'kostenart': None, 'punkte': ist['punkte'],
                                   'vermoegen': ist['vermoegen']})
            self._schreibe_log()
        return ergebnis

    def speichern(self, pfad):
        os.makedirs(os.path.dirname(pfad) or '.', exist_ok=True)
        ok = self.controller.speichere_charakter_als_json(pfad)
        self.schritte.append({'aktion': f'speichern({pfad})', 'ok': bool(ok)})
        return ok

    def bericht(self, pfad=None):
        """Schreibt einen sauberen JSON-Gesamtbericht (für den Read-Tool-Konsum).
        Enthält alle Schritte, Anomalien und Endzustand. Gibt das dict zurück."""
        b = {
            'name': self.name,
            'setting': self.setting,
            'schritte': self.schritte,
            'anomalien': self.anomalien,
            'anomalien_anzahl': len(self.anomalien),
            'endzustand': snap(self.ch),
        }
        if pfad:
            os.makedirs(os.path.dirname(pfad) or '.', exist_ok=True)
            with open(pfad, 'w', encoding='utf-8') as fh:
                json.dump(b, fh, ensure_ascii=False, indent=2)
        return b

    # ---- CharGen-Abschluss: Aufstiege für D-Advances ----
    def abschliessen(self, n_aufstiege=4):
        """Schließt CharGen ab und gibt dem Charakter n Aufstiege (Rang Fortgeschritten = 4).
        Die verbleibenden Aufstiege bleiben verfügbar für D-Advances.
        """
        self.ch.char_gen_completed = True
        for _ in range(n_aufstiege):
            from functions.character_advancement import increase_aufstiege
            increase_aufstiege(self.ch)
        return {
            'ok': True,
            'aktion': f'abschliessen(n={n_aufstiege})',
            'rang': self.ch.rang,
            'aufstiege_gesamt': self.ch.aufstiege_gesamt,
            'verbleibende_aufstiege': self.ch.verbleibende_aufstiege,
        }

    def talent_mit_aufstieg(self, name, ignore_voraussetzungen=True):
        """Wählt ein Talent mit einem Aufstieg (D-Advance nach CharGen)."""
        return self._try(
            f'talent_mit_aufstieg({name})',
            lambda: self.controller.waehle_talent(
                name, ignore_rang_check=True,
                ignore_voraussetzungen=ignore_voraussetzungen))

    def fertigkeit_mit_aufstieg(self, name, zielwert=None):
        """Steigert eine Fertigkeit mit Aufstieg (D-Advance nach CharGen).
        Wenn zielwert angegeben ist, wird bis zum Zielwert gesteigert.
        confirm_double_cost=True ist Default, weil D-Advances das Überschreiten
        des verknüpften Attributs explizit erlauben."""
        ergebnisse = []
        if zielwert:
            w = self.ch.fertigkeiten[name].wuerfel
            while w.value < zielwert or w.modifier < 0:
                vor = self._fortschritt(w)
                r = self._try(f'fertigkeit_mit_aufstieg({name})',
                             lambda: self.controller.steigere_fertigkeit(name, confirm_double_cost=True))
                ergebnisse.append(r)
                if self._fortschritt(w) == vor:
                    break
        else:
            r = self._try(f'fertigkeit_mit_aufstieg({name})',
                         lambda: self.controller.steigere_fertigkeit(name, confirm_double_cost=True))
            ergebnisse.append(r)
        return ergebnisse

    def charakter_mit_aufstieg(self, name, zielwert):
        """Steigert ein Attribut mit Aufstieg (D-Advance nach CharGen)."""
        ergebnisse = []
        while self.ch.attribute[name].wuerfel.value < zielwert:
            vor = self._fortschritt(self.ch.attribute[name].wuerfel)
            r = self._try(f'attribut_mit_aufstieg({name})',
                         lambda: self.controller.steigere_attribut(name))
            ergebnisse.append(r)
            if self._fortschritt(self.ch.attribute[name].wuerfel) == vor:
                break
        return ergebnisse
