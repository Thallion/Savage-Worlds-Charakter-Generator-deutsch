# volk_manager.py
from kivy.event import EventDispatcher
from kivy.logger import Logger

class VolkManager(EventDispatcher):
    __events__ = ('on_volk_change',)
    
    def __init__(self, charakter):
        super().__init__()
        self.charakter = charakter
        self.voelker = {}
        self.voelker_selected = {}

    def on_volk_change(self):  # MUSS vorhanden sein
        """Default-Handler für das Event"""
        pass

    def set_selected_volk(self, volk_name):
        """Setzt das ausgewählte Volk und aktualisiert die anderen auf False."""
        if volk_name not in self.voelker_selected:
            Logger.warning(f"Volk '{volk_name}' existiert nicht.")
            return

        # Setze alle Völker auf False
        for volk in self.voelker_selected.keys():
            if self.voelker_selected[volk]:
                self.voelker_selected[volk] = False

        # Setze das ausgewählte Volk auf True
        self.voelker_selected[volk_name] = True

        # Dispatch das Event zur Aktualisierung der UI
        self.dispatch('on_charakter_change')
    
    def toggle_selected_volk(self, volk_name, value):
        """Toggle-Funktion, die das ausgewählte Volk setzt oder entfernt."""
        if volk_name not in self.voelker_selected:
            Logger.warning(f"Volk '{volk_name}' existiert nicht.")
            return

        self.voelker_selected[volk_name] = value
        self.dispatch('on_charakter_change')

    # Methode zum Auswählen eines Volkes
    def waehle_volk(self, volk_name):
        if volk_name in self.voelker:
            for volk in self.voelker.values():
                volk.ausgewaehlt = False
            self.voelker[volk_name].ausgewaehlt = True
            Logger.info(f"Volk '{volk_name}' wurde ausgewählt.")
            return True
        else:
            Logger.error(f"Volk '{volk_name}' existiert nicht.")
            return False

    # Methode zum Abwählen des aktuellen Volkes
    def entferne_volk(self):
        for volk in self.voelker.values():
            if volk.ausgewaehlt:
                volk.ausgewaehlt = False
                Logger.info(f"Volk '{volk.name}' wurde abgewählt.")
                return True
        Logger.warning("Kein Volk war ausgewählt.")
        return False
