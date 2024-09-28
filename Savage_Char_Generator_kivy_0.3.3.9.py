from Savage_Char_Datenbasis_0_9_9 import *
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.logger import Logger
import json, os, logging, ctypes, math, json, functools

def is_hidden(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
        assert attrs != -1
        return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
    except:
        return False

def get_valid_files(directory):
    files = []
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path) and not is_hidden(full_path):
            try:
                open(full_path).close()  # Testen, ob die Datei geöffnet werden kann
                files.append(file)
            except:
                continue
    return files

class CustomFileChooser(BoxLayout):
    def __init__(self, directory, popup, **kwargs):
        super(CustomFileChooser, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.directory = directory
        self.popup = popup  # Übergib das Popup als Attribut
        self.files = get_valid_files(self.directory)
        
        for file in self.files:
            self.add_widget(Button(text=file, on_release=self.select_file))
        
        self.selection = TextInput(text="", multiline=False)
        self.add_widget(self.selection)
        self.add_widget(Button(text="Auswählen", on_release=self.submit_selection))
        
    def select_file(self, instance):
        self.selection.text = os.path.join(self.directory, instance.text)
    
    def submit_selection(self, instance):
        self.popup.dismiss()  # Hier wird das Popup geschlossen

class Fehlerbehandlung:
    @staticmethod
    def handle_errors(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Fehlerbehandlung, z.B. Logging oder Anzeige einer Fehlermeldung
                print(f"An error occurred in {func.__name__}: {e}")
                # Optional: Erneutes Werfen der Ausnahme
                # raise
        return wrapper

class Würfel:
    def __init__(self, value, modifier=0):
        self.value = value
        self.modifier = modifier
        self.stufe = self.berechne_stufe()
        self.total_value = self.calculate_total_value()

    def __str__(self):
        if self.modifier >= 0:
            return f'{self.value}{"+" + str(self.modifier) if self.modifier else ""}'
        else:
            return f'{self.value}{str(self.modifier) if self.modifier else ""}'

    def berechne_stufe(self):
        stufen = {4: 1, 6: 2, 8: 3, 10: 4, 12: 5}
        if self.value in stufen:
            return stufen[self.value] + (self.modifier if self.value == 12 else 0)
        return 0

    def calculate_total_value(self):
        if self.value == 12:
            return self.value + self.modifier
        else:
            return self.value

    def increase(self):
        if self.value == 12 and self.modifier < 2:
            self.modifier += 1
        elif self.value == 4 and self.modifier == -2:   
            self.modifier += 2
        elif self.value < 12:
            self.value += 2
        self.stufe = self.berechne_stufe()
        self.total_value = self.calculate_total_value()
        #print(f"Nachher: self.total_value = {self.total_value}")        

    def decrease(self):
        if self.value == 12 and self.modifier > 0:
            self.modifier -= 1
        elif self.value > 4:
            self.value -= 2
        elif self.value == 4 and self.modifier == 0:  
            self.modifier -= 2
        self.stufe = self.berechne_stufe()
        self.total_value = self.calculate_total_value()
        #print(f"Nachher: self.total_value = {self.total_value}")

    def to_dict(self):
        return {
            'value': self.value,
            'modifier': self.modifier
        }

    @classmethod
    def from_dict(cls, data):
        return cls(value=data['value'], modifier=data.get('modifier', 0))    

class CharakterModel:
    Logger.setLevel('DEBUG')
    def __init__(self, callback=None):
        self.callback = callback
        self.loading = False  # Neuer Lade-Modus
        self.konzept = konzept.copy()
        self.konzept_widgets = {}
        self.details_widgets = {}
        self.details = details.copy()
        self.voelker = voelker.copy()
        self.settingregeln = settingregeln.copy()
        self.vermoegen = 1000
        self.gesamtgewicht = 0
        self.maximale_traglast = 40  
        self.attribute = {attr: Würfel(4) for attr in ['Geschicklichkeit', 'Verstand', 'Willenskraft', 'Stärke', 'Konstitution']}
        self.fertigkeiten = {fert: Würfel(4, -2 if fert not in grundfertigkeiten else 0) for fert in fertigkeiten}
        self.maechte = maechte.copy()
        self.hintergrund_talente = hintergrund_talente.copy()
        self.kampf_talente = kampf_talente.copy()
        self.anfuehrer_talente = anfuehrer_talente.copy()
        self.macht_talente = macht_talente.copy()
        self.experten_talente = experten_talente.copy()
        self.sozial_talente = sozial_talente.copy()
        self.uebersinnliche_talente = uebersinnliche_talente.copy()
        self.legendaere_talente = legendaere_talente.copy()
        self.handicaps = handicaps.copy()
        self.nahkampf_waffe = nahkampf_waffe.copy()
        self.fernkampf_waffe = fernkampf_waffe.copy()
        #self.spezielle_waffe = spezielle_waffe.copy()
        #self.fahrzeug_waffe = fahrzeug_waffe.copy()
        self.ausruestung = ausruestung.copy()
        self.ruestung = ruestung.copy()
        self.schilde = schilde.copy()
        self.grundfertigkeiten = grundfertigkeiten.copy()
        #self.charakter_daten_selected_fertigkeiten = {}

        self.charakter_daten_values_attribute = {}
        self.charakter_daten_values_fertigkeiten = {}

        # Erstelle und zeige die gemeinsamen Steigerungs-Zähler an
        self.gesamt_attributsteigerungen = 0
        self.gesamt_fertigkeitensteigerungen = 0

        self.gear = {
            'Ausrüstung': self.ausruestung,
            'Rüstung': self.ruestung,
            'Schilde': self.schilde,
            'Nahkampfwaffen': self.nahkampf_waffe,
            'Fernkampfwaffen': self.fernkampf_waffe,
            #'Spezielle Waffen': self.spezielle_waffe,
            #'Fahrzeugwaffen': self.fahrzeug_waffe
        }

        self.charakter_daten = {
            'Vermögen': self.vermoegen,
            'Konzept': self.konzept,
            'Details': self.details,
            'Volk': self.voelker,
            'Settingregeln': self.settingregeln,
            'Attribute': self.attribute, # Speichern der Würfel-Objekte direkt
            'Fertigkeiten': self.fertigkeiten, # Speichern der Würfel-Objekte direkt
            'Mächte': {},
            'Abgeleitete Werte': {},
            'Handicaps': {},
            'Hintergrund Talente': {},
            'Kampf Talente': {},
            'Anführer Talente': {},
            'Macht Talente': {},
            'Experten Talente': {},
            'Sozial Talente': {},
            'Übersinnliche Talente': {},
            'Legendäre Talente': {},
            'Ausrüstung': {},
            'Rüstung': {},
            'Schilde': {},
            'Nahkampfwaffen': {},
            'Fernkampfwaffen': {}
            #'Spezielle Waffen': {},
            #'Fahrzeugwaffen': {}
        }

        self.charakter_daten_selected = {key: {} for key in self.charakter_daten.keys()}
        self.charakter_daten_selected_char_details = {settingregel: False for settingregel in settingregeln}
        self.charakter_daten_selected_char_details = {volk: False for volk in voelker}
        self.berechne_traglast()

    @Fehlerbehandlung.handle_errors   
    def increase_attribute(self, attribute_name):
        wuerfel = self.attribute.get(attribute_name)
        if isinstance(wuerfel, Würfel):
            wuerfel.increase()
            # Synchronisieren Sie self.charakter_daten['Attribute']
            self.charakter_daten['Attribute'][attribute_name] = wuerfel
        else:
            logging.error(f"{attribute_name}-Würfel ist kein Würfel-Objekt")
            raise TypeError(f"{attribute_name}-Würfel ist kein Würfel-Objekt")

    @Fehlerbehandlung.handle_errors    
    def decrease_attribute(self, attribute_name):
        wuerfel = self.attribute.get(attribute_name)
        if isinstance(wuerfel, Würfel):
            if wuerfel.value > 4 or (wuerfel.value == 4 and wuerfel.modifier > -2):
                wuerfel.decrease()
                # Synchronisieren Sie self.charakter_daten['Attribute']
                self.charakter_daten['Attribute'][attribute_name] = wuerfel
                self.berechne_traglast()
            else:
                print(f"Das Attribut {attribute_name} kann nicht weiter verringert werden, da es bereits den minimalen Wert erreicht hat.")
        else:
            logging.error(f"{attribute_name}-Würfel ist kein Würfel-Objekt")
            raise TypeError(f"{attribute_name}-Würfel ist kein Würfel-Objekt")

    @Fehlerbehandlung.handle_errors
    def increase_fertigkeit(self, fertigkeit_name):
        wuerfel = self.fertigkeiten.get(fertigkeit_name)
        if isinstance(wuerfel, Würfel):
            wuerfel.increase()
            # Synchronisieren Sie self.charakter_daten['Fertigkeiten']
            self.charakter_daten['Fertigkeiten'][fertigkeit_name] = wuerfel
            self.berechne_traglast()
        else:
            logging.error(f"{fertigkeit_name}-Würfel ist kein Würfel-Objekt")
            raise TypeError(f"{fertigkeit_name}-Würfel ist kein Würfel-Objekt")

    @Fehlerbehandlung.handle_errors
    def decrease_fertigkeit(self, fertigkeit_name):
        wuerfel = self.fertigkeiten.get(fertigkeit_name)
        if isinstance(wuerfel, Würfel):
            if wuerfel.value > 4 or (wuerfel.value == 4 and wuerfel.modifier > -2):
                wuerfel.decrease()
                # Synchronisieren Sie self.charakter_daten['Fertigkeiten']
                self.charakter_daten['Fertigkeiten'][fertigkeit_name] = wuerfel
                self.berechne_traglast()
            else:
                print(f"Die Fertigkeit {fertigkeit_name} kann nicht weiter verringert werden, da sie bereits den minimalen Wert erreicht hat.")
        else:
            logging.error(f"{fertigkeit_name}-Würfel ist kein Würfel-Objekt")
            raise TypeError(f"{fertigkeit_name}-Würfel ist kein Würfel-Objekt")

    @Fehlerbehandlung.handle_errors
    def berechne_abgeleitete_werte(self):
        bewegungsweite = "6\""
        bennys = "3"
        entschlossenheit = "0"
        machtpunkte = "0"
        wunden = "0"
        erschoepfung = "0"
        
        # Berechnung der Parade
        kaempfen_wuerfel = self.charakter_daten.get('Fertigkeiten', {}).get('Kämpfen', Würfel(4))
        parade = 2 + math.ceil(kaempfen_wuerfel.total_value / 2)
        
        # Berechnung der Robustheit
        konstitution_wuerfel = self.charakter_daten.get('Attribute', {}).get('Konstitution', Würfel(4))
        konstitution_wert = konstitution_wuerfel.total_value
        
        # Gesamtrüstungsschutz berechnen
        gesamt_ruestungsschutz = self.berechne_gesamt_ruestungsschutz()
        gesamt_torso = gesamt_ruestungsschutz.get('Torso', 0)
        
        # Robustheit berechnen
        robustheit = math.ceil((konstitution_wert / 2) + 2) + gesamt_torso
        
        # Maximale Traglast berechnen
        try:
            maximale_traglast = self.berechne_traglast()
            print(f"Maximale Traglast: {maximale_traglast} kg")
        except Exception as e:
            print(f"Fehler bei der Berechnung der maximalen Traglast: {e}")
            maximale_traglast = 0
        
        # Gesamtgewicht berechnen
        try:
            gesamtgewicht = self.berechne_gesamtgewicht()
            print(f"Gesamtgewicht: {gesamtgewicht} kg")
        except Exception as e:
            print(f"Fehler bei der Berechnung des Gesamtgewichts: {e}")
            gesamtgewicht = 0
        
        return {
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

    @Fehlerbehandlung.handle_errors
    def berechne_traglast(self):
        attribute = self.charakter_daten.get('Attribute')
        if not attribute:
            logging.error("Keine Attribute gefunden")
            return 0
        
        staerke_wuerfel = attribute.get('Stärke', Würfel(4))
        if not isinstance(staerke_wuerfel, Würfel):
            logging.error("Stärke-Würfel ist kein Würfel-Objekt")
            return 0
        
        total_value = staerke_wuerfel.total_value
        maximale_traglast = total_value * 10  # 10 kg pro Punkt Stärke
        return maximale_traglast
    
    @Fehlerbehandlung.handle_errors
    def berechne_gesamtgewicht(self):
        gesamtgewicht = 0

        kategorien = {
            'Ausrüstung': self.ausruestung,
            'Rüstung': self.ruestung,
            'Nahkampfwaffen': self.nahkampf_waffe,
            'Fernkampfwaffen': self.fernkampf_waffe
        }

        for kategorie, items in kategorien.items():
            if not isinstance(self.charakter_daten, dict):
                logging.error(f"Fehler: charakter_daten ist kein Dictionary")
                continue

            kategorie_daten = self.charakter_daten.get(kategorie)
            if not isinstance(kategorie_daten, dict):
                logging.error(f"Fehler: Keine gültigen Daten für {kategorie} gefunden")
                continue

            if isinstance(items, dict):
                # Für Strukturen wie nahkampf_waffe
                for item_name, item_details in items.items():
                    if kategorie_daten.get(item_name, False):
                        gesamtgewicht += item_details.get('Gewicht', 0)
            else:
                # Für Listen von Items
                for item in items:
                    if isinstance(item, dict):
                        item_name = item.get('Name', '')
                        item_gewicht = item.get('Gewicht', 0)
                    elif isinstance(item, str):
                        item_name = item
                        item_gewicht = kategorie_daten.get(item, {}).get('Gewicht', 0)
                    else:
                        logging.warning(f"Warnung: Ungültiges Item-Format in {kategorie}: {item}")
                        continue

                    if kategorie_daten.get(item_name, False):
                        gesamtgewicht += item_gewicht

        return gesamtgewicht

    @Fehlerbehandlung.handle_errors    
    def verwalte_gegenstand(self, gegenstand, gegenstand_typ, kaufen=True):

        if self.loading:
            return  # Kauf-Funktion nicht ausführen, wenn im Lade-Modus

        logging.debug(f"verwalte_gegenstand aufgerufen mit: {gegenstand}, {gegenstand_typ}, {kaufen}")
        
        if gegenstand_typ not in self.gear:
            return False, f"Ungültiger Gegenstandstyp: {gegenstand_typ}"

        if gegenstand not in self.gear[gegenstand_typ]:
            return False, f"{gegenstand} ist nicht in der Liste der verfügbaren {gegenstand_typ}"

        details = self.gear[gegenstand_typ][gegenstand]
        kosten = details['Kosten']
        gewicht = details['Gewicht']

        if kaufen:
            if self.vermoegen < kosten:
                return False, f"Du hast nicht genug Gold, um {gegenstand} zu kaufen. (Benötigt: {kosten}, Vorhanden: {self.vermoegen})"
            if self.gesamtgewicht + gewicht > self.maximale_traglast:
                return False, f"Der Gegenstand {gegenstand} würde deine maximale Traglast überschreiten. (Aktuell: {self.gesamtgewicht}/{self.maximale_traglast} kg)"
            
            self.vermoegen -= kosten
            self.gesamtgewicht += gewicht
            self.charakter_daten_selected[gegenstand_typ][gegenstand] = True
            aktion = "gekauft und zum Charakterbogen hinzugefügt"
        else:
            if gegenstand not in self.charakter_daten_selected[gegenstand_typ]:
                return False, f"{gegenstand} ist nicht im Besitz des Charakters"
            
            self.vermoegen += kosten
            self.gesamtgewicht -= gewicht
            self.charakter_daten_selected[gegenstand_typ].pop(gegenstand, None)
            aktion = "verkauft und aus dem Charakterbogen entfernt"

        self.berechne_traglast()
        result = True, f"{gegenstand} wurde erfolgreich {aktion}.\nNeues Vermögen: {self.vermoegen} Gold\nNeue Traglast: {self.gesamtgewicht}/{self.maximale_traglast} kg"
        logging.debug(f"verwalte_gegenstand gibt zurück: {result}")
        return result

    @Fehlerbehandlung.handle_errors
    def berechne_gesamt_ruestungsschutz(self):
        gesamt_torso = sum(details['Torso'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_arme = sum(details['Arme'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_beine = sum(details['Beine'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_kopf = sum(details['Kopf'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        return {'Torso': gesamt_torso, 'Arme': gesamt_arme, 'Beine': gesamt_beine, 'Kopf': gesamt_kopf}
    
    @Fehlerbehandlung.handle_errors
    def speichern(self, typ, daten, berechnung_traglast=False):
        print(f"Typ: {typ}")
        print(f"Charakter_daten_selected: {self.charakter_daten_selected}")
        try:
            logging.debug(f"Speichern aufgerufen mit typ: {typ}, daten: {daten}")
            if typ in  ['Konzept','Details']:
                # Sicherstellen, dass die Widgets übergeben wurden
                if isinstance(daten, dict) and all(isinstance(widget, TextInput) for widget in daten.values()):
                    # **Daten aufteilen in Konzept und Details**
                    konzept_data = {key: widget.text for key, widget in daten.items() if key in self.konzept_widgets}
                    details_data = {key: widget.text for key, widget in daten.items() if key in self.details_widgets}
                    
                    self.charakter_daten['Konzept'] = konzept_data
                    self.charakter_daten['Details'] = details_data
                    
                    # **Model-Daten aktualisieren**
                    self.konzept = konzept_data
                    self.details = details_data       
            elif typ == 'Attribute':
                self.attribute = daten  # daten ist ein Dictionary von Würfel-Objekten
                self.charakter_daten[typ] = self.attribute
            elif typ == 'Fertigkeiten':
                self.fertigkeiten = daten  # daten ist ein Dictionary von Würfel-Objekten
                self.charakter_daten[typ] = self.fertigkeiten
            elif typ == 'Settingregeln':
                self.charakter_daten[typ] = {regel: str(wert) for regel, wert in self.settingregeln.items()}
            elif typ in ['Ausrüstung', 'Rüstung', 'Nahkampfwaffen', 'Fernkampfwaffen', 'Schilde', 'Spezielle Waffen', 'Fahrzeugwaffen']:
                if isinstance(daten, dict):
                    selected_items = {
                        item: details for item, details in daten.items()
                        if self.charakter_daten_selected.get(typ, {}).get(item, False)
                    }
                    self.charakter_daten[typ] = selected_items
                    print(f"selected_items: {selected_items}")
                    print(f"Charakter_daten_selected: {self.charakter_daten_selected}")
                else:
                    print(f"Warnung: 'daten' ist kein Dictionary für {typ}")
                    self.charakter_daten[typ] = {}
            elif typ == 'Handicaps':
                print("Speichere Handicaps:")
                self.charakter_daten[typ] = {}
                for handicap, is_selected in self.charakter_daten_selected.get(typ, {}).items():
                    if is_selected:
                        # Hole die vollständigen Daten aus self.handicaps
                        handicap_details = self.handicaps.get(handicap, {})
                        self.charakter_daten[typ][handicap] = handicap_details
                        print(f"  {handicap}: {handicap_details}")
            elif typ in ['Mächte', 'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente', 'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente']:
                if isinstance(daten, dict):
                    selected_items = {item: details for item, details in daten.items() if self.charakter_daten_selected.get(item, False)}
                    self.charakter_daten[typ] = selected_items
                    print(f"Selected {self.charakter_daten_selected}")
                else:
                    print(f"Warning: daten is not a dictionary for {typ}")
                    self.charakter_daten[typ] = {}
            else:
                if isinstance(daten, dict):
                    selected_items = {item: details for item, details in daten.items() if self.charakter_daten_selected.get(typ, {}).get(item, False)}
                    self.charakter_daten[typ] = selected_items
                else:
                    print(f"Warning: daten is not a dictionary for {typ}")
                    self.charakter_daten[typ] = {}

            # Aktualisieren der abgeleiteten Werte
            self.charakter_daten['Abgeleitete Werte'] = self.berechne_abgeleitete_werte()
            print(f"Abgeleitete Werte: {self.charakter_daten['Abgeleitete Werte']}")

            # Erfolgsmeldung
            self.show_popup("Erfolg", f"{typ} gespeichert!")

        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            self.show_popup("Fehler", f"Beim Speichern von {typ} ist ein Fehler aufgetreten.")
            logging.error(f"Fehler beim Speichern von {typ}: {e}")
            raise

    @Fehlerbehandlung.handle_errors
    def speichern_in_datei(self, dateiname):
        try:
            # Konvertieren der Würfel-Objekte in Dictionaries
            attribute_data = {attr: wuerfel.to_dict() for attr, wuerfel in self.attribute.items()}
            fertigkeiten_data = {fert: wuerfel.to_dict() for fert, wuerfel in self.fertigkeiten.items()}
            
            # Erstellen einer Kopie von charakter_daten zum Speichern
            speicher_daten = self.charakter_daten.copy()
            speicher_daten['Attribute'] = attribute_data
            speicher_daten['Fertigkeiten'] = fertigkeiten_data
            speicher_daten['Vermögen'] = self.vermoegen  # Vermögen hinzufügen
            
            with open(dateiname, 'w', encoding='utf-8') as datei:
                json.dump(speicher_daten, datei, ensure_ascii=False, indent=4)
            self.show_popup("Erfolg", f"Charakterdaten wurden in {dateiname} gespeichert.")
        except IOError as e:
            self.show_popup("Fehler", f"Die Datei konnte nicht gespeichert werden: {e}")
        except Exception as e:
            self.show_popup("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    @Fehlerbehandlung.handle_errors
    def is_valid_save_location(self, path):
        # Überprüfen Sie, ob der Pfad gültig ist und keine Systemdatei ist
        system_files = ['C:\\swapfile.sys', 'C:\\pagefile.sys', 'C:\\hiberfil.sys']

        return os.access(os.path.dirname(path), os.W_OK) and path not in system_files

    @Fehlerbehandlung.handle_errors
    def laden_aus_datei(self, dateiname):
        try:
            self.loading = True  # Lade-Modus aktivieren
            if os.path.exists(dateiname):
                with open(dateiname, 'r', encoding='utf-8') as datei:
                    self.charakter_daten = json.load(datei)

                    # Update der ausgewählten Daten
                    self.charakter_daten_selected = self.charakter_daten.get('Charakter_daten_selected', {})

                    # Vermögen laden
                    self.vermoegen = self.charakter_daten.get('Vermögen', 0)
                    self.charakter_daten['Vermögen'] = self.vermoegen  # Synchronisieren

                    # **Konzept und Details aktualisieren**
                    self.konzept = self.charakter_daten.get('Konzept', {})
                    self.details = self.charakter_daten.get('Details', {})

                    # **Widgets aktualisieren**
                    for key, widget in self.konzept_widgets.items():
                        widget.text = self.konzept.get(key, '')
        
                    for key, widget in self.details_widgets.items():
                        widget.text = self.details.get(key, '')

                    # Rekonstruieren der Würfel-Objekte für Attribute
                    attribute_daten = self.charakter_daten.get('Attribute', {})
                    self.attribute = {attr: Würfel.from_dict(wuerfel_dict) for attr, wuerfel_dict in attribute_daten.items()}
                    self.charakter_daten['Attribute'] = self.attribute  # Aktualisieren Sie charakter_daten mit den Würfel-Objekten
                    
                    # Rekonstruieren der Würfel-Objekte für Fertigkeiten
                    fertigkeiten_daten = self.charakter_daten.get('Fertigkeiten', {})
                    self.fertigkeiten = {fert: Würfel.from_dict(wuerfel_dict) for fert, wuerfel_dict in fertigkeiten_daten.items()}
                    self.charakter_daten['Fertigkeiten'] = self.fertigkeiten  # Aktualisieren Sie charakter_daten mit den Würfel-Objekten
        
                    # Liste aller Kategorien, die überprüft werden sollen
                    kategorien = ['Ausrüstung','Rüstung', 'Nahkampfwaffen', 'Fernkampfwaffen', 'Spezielle Waffen', 
                                'Fahrzeugwaffen', 'Handicaps', 'Mächte', 'Hintergrund Talente', 
                                'Kampf Talente', 'Anführer Talente', 'Macht Talente', 'Experten Talente', 
                                'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente']
                    
                    for kategorie in kategorien:
                        if kategorie not in self.charakter_daten_selected:
                            self.charakter_daten_selected[kategorie] = {}
                        
                        if kategorie == 'Handicaps':
                            for item in self.handicaps:
                                self.charakter_daten_selected[kategorie][item] = item in self.charakter_daten.get(kategorie, {})
                        elif kategorie.endswith('Talente') or kategorie == 'Mächte':
                            for item in self.charakter_daten.get(kategorie, {}):
                                self.charakter_daten_selected[item] = True
                        else:
                            for item in self.charakter_daten.get(kategorie, {}):
                                self.charakter_daten_selected[kategorie][item] = True
                                  
                self.show_popup("Erfolg", f"Charakterdaten wurden aus {dateiname} geladen.")
                
                # Rufen Sie den Callback auf, um die UI zu aktualisieren
                if self.callback:
                    self.callback()
            else:
                self.show_popup("Fehler", "Datei existiert nicht.")
        except IOError as e:
            self.show_popup("Fehler", f"Die Datei konnte nicht geöffnet werden: {e}")
        except json.JSONDecodeError as e:
            self.show_popup("Fehler", f"Die Datei enthält ungültiges JSON: {e}")
        except Exception as e:
            self.show_popup("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        finally:
            self.loading = False  # Lade-Modus deaktivieren    
            
    @Fehlerbehandlung.handle_errors
    def show_popup(self, title, message):
        layout = BoxLayout(orientation='vertical', padding=10)
        
        # Label für die Nachricht hinzufügen
        label = Label(text=message)
        layout.add_widget(label)
        
        # Schließen-Button hinzufügen
        close_button = Button(text='Schließen', size_hint=(1, 0.25))
        layout.add_widget(close_button)

        # Logge das Popup
        logging.info(f"Popup: {title} - {message}")

        # Aktionen an den Button binden
        close_button.bind(on_release=lambda instance: popup.dismiss())
        
        # Popup erstellen und öffnen
        popup = Popup(title=title, content=layout, size_hint=(0.75, 0.5))
        popup.open()            

class SavageWorldsApp(App):

    @Fehlerbehandlung.handle_errors
    def init_app(self, dt):
        # Hier können Sie die Initialisierung der App übernehmen
        print("App initialisiert")
        # Führen Sie hier Ihre Initialisierungscode aus

    @Fehlerbehandlung.handle_errors
    def build(self):
        print("Initializing SavageWorldsApp")
        
        Clock.schedule_once(self.init_app, 0)
        Window.size = (1000, 620)
        self.model = CharakterModel(callback=self.model_callback)
        root = BoxLayout(orientation='horizontal')
        
        print("Root layout created")
        
        sidebar = BoxLayout(orientation='vertical', size_hint=(0.2, 1), padding=10, spacing=10)
        self.tab_panel = TabbedPanel(do_default_tab=False, tab_pos='top_mid', size_hint=(0.8, 1))
        self.tab_panel.tab_height = 0
        
        print("Sidebar and tab panel created")

        self.tabs = [
            "Einstellungen", "Settingregeln", "Konzept", "Völker", "Attribute", "Fertigkeiten", "Handicaps",
            "Talente",  # Main button for Talente
            "Mächte", "Ausrüstung", "Rüstung", "Schilde", 
            "Waffen",  # Main button for Waffen 
            "Notizen", "Charakterbogen", "Export"] 
        
        button_labels = self.tabs
        self.button_to_tab = {}
        
        for label in button_labels:
            tab = TabbedPanelItem(text=label, size_hint=(1, 1))
            self.create_tab_content(tab, label)
            self.tab_panel.add_widget(tab)
            
            btn = Button(text=label, size_hint=(1, None), height=30)
            sidebar.add_widget(btn)
            self.button_to_tab[btn] = tab

            btn.bind(on_release=self.on_button_click)

            # Speichern Sie die Referenz auf den Attribute-Tab
            if label == 'Attribute':
                self.attribute_tab = tab
            elif label == 'Fertigkeiten':
                self.fertigkeiten_tab = tab

        # Create and store the charakterbogen_tab
        self.charakterbogen_tab = TabbedPanelItem(text='Charakterbogen', size_hint=(1, 1))
        self.create_bogen_tab(self.charakterbogen_tab, self.model.charakter_daten)
        
        # Initialize talente_tabs and waffen_tabs
        self.talente_tabs = []
        self.waffen_tabs = []
        self.ausruestung_tabs = []   # NEW: List for Ausrüstung
        self.ruestung_tabs = []   # NEW: List for rüstung
        self.handicap_tabs = []      # NEW: List for Handicaps
        self.maechte_tabs = []       # NEW: List for Mächte
        
        self.create_talente_tabs()
        self.create_waffen_tabs()
        self.create_ausruestung_tabs()  # NEW: Create Ausrüstung tabs
        self.create_ruestung_tabs()  # NEW: Create rüstung tabs
        self.create_handicap_tabs()     # NEW: Create Handicaps tabs
        self.create_maechte_tabs()      # NEW: Create Mächte tabs
        
        print("Sidebar and tab panel populated with buttons and tabs")
        
        self.tab_panel.bind(width=self.adjust_tab_width)
        root.add_widget(sidebar)
        root.add_widget(self.tab_panel)
        
        print("Returning root layout from build()")
        
        return root

    @Fehlerbehandlung.handle_errors
    def model_callback(self):
        self.update_ui_after_load()
        self.create_bogen_tab_callback()

    @Fehlerbehandlung.handle_errors
    def create_talente_tabs(self):
        talente_mapping = {
            "Hintergrund Talente": self.model.hintergrund_talente,
            "Kampf Talente": self.model.kampf_talente,
            "Anführer Talente": self.model.anfuehrer_talente,
            "Macht Talente": self.model.macht_talente,
            "Experten Talente": self.model.experten_talente,
            "Sozial Talente": self.model.sozial_talente,
            "Übersinnliche Talente": self.model.uebersinnliche_talente,
            "Legendäre Talente": self.model.legendaere_talente
        }
        for label, items in talente_mapping.items():
            tab = TabbedPanelItem(text=label)
            self.create_tab_with_sorting(tab, items, label)
            self.talente_tabs.append(tab)

    @Fehlerbehandlung.handle_errors    
    def create_waffen_tabs(self):
        waffen_mapping = {
            "Nahkampfwaffen": self.model.nahkampf_waffe,
            "Fernkampfwaffen": self.model.fernkampf_waffe
            #"Spezielle Waffen": self.model.spezielle_waffe,
            #"Fahrzeug Waffen": self.model.fahrzeug_waffe,
        }
        for label, items in waffen_mapping.items():
            tab = TabbedPanelItem(text=label)
            self.create_gear_tab(tab, label, items)
            self.waffen_tabs.append(tab)

    @Fehlerbehandlung.handle_errors
    def create_ausruestung_tabs(self):
        # Create tabs for Ausrüstung and add to ausruestung_tabs
        ausruestung_items = self.model.ausruestung  # Assuming this data exists
        tab = TabbedPanelItem(text='Ausrüstung')
        self.create_gear_tab(tab, 'Ausrüstung', ausruestung_items)
        self.ausruestung_tabs.append(tab)

    @Fehlerbehandlung.handle_errors
    def create_ruestung_tabs(self):
        # Create tabs for Ausrüstung and add to ausruestung_tabs
        ruestung_items = self.model.ruestung  # Assuming this data exists
        tab = TabbedPanelItem(text='Rüstung')
        self.create_gear_tab(tab, 'Rüstung', ruestung_items)
        self.ruestung_tabs.append(tab)

    @Fehlerbehandlung.handle_errors
    def create_handicap_tabs(self):
        # Create tabs for Handicaps and add to handicap_tabs
        handicap_items = self.model.handicaps  # Assuming this data exists
        tab = TabbedPanelItem(text='Handicaps')
        self.create_tab_handicaps(tab, handicap_items, 'Handicaps')
        self.handicap_tabs.append(tab)

    @Fehlerbehandlung.handle_errors
    def create_maechte_tabs(self):
        # Create tabs for Mächte and add to maechte_tabs
        maechte_items = self.model.maechte  # Assuming this data exists
        tab = TabbedPanelItem(text='Mächte')
        self.create_tab_with_sorting(tab, maechte_items, 'Mächte')
        self.maechte_tabs.append(tab)

    @Fehlerbehandlung.handle_errors
    def on_button_click(self, instance):
        # Clear all tabs before adding new ones
        self.tab_panel.clear_tabs()
        
        if instance.text == "Talente":
            self.tab_panel.tab_height = 40
            for tab in self.talente_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.talente_tabs[0])
        elif instance.text == "Waffen":
            self.tab_panel.tab_height = 40
            for tab in self.waffen_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.waffen_tabs[0])
        elif instance.text == "Ausrüstung":
            self.tab_panel.tab_height = 40
            for tab in self.ausruestung_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.ausruestung_tabs[0])
        elif instance.text == "Rüstung":
            self.tab_panel.tab_height = 40
            for tab in self.ruestung_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.ruestung_tabs[0])
        elif instance.text == "Handicaps":
            self.tab_panel.tab_height = 40
            for tab in self.handicap_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.handicap_tabs[0])
        elif instance.text == "Mächte":
            self.tab_panel.tab_height = 40
            for tab in self.maechte_tabs:
                self.tab_panel.add_widget(tab)
            self.tab_panel.switch_to(self.maechte_tabs[0])
        elif instance.text == "Charakterbogen":
            self.tab_panel.clear_tabs()  # Clear again for safety
            self.tab_panel.tab_height = 0
            self.tab_panel.add_widget(self.charakterbogen_tab)
            self.tab_panel.switch_to(self.charakterbogen_tab)
        else:
            self.tab_panel.tab_height = 0
            self.tab_panel.switch_to(self.button_to_tab[instance])

    @Fehlerbehandlung.handle_errors
    def adjust_tab_width(self, instance, value):
        tabs = instance.tab_list
        num_tabs = len(tabs)
        if num_tabs > 0:
            tab_width = instance.width / num_tabs
            for tab in tabs:
                tab.width = tab_width

    @Fehlerbehandlung.handle_errors
    def create_tab_content(self, layout, label):

        # Debugging-Ausgabe für den aktuellen Tab
        print(f"Erstelle Tab für: {label}")

        # Layout leeren
        layout.clear_widgets()

        if label == 'Attribute':
            self.create_tab(layout, self.model.attribute, 'attribute')
        elif label == 'Fertigkeiten':
            self.create_tab(layout, self.model.fertigkeiten, 'fertigkeiten')
        elif label == 'Settingregeln':
            self.create_setting_tab(layout, 'Settingregeln', settingregeln)
        elif label == 'Völker':
            self.create_voelker_tab(layout, 'Völker', voelker)
        elif label == 'Handicaps':
            items = self.model.handicaps
            self.create_tab_handicaps(layout, items, label)
        elif label == 'Ausrüstung':
            self.create_gear_tab(layout, 'Ausrüstung', ausruestung)
        elif label == 'Konzept':
            self.create_konzept_tab(layout)            
        elif label == 'Rüstung':
            self.create_gear_tab(layout, 'Rüstung', ruestung)
        elif label == 'Schilde':
            self.create_gear_tab(layout, 'Schilde', schilde)
        elif label in ['Mächte', 'Talente']:
            items = self.model.maechte if label == 'Mächte' else self.model.hintergrund_talente
            self.create_tab_with_sorting(layout, items, label)
        elif label == 'Export':
            self.create_export_tab(layout)
        else:
            layout.add_widget(Label(text=f"Inhalt für {label}"))

    @Fehlerbehandlung.handle_errors  
    def create_tab_handicaps(self, tab, items, item_type):
        # Initialize 'Handicaps' key in charakter_daten_selected if it doesn't exist
        if 'Handicaps' not in self.model.charakter_daten_selected:
            self.model.charakter_daten_selected['Handicaps'] = {}

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        sort_alpha_button = Button(text='Sortiere Alphabetisch', size_hint=(1, None), height=40)
        sort_difficulty_button = Button(text='Sortiere nach Schwer/Leicht', size_hint=(1, None), height=40)
        
        button_layout.add_widget(sort_alpha_button)
        button_layout.add_widget(sort_difficulty_button)
        
        layout.add_widget(button_layout)
        
        item_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        item_layout.bind(minimum_height=item_layout.setter('height'))
            
        @Fehlerbehandlung.handle_errors
        def populate_item_layout(sorted_items):
            item_layout.clear_widgets()
            for item, details in sorted_items:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
                item_label = Label(text=f"{item} ({details['Stufe']})", size_hint=(0.7, None), height=40)
                item_label.text_size = (200, None)  # Set the width to 200 pixels
                
                @Fehlerbehandlung.handle_errors
                def create_callback(item, checkbox):
                    def callback(instance, value):
                        if value:
                            self.model.charakter_daten_selected['Handicaps'][item] = True
                        else:
                            self.model.charakter_daten_selected['Handicaps'].pop(item, None)
                    return callback
                
                checkbox.bind(active=create_callback(item, checkbox))
                
                # Set the checkbox state based on the selected status
                checkbox.active = self.model.charakter_daten_selected.get('Handicaps', {}).get(item, False)
                
                row.add_widget(checkbox)
                row.add_widget(item_label)
                item_layout.add_widget(row)
        
        sorted_items_alpha = sorted(items.items(), key=lambda item: item[0])
        sorted_items_difficulty = sorted(items.items(), key=lambda item: item[1]['Stufe'])
        
        sort_alpha_button.bind(on_release=lambda instance: populate_item_layout(sorted_items_alpha))
        sort_difficulty_button.bind(on_release=lambda instance: populate_item_layout(sorted_items_difficulty))
        
        populate_item_layout(sorted_items_alpha)  # Default sorting
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(item_layout)
        layout.add_widget(scroll_view)
        
        # Add the save button using the provided function
        self.add_save_button(layout, item_type, items)
        
        tab.add_widget(layout)

    @Fehlerbehandlung.handle_errors
    def create_tab(self, tab, items, item_type):
        layout = GridLayout(cols=4, spacing=0, padding=0, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        def create_callback(item, action, label):
            def callback(instance):
                if action == 'increase':
                    if item_type == 'attribute':
                        self.model.increase_attribute(item)
                    else:
                        self.model.increase_fertigkeit(item)
                else:
                    if item_type == 'attribute':
                        self.model.decrease_attribute(item)
                    else:
                        self.model.decrease_fertigkeit(item)
                    # Aktualisieren des Labels
                label.text = f'{self.model.attribute[item]}' if item_type == 'attribute' else f'{self.model.fertigkeiten[item]}'
                self.refresh_layout(layout, items, create_callback, item_type)
            return callback
        
        self.refresh_layout(layout, items, create_callback, item_type)
        
        # Korrigierte Parameterreihenfolge
        tab.add_widget(self.create_scroll_view(layout, item_type, items))

    @Fehlerbehandlung.handle_errors
    def create_scroll_view(self, item_layout, item_type, items):
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=10, bar_color=[0.1, 0.1, 0.1, 1])
        scroll_view.add_widget(item_layout)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(scroll_view)
        
        # Mapping von item_type zu typ
        if item_type == 'attribute':
            typ = 'Attribute'
        elif item_type == 'fertigkeiten':
            typ = 'Fertigkeiten'
        else:
            typ = item_type
        
        self.add_save_button(layout, typ, items)
        return layout

    @Fehlerbehandlung.handle_errors
    def add_save_button(self, layout, typ, daten):
        save_button = Button(text='Speichern', size_hint_y=None, height=40)
        save_button.bind(on_release=lambda instance: self.save_and_update(typ, daten))
        layout.add_widget(save_button)

    @Fehlerbehandlung.handle_errors
    def save_and_update(self, typ, daten):
        try:
            self.model.speichern(typ, daten)
            self.create_bogen_tab(self.charakterbogen_tab, self.model.charakter_daten)
        except Exception as e:
            logging.error(f"Fehler beim Speichern und Aktualisieren: {e}")
            self.show_popup("Fehler", f"Beim Speichern ist ein Fehler aufgetreten: {e}")

    @Fehlerbehandlung.handle_errors   
    def refresh_layout(self, layout, items, create_callback, typ):
        layout.clear_widgets()
        for item, wuerfel in items.items():
            item_label = Label(text=f'{item}', size_hint=(0.45, None), height=30, halign='left')
            item_label.bind(size=item_label.setter('text_size'))  # Ensure text is wrapped within the label
            wuerfel_label = Label(text=f'{wuerfel}', size_hint=(0.15, None), height=30, halign='left')
            wuerfel_label.bind(size=wuerfel_label.setter('text_size'))  # Ensure text is wrapped within the label
            inc_button = Button(text='+', size_hint=(None, None), size=(30, 30))
            dec_button = Button(text='-', size_hint=(None, None), size=(30, 30))

            inc_button.bind(on_release=create_callback(item, 'increase', wuerfel_label))
            dec_button.bind(on_release=create_callback(item, 'decrease', wuerfel_label))

            layout.add_widget(item_label)
            layout.add_widget(wuerfel_label)
            layout.add_widget(inc_button)
            layout.add_widget(dec_button)  

    @Fehlerbehandlung.handle_errors
    def create_tab_with_sorting(self, tab, items, item_type):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Sortierstatus initialisieren
        self.sort_alpha_ascending = True
        self.sort_rank_ascending = True
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        sort_alpha_button = Button(text='Sortiere Alphabetisch', size_hint=(1, None), height=40)
        sort_rank_button = Button(text='Sortiere nach Rang', size_hint=(1, None), height=40)
        
        button_layout.add_widget(sort_alpha_button)
        button_layout.add_widget(sort_rank_button)
        
        layout.add_widget(button_layout)
        
        item_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        item_layout.bind(minimum_height=item_layout.setter('height'))
        
        # Funktion zum Füllen des Item-Layouts
        @Fehlerbehandlung.handle_errors
        def populate_item_layout(sorted_items):
            item_layout.clear_widgets()
            for item, details in sorted_items:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
        
                # Checkbox-Status setzen
                checkbox.active = self.model.charakter_daten_selected.get(item, False)
        
                item_label = Label(text=item, size_hint=(0.3, None), height=40)
                item_label.text_size = (200, None)
                item_label.halign = 'left'
                item_label.valign = 'middle'
        
                rank_label = Label(text=f'Rang: {details.get("Rang", "Unbekannt")}', size_hint=(0.3, None), height=40)
                rank_label.text_size = (200, None)
                rank_label.halign = 'left'
                rank_label.valign = 'middle'
        
                @Fehlerbehandlung.handle_errors
                def create_callback(item, checkbox):
                    def callback(instance, value):
                        if value:
                            self.model.charakter_daten_selected[item] = True
                        else:
                            self.model.charakter_daten_selected.pop(item, None)
                    return callback
        
                checkbox.bind(active=create_callback(item, checkbox))
        
                row.add_widget(checkbox)
                row.add_widget(item_label)
                row.add_widget(rank_label)
                item_layout.add_widget(row)
        
        # Funktion zum Umschalten der alphabetischen Sortierung
        def toggle_sort_alpha(instance):
            if self.sort_alpha_ascending:
                sorted_items = sorted(items.items(), key=lambda item: item[0], reverse=False)
                sort_alpha_button.text = 'Sortiere Alphabetisch'
            else:
                sorted_items = sorted(items.items(), key=lambda item: item[0], reverse=True)
                sort_alpha_button.text = 'Sortiere Alphabetisch'
            self.sort_alpha_ascending = not self.sort_alpha_ascending
            populate_item_layout(sorted_items)
        
        # Funktion zum Umschalten der Rangsortierung
        def toggle_sort_rank(instance):
            if self.sort_rank_ascending:
                sorted_items = sorted(items.items(), key=lambda item: item[1].get("Rang", ""), reverse=False)
                sort_rank_button.text = 'Sortiere nach Rang'
            else:
                sorted_items = sorted(items.items(), key=lambda item: item[1].get("Rang", ""), reverse=True)
                sort_rank_button.text = 'Sortiere nach Rang'
            self.sort_rank_ascending = not self.sort_rank_ascending
            populate_item_layout(sorted_items)
        
        # Bindet die Umschaltfunktionen an die Schaltflächen
        sort_alpha_button.bind(on_release=toggle_sort_alpha)
        sort_rank_button.bind(on_release=toggle_sort_rank)
        
        # Initiale Sortierung
        sorted_items_alpha = sorted(items.items(), key=lambda item: item[0], reverse=False)
        populate_item_layout(sorted_items_alpha)
        
        # ScrollView hinzufügen
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=10, bar_color=[0.1, 0.1, 0.1, 1])
        scroll_view.add_widget(item_layout)
        layout.add_widget(scroll_view)
        
        self.add_save_button(layout, item_type, items)
        tab.add_widget(layout)

    @Fehlerbehandlung.handle_errors
    def create_gear_callback(self, item, checkbox, gear_name):
        def callback(instance, value):
            logging.debug(f"Checkbox for {item} in {gear_name} changed to {value}")
            
            # Prüfen Sie den aktuellen Zustand des Gegenstands
            current_state = self.model.charakter_daten_selected.get(gear_name, {}).get(item, False)
            
            # Nur fortfahren, wenn sich der Zustand tatsächlich geändert hat
            if current_state != value:
                try:
                    result = self.model.verwalte_gegenstand(item, gear_name, kaufen=value)
                    if result is None or not isinstance(result, tuple) or len(result) != 2:
                        raise ValueError(f"Unerwarteter Rückgabewert von verwalte_gegenstand: {result}")
                    
                    success, message = result
                    if success:
                        if value:
                            self.model.charakter_daten_selected[gear_name][item] = True
                            title = "Kauf erfolgreich"
                        else:
                            self.model.charakter_daten_selected[gear_name].pop(item, None)
                            title = "Verkauf erfolgreich"
                        self.show_popup(title, message)
                    else:
                        checkbox.active = not value  # Setze Checkbox auf vorherigen Zustand zurück
                        if value:
                            title = "Kauf fehlgeschlagen"
                        else:
                            title = "Verkauf fehlgeschlagen"
                        self.show_popup(title, message)
                except Exception as e:
                    logging.exception(f"Fehler beim Verwalten des Gegenstands {item}")
                    checkbox.active = not value  # Setze Checkbox auf vorherigen Zustand zurück
                    self.show_popup("Fehler", str(e))
            else:
                logging.debug(f"Zustand für {item} hat sich nicht geändert. Keine Aktion erforderlich.")
        
        return callback

    @Fehlerbehandlung.handle_errors
    def create_gear_tab(self, tab, gear_name, gear_items):
        if not gear_items:
            logging.warning(f"Warnung: {gear_name} enthält keine Gegenstände.")
            return
        
        # Überprüfen der items in gear_items
        for item_name, details in gear_items.items():
            if not isinstance(details, dict):
                logging.warning(f"Warnung: {item_name} hat unerwarteten Wert: {details}")
                continue
            if 'Gewicht' not in details or 'Kosten' not in details:
                logging.warning(f"Warnung: {item_name} im {gear_name} fehlt Gewicht oder Kosten.")
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)       
    
        # Buttons zum Sortieren hinzufügen
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        sort_alpha_button = Button(text='Sortiere Alphabetisch', size_hint=(1, None), height=40)
        sort_rank_button = Button(text='Sortiere nach Gewicht', size_hint=(1, None), height=40)
        sort_cost_button = Button(text='Sortiere nach Kosten', size_hint=(1, None), height=40)
        
        button_layout.add_widget(sort_alpha_button)
        button_layout.add_widget(sort_rank_button)
        button_layout.add_widget(sort_cost_button)
        
        layout.add_widget(button_layout)
        
        item_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        item_layout.bind(minimum_height=item_layout.setter('height'))

        def populate_item_layout(sorted_items):
            item_layout.clear_widgets()
            
            for item, details in sorted_items:
                if not isinstance(details, dict):
                    logging.warning(f"Warnung: {item} hat unerwarteten Wert: {details}")
                    continue

                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
                item_label = Label(text=item, size_hint=(0.3, None), height=40)
                item_label.text_size = (200, None)  # Set the width to 200 pixels
                weight_label = Label(text=f'Gewicht: {details.get("Gewicht", "")}', size_hint=(0.3, None), height=40)
                weight_label.text_size = (200, None)  # Set the width to 200 pixels
                cost_label = Label(text=f'Kosten: {details.get("Kosten", "")}', size_hint=(0.3, None), height=40)
                cost_label.text_size = (200, None)  # Set the width to 200 pixels

                row.add_widget(checkbox)
                row.add_widget(item_label)
                row.add_widget(weight_label)
                row.add_widget(cost_label)

                checkbox.bind(active=self.create_gear_callback(item, checkbox, gear_name))
                
                item_layout.add_widget(row)

        sorted_items_alpha = sorted(gear_items.items(), key=lambda item: item[0])
        sorted_items_rank = sorted(gear_items.items(), key=lambda item: item[1].get('Gewicht', 0))
        sorted_items_cost = sorted(gear_items.items(), key=lambda item: item[1].get('Kosten', 0))
        
        sort_alpha_button.bind(on_release=lambda instance: populate_item_layout(sorted_items_alpha))
        sort_rank_button.bind(on_release=lambda instance: populate_item_layout(sorted_items_rank))
        sort_cost_button.bind(on_release=lambda instance: populate_item_layout(sorted_items_cost))
        
        # Standardmäßige Sortierung
        sorted_items = sorted(gear_items.items(), key=lambda item: list(gear_items.keys()).index(item[0]))
        populate_item_layout(sorted_items)
        
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=10, bar_color=[0.1, 0.1, 0.1, 1])
        scroll_view.add_widget(item_layout)
        layout.add_widget(scroll_view)
        
        self.add_save_button(layout, gear_name, gear_items)
        tab.add_widget(layout)

    @Fehlerbehandlung.handle_errors
    def callback(self, instance, value):
        gear_name = 'Ausrüstung'
        item = instance.text  # Hier wird angenommen, dass der Text der Checkbox der Item-Name ist

        print(f"Item ausgewählt: {item} in {gear_name}")

        if gear_name not in self.model.charakter_daten_selected:
            self.model.charakter_daten_selected[gear_name] = {}

        self.model.charakter_daten_selected[gear_name][item] = value
        print(f"Modell aktualisiert: {self.model.charakter_daten_selected}")

    @Fehlerbehandlung.handle_errors
    def create_setting_tab(self, tab, char_details_name, char_details_items):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        item_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        item_layout.bind(minimum_height=item_layout.setter('height'))

        def populate_item_layout(items):
            item_layout.clear_widgets()

            for item, details in items.items():
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
                item_label = Label(text=item, size_hint=(0.3, None), height=40)
                item_label.text_size = (200, None)  # Set the width to 200 pixels
                
                def create_callback(item, checkbox):
                    def callback(instance, value):
                        if value:
                            self.model.charakter_daten_selected_char_details[item] = True
                        else:
                            self.model.charakter_daten_selected_char_details[item] = False
                    return callback
                
                checkbox.bind(active=create_callback(item, checkbox))
                
                row.add_widget(checkbox)
                row.add_widget(item_label)
                item_layout.add_widget(row)  # Add row to item_layout

        populate_item_layout(char_details_items)  # Default layout

        tab.add_widget(self.create_scroll_view(item_layout, char_details_name, char_details_items))

    @Fehlerbehandlung.handle_errors
    def create_voelker_tab(self, tab, char_details_name, char_details_items):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        item_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        item_layout.bind(minimum_height=item_layout.setter('height'))

        def populate_item_layout(items):
            item_layout.clear_widgets()

            for item, details in items.items():
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
                checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
                item_label = Label(text=item, size_hint=(0.3, None), height=40)
                item_label.text_size = (200, None)  # Set the width to 200 pixels
                
                # Add a label to display additional details
                details_text = ''
                if 'Handicaps' in details:
                    details_text += 'Handicaps: '+ ', '.join(details['Handicaps']) + '\n'
                if 'Talente' in details:
                    details_text += 'Talente: '+ ', '.join(details['Talente']) + '\n'
                if 'Besonderheiten' in details:
                    details_text += 'Besonderheiten: '+ ', '.join(details['Besonderheiten'])
                
                details_label = Label(text=details_text, size_hint=(0.7, None))
                details_label.text_size = (400, None)  # Set the width to 400 pixels
                details_label.valign = 'top'  # Top-align the text
                
                def create_callback(item, checkbox):
                    def callback(instance, value):
                        if value:
                            self.model.charakter_daten_selected_char_details[item] = True
                        else:
                            self.model.charakter_daten_selected_char_details[item] = False
                    return callback
                
                checkbox.bind(active=create_callback(item, checkbox))
                
                row.add_widget(checkbox)
                row.add_widget(item_label)
                row.add_widget(details_label)  # Add details label to the row
                item_layout.add_widget(row)  # Add row to item_layout

        populate_item_layout(char_details_items)  # Default layout
        
        tab.add_widget(self.create_scroll_view(item_layout, char_details_name, char_details_items))

    @Fehlerbehandlung.handle_errors
    def create_konzept_tab(self, tab):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Konzept Eingabefelder
        for key in self.model.konzept.keys():
            box = BoxLayout(orientation='horizontal')
            box.add_widget(Label(text=key))
            text_input = TextInput(text=self.model.konzept[key])
            box.add_widget(text_input)
            layout.add_widget(box)
            self.model.konzept_widgets[key] = text_input  # Widgets speichern
        
        # Details Eingabefelder
        for key in self.model.details.keys():
            box = BoxLayout(orientation='horizontal')
            box.add_widget(Label(text=key))
            text_input = TextInput(text=self.model.details[key])
            box.add_widget(text_input)
            layout.add_widget(box)
            self.model.details_widgets[key] = text_input  # Widgets speichern
        
        # **Alle Widgets zusammenführen**
        all_widgets = {}
        all_widgets.update(self.model.konzept_widgets)
        all_widgets.update(self.model.details_widgets)
        
        # **Übergeben der kombinierten Widgets an die Speichern-Funktion**
        self.add_save_button(layout, 'Konzept', all_widgets)
        tab.add_widget(layout)


    @Fehlerbehandlung.handle_errors
    def create_export_tab(self, tab):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        save_button = Button(text='Charakterdaten speichern', size_hint_y=None, height=40)
        load_button = Button(text='Charakterdaten laden', size_hint_y=None, height=40)
        
        save_button.bind(on_release=self.save_character_data)
        load_button.bind(on_release=self.load_character_data)
        
        layout.add_widget(save_button)
        layout.add_widget(load_button)
        
        tab.add_widget(layout)

    @Fehlerbehandlung.handle_errors
    def create_bogen_tab(self, tab, char_details):
        # Kombinieren der Charakterdaten
        char_data = {}
        char_data.update(self.model.charakter_daten_selected_char_details)
        char_data.update(self.model.charakter_daten_selected)

        # Sicherstellen, dass Konzept als eigener Abschnitt in char_data existiert
        konzept_data = self.model.charakter_daten.get('Konzept', {})
        if isinstance(konzept_data, dict):
            char_data['Konzept'] = konzept_data
        elif isinstance(konzept_data, str):
            char_data['Konzept'] = {'Beschreibung': konzept_data}

        # Fertigkeiten filtern: Nur Fertigkeiten mit positivem oder neutralem Modifikator anzeigen
        fertigkeiten = {
            key: value for key, value in self.model.charakter_daten.get('Fertigkeiten', {}).items()
            if value.modifier >= 0
        }
        char_data.update(fertigkeiten)
        char_data.update(self.model.charakter_daten.get('Attribute', {}))

        # Vollständige Handicap-Daten verwenden
        char_data['Handicaps'] = self.model.charakter_daten.get('Handicaps', {})

        # Entfernen falscher Werte
        char_data = {key: value for key, value in char_data.items() if value}

        # Ausgabe aller char_data-Variablen (Debugging)
        print("char_data:")
        for key, value in char_data.items():
            print(f"  {key}: {value}")

        # Hauptlayout horizontal (zwei Spalten)
        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)

        ### **Spalte 0: Konzept-Widget fixiert oben, dann ScrollView für Attribute, Fertigkeiten, Handicaps und Talente**
        column0 = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=10)

        # Konzept-Widget erstellen und hinzufügen (fixiert oben)
        konzept_widget = self.create_concept_widget(char_data)
        column0.add_widget(konzept_widget)

        # ScrollView für Attribute, Fertigkeiten, Handicaps und Talente
        column0_scroll = ScrollView(size_hint=(1, 1))
        column0_content = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        column0_content.bind(minimum_height=column0_content.setter('height'))

        # Attribute hinzufügen
        self.add_section_to_column(column0_content, "Attribute:", self.model.charakter_daten.get('Attribute', {}))

        # Fertigkeiten hinzufügen
        self.add_section_to_column(column0_content, "Fertigkeiten:", fertigkeiten)

        # Handicaps hinzufügen
        handicaps_data = {
            f"{item} ({details.get('Stufe', 'Unbekannt')})": ""
            for item, details in char_data.get('Handicaps', {}).items()
        }
        self.add_section_to_column(column0_content, "Handicaps:", handicaps_data)

        # Talente hinzufügen
        self.add_talents_to_column(column0_content)

        column0_scroll.add_widget(column0_content)
        column0.add_widget(column0_scroll)

        ### **Spalte 1: Abgeleitete Werte fixiert oben, dann ScrollView für Ausrüstung, Waffen und Mächte**
        column1 = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=10)

        # Abgeleitete Werte hinzufügen (fixiert oben)
        abgeleitete_werte = self.model.berechne_abgeleitete_werte()
        self.add_section_to_column(column1, "Abgeleitete Werte:", abgeleitete_werte)

        # ScrollView für Ausrüstung, Waffen und Mächte
        column1_scroll = ScrollView(size_hint=(1, 1))
        column1_content = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        column1_content.bind(minimum_height=column1_content.setter('height'))

        # Ausrüstung hinzufügen
        self.add_equipment_to_column(column1_content)

        # Waffen hinzufügen
        self.add_weapons_to_column(column1_content)

        # Mächte hinzufügen
        self.add_powers_to_column(column1_content)

        column1_scroll.add_widget(column1_content)
        column1.add_widget(column1_scroll)

        # Spalten zum Hauptlayout hinzufügen
        layout.add_widget(column0)
        layout.add_widget(column1)

        # Layout zum Tab hinzufügen
        tab.clear_widgets()
        tab.add_widget(layout)

    @Fehlerbehandlung.handle_errors
    def create_bogen_tab_callback(self):
        self.create_bogen_tab(self.charakterbogen_tab, self.model.charakter_daten)

    # Helper methods (to be added to the class)

    @Fehlerbehandlung.handle_errors
    def add_label_to_column(self, column, text, font_size, bold, size_hint_y, height, line_height=None):
        label = Label(
            text=text,
            font_size=font_size,
            bold=bold,
            size_hint_y=size_hint_y,
            height=height,
            size_hint_x=1
        )
        label.text_size = (label.width, None)
        label.bind(size=lambda *args: setattr(label, 'text_size', (label.width, None)))
        label.halign = 'left'
        label.valign = 'top'

        if line_height is not None:
            label.line_height = line_height

        column.add_widget(label)

    @Fehlerbehandlung.handle_errors
    def add_section_to_column(self, column, title, data):
        # Abschnittstitel hinzufügen
        self.add_label_to_column(
            column,
            title,
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=30,
            line_height=1.5
        )

        # Daten hinzufügen
        for key, value in data.items():
            # Wenn value leer ist, nur den Schlüssel anzeigen
            if value == "":
                display_text = key
            else:
                display_text = f"{key}: {value}"
            self.add_label_to_column(
                column,
                display_text,
                font_size=15,
                bold=False,
                size_hint_y=None,
                height=20,
                line_height=1.2
            )

    @Fehlerbehandlung.handle_errors
    def create_concept_widget(self, char_data, line_height=None):
        konzept_widget = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        konzept_widget.bind(minimum_height=konzept_widget.setter('height'))

        # Abschnittstitel hinzufügen
        self.add_label_to_column(konzept_widget, "Konzept:", font_size=24, bold=True, size_hint_y=None, height=30, line_height=line_height)        

        konzept_data = char_data.get('Konzept', {})        
        if isinstance(konzept_data, dict):
            for key, value in konzept_data.items():
                self.add_label_to_column(konzept_widget, f"{key}: {value}", font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)
        elif isinstance(konzept_data, str):
            self.add_label_to_column(konzept_widget, konzept_data, font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)
        else:
            self.add_label_to_column(konzept_widget, "Kein Konzept verfügbar", font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)

        return konzept_widget

    @Fehlerbehandlung.handle_errors
    def add_powers_to_column(self, column, line_height=None):
        # Add the "Mächte:" label
        self.add_label_to_column(column, "Mächte", font_size=24, bold=True, size_hint_y=None, height=30, line_height=line_height)
        self.add_label_to_column(column, "Kosten / Reichweite / Dauer ", font_size=20, bold=True, size_hint_y=None, height=30, line_height=line_height)
        maechte = self.model.charakter_daten.get('Mächte', {})
        if maechte:
            for macht, details in maechte.items():
                text = f"{macht} ({details['Machtpunkte']}, {details['Reichweite']}, {details['Dauer']})"
                self.add_label_to_column(column, text=text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)
        else:
            self.add_label_to_column(column, text="Keine Mächte ausgewählt", font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)

    @Fehlerbehandlung.handle_errors
    def add_weapons_to_column(self, column, line_height=None):
        # Überschrift für Waffen
        self.add_label_to_column(column, "Waffen:", font_size=24, bold=True, size_hint_y=None, height=30, line_height=1.5)
        
        # Nahkampfwaffen Abschnitt
        self.add_label_to_column(column, "Nahkampfwaffen:", font_size=20, bold=True, size_hint_y=None, height=30, line_height=1.5)
        self.add_label_to_column(column, "Schaden / Reichweite / PB / Mindeststärke ", font_size=15, bold=True, size_hint_y=None, height=30, line_height=1.2)

        # Details der Nahkampfwaffen
        for waffe, details in self.model.charakter_daten.get('Nahkampfwaffen', {}).items():
            if isinstance(details, dict):
                text = (f"{waffe} ({details.get('Schaden', 'N/A')}, {details.get('Reichweite', 'N/A')}, {details.get('PB', 'N/A')}, {details.get('Mindeststärke', 'N/A')})")
                self.add_label_to_column(column, text=text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)
            elif details:
                self.add_label_to_column(column, text=waffe, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)
        
        # Fernkampfwaffen Abschnitt
        self.add_label_to_column(column, "Fernkampfwaffen:", font_size=20, bold=True, size_hint_y=None, height=30, line_height=1.5)
        self.add_label_to_column(column, "Schaden / Reichweite / PB / FR / Schuss / Mindeststärke ", font_size=15, bold=True, size_hint_y=None, height=30, line_height=1.2)
       
        # Details der Fernkampfwaffen
        for waffe, details in self.model.charakter_daten.get('Fernkampfwaffen', {}).items():
            if isinstance(details, dict):
                text = (f"{waffe} ({details.get('Schaden', 'N/A')}, {details.get('Reichweite', 'N/A')}, {details.get('PB', 'N/A')}, {details.get('FR', 'N/A')}, {details.get('Schuss', 'N/A')}, {details.get('Mindeststärke', 'N/A')})")
                self.add_label_to_column(column, text=text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)
            elif details:
                self.add_label_to_column(column, text=waffe, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)

    @Fehlerbehandlung.handle_errors
    def add_equipment_to_column(self, column, line_height=None):
        # Überschrift für Ausrüstung
        self.add_label_to_column(column, "Ausrüstung:", font_size=24, bold=True, size_hint_y=None, height=30, line_height=line_height)

        # Vermögen
        vermögen_text = f"Vermögen: {self.model.vermoegen} Gold"
        self.add_label_to_column(column, text=vermögen_text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)

        # Ausrüstungsliste
        for item in self.model.charakter_daten_selected.get('Ausrüstung', {}):
            self.add_label_to_column(column, text=item, font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)

    @Fehlerbehandlung.handle_errors
    def add_armor_to_column(self, column, line_height=None):
        # Überschrift für Rüstung
        self.add_label_to_column(column, "Rüstung:", font_size=24, bold=True, size_hint_y=None, height=30, line_height=line_height)
        
        # Rüstungsdaten abrufen
        ruestung_data = self.model.charakter_daten.get('Rüstung', {})
        
        if ruestung_data:
            for ruest, details in ruestung_data.items():
                # Rüstungsdetails hinzufügen
                text = (f"{ruest} (Torso: {details['Torso']}, Arme: {details['Arme']}, "
                    f"Beine: {details['Beine']}, Kopf: {details['Kopf']})")
                self.add_label_to_column(column, text=text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)
            
            # Gesamt-Rüstungsschutz berechnen und anzeigen
            self.model.gesamt_ruestungsschutz = self.model.berechne_gesamt_ruestungsschutz()
            gesamt_text = (
                f"Gesamt (Torso: {self.model.gesamt_ruestungsschutz['Torso']}, Arme: {self.model.gesamt_ruestungsschutz['Arme']}, "
                f"Beine: {self.model.gesamt_ruestungsschutz['Beine']}, Kopf: {self.model.gesamt_ruestungsschutz['Kopf']})"
            )
            self.add_label_to_column(column, text=gesamt_text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)
        else:
            # Keine Rüstung ausgewählt
            self.add_label_to_column(column, text="Keine Rüstung ausgewählt", font_size=15, bold=False, size_hint_y=None, height=20, line_height=line_height)

    @Fehlerbehandlung.handle_errors
    def add_handicaps_to_column(self, column_content, char_data, line_height=None):
        # Erstellen des Abschnitts für Handicaps
        handicaps_section = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        handicaps_section.bind(minimum_height=handicaps_section.setter('height'))

        # Überschrift für Handicaps
        self.add_label_to_column(handicaps_section, "Handicaps:", font_size=24, bold=True, size_hint_y=None, height=30, line_height=line_height)

        # Durchlaufen der Handicaps und deren Details hinzufügen
        for item, details in char_data.get('Handicaps', {}).items():
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)

            # Text für das Handicap mit Stufe
            item_text = f"{item} ({details.get('Stufe', 'Unbekannt')})"
            
            # Label erstellen und zum BoxLayout hinzufügen
            self.add_label_to_column(row, text=item_text, font_size=15, bold=False, size_hint_y=None, height=20, line_height=1.2)
            handicaps_section.add_widget(row)

        # Abschnitt für Handicaps zur Spalte hinzufügen
        column_content.add_widget(handicaps_section)

    @Fehlerbehandlung.handle_errors
    def add_talents_to_column(self, column, line_height=None):
        # Überschrift für Talente
        self.add_label_to_column(
            column,
            "Talente:",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=30,         # Höhe auf 30 setzen
            line_height=1.5    # Zeilenhöhe auf 1.5 setzen
        )
        
        # Kategorien von Talenten
        talent_kategorien = [
            'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente',
            'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente'
        ]
        
        for kategorie in talent_kategorien:
            kategorie_data = self.model.charakter_daten.get(kategorie, {})            
            if isinstance(kategorie_data, dict):
                for talent, selected in kategorie_data.items():
                    if selected:
                        self.add_label_to_column(
                            column,
                            text=talent,
                            font_size=15,
                            bold=False,
                            size_hint_y=None,
                            height=20,
                            line_height=1.2
                        )
            elif isinstance(kategorie_data, bool) and kategorie_data:
                self.add_label_to_column(
                    column,
                    text=kategorie,
                    font_size=15,
                    bold=False,
                    size_hint_y=None,
                    height=20,
                    line_height=1.2
                )

    @Fehlerbehandlung.handle_errors
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    @Fehlerbehandlung.handle_errors
    def save_character_data(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path=os.path.expanduser('~'))
        content.add_widget(file_chooser)

        filename_input = TextInput(text='character.json', multiline=False, size_hint_y=None, height=40)
        content.add_widget(filename_input)
        
        def save_file(instance):
            path = file_chooser.path
            filename = filename_input.text
            full_path = os.path.join(path, filename)
            
            if self.model.is_valid_save_location(full_path):
                self.model.speichern_in_datei(full_path)
                popup.dismiss()
            else:
                self.show_popup('Fehler', 'Ungültiger Speicherort oder Dateiname.')

        save_button = Button(text='Speichern', size_hint_y=None, height=50)
        save_button.bind(on_release=save_file)
        content.add_widget(save_button)

        popup = Popup(title='Datei speichern', content=content, size_hint=(0.9, 0.9))
        popup.open()

    @Fehlerbehandlung.handle_errors
    def load_character_data(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path=os.path.expanduser('~'))
        content.add_widget(file_chooser)
        
        def load_selected_file(instance):
            selection = file_chooser.selection
            if selection:
                try:
                    dateiname = selection[0]
                    if os.path.isfile(dateiname):
                        self.model.laden_aus_datei(dateiname)
                        #print(f"Selected {self.model.charakter_daten_selected}")
                        popup.dismiss()
                        
                        # Aktualisiere die UI
                        self.update_ui_after_load()
                        
                        self.show_popup('Erfolg', f'Charakterdaten wurden aus {dateiname} geladen.')
                    else:
                        self.show_popup('Fehler', 'Bitte wählen Sie eine gültige Datei aus.')
                except Exception as e:
                    self.show_popup('Fehler', f'Fehler beim Laden der Datei: {str(e)}')
            else:
                self.show_popup('Fehler', 'Bitte wählen Sie eine Datei aus.')

        select_button = Button(text='Auswählen', size_hint_y=None, height=50)
        select_button.bind(on_release=load_selected_file)
        content.add_widget(select_button)

        popup = Popup(title='Datei laden', content=content, size_hint=(0.9, 0.9))
        popup.open()

    @Fehlerbehandlung.handle_errors
    def update_ui_after_load(self):
        # Debug-Ausgabe zur Überprüfung der geladenen Daten
        #print(f"Charakterdaten nach dem Laden: {self.model.charakter_daten_selected}")
        
        logging.debug("Aktualisiere UI nach dem Laden der Daten.")
        logging.debug(f"Geladene Attribute: {self.model.attribute}")      

        # Aktualisiere den Charakterbogen
        self.create_bogen_tab(self.charakterbogen_tab, self.model.charakter_daten)

        # Aktualisieren der Konzept-Widgets
        for key, widget in self.model.konzept_widgets.items():
            widget.text = self.model.konzept.get(key, '')

        # Aktualisieren der Detail-Widgets
        for key, widget in self.model.details_widgets.items():
            widget.text = self.model.details.get(key, '')

        # Aktualisieren Sie den Attribute-Tab
        self.attribute_tab.clear_widgets()
        self.create_tab_content(self.attribute_tab, 'Attribute')
        # Aktualisieren Sie den Fertigkeiten-Tab
        self.fertigkeiten_tab.clear_widgets()
        self.create_tab_content(self.fertigkeiten_tab, 'Fertigkeiten')
        
        if 'Rüstung' not in self.model.charakter_daten_selected:
            self.model.charakter_daten_selected['Rüstung'] = {}

        kategorien = ['Ausrüstung','Rüstung', 'Nahkampfwaffen', 'Fernkampfwaffen', 'Spezielle Waffen', 
                    'Fahrzeugwaffen', 'Handicaps', 'Mächte', 'Hintergrund Talente', 
                    'Kampf Talente', 'Anführer Talente', 'Macht Talente', 'Experten Talente', 
                    'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente']
        
        for kategorie in kategorien:
            tab = next((tab for tab in self.tab_panel.tab_list if tab.text == kategorie), None)
            if tab:
                #print(f"Update Checkboxes für {kategorie}")
                if kategorie.endswith('Talente') or kategorie == 'Mächte':
                    self.update_checkboxes_waffen(tab.content, self.model.charakter_daten_selected)
                    self.update_checkboxes_talente(tab.content, self.model.charakter_daten_selected)                    
                else:
                    self.update_checkboxes_waffen(tab.content, self.model.charakter_daten_selected.get(kategorie, {}))
                    self.update_checkboxes_talente(tab.content, self.model.charakter_daten_selected.get(kategorie, {}))                    
        
        # Aktualisiere auch die Talente- und Waffen-Tabs
        for tab in self.talente_tabs + self.waffen_tabs + self.ausruestung_tabs + self.ruestung_tabs + self.handicap_tabs + self.maechte_tabs :
            #print(f"Update Checkboxes für Tabs: {tab.text}")
            self.update_checkboxes_waffen(tab.content, self.model.charakter_daten_selected)
            self.update_checkboxes_talente(tab.content, self.model.charakter_daten_selected)
            self.update_checkboxes_handicaps(tab.content, self.model.charakter_daten_selected)

        # Checkboxes aktualisieren
        #print(f"Rüstung selected: {self.model.charakter_daten_selected.get('Rüstung', {})}")
        self.update_checkboxes_ruestung(self.ruestung_tabs[0].content, self.model.charakter_daten_selected.get('Rüstung', {}))

    @Fehlerbehandlung.handle_errors
    def update_checkboxes_waffen(self, window, charakter_daten_selected):
        def update_widget(widget):
            if isinstance(widget, CheckBox):
                parent = widget.parent
                if isinstance(parent, BoxLayout):
                    item_name = None
                    for sibling in parent.children:
                        if isinstance(sibling, Label):
                            print(f"Gefundenes Label: {sibling.text}")
                        if sibling != widget and isinstance(sibling, Label):
                            if not ("Kosten" in sibling.text or "Rang" in sibling.text or "Gewicht" in sibling.text):
                                item_name = sibling.text
                                break

        #print(f"Aktualisiere Checkboxes mit Daten: {charakter_daten_selected}")
        update_widget(window)

    @Fehlerbehandlung.handle_errors
    def update_checkboxes_talente(self, window, charakter_daten_selected):
        def update_widget(widget):
            # Überprüfen, ob das aktuelle Widget eine Checkbox ist
            if isinstance(widget, CheckBox):
                parent = widget.parent
                if isinstance(parent, BoxLayout):
                    # Durchsuche die Geschwister-Widgets, um das entsprechende Label/Item zu finden
                    item_name = None
                    for sibling in parent.children:
                        if sibling != widget and isinstance(sibling, Label):
                            # Nur das Hauptlabel, nicht Gewicht, Kosten oder Rang
                            if not ("Kosten" in sibling.text or "Rang" in sibling.text or "Gewicht" in sibling.text):
                                item_name = sibling.text
                                break

                    if item_name is not None:
                        # Zuerst prüfen wir, ob das Item direkt in charakter_daten_selected steht
                        if item_name in charakter_daten_selected:
                            checkbox_status = charakter_daten_selected[item_name]
                            if widget.active != checkbox_status:
                                widget.active = checkbox_status
                                #print(f"Setze Item: {item_name} auf {checkbox_status}")

                        else:
                            # Wenn nicht, prüfen wir, ob das Item in einer der Kategorien (z.B. Handicaps, Mächte) liegt
                            for kategorie, items in charakter_daten_selected.items():
                                if isinstance(items, dict) and item_name in items:
                                    checkbox_status = items[item_name]
                                    if widget.active != checkbox_status:
                                        widget.active = checkbox_status
                                        #print(f"Setze Item aus Kategorie {kategorie}: {item_name} auf {checkbox_status}")
                                    break

            # Wenn das Widget Container für weitere Widgets ist, überprüfe dessen Kinder
            elif hasattr(widget, 'children'):
                for child in widget.children:
                    update_widget(child)

        #print(f"Aktualisiere Checkboxes mit Daten: {charakter_daten_selected}")
        update_widget(window)

    @Fehlerbehandlung.handle_errors
    def update_checkboxes_handicaps(self, window, charakter_daten_selected):
        print("Funktion update_checkboxes_handicaps wurde aufgerufen.")
        
        # Funktion zum Aktualisieren aller Checkboxen für Handicaps
        def update_widget(widget):
            if isinstance(widget, CheckBox):
                parent = widget.parent
                if isinstance(parent, BoxLayout):
                    item_name = None
                    # Finde das passende Label für die Checkbox, um den Namen des Handicaps zu bestimmen
                    for sibling in parent.children:
                        if isinstance(sibling, Label):
                            label_text = sibling.text.split(' ')[0]  # Nur den Handicap-Namen ohne Zusatz "Stufe" holen
                            #print(f"Überprüfe Label: {label_text}")
                            if label_text in charakter_daten_selected.get('Handicaps', {}):
                                item_name = label_text
                                #print(f"Passendes Handicap gefunden: {item_name}")
                                break
                    
                    # Wenn ein passender Name gefunden wurde, setzen wir den Status der Checkbox
                    if item_name:
                        checkbox_status = charakter_daten_selected['Handicaps'][item_name]
                        if widget.active != checkbox_status:
                            widget.active = checkbox_status
                            #print(f"Setze Handicap {item_name} auf {checkbox_status}")
                    # else:
                    #     print("Kein passendes Handicap-Label gefunden.")
        
        # Update alle Widgets im Fenster
        #print(f"Aktualisiere Checkboxes für Handicaps: {charakter_daten_selected['Handicaps']}")
        for widget in window.walk():
            update_widget(widget)

    @Fehlerbehandlung.handle_errors
    def update_checkboxes_ruestung(self, window, charakter_daten_selected):

        print("Funktion update_checkboxes_ruestung wurde aufgerufen.")
        print(f"Charakterdaten geladen: {charakter_daten_selected}")
        ruestung_data = charakter_daten_selected.get('Rüstung', {})
        print(f"Aktualisiere Checkboxes für Rüstung: {ruestung_data}")

        def update_widget(widget):
            if isinstance(widget, CheckBox):
                parent = widget.parent
                if isinstance(parent, BoxLayout):
                    item_name = None
                    for sibling in parent.children:
                        if isinstance(sibling, Label):
                            # Verwende strip(), um sicherzustellen, dass keine unnötigen Leerzeichen verarbeitet werden.
                            label_text = sibling.text.strip()
                            # Extrahiere den tatsächlichen Item-Namen ohne nach Leerzeichen zu splitten
                            if label_text in charakter_daten_selected.get('Rüstung', {}):
                                item_name = label_text
                                break
                    if item_name:
                        checkbox_status = charakter_daten_selected['Rüstung'][item_name]
                        if widget.active != checkbox_status:
                            widget.active = checkbox_status
                            #print(f"Setze Rüstung {item_name} auf {checkbox_status}")

        print(f"Aktualisiere Checkboxes für Rüstung: {charakter_daten_selected.get('Rüstung', {})}")
        
        for widget in window.walk():
            update_widget(widget)

    @Fehlerbehandlung.handle_errors
    def update_attribute_tab(self):
        # Nehmen wir an, Sie haben eine Referenz auf den Attribute-Tab gespeichert
        attribute_tab = self.attribute_tab
        # Löschen Sie den Inhalt des Tabs
        attribute_tab.clear_widgets()
        # Erstellen Sie den Tab neu mit den aktualisierten Daten
        self.create_tab(attribute_tab, self.model.attribute, 'Attribute')

    @Fehlerbehandlung.handle_errors
    def update_fertigkeiten_tab(self):
        fertigkeiten_tab = self.fertigkeiten_tab
        fertigkeiten_tab.clear_widgets()
        self.create_tab(fertigkeiten_tab, self.model.fertigkeiten, 'Fertigkeiten')

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    try:
        SavageWorldsApp().run()
    except Exception as e:
        logging.exception("Unerwarteter Fehler beim Ausführen der App")
