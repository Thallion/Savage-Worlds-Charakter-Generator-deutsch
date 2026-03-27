"""
Undo-Manager für den Charakter-Generator.
Implementiert eine Snapshot-basierte Undo-Funktion für alle Charakter-Änderungen.
Speichert den kompletten Zustand vor jeder Aktion und ermöglicht das Rückgängigmachen.
"""

import copy
from kivy.logger import Logger


class UndoManager:
    """
    Verwaltet Undo-Snapshots für den Charakter.
    Speichert den Zustand vor jeder Aktion und erlaubt das Rückgängigmachen.
    """

    MAX_UNDO_SCHRITTE = 30

    def __init__(self):
        self._undo_stack = []
        self._enabled = True

    @property
    def kann_undo(self):
        """Gibt True zurück, wenn ein Undo möglich ist."""
        return len(self._undo_stack) > 0

    @property
    def undo_schritte(self):
        """Gibt die Anzahl der verfügbaren Undo-Schritte zurück."""
        return len(self._undo_stack)

    def snapshot_erstellen(self, charakter, beschreibung=""):
        """
        Erstellt einen Snapshot des aktuellen Charakter-Zustands.
        Wird vor jeder Aktion aufgerufen.

        Args:
            charakter: Das Charakter-Objekt
            beschreibung: Beschreibung der bevorstehenden Aktion
        """
        if not self._enabled:
            return

        try:
            snapshot = self._erfasse_zustand(charakter)
            snapshot['_beschreibung'] = beschreibung

            self._undo_stack.append(snapshot)

            # Stack-Größe begrenzen
            if len(self._undo_stack) > self.MAX_UNDO_SCHRITTE:
                self._undo_stack.pop(0)

            Logger.debug(f"UndoManager: Snapshot erstellt - '{beschreibung}' (Stack: {len(self._undo_stack)})")
        except Exception as e:
            Logger.error(f"UndoManager: Fehler beim Erstellen des Snapshots: {e}")

    def undo(self, charakter):
        """
        Macht die letzte Aktion rückgängig.

        Args:
            charakter: Das Charakter-Objekt

        Returns:
            str: Beschreibung der rückgängig gemachten Aktion, oder None bei Fehler
        """
        if not self._undo_stack:
            Logger.warning("UndoManager: Kein Undo verfügbar.")
            return None

        try:
            snapshot = self._undo_stack.pop()
            beschreibung = snapshot.get('_beschreibung', '')

            # Undo temporär deaktivieren, damit die Wiederherstellung keinen neuen Snapshot erstellt
            self._enabled = False
            self._stelle_zustand_wieder_her(charakter, snapshot)
            self._enabled = True

            Logger.info(f"UndoManager: Undo durchgeführt - '{beschreibung}' (Stack: {len(self._undo_stack)})")
            return beschreibung
        except Exception as e:
            self._enabled = True
            Logger.error(f"UndoManager: Fehler beim Undo: {e}")
            return None

    def leere_stack(self):
        """Leert den Undo-Stack (z.B. bei Neuladen eines Charakters)."""
        self._undo_stack.clear()
        Logger.debug("UndoManager: Stack geleert.")

    def letzte_beschreibung(self):
        """Gibt die Beschreibung der letzten rückgängig machbaren Aktion zurück."""
        if self._undo_stack:
            return self._undo_stack[-1].get('_beschreibung', '')
        return ''

    def _erfasse_zustand(self, charakter):
        """
        Erfasst den kompletten relevanten Zustand des Charakters.

        Args:
            charakter: Das Charakter-Objekt

        Returns:
            dict: Snapshot des Zustands
        """
        snapshot = {}

        # Punkte-Werte
        snapshot['verbleibende_attributsteigerungen'] = charakter.verbleibende_attributsteigerungen
        snapshot['verbleibende_fertigkeitssteigerungen'] = charakter.verbleibende_fertigkeitssteigerungen
        snapshot['maximale_attributsteigerungen'] = charakter.maximale_attributsteigerungen
        snapshot['maximale_fertigkeitssteigerungen'] = charakter.maximale_fertigkeitssteigerungen
        snapshot['verbleibende_handicap_punkte'] = charakter.verbleibende_handicap_punkte
        snapshot['gesamt_handicap_punkte'] = charakter.gesamt_handicap_punkte
        snapshot['verbleibende_aufstiege'] = charakter.verbleibende_aufstiege
        snapshot['aufstiege_gesamt'] = charakter.aufstiege_gesamt
        snapshot['char_gen_completed'] = charakter.char_gen_completed

        # Mächte und Superkräfte
        snapshot['verfuegbare_maechte'] = charakter.verfuegbare_maechte
        snapshot['anzahl_maechte'] = charakter.anzahl_maechte
        snapshot['machtpunkte'] = charakter.machtpunkte
        snapshot['superkraft_punkte_gesamt'] = charakter.superkraft_punkte_gesamt
        snapshot['superkraft_punkte_verbraucht'] = charakter.superkraft_punkte_verbraucht

        # Vermögen
        snapshot['vermoegen'] = charakter.vermoegen

        # Abgeleitete Werte
        snapshot['bewegungsweite'] = charakter.bewegungsweite
        snapshot['parade'] = charakter.parade
        snapshot['robustheit'] = charakter.robustheit
        snapshot['rang'] = charakter.rang

        # Pathfinder
        snapshot['pathfinder_kostenlose_talente_gewaehlt'] = getattr(
            charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0
        )
        snapshot['zusaetzliche_talente'] = charakter.zusaetzliche_talente

        # Attribut-Werte
        snapshot['attribute_werte'] = {}
        for name, attribut in charakter.attribute.items():
            snapshot['attribute_werte'][name] = {
                'value': attribut.wuerfel.value,
                'modifier': attribut.wuerfel.modifier
            }

        # Fertigkeiten-Werte
        snapshot['fertigkeiten_werte'] = {}
        for name, fertigkeit in charakter.fertigkeiten.items():
            snapshot['fertigkeiten_werte'][name] = {
                'value': fertigkeit.wuerfel.value,
                'modifier': fertigkeit.wuerfel.modifier
            }

        # Auswahl-Listen (Kopien)
        snapshot['selected_handicaps'] = list(charakter.selected_handicaps)
        snapshot['selected_talente'] = list(charakter.selected_talente)
        snapshot['selected_maechte'] = list(charakter.selected_maechte)
        snapshot['selected_superkraefte'] = list(charakter.selected_superkraefte)

        # Handicap-Zustände
        snapshot['handicap_zustaende'] = {}
        for name, handicap in charakter.handicaps.items():
            snapshot['handicap_zustaende'][name] = {
                'ausgewaehlt': handicap.ausgewaehlt,
                'stufe': handicap.stufe,
                'punkte': handicap.punkte,
                'auto_applied': getattr(handicap, 'auto_applied', False)
            }

        # Talent-Zustände
        snapshot['talent_zustaende'] = {}
        for name, talent in charakter.talente.items():
            snapshot['talent_zustaende'][name] = {
                'ausgewaehlt': talent.ausgewaehlt,
            }

        # Macht-Zustände
        snapshot['macht_zustaende'] = {}
        for name, macht in charakter.maechte.items():
            snapshot['macht_zustaende'][name] = {
                'ausgewaehlt': macht.ausgewaehlt,
            }

        # Superkraft-Zustände
        snapshot['superkraft_zustaende'] = {}
        for name, kraft in getattr(charakter, 'superkraefte', {}).items():
            snapshot['superkraft_zustaende'][name] = {
                'ausgewaehlt': kraft.ausgewaehlt,
                'gewaehlte_kosten': getattr(kraft, 'gewaehlte_kosten', 0),
            }

        # Völker-Auswahl
        snapshot['voelker_selected'] = dict(charakter.voelker_selected)

        return snapshot

    def _stelle_zustand_wieder_her(self, charakter, snapshot):
        """
        Stellt den Charakter-Zustand aus einem Snapshot wieder her.

        Args:
            charakter: Das Charakter-Objekt
            snapshot: Der wiederherzustellende Snapshot
        """
        # Punkte-Werte wiederherstellen
        charakter.verbleibende_attributsteigerungen = snapshot['verbleibende_attributsteigerungen']
        charakter.verbleibende_fertigkeitssteigerungen = snapshot['verbleibende_fertigkeitssteigerungen']
        charakter.maximale_attributsteigerungen = snapshot['maximale_attributsteigerungen']
        charakter.maximale_fertigkeitssteigerungen = snapshot['maximale_fertigkeitssteigerungen']
        charakter.verbleibende_handicap_punkte = snapshot['verbleibende_handicap_punkte']
        charakter.gesamt_handicap_punkte = snapshot['gesamt_handicap_punkte']
        charakter.verbleibende_aufstiege = snapshot['verbleibende_aufstiege']
        charakter.aufstiege_gesamt = snapshot['aufstiege_gesamt']
        charakter.char_gen_completed = snapshot['char_gen_completed']

        # Mächte und Superkräfte
        charakter.verfuegbare_maechte = snapshot['verfuegbare_maechte']
        charakter.anzahl_maechte = snapshot['anzahl_maechte']
        charakter.machtpunkte = snapshot['machtpunkte']
        charakter.superkraft_punkte_gesamt = snapshot['superkraft_punkte_gesamt']
        charakter.superkraft_punkte_verbraucht = snapshot['superkraft_punkte_verbraucht']

        # Vermögen
        charakter.vermoegen = snapshot['vermoegen']

        # Abgeleitete Werte
        charakter.bewegungsweite = snapshot['bewegungsweite']
        charakter.parade = snapshot['parade']
        charakter.robustheit = snapshot['robustheit']
        charakter.rang = snapshot['rang']

        # Pathfinder
        charakter.pathfinder_kostenlose_talente_gewaehlt = snapshot.get(
            'pathfinder_kostenlose_talente_gewaehlt', 0
        )
        charakter.zusaetzliche_talente = snapshot.get('zusaetzliche_talente', 0)

        # Attribut-Werte wiederherstellen
        for name, werte in snapshot.get('attribute_werte', {}).items():
            if name in charakter.attribute:
                attribut = charakter.attribute[name]
                attribut.wuerfel.value = werte['value']
                attribut.wuerfel.modifier = werte['modifier']

        # Fertigkeiten-Werte wiederherstellen
        for name, werte in snapshot.get('fertigkeiten_werte', {}).items():
            if name in charakter.fertigkeiten:
                fertigkeit = charakter.fertigkeiten[name]
                fertigkeit.wuerfel.value = werte['value']
                fertigkeit.wuerfel.modifier = werte['modifier']

        # Handicap-Zustände wiederherstellen
        for name, zustand in snapshot.get('handicap_zustaende', {}).items():
            if name in charakter.handicaps:
                handicap = charakter.handicaps[name]
                handicap.ausgewaehlt = zustand['ausgewaehlt']
                handicap.stufe = zustand['stufe']
                handicap.punkte = zustand['punkte']
                if 'auto_applied' in zustand:
                    handicap.auto_applied = zustand['auto_applied']

        # Auswahl-Listen wiederherstellen
        charakter.selected_handicaps = list(snapshot['selected_handicaps'])

        # Talent-Zustände wiederherstellen
        for name, zustand in snapshot.get('talent_zustaende', {}).items():
            if name in charakter.talente:
                charakter.talente[name].ausgewaehlt = zustand['ausgewaehlt']
        charakter.selected_talente = list(snapshot['selected_talente'])

        # Macht-Zustände wiederherstellen
        for name, zustand in snapshot.get('macht_zustaende', {}).items():
            if name in charakter.maechte:
                charakter.maechte[name].ausgewaehlt = zustand['ausgewaehlt']
        charakter.selected_maechte = list(snapshot['selected_maechte'])

        # Superkraft-Zustände wiederherstellen
        for name, zustand in snapshot.get('superkraft_zustaende', {}).items():
            if name in getattr(charakter, 'superkraefte', {}):
                kraft = charakter.superkraefte[name]
                kraft.ausgewaehlt = zustand['ausgewaehlt']
                kraft.gewaehlte_kosten = zustand.get('gewaehlte_kosten', 0)
        charakter.selected_superkraefte = list(snapshot.get('selected_superkraefte', []))

        # Völker-Auswahl
        charakter.voelker_selected = dict(snapshot.get('voelker_selected', {}))
        for name, selected in charakter.voelker_selected.items():
            if name in charakter.voelker:
                charakter.voelker[name].ausgewaehlt = selected

        # Abgeleitete Werte neu berechnen
        charakter.berechne_abgeleitete_werte()

        Logger.info("UndoManager: Zustand wiederhergestellt.")
