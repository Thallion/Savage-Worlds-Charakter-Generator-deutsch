from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.uix.widget import Widget
import logging
#from .wuerfel import Wuerfel
from .attribut import Attribut
from .fertigkeit import Fertigkeit
from .handicap import Handicap
from .talent import Talent
from .macht import Macht
from .ausruestung import Ausruestung
from .waffe import Waffe
from .ruestung import Ruestung
from .schild import Schild

from data.initialisiere_ausruestung import initialisiere_ausruestung
from data.handicap_daten import handicap_liste
from data.talent_daten import talent_daten
from data.maechte_daten import maechte_daten
from data.ausruestung_daten import ausruestung_daten
from data.waffen_daten import waffen_daten
from data.schilde_daten import schilde_daten
from data.ruestung_daten import ruestung_daten

from kivy.logger import Logger, LOG_LEVELS

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['info'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

class Charakter(Widget):
    """
    Klasse zur Darstellung eines Charakters.
    """

    # Definierte Properties auf Klassenebene
    name = StringProperty("")
    verbleibende_attributsteigerungen = NumericProperty(5)  
    verbleibende_fertigkeitssteigerungen = NumericProperty(12)  
    maximale_attributsteigerungen = NumericProperty(5)  
    maximale_fertigkeitssteigerungen = NumericProperty(12)  
    verbleibende_aufstiege = NumericProperty(0) 
    aufstiege_gesamt = NumericProperty(0)
    verfuegbare_maechte = NumericProperty(0)
    machtpunkte = NumericProperty(0)
    vermoegen = NumericProperty(5000)
    erschoepfung = NumericProperty(0)
    talente = DictProperty({})
    handicaps = DictProperty({})
    zusaetzliche_talente = NumericProperty(0)
    gesamt_handicap_punkte = NumericProperty(0)
    maechte = DictProperty({})
    ausruestung_daten = DictProperty({})
    ruestung_daten = DictProperty({})
    schilde_daten = DictProperty({})    
    waffen_daten = DictProperty({})
    konzept = DictProperty({})
    details = DictProperty({})
    settingregeln = DictProperty({})
    voelker = DictProperty({})
    maximale_traglast = NumericProperty(40)
    gesamtgewicht = NumericProperty(0)
    ausruestung_daten = DictProperty({})
    selected_handicaps = ListProperty([])
    selected_talente = ListProperty([])
    selected_maechte = ListProperty([])
    selected_ausruestung = ListProperty([])
    selected_waffen = ListProperty([])
    selected_ruestungen = ListProperty([])

    # Attribute und Fertigkeiten
    attribute = ObjectProperty({})
    fertigkeiten = ObjectProperty({})

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.handicaps = {}
        self.gesamt_handicap_punkte = 0
        self.zusaetzliche_talente = 0
        self.talente = {}
        self.maechte = {}
        self.ruestungen = {}
        self.verfuegbare_maechte = 0
        self.machtpunkte = 0
        self.selected_waffen = []
        self.selected_ruestungen = []

        # Initialisierung der Ausrüstung
        self.ausruestung_daten = initialisiere_ausruestung()
        Logger.debug(f"Alle Ausrüstungsgegenstände für Charakter '{self.name}' initialisiert.")
    

        # Initialisierung der Attribute
        attribut_namen = ["Geschicklichkeit", "Verstand", "Heimlichkeit", "Stärke", "Konstitution"]
        self.attribute = {attr: Attribut(attr) for attr in attribut_namen}

        # Bereinigte Fertigkeiten-Daten
        fertigkeiten_daten = {
            "Allgemeinwissen": {"Verstand"},
            "Athletik": {"Geschicklichkeit"},
            "Heimlichkeit": {"Geschicklichkeit"},
            "Überreden": {"Heimlichkeit"},
            "Wahrnehmung": {"Verstand"},
            "Kämpfen": {"Geschicklichkeit"},
            "Schießen": {"Geschicklichkeit"},
            "Diebeskunst": {"Geschicklichkeit"},
            "Überleben": {"Geschicklichkeit"},
            "Reiten": {"Geschicklichkeit"},
            "Fahren": {"Geschicklichkeit"},
            "Seefahrt": {"Geschicklichkeit"},
            "Pilot": {"Geschicklichkeit"},
            "Darbietung": {"Heimlichkeit"},
            "Einschüchtern": {"Heimlichkeit"},
            "Fokus": {"Heimlichkeit"},
            "Glaube": {"Heimlichkeit"},
            "Heilen": {"Verstand"},
            "Provozieren": {"Verstand"},
            "Recherche": {"Verstand"},
            "Reparieren": {"Verstand"},
            "Glücksspiel": {"Verstand"},
            "Kriegskunst": {"Verstand"},
            "Okkultismus": {"Verstand"},
            "Geisteswissenschaften": {"Verstand"},
            "Naturwissenschaften": {"Verstand"},
            "Sprache": {"Verstand"},
            "Elektronik": {"Verstand"},
            "Hacken": {"Verstand"},
            "Zaubern": {"Verstand"},
            "Psionik": {"Verstand"},
            "Verrückte Wissenschaft": {"Verstand"},
        }

        # Bereinigte Grundfertigkeiten-Liste
        grundfertigkeiten = [
            "Allgemeinwissen",
            "Athletik",
            "Heimlichkeit",
            "Überreden",
            "Wahrnehmung",
        ]

        # Initialisierung der Fertigkeiten
        fertigkeiten_dict = {}
        for fertigkeit_name, attribut_set in fertigkeiten_daten.items():
            # Annahme: Jede Fertigkeit hat nur ein zugeordnetes Attribut
            attribut_name = next(iter(attribut_set))
            attribut_obj = self.attribute.get(attribut_name)
            if attribut_obj is None:
                logging.error(
                    f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' ist nicht definiert."
                )
                continue

            # Überprüfen, ob die Fertigkeit eine Grundfertigkeit ist
            ist_grundfertigkeit = fertigkeit_name in grundfertigkeiten

            # Initialisierung der Fertigkeit
            fertigkeit = Fertigkeit(
                name=fertigkeit_name,
                attribut=attribut_obj,
                grundfertigkeit=ist_grundfertigkeit,
            )

            # Hinzufügen zur fertigkeitenliste
            fertigkeiten_dict[fertigkeit_name] = fertigkeit

        self.fertigkeiten = fertigkeiten_dict

        # Initialisierung der Handicaps
        self.initialisiere_handicaps(handicap_liste)

        # Initialisierung der Talente
        self.initialisiere_talente(talent_daten)

        # Initialisierung der Mächte
        self.initialisiere_maechte(maechte_daten)

        # Initialisierung der Ausrüstung
        self.initialisiere_ausruestung(ausruestung_daten)

        # Initialisierung der Waffen und Rüstungen
        self.initialisiere_waffen(waffen_daten)
        self.initialisiere_ruestungen(ruestung_daten)

    def __str__(self):
        output = f"Charakter: {self.name}\n\nAttribute:\n"
        for attribut in self.attribute.values():
            output += f"{attribut}\n"
        output += "\nFertigkeiten:\n"
        for fertigkeit in self.fertigkeiten.values():
            output += f"{fertigkeit}\n"
        output += f"\nVerbleibende Attributsteigerungen: {self.verbleibende_attributsteigerungen}"
        output += f"\nVerbleibende Fertigkeitssteigerungen: {self.verbleibende_fertigkeitssteigerungen}"
        return output

    def steigere_attribut(self, attribut_name):
        """
        Steigert ein Attribut um eine Stufe, sofern möglich.
        """
        if self.verbleibende_attributsteigerungen > 0:
            attribut = self.attribute.get(attribut_name)
            if attribut:
                vorheriger_wert = attribut.wuerfel.value
                vorheriger_modifier = attribut.wuerfel.modifier
                erfolg = attribut.wuerfel.increase()
                if erfolg:
                    self.verbleibende_attributsteigerungen -= 1
                    # logging.debug(
                    #     f"Attribut '{attribut_name}' gesteigert. Verbleibende Attributsteigerungen: {self.verbleibende_attributsteigerungen}"
                    # )
                return erfolg
            else:
                logging.error(f"Attribut '{attribut_name}' existiert nicht.")
                return False
        else:
            logging.warning("Keine Attributsteigerungen mehr verfügbar.")
            return False

    def senke_attribut(self, attribut_name):
        """
        Senkt ein Attribut um eine Stufe, sofern möglich.
        """
        attribut = self.attribute.get(attribut_name)
        if attribut:
            vorheriger_wert = attribut.wuerfel.value
            vorheriger_modifier = attribut.wuerfel.modifier
            erfolg = attribut.wuerfel.decrease()
            if erfolg:
                self.verbleibende_attributsteigerungen += 1
                # logging.debug(
                #     f"Attribut '{attribut_name}' gesenkt. Verbleibende Attributsteigerungen: {self.verbleibende_attributsteigerungen}"
                # )
            return erfolg
        else:
            logging.error(f"Attribut '{attribut_name}' existiert nicht.")
            return False

    def steigere_fertigkeit(self, fertigkeit_name):
        fertigkeit = self.fertigkeiten.get(fertigkeit_name)
        if fertigkeit:
            zugehoeriges_attribut = fertigkeit.attribut
            # Berechne den neuen total_value nach der Steigerung
            aktueller_total_value = fertigkeit.wuerfel.value + fertigkeit.wuerfel.modifier
            attribut_total_value = zugehoeriges_attribut.wuerfel.value + zugehoeriges_attribut.wuerfel.modifier

            # Bestimme den neuen Wert und Modifier nach der Steigerung
            if fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == -2:
                # Steigerung von W4-2 auf W4+0
                neuer_wert = fertigkeit.wuerfel.value
                neuer_modifier = fertigkeit.wuerfel.modifier + 2
            elif fertigkeit.wuerfel.value < 12:
                neuer_wert = fertigkeit.wuerfel.value + 2
                neuer_modifier = fertigkeit.wuerfel.modifier
            elif fertigkeit.wuerfel.value == 12 and fertigkeit.wuerfel.modifier < 2:
                neuer_wert = fertigkeit.wuerfel.value
                neuer_modifier = fertigkeit.wuerfel.modifier + 1
            else:
                logging.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
                return False

            neuer_total_value = neuer_wert + neuer_modifier

            # Bestimme die Kosten
            if neuer_total_value > attribut_total_value:
                kosten = 2
            else:
                kosten = 1

            if self.verbleibende_fertigkeitssteigerungen >= kosten:
                erfolg = fertigkeit.wuerfel.increase()
                if erfolg:
                    self.verbleibende_fertigkeitssteigerungen -= kosten
                    fertigkeit.ausgewaehlt = True
                    # logging.debug(
                    #     f"Fertigkeit '{fertigkeit_name}' gesteigert. Verbleibende Fertigkeitssteigerungen: {self.verbleibende_fertigkeitssteigerungen}"
                    # )
                    return True
                else:
                    logging.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
                    return False
            else:
                logging.warning("Nicht genügend verbleibende Fertigkeitssteigerungen.")
                return False
        else:
            logging.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
            return False

    def senke_fertigkeit(self, fertigkeit_name):
        """
        Senkt eine Fertigkeit um eine Stufe und gibt die entsprechenden Steigerungen zurück.
        """
        fertigkeit = self.fertigkeiten.get(fertigkeit_name)
        if fertigkeit:
            zugehoeriges_attribut = fertigkeit.attribut
            kosten = 1
            if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
                kosten = 2
            vorheriger_wert = fertigkeit.wuerfel.value
            vorheriger_modifier = fertigkeit.wuerfel.modifier
            erfolg = fertigkeit.wuerfel.decrease()
            if erfolg:
                self.verbleibende_fertigkeitssteigerungen += kosten
                # logging.debug(
                #     f"Fertigkeit '{fertigkeit_name}' gesenkt. Verbleibende Fertigkeitssteigerungen: {self.verbleibende_fertigkeitssteigerungen}"
                # )
            else:
                logging.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesenkt werden.")
            return erfolg
        else:
            logging.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
            return False

    def steigerung_anzeigen(self):
        """
        Zeigt die verbleibenden Attribut- und Fertigkeitssteigerungen an.
        """
        return (
            f"Verbleibende Attributsteigerungen: {self.verbleibende_attributsteigerungen}\n"
            f"Verbleibende Fertigkeitssteigerungen: {self.verbleibende_fertigkeitssteigerungen}"
        )
        
    def initialisiere_handicaps(self, handicap_liste):
        """
        Initialisiert die Handicaps des Charakters basierend auf der bereitgestellten Liste.
        """
        self.handicaps = {}
        try:
            #logging.debug(f"Typ von handicap_liste: {type(handicap_liste)}")
            # if len(handicap_liste) > 0:
            #     logging.debug(f"Typ von handicap_liste[0]: {type(handicap_liste[0])}")

            for daten in handicap_liste:
                name = daten.get('Name', '')
                stufe = daten.get('Stufe', '').lower()
                beschreibung = ' '  # Setze die Beschreibung auf einen Platzhalter

                # Immer ein eindeutiger Schlüssel mit Name und Stufe
                name_key = f"{name} ({stufe})"

                # Initialisiere das Handicap
                handicap = Handicap(
                    name=name,  # Name ohne Stufe
                    stufe=stufe,
                    beschreibung=beschreibung
                )
                self.handicaps[name_key] = handicap
            #logging.debug(f"Handicaps erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Handicaps: {e}")

    def waehle_handicap(self, handicap_name):
        if handicap_name in self.handicaps:
            handicap = self.handicaps[handicap_name]
            if not handicap.ausgewaehlt:
                neue_gesamtpunkte = self.gesamt_handicap_punkte + handicap.punkte
                if neue_gesamtpunkte <= 4:
                    handicap.auswaehlen()
                    self.gesamt_handicap_punkte = neue_gesamtpunkte
                    self.berechne_zusaetzliche_talente()
                    self.selected_handicaps.append(handicap)
                    self.selected_handicaps = self.selected_handicaps  # Neu zuweisen
                else:
                    logging.warning(f"Handicap '{handicap_name}' kann nicht ausgewählt werden. Gesamt Handicappunkte würden {neue_gesamtpunkte} überschreiten.")
            else:
                logging.warning(f"Handicap '{handicap_name}' ist bereits ausgewählt.")
        else:
            logging.error(f"Handicap '{handicap_name}' existiert nicht.")


    def entferne_handicap(self, handicap_name):
        if handicap_name in self.handicaps:
            handicap = self.handicaps[handicap_name]
            if handicap.ausgewaehlt:
                handicap.abwaehlen()
                self.gesamt_handicap_punkte -= handicap.punkte
                self.berechne_zusaetzliche_talente()
                if handicap in self.selected_handicaps:
                    self.selected_handicaps.remove(handicap)
                    self.selected_handicaps = self.selected_handicaps  # Neu zuweisen
            else:
                logging.warning(f"Handicap '{handicap_name}' ist nicht ausgewählt.")
        else:
            logging.error(f"Handicap '{handicap_name}' existiert nicht.")
 

    def aktive_handicaps(self):
        return [handicap for handicap in self.handicaps.values() if handicap.aktiv]

    def ausgewaehlte_handicaps(self):
        return [handicap for handicap in self.handicaps.values() if handicap.ausgewaehlt]

    def berechne_zusaetzliche_talente(self):
        self.zusaetzliche_talente = self.gesamt_handicap_punkte // 2
        #logging.debug(f"Zusätzliche Talente berechnet: {self.zusaetzliche_talente}")

    def initialisiere_talente(self, talent_daten):
        try:
            for kategorie, talente in talent_daten.items():
                for name, daten in talente.items():
                    talent = Talent(
                        name=name,
                        kategorie=kategorie,
                        rang=daten.get('Rang', ''),
                        voraussetzungen=daten.get('Voraussetzungen', []),
                        beschreibung=daten.get('Beschreibung', ''),
                        neue_maechte=daten.get('neue_maechte', 0),
                        machtpunkte=daten.get('machtpunkte', 0)
                    )
                    self.talente[name] = talent
            #logging.debug(f"Talente erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Talente: {e}")

    def ausgewaehlte_talente(self):
        return [talent for talent in self.talente.values() if talent.ausgewaehlt]
    
    def waehle_talent(self, talent_name):
        max_talente = 1 + self.zusaetzliche_talente
        if len(self.selected_talente) < max_talente:
            if talent_name in self.talente:
                talent = self.talente[talent_name]
                if not talent.ausgewaehlt:
                    if talent.voraussetzungen_erfuellt(self):
                        talent.auswaehlen(self)
                        self.verfuegbare_maechte += talent.neue_maechte
                        self.erhoehe_machtpunkte(talent.machtpunkte)
                        self.selected_talente.append(talent)
                        self.selected_talente = self.selected_talente  # Neu zuweisen
                    else:
                        logging.warning(f"Voraussetzungen für Talent '{talent_name}' nicht erfüllt.")
                else:
                    logging.warning(f"Talent '{talent_name}' ist bereits ausgewählt.")
            else:
                logging.error(f"Talent '{talent_name}' existiert nicht.")
        else:
            logging.warning(f"Maximale Anzahl an Talenten erreicht ({max_talente}).")


    def entferne_talent(self, talent_name):
        if talent_name in self.talente:
            talent = self.talente[talent_name]
            if talent.ausgewaehlt:
                talent.abwaehlen(self)
                if talent in self.selected_talente:
                    self.selected_talente.remove(talent)
                    self.selected_talente = self.selected_talente  # Neu zuweisen
            else:
                logging.warning(f"Talent '{talent_name}' ist nicht ausgewählt.")
        else:
            logging.error(f"Talent '{talent_name}' existiert nicht.")


    def ausgewaehlte_talente(self):
        """
        Gibt eine Liste aller ausgewählten Talente zurück.
        """
        return [talent for talent in self.talente.values() if talent.ausgewaehlt]

    def aktive_talente(self):
        """
        Gibt eine Liste aller aktiven Talente zurück.
        """
        return [talent for talent in self.talente.values() if talent.aktiv]

    def erfuellt_voraussetzung(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für das Talent erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True


    # def erfuellt_voraussetzung(self, voraussetzung):
    #     """
    #     Prüft, ob der Charakter eine bestimmte Voraussetzung erfüllt.
    #     """
    #     # Prüfen, ob die Voraussetzung ein Talent ist
    #     if voraussetzung in self.talente and self.talente[voraussetzung].ausgewaehlt:
    #         return True
    #     # Prüfen auf Wild Card (WC)
    #     if voraussetzung == 'WC':
    #         return True  # Annahme: Der Charakter ist eine Wild Card
    #     # Prüfen auf Rang (A für Anfänger, F für Fortgeschritten, etc.)
    #     if voraussetzung in ['A', 'F', 'V', 'H', 'L']:
    #         # Hier müssten Sie den Rang des Charakters überprüfen
    #         # Zum Beispiel:
    #         # if self.rang == voraussetzung:
    #         #     return True
    #         pass  # Platzhalter
    #     # Prüfen auf Attributswert (z. B. "WIL W8")
    #     if ' ' in voraussetzung:
    #         attribut_name, wert = voraussetzung.split()
    #         if attribut_name in self.attribute:
    #             attribut = self.attribute[attribut_name]
    #             geforderter_wert = int(wert.replace('W', ''))
    #             if attribut.wert >= geforderter_wert:
    #                 return True
    #     # Prüfen auf Fertigkeit (z. B. "Kämpfen W8")
    #     if ' ' in voraussetzung:
    #         fertigkeit_name, wert = voraussetzung.split()
    #         if fertigkeit_name in self.fertigkeiten:
    #             fertigkeit = self.fertigkeiten[fertigkeit_name]
    #             geforderter_wert = int(wert.replace('W', ''))
    #             if fertigkeit.wert >= geforderter_wert:
    #                 return True
    #     # Wenn keine der obigen Prüfungen erfolgreich war
    #     return False

    def initialisiere_maechte(self, maechte_daten):
        self.maechte = {}
        try:
            for name, daten in maechte_daten.items():
                if not all(key in daten for key in ['Rang', 'Machtpunkte', 'Reichweite', 'Dauer']):
                    logging.warning(f"Ungültige oder fehlende Daten für Macht '{name}': {daten}")
                    continue
                macht = Macht(
                    name=name,
                    rang=daten.get('Rang', ''),
                    machtpunkte=daten.get('Machtpunkte', 0),
                    reichweite=daten.get('Reichweite', ''),
                    dauer=daten.get('Dauer', ''),
                    effekt=daten.get('Effekt', ''),
                    anmerkungen=daten.get('Anmerkungen', ''),
                    voraussetzungen=daten.get('Voraussetzungen', [])
                )
                self.maechte[name] = macht
            #logging.debug(f"Mächte erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Mächte: {e}")

    def waehle_macht(self, macht_name):
        if self.verfuegbare_maechte > 0:
            if macht_name in self.maechte:
                macht = self.maechte[macht_name]
                if not macht.ausgewaehlt:
                    if macht.voraussetzungen_erfuellt(self):
                        macht.auswaehlen()
                        self.verfuegbare_maechte -= 1
                        self.selected_maechte.append(macht)
                        self.selected_maechte = self.selected_maechte  # Neu zuweisen, um Kivy zu informieren
                        logging.debug(f"Macht '{macht_name}' wurde ausgewählt.")
                        return True
                    else:
                        logging.warning(f"Voraussetzungen für Macht '{macht_name}' nicht erfüllt.")
                else:
                    logging.warning(f"Macht '{macht_name}' ist bereits ausgewählt.")
            else:
                logging.error(f"Macht '{macht_name}' existiert nicht.")
        else:
            logging.warning("Keine verfügbaren Mächte mehr zum Auswählen.")
        return False

    def entferne_macht(self, macht_name):
        if macht_name in self.maechte:
            macht = self.maechte[macht_name]
            if macht.ausgewaehlt:
                macht.abwaehlen()
                self.verfuegbare_maechte += 1
                if macht in self.selected_maechte:
                    self.selected_maechte.remove(macht)
                    self.selected_maechte = self.selected_maechte  # Neu zuweisen
                logging.debug(f"Macht '{macht_name}' wurde entfernt.")
                return True
            else:
                logging.warning(f"Macht '{macht_name}' ist nicht ausgewählt.")
        else:
            logging.error(f"Macht '{macht_name}' existiert nicht.")
        return False


    def erhoehe_machtpunkte(self, punkte):
        """
        Erhöht die Machtpunkte des Charakters.
        """
        self.machtpunkte += punkte

    def senke_machtpunkte(self, punkte):
        """
        Verringert die Machtpunkte des Charakters.
        """
        self.machtpunkte -= punkte

    def aktive_maechte(self):
        """
        Gibt eine Liste aller aktiven Mächte zurück.
        """
        return [macht for macht in self.maechte.values() if macht.aktiv]

    def ausgewaehlte_maechte(self):
        """
        Gibt eine Liste aller ausgewählten Mächte zurück.
        """
        return [macht for macht in self.maechte.values() if macht.ausgewaehlt]

    def initialisiere_ausruestung(self, ausruestung_daten):
        """
        Initialisiert die Ausrüstung des Charakters basierend auf den bereitgestellten Daten.
        """
        self.ausruestung_daten = {}
        try:
            for name, daten in ausruestung_daten.items():
                ausruestung_daten = Ausruestung(
                    name=name,
                    gewicht=daten.get('Gewicht', 0),
                    kosten=daten.get('Kosten', 0),
                    setting=daten.get('Setting', 'unbekannt'),
                    beschreibung=daten.get('Beschreibung', '')
                )
                self.ausruestung_daten[name] = ausruestung_daten
            logging.debug(f"Ausrüstung erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Ausrüstung: {e}")

    def initialisiere_waffen(self, waffen_daten):
        """
        Initialisiert die Waffen des Charakters.
        """
        if not hasattr(self, 'waffen_daten'):
            self.waffen_daten = {}
        try:
            for name, daten in waffen_daten.items():
                waffe = Waffe(
                    name=name,
                    gewicht=daten.get('Gewicht', 0),
                    kosten=daten.get('Kosten', 0),
                    setting=daten.get('Setting', 'unbekannt'),
                    typ=daten.get('Typ', ''),
                    mindeststaerke=daten.get('Mindeststärke', 'W4'),
                    beschreibung=daten.get('Beschreibung', ''),
                    eigenschaften=daten.get('Eigenschaften', {})
                )
                self.waffen_daten[name] = waffe
            logging.debug(f"Waffen erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Waffen: {e}")

    def initialisiere_ruestungen(self, ruestung_daten):
        """
        Initialisiert die Rüstungen des Charakters.
        """
        if not hasattr(self, 'ruestungen'):
            self.ruestungen = {}
        try:
            for name, daten in ruestung_daten.items():
                ruestung = Ruestung(
                    torso=daten.get('Torso', 0),
                    arme=daten.get('Arme', 0),
                    name=name,
                    beine=daten.get('Beine', 0),
                    kopf=daten.get('Kopf', 0),
                    mindeststaerke=daten.get('Mindeststärke', 'W4'),
                    setting=daten.get('Setting', ""),  
                    gewicht=daten.get('Gewicht', 0),
                    kosten=daten.get('Kosten', 0),
                    beschreibung=daten.get('Anmerkungen', '')
                )
                self.ruestungen[name] = ruestung
            logging.debug(f"Rüstungen erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Rüstungen: {e}")

    def initialisiere_schilde(self, schild_daten):
        """
        Initialisiert die Schilde des Charakters.
        """
        self.schilde_daten = {}
        try:
            for name, daten in schild_daten.items():
                schild = Schild(
                    name=name,
                    gewicht=daten.get('Gewicht', 0),
                    kosten=daten.get('Kosten', 0),
                    setting=daten.get('Setting', 'unbekannt'),
                    parade=daten.get('Parade', 0),
                    deckung=daten.get('Deckung', 0),
                    mindeststaerke=daten.get('Mindeststärke', 'W4'),
                    beschreibung=daten.get('Beschreibung', '')
                )
                self.schilde_daten[name] = schild
            logging.debug(f"Schilde erfolgreich initialisiert für Charakter {self.name}.")
        except Exception as e:
            logging.error(f"Fehler bei der Initialisierung der Schilde: {e}")

    def berechne_abgeleitete_werte(self):
        """
        Berechnet die abgeleiteten Werte des Charakters, wie Parade, Robustheit usw.
        Berücksichtigt die Erschöpfung.
        """
        try:
            # Standardwerte
            bewegungsweite = 6
            bennys = 3
            entschlossenheit = 0
            machtpunkte = self.machtpunkte  # Machtpunkte aus dem Charakter übernehmen
            wunden = 0  # Kann später durch Spielereignisse verändert werden
            erschoepfung = self.erschoepfung  # Aktuelle Erschöpfung

            # Berechnung der Parade
            kaempfen_fertigkeit = self.fertigkeiten.get('Kämpfen')
            if kaempfen_fertigkeit:
                kaempfen_wert = kaempfen_fertigkeit.wert
            else:
                kaempfen_wert = 4  # Standardwert, wenn Kämpfen nicht vorhanden
            parade = 2 + kaempfen_wert // 2

            # Berechnung der Robustheit
            konstitution_attribut = self.attribute.get('Konstitution')
            if konstitution_attribut:
                konstitution_wert = konstitution_attribut.wert
            else:
                konstitution_wert = 4  # Standardwert, wenn Konstitution nicht vorhanden

            # Gesamtrüstungsschutz berechnen
            gesamt_ruestungsschutz = self.berechne_gesamt_ruestungsschutz()
            gesamt_torso = gesamt_ruestungsschutz.get('Torso', 0)

            # Robustheit berechnen
            robustheit_basis = (konstitution_wert // 2) + 2
            robustheit = robustheit_basis + gesamt_torso

            # Maximale Traglast berechnen
            maximale_traglast = self.berechne_traglast()

            # Gesamtgewicht berechnen
            gesamtgewicht = self.berechne_gesamtgewicht()

            # Zusammenstellen der abgeleiteten Werte
            abgeleitete_werte = {
                'Bewegungsweite': bewegungsweite,
                'Parade': parade,
                'Robustheit': f"{robustheit} ({gesamt_torso})",
                'Machtpunkte': machtpunkte,
                'Wunden': wunden,
                'Erschöpfung': erschoepfung,
                'Bennys': bennys,
                'Entschlossenheit': entschlossenheit,
                'Maximale Traglast': maximale_traglast,
                'Gesamtgewicht': gesamtgewicht
            }

            logging.debug(f"Abgeleitete Werte berechnet: {abgeleitete_werte}")
            return abgeleitete_werte

        except Exception as e:
            logging.error(f"Fehler bei der Berechnung der abgeleiteten Werte: {e}")
            return {}

    def berechne_traglast(self):
        """
        Berechnet die maximale Traglast des Charakters basierend auf Stärke.
        """
        try:
            staerke_attribut = self.attribute.get('Stärke')
            if staerke_attribut:
                staerke_wert = staerke_attribut.wert
            else:
                staerke_wert = 4  # Standardwert, wenn Stärke nicht vorhanden

            maximale_traglast = staerke_wert * 10  # 10 kg pro Punkt Stärke
            logging.debug(f"Maximale Traglast berechnet: {maximale_traglast} kg")
            return maximale_traglast

        except Exception as e:
            logging.error(f"Fehler bei der Berechnung der maximalen Traglast: {e}")
            return 0

    def berechne_gesamtgewicht(self):
        """
        Berechnet das Gesamtgewicht aller ausgewählten Ausrüstungsgegenstände.
        Berücksichtigt die Menge und ob Gegenstände angelegt sind (halbes Gewicht).
        """
        gesamtgewicht = 0

        # Normale Ausrüstung
        for item in self.ausruestung_daten.values():
            if item.menge > 0:
                gesamtgewicht += item.gewicht * item.menge

        # Waffen
        for waffe in self.waffen_daten.values():
            if waffe.menge > 0:
                gewicht = waffe.berechne_gewicht() * waffe.menge
                gesamtgewicht += gewicht

        # Rüstungen
        for ruestung in self.ruestung_daten.values():
            if ruestung.menge > 0:
                gewicht = ruestung.berechne_gewicht() * ruestung.menge
                gesamtgewicht += gewicht

        # Schilde
        for schild in self.schilde_daten.values():
            if schild.menge > 0:
                gewicht = schild.berechne_gewicht() * schild.menge
                gesamtgewicht += gewicht

        self.gesamtgewicht = gesamtgewicht  # Optional: Speichern des Gesamtgewichts
        logging.debug(f"Gesamtgewicht berechnet: {gesamtgewicht} kg")
        return gesamtgewicht

    def berechne_gesamt_ruestungsschutz(self):
        """
        Berechnet den gesamten Rüstungsschutz für die verschiedenen Körperbereiche.
        Berücksichtigt nur angelegte Rüstungen.
        """
        gesamt_torso = 0
        gesamt_arme = 0
        gesamt_beine = 0
        gesamt_kopf = 0

        for ruestung in self.ruestungen.values():
            if ruestung.angelegt:
                gesamt_torso += ruestung.torso
                gesamt_arme += ruestung.arme
                gesamt_beine += ruestung.beine
                gesamt_kopf += ruestung.kopf

        ruestungsschutz = {
            'Torso': gesamt_torso,
            'Arme': gesamt_arme,
            'Beine': gesamt_beine,
            'Kopf': gesamt_kopf
        }
        logging.debug(f"Gesamter Rüstungsschutz berechnet: {ruestungsschutz}")
        return ruestungsschutz

    def ausruestung_nach_setting(self, setting):
        """
        Gibt eine Liste der Ausrüstung für ein bestimmtes Setting zurück.

        :param setting: Das gewünschte Setting ('modern', 'mittelalter', 'futuristisch').
        """
        return [ausr for ausr in self.ausruestung_daten.values() if ausr.setting == setting.lower()]

    def kaufen(self, item, anzahl=1, preis_pro_stueck=None):
        preis_pro_stueck = preis_pro_stueck or item.kosten
        gesamtpreis = preis_pro_stueck * anzahl

        if self.vermoegen < gesamtpreis:
            logging.warning(f"Nicht genügend Vermögen, um {anzahl}x {item.name} zu kaufen.")
            return False

        self.vermoegen -= gesamtpreis
        item.erhoehe_menge(anzahl)
        logging.debug(f"{anzahl}x {item.name} gekauft für insgesamt {gesamtpreis}. Neues Vermögen: {self.vermoegen}.")

        self.berechne_gesamtgewicht()

        maximale_traglast = self.berechne_traglast()
        if self.gesamtgewicht > maximale_traglast:
            if self.erschoepfung < 3:
                self.erschoepfung += 1
                logging.warning(f"Traglast überschritten! Erschöpfung steigt auf {self.erschoepfung}.")
            else:
                logging.warning("Traglast überschritten, Erschöpfung ist bereits maximal.")

        # Hinzufügen zur Ausrüstungsliste
        if item not in self.selected_ausruestung:
            self.selected_ausruestung.append(item)
            self.selected_ausruestung = self.selected_ausruestung  # Neu zuweisen
            Logger.debug(f"{item.name} zur Ausrüstungsliste hinzugefügt.")

        # Hinzufügen zu Waffen oder Rüstungen
        if isinstance(item, Waffe):
            if item not in self.selected_waffen:
                self.selected_waffen.append(item)
                self.selected_waffen = self.selected_waffen  # Neu zuweisen
        elif isinstance(item, Ruestung):
            if item not in self.selected_ruestungen:
                self.selected_ruestungen.append(item)
                self.selected_ruestungen = self.selected_ruestungen  # Neu zuweisen

        return True

    def verkaufen(self, item, anzahl=1, preis_pro_stueck=None):
        if item.menge >= anzahl:
            item.verringere_menge(anzahl)
            preis_pro_stueck = preis_pro_stueck or item.kosten
            gesamtpreis = preis_pro_stueck * anzahl
            self.vermoegen += gesamtpreis
            logging.debug(f"{anzahl}x {item.name} verkauft für insgesamt {gesamtpreis}. Neues Vermögen: {self.vermoegen}.")

            self.berechne_gesamtgewicht()

            maximale_traglast = self.berechne_traglast()
            if self.gesamtgewicht <= maximale_traglast and self.erschoepfung > 0:
                self.erschoepfung -= 1
                logging.info(f"Traglast nicht mehr überschritten. Erschöpfung reduziert auf {self.erschoepfung}.")

            # Entfernen aus den Listen, wenn Menge null ist
            if item.menge == 0:
                if item in self.selected_ausruestung:
                    self.selected_ausruestung.remove(item)
                    self.selected_ausruestung = self.selected_ausruestung  # Neu zuweisen
                if isinstance(item, Waffe) and item in self.selected_waffen:
                    self.selected_waffen.remove(item)
                    self.selected_waffen = self.selected_waffen  # Neu zuweisen
                elif isinstance(item, Ruestung) and item in self.selected_ruestungen:
                    self.selected_ruestungen.remove(item)
                    self.selected_ruestungen = self.selected_ruestungen  # Neu zuweisen

            return True
        else:
            logging.warning(f"Nicht genügend {item.name}, um {anzahl} Stück zu verkaufen.")
            return False

    def berechne_gesamtkosten(self):
        """
        Berechnet die Gesamtkosten der ausgewählten Ausrüstung.
        """
        gesamtkosten = 0
        for ausr in self.ausruestung_daten.values():
            if ausr.ausgewaehlt:
                gesamtkosten += ausr.kosten * ausr.menge
        for waffe in self.waffen_daten.values():
            if waffe.ausgewaehlt:
                gesamtkosten += waffe.kosten * waffe.menge
        for ruestung in self.ruestung_daten.values():
            if ruestung.ausgewaehlt:
                gesamtkosten += ruestung.kosten * ruestung.menge
        for schild in self.schilde_daten.values():
            if schild.ausgewaehlt:
                gesamtkosten += schild.kosten * schild.menge
        return gesamtkosten
