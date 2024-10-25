# controllers/charakter_controller.py
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger, LOG_LEVELS
from models.charakter import Charakter
from data.handicap_daten import handicap_liste
from data.talent_daten import talent_daten
from data.ausruestung_daten import ausruestung_daten
from data.maechte_daten import maechte_daten
#from models.handicap import Handicap
from models.talent import Talent
from models.macht import Macht
#from models.ausruestung import Ausruestung
from data.waffen_daten import waffen_daten
from data.schilde_daten import schilde_daten
from data.ruestung_daten import ruestung_daten
import logging

from kivy.logger import Logger, LOG_LEVELS

# Import der initialisiere_ausruestung-Funktion
from data.initialisiere_ausruestung import initialisiere_ausruestung

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['info'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")


class CharakterController:
    def __init__(self, name):
        self.charakter = Charakter(name)
        
        # Initialisiere Talente und Mächte
        self.initialisiere_talente(talent_daten)  # Initialize talents
        self.initialisiere_maechte(maechte_daten)  # Initialize powers
        self.initialisiere_waffen(waffen_daten)
        self.initialisiere_schilde(schilde_daten)
        self.initialisiere_ruestungen(ruestung_daten)
        # Initialisiere Ausrüstung und weise sie dem Charakter zu
        self.initialisiere_ausruestung_daten()

        Logger.info(f"CharakterController initialisiert für Charakter: {name}")

    def initialisiere_ausruestung_daten(self):
        try:
            ausruestung = initialisiere_ausruestung()
            self.charakter.ausruestung_daten = ausruestung
            Logger.info(f"Ausrüstungsdaten initialisiert und dem Charakter zugewiesen: {len(ausruestung)} Gegenstände.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Ausrüstung: {e}")

    # def print_character(self):
    #     charakter = self.charakter
    #     print("\nCharakterübersicht:")

    #     print("Attribute:")
    #     for attribut in charakter.attribute.values():
    #         print(f"{attribut.name}: W{attribut.wert}")

    #     print("\nFertigkeiten:")
    #     for fertigkeit in charakter.fertigkeiten.values():
    #         if fertigkeit.wert > 4:
    #             print(f"{fertigkeit.name}: W{fertigkeit.wert}")

    #     print("\nHandicaps:")
    #     for handicap in charakter.ausgewaehlte_handicaps():
    #         print(f"{handicap.name} ({handicap.stufe}): {handicap.beschreibung}")

    #     print("\nTalente:")
    #     for talent in charakter.ausgewaehlte_talente():
    #         print(f"{talent.name}: {talent.beschreibung}")

    #     print("\nMächte:")
    #     for macht in charakter.ausgewaehlte_maechte():
    #         print(f"{macht.name}, Rang: {macht.rang}, 'Machtpunkte' {macht.machtpunkte}, 'Reichweite': {macht.reichweite}, 'Dauer': {macht.dauer}, Effekt: {macht.effekt}")

    #     print("\nAusrüstung:")
    #     for item in charakter.ausruestung_daten.values():
    #         if item.menge > 0:
    #             print(f"{item.name} x{item.menge}")

    #     print("\nWaffen:") 
    #     for waffe in charakter.waffen_daten.values():
    #         if waffe.menge > 0:
    #             status = "Angelegt" if waffe.angelegt else "Nicht angelegt"
    #             # Formatieren der Eigenschaften als Schlüssel=Wert
    #             eigenschaften = ', '.join(f"{k}={v}" for k, v in waffe.eigenschaften.items()) if waffe.eigenschaften else 'Keine'
    #             print(f"{waffe.name}: {eigenschaften}")

    #     print("\nRüstungen:")
    #     for ruestung in charakter.ruestungen.values():
    #         if ruestung.angelegt:
    #             status = "Angelegt"
    #             print(f"{ruestung.name}: Torso={ruestung.torso}, Arme={ruestung.arme}, Beine={ruestung.beine}, Kopf={ruestung.kopf}, Status={status}")
    #         else:
    #             status = "Nicht angelegt"
    #             print(f"{ruestung.name}: Status={status}")

    def steigere_attribut(self, attribut_name):
        Logger.info(f"[Increasing attribute] {attribut_name} (attribute)")
        success = self.charakter.steigere_attribut(attribut_name)
        if success:
            Logger.info(f"Attribut '{attribut_name}' gesteigert. Verbleibende Attributsteigerungen: {self.charakter.verbleibende_attributsteigerungen}")
            self.update_charakterbogen()
        else:
            Logger.info(f"Attribut '{attribut_name}' konnte nicht gesteigert werden.")
        return success
    
    def senke_attribut(self, attribut_name):
        success = self.charakter.senke_attribut(attribut_name)
        if success:
            Logger.info(f"Attribut '{attribut_name}' gesenkt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Attribut '{attribut_name}' konnte nicht gesenkt werden.")
        return success
    
    def steigere_fertigkeit(self, fertigkeit_name):
        success = self.charakter.steigere_fertigkeit(fertigkeit_name)
        if success:
            Logger.info(f"Fertigkeit '{fertigkeit_name}' gesteigert.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Fertigkeit '{fertigkeit_name}' konnte nicht gesteigert werden.")
        return success
    
    def senke_fertigkeit(self, fertigkeit_name):
        success = self.charakter.senke_fertigkeit(fertigkeit_name)
        if success:
            Logger.info(f"Fertigkeit '{fertigkeit_name}' gesenkt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Fertigkeit '{fertigkeit_name}' konnte nicht gesenkt werden.")
        return success
       
    # Methoden für Handicaps
    def initialisiere_handicaps(self, handicap_liste):
        self.charakter.initialisiere_handicaps(handicap_liste)
        Logger.info("Handicaps initialisiert.")
        self.update_charakterbogen()

    def initialisiere_waffen(self, waffen_daten):
        self.charakter.initialisiere_waffen(waffen_daten)
        Logger.info("Waffen initialisiert.")
        self.update_charakterbogen()

    def initialisiere_schilde(self, schild_daten):
        self.charakter.initialisiere_schilde(schild_daten)
        Logger.info("Schilde initialisiert.")
        self.update_charakterbogen()

    def initialisiere_ruestungen(self, ruestung_daten):
        self.charakter.initialisiere_ruestungen(ruestung_daten)
        Logger.info("Rüstungen initialisiert.")
        self.update_charakterbogen()

    def waehle_handicap(self, handicap_name):
        success = self.charakter.waehle_handicap(handicap_name)
        if success:
            Logger.info(f"Handicap '{handicap_name}' wurde ausgewählt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Handicap '{handicap_name}' konnte nicht ausgewählt werden.")
        return success
    
    def entferne_handicap(self, handicap_name):
        success = self.charakter.entferne_handicap(handicap_name)
        if success:
            Logger.info(f"Handicap '{handicap_name}' wurde entfernt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Handicap '{handicap_name}' konnte nicht entfernt werden.")
        return success
    
    def aktive_handicaps(self):
        return self.charakter.aktive_handicaps()
    
    def ausgewaehlte_handicaps(self):
        return self.charakter.ausgewaehlte_handicaps()
       
    # Methoden für Talente
    def initialisiere_talente(self, talent_daten):
        for kategorie, talents_in_category in talent_daten.items():
            for talent_name, talent_data in talents_in_category.items():
                talent = Talent(
                    name=talent_name,
                    kategorie=kategorie,
                    rang=talent_data.get('Rang', ''),
                    voraussetzungen=talent_data.get('Voraussetzungen', []),
                    beschreibung=talent_data.get('Beschreibung', ''),
                    neue_maechte=talent_data.get('neue_maechte', 0),
                    machtpunkte=talent_data.get('machtpunkte', 0)
                )
                self.charakter.talente[talent_name] = talent
        Logger.info("Talente initialisiert.")
        self.update_charakterbogen()
    
    def waehle_talent(self, talent_name):
        success = self.charakter.waehle_talent(talent_name)
        if success:
            Logger.info(f"Talent '{talent_name}' wurde ausgewählt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Talent '{talent_name}' konnte nicht ausgewählt werden.")
        return success
    
    def entferne_talent(self, talent_name):
        success = self.charakter.entferne_talent(talent_name)
        if success:
            Logger.info(f"Talent '{talent_name}' wurde entfernt.")
            self.update_charakterbogen()
        else:
            Logger.info(f"Talent '{talent_name}' konnte nicht entfernt werden.")
        return success
    
    def aktive_talente(self):
        return self.charakter.aktive_talente()
    
    def ausgewaehlte_talente(self):
        return self.charakter.ausgewaehlte_talente()
    
    def initialisiere_maechte(self, macht_daten):
        for name, daten in macht_daten.items():
            if name not in self.charakter.maechte:
                self.charakter.maechte[name] = Macht(
                    name=name,
                    rang=daten.get('rang', ''),
                    machtpunkte=daten.get('machtpunkte', 0),
                    reichweite=daten.get('reichweite', ''),
                    dauer=daten.get('dauer', ''),
                    effekt=daten.get('effekt', ''),
                    anmerkungen=daten.get('anmerkungen', ''),
                    voraussetzungen=daten.get('voraussetzungen', [])
                )
        Logger.info("Mächte initialisiert.")
        self.update_charakterbogen()
    
    def waehle_macht(self, macht_name):
        success = self.charakter.waehle_macht(macht_name)
        if success:
            Logger.info(f"Macht '{macht_name}' wurde ausgewählt.")
            self.update_charakterbogen()
            return True
        else:
            Logger.info(f"Macht '{macht_name}' konnte nicht ausgewählt werden.")
            return False

    
    def entferne_macht(self, macht_name):
        success = self.charakter.entferne_macht(macht_name)
        if success:
            Logger.info(f"Macht '{macht_name}' wurde abgewählt.")
            self.update_charakterbogen()
            return True
        else:
            Logger.info(f"Macht '{macht_name}' konnte nicht abgewählt werden.")
            return False


    # Methoden für Ausrüstung (bereits angepasst)
    def kaufen_ausruestung(self, ausruestung_name, anzahl=1, preis_pro_stueck=None):
        ausruestung = self.charakter.ausruestung_daten.get(ausruestung_name)
        if not ausruestung:
            Logger.warning(f"Ausrüstung '{ausruestung_name}' nicht gefunden.")
            return False
        success = self.charakter.kaufen(ausruestung, anzahl, preis_pro_stueck)
        if success:
            self.update_charakterbogen()
        return success

    def verkaufen_ausruestung(self, ausruestung_name, anzahl=1, preis_pro_stueck=None):
        ausruestung = self.charakter.ausruestung_daten.get(ausruestung_name)
        if not ausruestung:
            Logger.warning(f"Ausrüstung '{ausruestung_name}' nicht gefunden.")
            return False
        success = self.charakter.verkaufen(ausruestung, anzahl, preis_pro_stueck)
        if success:
            self.update_charakterbogen()
        return success

    def update_charakterbogen(self):
        try:
            # Zugriff auf das Charakterbogen-Widget über die ID
            charakterbogen_widget = App.get_running_app().root.ids.charakterbogen_widget
            charakterbogen_widget.update_overview(0)  # Parameter dt benötigt
            Logger.info("Charakterbogen aktualisiert.")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Charakterbogens: {e}")