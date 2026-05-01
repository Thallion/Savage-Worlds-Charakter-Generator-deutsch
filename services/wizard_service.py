# services/wizard_service.py
"""
Wizard-Service für geführte Charaktererstellung.
Verwaltet den Zustand und die Schritte des Charakter-Erstellungs-Assistenten.
"""

import logging
from typing import Optional, Callable, List, Dict, Any
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ListProperty
from kivy.logger import Logger


class WizardSchritt:
    """Ein einzelner Schritt im Wizard."""
    
    def __init__(self, tab_id: str, tab_name: str, title: str, description: str,
                 popup_title: str = "", popup_text: str = "",
                 is_required: bool = True, validator: Optional[Callable] = None):
        self.tab_id = tab_id
        self.tab_name = tab_name
        self.title = title
        self.description = description
        self.popup_title = popup_title
        self.popup_text = popup_text
        self.is_required = is_required
        self.validator = validator or (lambda charakter: True)
    
    def validate(self, charakter) -> tuple[bool, str]:
        """
        Validiert den Schritt.
        
        Returns:
            Tuple aus (is_valid, error_message)
        """
        try:
            if self.validator(charakter):
                return (True, "")
            return (False, "Validierung fehlgeschlagen")
        except Exception as e:
            Logger.error(f"Validierungsfehler bei Schritt '{self.tab_id}': {e}")
            return (False, str(e))


class WizardService(EventDispatcher):
    """
    Service für den geführten Charakter-Erstellungs-Assistenten.
    
    Führt den Benutzer Schritt für Schritt durch die Charaktererstellung.
    """
    
    aktiv = BooleanProperty(False)
    aktueller_schritt_index = NumericProperty(0)
    schritte: List[WizardSchritt] = ListProperty([])
    
    def __init__(self, charakter_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.charakter_controller = charakter_controller
        self._callbacks: Dict[str, List[Callable]] = {
            'on_wizard_started': [],
            'on_wizard_finished': [],
            'on_wizard_cancelled': [],
            'on_step_changed': [],
            'on_step_validated': [],
        }
        self._initialize_schritte()
    
    def _initialize_schritte(self):
        """Initialisiert die Wizard-Schritte."""
        self.schritte = [
            WizardSchritt(
                tab_id='neuer_charakter',
                tab_name='Neuer Charakter',
                title='Neuen Charakter erstellen',
                description='Gib deinem Charakter einen Namen und wähle ein Setting.\n\nEin Setting bestimmt die verfügbaren Abstammungen, Talente und Regeln.',
                popup_title='Charakter erstellen',
                popup_text='Große Helden sind mehr als nur eine Ansammlung von Werten und Zahlen, doch hier nehmen sie ihren Anfang.\n\nVeröffentlichte Settings enthalten oft vorgefertigte Archetypen als Inspiration. Du kannst sie so spielen oder eigene Ideen entwickeln.\n\nSchau dir den Spielerabschnitt deines Settings an oder sprich mit der Spielleitung, um zu sehen, welche Art von Charakter dich interessiert.',
                is_required=True,
                validator=self._validate_neuer_charakter
            ),
            WizardSchritt(
                tab_id='voelker',
                tab_name='Abstammungen',
                title='Abstammung auswählen',
                description='Wähle die Abstammung deines Charakters.\n\nJede Abstammung hat besondere Fähigkeiten und Boni.',
                popup_title='Abstammung wählen',
                popup_text='Settings können alles von Menschen bis zu seltsamen Aliens, anmutigen Elfen oder anderen exotischen Abstammungen enthalten. Du kannst jede Abstammung spielen, die in deinem Setting verfügbar ist.\n\nJede Abstammung bringt besondere Fähigkeiten mit – einige erhöhen Attribute, andere geben spezielle Fertigkeiten oder Vorteile.\n\nDie Boni werden automatisch verrechnet.',
                is_required=True,
                validator=self._validate_volk
            ),
            WizardSchritt(
                tab_id='profil',
                tab_name='Profil',
                title='Profil ausfüllen',
                description='Gib deinem Charakter ein Konzept und weitere Details.',
                popup_title='Konzept & Hintergrund',
                popup_text='Verleihe deinem Charakter den letzten Schliff, indem du dir Gedanken über seine Vergangenheit und seinen Hintergrund machst.\n\nStell dir die Frage, warum er ist, wo er ist, und was seine Ziele sind. Wo lebt er? Hat er enge Freunde oder Familie?\n\nOder beginne einfach zu spielen und trage diese Details nach, wenn sie wichtig werden.',
                is_required=False,
                validator=lambda c: True
            ),
            WizardSchritt(
                tab_id='eigenschaften',
                tab_name='Eigenschaften',
                title='Attribute & Fertigkeiten',
                description='Verteile 5 Attributpunkte und 12 Fertigkeitspunkte.',
                popup_title='Eigenschaften – Attribute & Fertigkeiten',
                popup_text='Attribute:\nJeder Charakter beginnt mit W4 in allen fünf Attributen: Geschicklichkeit, Konstitution, Stärke, Verstand und Willenskraft.\n\nDu bekommst 5 Punkte, um deine Attribute zu erhöhen. Es kostet 1 Punkt, einen W4 auf W6 anzuheben. Kein Attribut darf über W12 angehoben werden (außer bei besonderen Abstammungseigenarten).\n\nFertigkeiten:\nFünf Grundfertigkeiten starten mit W4: Athletik, Allgemeinwissen, Heimlichkeit, Überreden und Wahrnehmung.\n\nDu hast 12 Punkte, um Fertigkeiten zu kaufen oder zu erhöhen. Jeder Würfeltyp kostet 1 Punkt, solange die Fertigkeit gleich oder niedriger als das verknüpfte Attribut ist. Steigt die Fertigkeit über das Attribut, kosten weitere Stufen 2 Punkte pro Stufe.\n\nFertigkeiten dürfen während der Charaktererschaffung nicht über W12 angehoben werden.',
                is_required=True,
                validator=self._validate_eigenschaften
            ),
            WizardSchritt(
                tab_id='handicaps',
                tab_name='Handicaps',
                title='Handicaps wählen',
                description='Wähle Handicaps für bis zu 4 Bonuspunkte.',
                popup_title='Handicaps – Nachteile deines Helden',
                popup_text='Handicaps sind Nachteile, Schwächen oder dunkle Geheimnisse aus der Hintergrundgeschichte eines Charakters.\n\nDu kannst bis zu 4 Punkte an Handicaps auswählen:\n• Schweres Handicap = 2 Punkte\n• Leichtes Handicap = 1 Punkt\n\nFür 2 Punkte kannst du:\n• ein Attribut um einen Würfeltyp verbessern, oder\n• ein Talent auswählen\n\nFür 1 Punkt kannst du:\n• einen zusätzlichen Fertigkeitspunkt erhalten, oder\n• zusätzliches Startvermögen (doppeltes Startvermögen des Settings) erhalten\n\nHandicaps müssen zum Charakter passen und ausgespielt werden!',
                is_required=False,
                validator=lambda c: True
            ),
            WizardSchritt(
                tab_id='talente',
                tab_name='Talente',
                title='Talente wählen',
                description='Wähle Talente für deinen Charakter.\n\nJeder Charakter startet mit 1 kostenlosen Talent.',
                popup_title='Talente – Besondere Fähigkeiten',
                popup_text='Attribute und Fertigkeiten sind die grundlegenden Werte, aber was Individuen wirklich voneinander unterscheidet, sind ihre Talente.\n\nSelbst zwei Charaktere mit identischen Eigenschaften können im Spiel ganz anders sein, abhängig davon, welche Talente sie auswählen.\n\nCharaktere können Talente erhalten durch:\n• Handicaps (2 Punkte = 1 Talent)\n• Abstammungseigenarten\n• Aufstiege (wenn das Spiel beginnt)\n\nAchte auf die Voraussetzungen – viele Talente benötigen bestimmte Attribute, Fertigkeiten oder Ränge.',
                is_required=False,
                validator=lambda c: True
            ),
            WizardSchritt(
                tab_id='maechte',
                tab_name='Mächte',
                title='Arkane Mächte',
                description='Wähle arkane Mächte (nur mit Arkanem Hintergrund).',
                popup_title='Arkane Mächte',
                popup_text='Arkane Mächte stehen nur Charakteren mit dem Talent "Arkaner Hintergrund" zur Verfügung.\n\nJede Macht kostet Machtpunkte. Die verfügbaren Mächte hängen vom gewählten Arkanen Hintergrund ab (z.B. Magie, Wunder, Psionik).\n\nOhne Arkanen Hintergrund kannst du diesen Schritt überspringen.',
                is_required=False,
                validator=lambda c: True
            ),
            WizardSchritt(
                tab_id='ausruestung',
                tab_name='Ausrüstung',
                title='Ausrüstung kaufen',
                description='Kaufe Waffen, Rüstung und Ausrüstung mit deinem Startkapital.',
                popup_title='Ausrüstung & Startkapital',
                popup_text='Die meisten Settings versorgen Helden mit einer gewissen Menge an Startkapital, mit der du aus den entsprechenden Listen von Waffen, Rüstungen und Abenteurerausrüstung kaufst, was dir gefällt.\n\nDas übliche Startkapital beträgt $500 (kann je nach Setting variieren).\n\nDie Ausrüstung auf deinem Charakterblatt sollte nur deine "Abenteuerausrüstung" sein, keine umfassende Liste von allem, was du besitzt.\n\nDas Tragegewicht wird automatisch berechnet!',
                is_required=False,
                validator=lambda c: True
            ),
            WizardSchritt(
                tab_id='charakterbogen',
                tab_name='Charakterbogen',
                title='Charakterbogen prüfen',
                description='Überprüfe deinen fertigen Charakter und exportiere ihn als PDF.',
                popup_title='Fertig!',
                popup_text='Dein Charakter ist fertig!\n\nDenke daran, Waffen, Rüstung und Schilde im Ausrüstungs-Tab nicht nur zu kaufen, sondern auch anzulegen. Nur angelegte Ausrüstung wirkt sich auf Parade und Robustheit aus.\n\nUm deinen Charakter weiterzuentwickeln, schließe die Charaktererstellung ab. Danach werden Aufstiege freigeschaltet, mit denen du Attribute, Fertigkeiten und Talente steigern kannst.\n\nDu kannst deinen Charakter jederzeit als PDF exportieren.\n\nViel Spaß mit deinem Helden!',
                is_required=False,
                validator=lambda c: True
            ),
        ]
    
    def _validate_neuer_charakter(self, charakter) -> bool:
        """Validiert ob ein neuer Charakter erstellt wurde (Name + Setting)."""
        if not charakter:
            return False
        name = getattr(charakter, 'char_name', None) or getattr(charakter, 'name', None)
        setting = getattr(charakter, 'active_setting_name', None)
        return bool(name and str(name).strip() and setting)
    
    def _validate_volk(self, charakter) -> bool:
        """Validiert ob ein Volk ausgewählt wurde."""
        if not charakter:
            return False
        return bool(getattr(charakter, 'volk', None))
    
    def _validate_profil(self, charakter) -> bool:
        """Validiert ob ein Name eingegeben wurde."""
        if not charakter:
            return False
        name = getattr(charakter, 'name', None) or getattr(charakter, 'charakter_name', None)
        return bool(name and str(name).strip())
    
    def _validate_eigenschaften(self, charakter) -> bool:
        """Validiert ob Punkte verteilt wurden."""
        if not charakter:
            return False
        return True
    
    def starten(self):
        """Startet den Wizard-Modus."""
        if self.aktiv:
            Logger.warning("Wizard ist bereits aktiv")
            return
        
        self.aktiv = True
        self.aktueller_schritt_index = 0
        Logger.info("Wizard gestartet")
        
        self._dispatch_event('on_wizard_started', self.get_aktueller_schritt())
    
    def beenden(self):
        """Beendet den Wizard-Modus."""
        if not self.aktiv:
            return
        
        self.aktiv = False
        self.aktueller_schritt_index = 0
        Logger.info("Wizard beendet")
        
        self._dispatch_event('on_wizard_finished')
    
    def abbrechen(self):
        """Bricht den Wizard ab."""
        if not self.aktiv:
            return
        
        self.aktiv = False
        self.aktueller_schritt_index = 0
        Logger.info("Wizard abgebrochen")
        
        self._dispatch_event('on_wizard_cancelled')
    
    def naechster_schritt(self) -> bool:
        """
        Wechselt zum nächsten Schritt.
        
        Returns:
            True wenn erfolgreich gewechselt, False wenn am Ende
        """
        if not self.aktiv:
            return False
        
        charakter = self._get_charakter()
        current_schritt = self.get_aktueller_schritt()
        
        if current_schritt:
            is_valid, error_msg = current_schritt.validate(charakter)
            self._dispatch_event('on_step_validated', current_schritt.tab_id, is_valid, error_msg)
            
            if current_schritt.is_required and not is_valid:
                Logger.warning(f"Schritt '{current_schritt.tab_id}' ist erforderlich aber nicht valide - trotzdem weiter...")
        
        if self.aktueller_schritt_index >= len(self.schritte) - 1:
            self.beenden()
            return False
        
        self.aktueller_schritt_index += 1
        new_schritt = self.get_aktueller_schritt()
        Logger.info(f"Wizard: Wechsle zu Schritt {self.aktueller_schritt_index + 1}/{len(self.schritte)}: {new_schritt.tab_id if new_schritt else '?'}")
        
        self._dispatch_event('on_step_changed', new_schritt)
        return True
    
    def vorheriger_schritt(self) -> bool:
        """
        Geht zum vorherigen Schritt zurück.
        
        Returns:
            True wenn erfolgreich gewechselt, False wenn am Anfang
        """
        if not self.aktiv:
            return False
        
        if self.aktueller_schritt_index <= 0:
            return False
        
        self.aktueller_schritt_index -= 1
        schritt = self.get_aktueller_schritt()
        Logger.info(f"Wizard: Zurück zu Schritt {self.aktueller_schritt_index + 1}/{len(self.schritte)}: {schritt.tab_id if schritt else '?'}")
        
        self._dispatch_event('on_step_changed', schritt)
        return True
    
    def gehe_zu_schritt(self, index: int) -> bool:
        """
        Geht zu einem bestimmten Schritt.
        
        Args:
            index: Der Index des Zielschritts
            
        Returns:
            True wenn erfolgreich, False bei ungültigem Index
        """
        if not self.aktiv:
            return False
        
        if index < 0 or index >= len(self.schritte):
            Logger.warning(f"Ungültiger Schritt-Index: {index}")
            return False
        
        self.aktueller_schritt_index = index
        schritt = self.get_aktueller_schritt()
        Logger.info(f"Wizard: Gehe zu Schritt {index + 1}/{len(self.schritte)}: {schritt.tab_id if schritt else '?'}")
        
        self._dispatch_event('on_step_changed', schritt)
        return True
    
    def get_aktueller_schritt(self) -> Optional[WizardSchritt]:
        """Gibt den aktuellen Schritt zurück."""
        if 0 <= self.aktueller_schritt_index < len(self.schritte):
            return self.schritte[self.aktueller_schritt_index]
        return None
    
    def get_fortschritt(self) -> tuple[int, int]:
        """
        Gibt den Fortschritt zurück.
        
        Returns:
            Tuple aus (current_index, total_count)
        """
        return (self.aktueller_schritt_index, len(self.schritte))
    
    def get_fortschritt_prozent(self) -> float:
        """
        Gibt den Fortschritt in Prozent zurück.
        
        Returns:
            Prozentwert zwischen 0 und 100
        """
        if len(self.schritte) <= 1:
            return 100.0
        return (self.aktueller_schritt_index / (len(self.schritte) - 1)) * 100.0
    
    def ist_letzter_schritt(self) -> bool:
        """Prüft ob der aktuelle Schritt der letzte ist."""
        return self.aktueller_schritt_index >= len(self.schritte) - 1
    
    def ist_erster_schritt(self) -> bool:
        """Prüft ob der aktuelle Schritt der erste ist."""
        return self.aktueller_schritt_index <= 0
    
    def schritt_ueberspringen(self) -> bool:
        """
        Überspringt den aktuellen Schritt (nur wenn optional).
        
        Returns:
            True wenn übersprungen, False wenn erforderlich
        """
        if not self.aktiv:
            return False
        
        schritt = self.get_aktueller_schritt()
        if not schritt:
            return False
        
        if schritt.is_required:
            Logger.warning(f"Schritt '{schritt.tab_id}' kann nicht übersprungen werden (erforderlich)")
            return False
        
        return self.naechster_schritt()
    
    def _get_charakter(self):
        """Gibt den aktuellen Charakter zurück."""
        if self.charakter_controller:
            return self.charakter_controller.charakter
        return None
    
    def _dispatch_event(self, event_name: str, *args):
        """Dispatcht ein Event an alle registrierten Callbacks."""
        if event_name not in self._callbacks:
            return
        
        for callback in self._callbacks[event_name]:
            try:
                callback(*args)
            except Exception as e:
                Logger.error(f"Fehler beim Aufruf von {event_name}-Callback: {e}")
    
    def bind_event(self, event_name: str, callback: Callable):
        """
        Bindet einen Callback an ein Event.
        
        Args:
            event_name: Name des Events (z.B. 'on_step_changed')
            callback: Die Callback-Funktion
        """
        if event_name in self._callbacks:
            self._callbacks[event_name].append(callback)
    
    def unbind_event(self, event_name: str, callback: Callable):
        """
        Entfernt einen Callback von einem Event.
        
        Args:
            event_name: Name des Events
            callback: Die Callback-Funktion
        """
        if event_name in self._callbacks and callback in self._callbacks[event_name]:
            self._callbacks[event_name].remove(callback)
