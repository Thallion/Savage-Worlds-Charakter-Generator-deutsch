import tkinter as tk
import math,json,traceback,inspect, sys 
import PyInstaller.__main__
from functools import partial
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk, ImageGrab
from Savage_Char_Datenbasis_0_9_1 import *

class Fehlerbehandlung:
    @staticmethod
    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                _, _, tb = sys.exc_info()
                frame = inspect.currentframe().f_back
                frameinfo = inspect.getframeinfo(frame)
                print(f"Fehler in Zeile {frameinfo.lineno} von '{frameinfo.filename}': Datei nicht gefunden: {str(e)}")
            except json.JSONDecodeError as e:
                _, _, tb = sys.exc_info()
                frame = inspect.currentframe().f_back
                frameinfo = inspect.getframeinfo(frame)
                print(f"Fehler in Zeile {frameinfo.lineno} von '{frameinfo.filename}': JSON-Fehler: {str(e)}")
            except KeyError as e:
                _, _, tb = sys.exc_info()
                frame = inspect.currentframe().f_back
                frameinfo = inspect.getframeinfo(frame)
                print(f"Fehler in Zeile {frameinfo.lineno} von '{frameinfo.filename}': Schlüssel-Fehler: {str(e)}")
            except Exception as e:
                _, _, tb = sys.exc_info()
                frame = inspect.currentframe().f_back
                frameinfo = inspect.getframeinfo(frame)
                print(f"Fehler in Zeile {frameinfo.lineno} von '{frameinfo.filename}': Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
                # Optional: Print variable values
                print(f"Variablenwerte:")
                for name, value in kwargs.items():
                    print(f"  - {name}: {value}")
        return wrapper

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)    

class Würfel:

    def __init__(self, seiten, modifikator=0):
        self.seiten = seiten
        self.modifikator = modifikator
        self.stufe = self.berechne_stufe()

    def berechne_stufe(self):
        stufen = {0: 0, 4: 1, 6: 2, 8: 3, 10: 4, 12: 5, 13: 6, 14: 7}
        return stufen.get(self.seiten + self.modifikator, 0)

    def __str__(self):
        if self.modifikator == 0:
            return f"W{self.seiten}"
        else:
            return f"W{self.seiten}{'+' if self.modifikator > 0 else ''}{self.modifikator}"

    @classmethod
    def von_stufe(cls, stufe):
        werte = {0: (4, -2), 1: (4, 0), 2: (6, 0), 3: (8, 0), 4: (10, 0), 5: (12, 0), 6: (12, 1), 7: (12, 2)}
        seiten, modifikator = werte.get(stufe, (4, 0))
        return cls(seiten, modifikator)  

class CharakterModel:
    def __init__(self):
        self.konzept = konzept.copy()
        self.voelker = voelker.copy()
        self.settingregeln = settingregeln.copy()
        self.vermoegen = 10000
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
        self.spezielle_waffe = spezielle_waffe.copy()
        self.fahrzeug_waffe = fahrzeug_waffe.copy()
        self.ausruestung = ausruestung.copy()
        self.ruestung = ruestung.copy()
        self.schilde = schilde.copy()
        self.grundfertigkeiten = grundfertigkeiten.copy()

        # Erstelle und zeige die gemeinsamen Steigerungs-Zähler an
        self.gesamt_attributsteigerungen = 0
        self.gesamt_fertigkeitensteigerungen = 0

        self.tabs = [
            'Settingregeln', 'Konzept', 'Volk', 'Attribute', 'Fertigkeiten', 'Handicaps',
            'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente',
            'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente',
            'Mächte', 'Ausrüstung', 'Rüstung', 'Schilde', 'Nahkampfwaffen', 'Fernkampfwaffen', 
            'Spezielle Waffen','Fahrzeug Waffen', 'Notizen', 'Charakterbogen', 'Export'
        ]

        self.charakter_daten = {
            'Konzept': self.konzept,
            'Volk': self.voelker,
            'Settingregeln': self.settingregeln,
            'Attribute': {attr: str(wuerfel) for attr, wuerfel in self.attribute.items()},
            'Fertigkeiten': {fert: str(wuerfel) for fert, wuerfel in self.fertigkeiten.items()},
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
            'Fernkampfwaffen': {},
            'Spezielle Waffen': {},
            'Fahrzeugwaffen': {}
        }

        self.charakter_daten_selected = {fertigkeit: False for fertigkeit in self.grundfertigkeiten}

    @Fehlerbehandlung.handle_errors
    def speichern_in_datei(self, dateiname):
        with open(dateiname, 'w') as datei:
            json.dump(self.charakter_daten, datei)

    @Fehlerbehandlung.handle_errors
    def laden_aus_datei(self, dateiname):
        with open(dateiname, 'r') as datei:
            self.charakter_daten = json.load(datei)
        self.update_model_from_data()

    @Fehlerbehandlung.handle_errors
    def update_model_from_data(self):
        self.konzept = self.charakter_daten['Konzept']
        self.attribute = {attr: self.wuerfel_von_string(wuerfel) for attr, wuerfel in self.charakter_daten['Attribute'].items()}
        self.fertigkeiten = {fert: self.wuerfel_von_string(wuerfel) for fert, wuerfel in self.charakter_daten['Fertigkeiten'].items()}

    def wuerfel_von_string(self, wuerfel_str):
        # Parse the dice string (e.g., "W8+1") to get the sides and modifier
        if '+' in wuerfel_str:
            seiten, modifikator = map(int, wuerfel_str[1:].split('+'))
        elif '-' in wuerfel_str:
            seiten, modifikator = map(int, wuerfel_str[1:].split('-'))
            modifikator = -modifikator
        else:
            seiten = int(wuerfel_str[1:])
            modifikator = 0
        return Würfel(seiten, modifikator)

    @Fehlerbehandlung.handle_errors
    def berechne_abgeleitete_werte(self):
        # Bewegungsweite ist standardmäßig 6
        bewegungsweite = "6\""
        # Parade ist 2 plus der halbe Kämpfen-Würfel
        kaempfen_wuerfel = self.charakter_daten['Fertigkeiten'].get('Kämpfen', 'd4')
        kaempfen_basis = int(kaempfen_wuerfel[1:].split('-')[0] if '-' in kaempfen_wuerfel else kaempfen_wuerfel[1:].split('+')[0])
        kaempfen_mod = -sum(int(mod) for mod in kaempfen_wuerfel[1:].split('-')[1:]) if '-' in kaempfen_wuerfel else sum(int(mod) for mod in kaempfen_wuerfel[1:].split('+')[1:])
        parade = 2 + math.ceil((kaempfen_basis + kaempfen_mod) / 2)
        # Robustheit ist 2 plus der halbe Konstitution-Würfel, aufgerundet bei ungeraden Werten
        konstitution_wuerfel = self.charakter_daten['Attribute'].get('Konstitution', 'd4')
        konstitution_basis = int(konstitution_wuerfel[1:].split('+')[0])
        konstitution_mod = sum(int(mod) for mod in konstitution_wuerfel[1:].split('+')[1:])
        robustheit = 2 + math.ceil((konstitution_basis + konstitution_mod) / 2)
        return {'Bewegungsweite': bewegungsweite, 'Parade': parade, 'Robustheit': robustheit}

    @Fehlerbehandlung.handle_errors
    def speichern(self):
        self.charakter_daten['Abgeleitete Werte'] = self.berechne_abgeleitete_werte()

    @Fehlerbehandlung.handle_errors
    def berechne_traglast(self):
        wuerfelstufen_gewicht = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70}
        staerke_wuerfel_daten = self.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        return wuerfelstufen_gewicht.get(staerke_wuerfel.stufe, 0)
    
    @Fehlerbehandlung.handle_errors
    def aktualisiere_traglast(self):
        maximale_traglast = self.berechne_traglast()
        gesamtgewicht = self.berechne_gesamtgewicht()

        # Labels für die Anzeige der Traglast und des Gesamtgewichts
        traglast_label = tk.Label(self.tabs['Ausrüstung'], text=f"Maximale Traglast: {maximale_traglast} kg")
        traglast_label.grid(row=len(self.ausruestung)+1, column=0, sticky='w')
        gesamtgewicht_label = tk.Label(self.tabs['Ausrüstung'], text=f"Gesamtgewicht der Ausrüstung: {gesamtgewicht} kg")
        gesamtgewicht_label.grid(row=len(self.ausruestung)+2, column=0, sticky='w')
        traglast_label = tk.Label(self.tabs['Rüstung'], text=f"Maximale Traglast: {maximale_traglast} kg")
        traglast_label.grid(row=len(self.ruestung)+1, column=0, sticky='w')
        gesamtgewicht_label = tk.Label(self.tabs['Rüstung'], text=f"Gesamtgewicht der Rüstung: {gesamtgewicht} kg")
        gesamtgewicht_label.grid(row=len(self.ruestung)+2, column=0, sticky='w')

    def berechne_gesamtgewicht(self):
        gesamtgewicht_ausruestung = sum(item['Gewicht'] for item in self.ausruestung if self.charakter_daten['Ausrüstung'].get(item, False))
        gesamtgewicht_ruestung = sum(item['Gewicht'] for item in self.ruestung if self.charakter_daten['Rüstung'].get(item, False))
        gesamtgewicht_nahkampfwaffen = sum(item['Gewicht'] for item in self.nahkampf_waffe if self.charakter_daten['Nahkampfwaffen'].get(item, False))
        gesamtgewicht_fernkampfwaffen = sum(item['Gewicht'] for item in self.fernkampf_waffe if self.charakter_daten['Fernkampfwaffen'].get(item, False))
        return gesamtgewicht_ausruestung + gesamtgewicht_ruestung + gesamtgewicht_nahkampfwaffen + gesamtgewicht_fernkampfwaffen

    def kaufe_gegenstand(self, gegenstand, gegenstand_typ):
        kosten = getattr(self, gegenstand_typ)[gegenstand]['Kosten']
        if self.vermoegen >= kosten:
            self.vermoegen -= kosten
            self.aktualisiere_traglast()  # Traglast aktualisieren
            return True, f"{gegenstand} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diesen Gegenstand zu kaufen."

    def berechne_gesamt_ruestungsschutz(self):
        gesamt_torso = sum(details['Torso'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_arme = sum(details['Arme'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_beine = sum(details['Beine'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        gesamt_kopf = sum(details['Kopf'] for ruest, details in self.ruestung.items() if self.charakter_daten['Rüstung'].get(ruest, False))
        return {
            'Torso': gesamt_torso,
            'Arme': gesamt_arme,
            'Beine': gesamt_beine,
            'Kopf': gesamt_kopf
        }

class CharakterView:
    # This class represents the view of the character creation application.
    # It includes methods for displaying and interacting with the character data
    def __init__(self, root, model):
        self.root = root
        self.model = model

        # Configure root to expand with window resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.tab_frame = ttk.Frame(self.main_frame)
        self.tab_frame.grid(row=0, column=0, sticky="ns")

        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.grid(row=0, column=1, sticky="nsew")

        # Tabs erstellen
        self.tabs = {}
        self.tab_buttons = {}
        tab_names = [
            'Settingregeln', 'Konzept', 'Volk', 'Attribute', 'Fertigkeiten', 'Handicaps',
            'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente',
            'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente',
            'Mächte', 'Ausrüstung', 'Rüstung', 'Schilde', 'Nahkampfwaffen', 'Fernkampfwaffen', 
            'Spezielle Waffen','Fahrzeug Waffen', 'Notizen', 'Charakterbogen', 'Export'
        ]

        # Remove the tab labels from the notebook
        for name in tab_names:
            tab = ScrollableFrame(self.display_frame)
            tab.grid(row=0, column=0, sticky='nsew')
            tab.grid_remove()
            self.tabs[name] = tab

            button = ttk.Button(self.tab_frame, text=name, command=lambda n=name: self.show_tab(n))
            button.grid(sticky='ew')
            self.tab_buttons[name] = button

        # Configure the main frame to expand
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Configure the display frame to expand
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)

        self.charakter_daten_values_attribute = {}
        self.charakter_daten_values_fertigkeiten = {}
        self.charakter_daten_selected_fertigkeiten = {}

        # Erstelle und zeige die gemeinsamen Steigerungs-Zähler an
        self.gesamt_attributsteigerungen = 0
        self.gesamt_fertigkeitensteigerungen = 0
        # Display initial tabs
        self.eingabe_konzept()

        # Aufrufe der eingabe Funktion mit spezifischer Spaltenanzahl

        self.eingabe('Attribute', self.model.attribute, 'attribute', 1)
        self.eingabe('Fertigkeiten', self.model.fertigkeiten, 'fertigkeiten', 2)
        self.eingabe('Mächte', self.model.maechte, 'eigenschaften', 3)
        self.eingabe('Hintergrund Talente', self.model.hintergrund_talente, 'eigenschaften', 2)
        self.eingabe('Kampf Talente', self.model.kampf_talente, 'eigenschaften', 2)
        self.eingabe('Anführer Talente', self.model.anfuehrer_talente, 'eigenschaften', 1)
        self.eingabe('Macht Talente', self.model.macht_talente, 'eigenschaften', 1)
        self.eingabe('Experten Talente', self.model.experten_talente, 'eigenschaften', 1)
        self.eingabe('Sozial Talente', self.model.sozial_talente, 'eigenschaften', 1)
        self.eingabe('Übersinnliche Talente', self.model.uebersinnliche_talente, 'eigenschaften', 1)
        self.eingabe('Legendäre Talente', self.model.legendaere_talente, 'eigenschaften', 1)
        self.eingabe('Handicaps', self.model.handicaps, 'eigenschaften', 3)
        self.eingabe('Ausrüstung', self.model.ausruestung, 'ausruestung', 3)
        self.eingabe('Rüstung', self.model.ruestung, 'ruestung', 3)
        # self.eingabe('Schilde', self.model.schilde, 'eigenschaften')
        self.eingabe('Nahkampfwaffen', self.model.nahkampf_waffe, 'nahkampf_waffe', 2)
        self.eingabe('Fernkampfwaffen', self.model.fernkampf_waffe, 'fernkampf_waffe', 1)
        #self.eingabe_spezielle_waffe()
        #self.eingabe_fahrzeug_waffe()
        self.eingabe_export()
        self.ausgabe_fenster(self.model.charakter_daten)

        # Standardmäßig das erste Tab anzeigen
        self.show_tab('Settingregeln')      

    def display_gesamtsteigerungen(self):
        #Display the total number of attribute and skill points that have been increased or decreased.
        attribut_label = ttk.Label(self.tabs['Attribute'], text=f"Gesamtsteigerungen Attribute: {self.model.gesamt_attributsteigerungen}")
        attribut_label.grid(row=0, column=0, sticky='w')
        fertigkeiten_label = ttk.Label(self.tabs['Fertigkeiten'], text=f"Gesamtsteigerungen Fertigkeiten: {self.model.gesamt_fertigkeitensteigerungen}")
        fertigkeiten_label.grid(row=0, column=0, sticky='w')

    def show_tab(self, tab_name):
        for name, tab in self.tabs.items():
            if name == tab_name:
                tab.grid()
            else:
                tab.grid_remove()

    @Fehlerbehandlung.handle_errors
    def steigerung_senkung(self, name, art, richtung):
        # This function is used to increase or decrease the skill or attribute level.
        # Parameters:
        # name (str): The name of the skill or attribute.
        # art (str): The type of the skill or attribute, either 'Attribute' or 'Fertigkeiten'.
        # richtung (str): The direction of the change, either '+' for increase or '-' for decrease.
        # Returns:
        # None
        if art == 'Attribute':
            current_stufe = self.model.attribute[name].stufe
            if richtung == '+':
                self.model.gesamt_attributsteigerungen += 1
                self.model.aktualisiere_traglast()  # Traglast aktualisieren
            else:
                self.model.gesamt_attributsteigerungen -= 1
                self.model.aktualisiere_traglast()  # Traglast aktualisieren
        elif art == 'Fertigkeiten':
            current_stufe = self.model.fertigkeiten[name].stufe
            if richtung == '+':
                self.model.gesamt_fertigkeitensteigerungen += 1
            else:
                self.model.gesamt_fertigkeitensteigerungen -= 1
        neue_stufe = current_stufe + (1 if richtung == '+' else -1)
        if art == 'Attribute' and 1 <= neue_stufe <= 7:
            self.model.attribute[name] = Würfel.von_stufe(neue_stufe)
        elif art == 'Fertigkeiten' and 0 <= neue_stufe <= 7:
            self.model.fertigkeiten[name] = Würfel.von_stufe(neue_stufe)
        self.update_view()

    @Fehlerbehandlung.handle_errors
    def update_view(self):
        # Updates the view by destroying all widgets in the 'Attribute' and 'Fertigkeiten' tabs,
        # then recreating the widgets with the updated data.
        # Parameters:
        # None
        # Returns:
        # None
        for tab_name in ['Attribute', 'Fertigkeiten']:
            for widget in self.tabs[tab_name].scrollable_frame.winfo_children():
                widget.destroy()
        self.eingabe('Attribute', self.model.attribute, 'attribute', 1)
        self.eingabe('Fertigkeiten', self.model.fertigkeiten, 'fertigkeiten', 2)        
        self.eingabe_konzept()
        self.display_gesamtsteigerungen()

    @Fehlerbehandlung.handle_errors
    def update_eingabe_felder(self): 
        # Define the categories to update along with the respective data keys
        categories = [
            ('Mächte', self.model.maechte, 'Mächte'),        
            ('Hintergrund Talente', self.model.hintergrund_talente, 'Hintergrund Talente'),
            ('Kampf Talente', self.model.kampf_talente, 'Kampf Talente'),         
            ('Handicaps', self.model.handicaps, 'Handicaps'),
            ('Ausrüstung', self.model.ausruestung, 'Ausrüstung'),
            ('Rüstung', self.model.ruestung, 'Rüstung'),
            ('Nahkampfwaffen', self.model.nahkampf_waffe, 'Nahkampfwaffen'),
            ('Fernkampfwaffen', self.model.fernkampf_waffe, 'Fernkampfwaffen')
        ]

        # Update fields for each category
        for category, model_items, data_key in categories:
            if category not in self.tabs:
                continue

            tab = self.tabs[category].scrollable_frame
            # Clear previous widgets in the tab
            for widget in tab.winfo_children():
                widget.destroy()

            # Populate the tab with new data
            for i, item in enumerate(model_items):
                label = tk.Label(tab, text=item)
                label.grid(row=i, column=0, sticky='w')

                var = tk.BooleanVar(value=item in self.model.charakter_daten[data_key])
                self.charakter_daten_selected_fertigkeiten[item] = var
                checkbox = tk.Checkbutton(tab, variable=var)
                checkbox.grid(row=i, column=1, sticky='w')

    @Fehlerbehandlung.handle_errors
    def speichern(self, typ, daten, item_type, berechnung_traglast=False):
        # Speichert die Daten eines bestimmten Typs im Charakterbogen.

        # Parameters:
        # typ (str): Der Typ der zu speichernden Daten.
        # daten (dict): Die Daten, die gespeichert werden sollen.
        # berechnung_traglast (bool, optional): Gibt an, ob die maximale Traglast berechnet werden soll. Standardmäßig ist es False.

        # Returns:
        # None

        # Raises:
        try:
            if typ == 'Konzept':
                self.model.charakter_daten[typ] = self.model.charakter_daten.get(typ, {})
            elif typ == 'Fertigkeiten':
                self.model.charakter_daten[typ] = {fert: str(wuerfel) for fert, wuerfel in self.model.fertigkeiten.items()}
            elif typ == 'Attribute':
                self.model.charakter_daten[typ] = {attr: str(wuerfel) for attr, wuerfel in self.model.attribute.items()}
            elif typ in ['Ausrüstung', 'Rüstung', 'Nahkampfwaffen', 'Fernkampfwaffen']:
                for item, details in daten.items():
                    if self.charakter_daten_selected_fertigkeiten[item].get():
                        success, message = self.model.kaufe_gegenstand(item, item_type)
                        if success:
                            self.model.charakter_daten[typ][item] = details
                            self.model.aktualisiere_traglast()  # Traglast aktualisieren
                        else:
                            messagebox.showwarning("Warnung", message)
            elif typ in ['Mächte', 'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente', 'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente', 'Handicaps']:
                self.model.charakter_daten[typ] = {eigenschaft: True for eigenschaft in daten if self.charakter_daten_selected_fertigkeiten[eigenschaft].get()}

            self.model.speichern()
            self.ausgabe_fenster(self.model.charakter_daten)

            if typ == 'Attribute':
                messagebox.showinfo("Erfolg", "Attribute gespeichert!")
            elif berechnung_traglast:
                staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
                seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
                staerke_wuerfel = Würfel(seiten, modifikator)
                maximale_traglast = self.model.berechne_traglast()
                
                # Berechne das Gesamtgewicht aller relevanten Gegenstände
                gesamtgewicht = sum(
                    item['Gewicht'] for typ in ['Ausrüstung', 'Rüstung', 'Nahkampfwaffen', 'Fernkampfwaffen']
                    for item in self.model.charakter_daten.get(typ, {}).values()
                )
                
                messagebox.showinfo("Erfolg", f"{typ} gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg\nVerbleibendes Vermögen: {self.model.vermoegen} Gold")
            else:
                messagebox.showinfo("Erfolg", f"{typ} gespeichert!")
        except Exception as e:
            print(f"An error occurred: {e}")
            messagebox.showerror("Fehler", f"Beim Speichern von {typ} ist ein Fehler aufgetreten.")

    @Fehlerbehandlung.handle_errors
    def eingabe_export(self):
        # Use the frame from the 'Export' tab
        tab = self.tabs['Export'].scrollable_frame
        
        # Configure the tab to use grid geometry manager
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Create buttons and place them using grid
        tk.Button(tab, text="Speichern in Datei", command=self.speichern_in_datei).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(tab, text="Laden aus Datei", command=self.laden_aus_datei).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(tab, text="Drucken als PDF", command=self.drucken_als_pdf).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(tab, text="Speichern als PNG", command=self.save_as_image).grid(row=3, column=0, padx=5, pady=5, sticky="ew")

    @Fehlerbehandlung.handle_errors
    def eingabe_konzept(self):
        tab = self.tabs['Konzept'].scrollable_frame
        labels = ['Name (Charakter)', 'Name (Spieler)', 'Geschlecht', 'Alter', 'Profession', 'Beschreibung', 'Hintergrund', 'Sprachen']
        for i, label in enumerate(labels):
            tk.Label(tab, text=label).grid(row=i, column=0, sticky='w')
            tk.Entry(tab).grid(row=i, column=1, sticky='w')
        tk.Button(tab, text="Speichern", command=lambda: self.speichern('Konzept', self.model.charakter_daten['Konzept'])).grid(row=len(labels), column=0)
    
    @Fehlerbehandlung.handle_errors
    def eingabe(self, tab_name, items, item_type, num_columns):
        frame = self.tabs[tab_name].scrollable_frame  # Frame des entsprechenden Tabs

        # Hilfsvariable zur Verfolgung der Zeilenanzahl
        row_count = 0

        def create_label(frame, text, row, column, columnspan=1):
            tk.Label(frame, text=text).grid(row=row, column=column, columnspan=columnspan, sticky='w')

        def create_checkbox(frame, name, row, column):
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[name] = selected
            checkbox = tk.Checkbutton(frame, variable=selected)
            checkbox.grid(row=row, column=column, sticky='w')
            return checkbox

        def create_buttons(frame, name, row, base_col, num_buttons=2):
            for j, richtung in enumerate(['+', '-']):
                tk.Button(frame, text=richtung.capitalize(), command=lambda n=name, r=richtung: self.steigerung_senkung(n, tab_name, r)).grid(row=row, column=base_col + j, sticky='w')

        if isinstance(items, dict):
            for i, (name, details) in enumerate(items.items()):
                row = i // num_columns
                column = i % num_columns

                if item_type == 'attribute':
                    create_label(frame, name, row_count, 0)
                    create_label(frame, str(details), row_count, 1)
                    create_buttons(frame, name, row_count, 2)
                    row_count += 1

                elif item_type == 'fertigkeiten':
                    base_col = column * 4  # Jede Fertigkeit hat 4 Spalten (Name, Wert, + Button, - Button)
                    create_label(frame, name, row, base_col)
                    value_text = str(details)
                    if "+" not in value_text and details.modifikator > 0:
                        value_text += f"+{details.modifikator}"
                    elif "+" in value_text and details.modifikator < 0:
                        value_text += f"{details.modifikator}"
                    create_label(frame, value_text, row, base_col + 1)
                    create_buttons(frame, name, row, base_col + 2)
                    row_count = max(row_count, row + 1)

                elif item_type in ['maechte', 'handicaps']:
                    base_col = column * 2  # Jede Macht und Handicap hat 2 Spalten
                    create_label(frame, name, row, base_col)
                    create_checkbox(frame, name, row, base_col + 1)
                    row_count = max(row_count, row + 1)

                elif item_type in ['ausruestung']:
                    base_col = column * 2  # Jede Ausrüstung hat 2 Spalten
                    label_text = f"{name} (Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})"
                    create_label(frame, label_text, row, base_col)
                    create_checkbox(frame, name, row, base_col + 1)
                    row_count = max(row_count, row + 1)

                elif item_type in ['nahkampf_waffe', 'fernkampf_waffe', 'ruestung']:
                    base_col = column * 2
                    label_text = f"{name} "
                    if item_type in ['nahkampf_waffe', 'fernkampf_waffe']:
                        label_text += f"(Schaden: {details['Schaden']}, Mindeststärke: {details['Mindeststärke']})"
                    if item_type in ['nahkampf_waffe', 'fernkampf_waffe', 'ausruestung']:
                        label_text += f"(Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})"
                    if item_type == 'ruestung':
                        label_text += f"(Torso: {details['Torso']}, Arme: {details['Arme']}, Beine: {details['Beine']}, Kopf: {details['Kopf']})"
                    create_label(frame, label_text, row, base_col)
                    create_checkbox(frame, name, row, base_col + 1)
                    row_count = max(row_count, row + 1)

                elif item_type == 'eigenschaften':
                    create_label(frame, name, row, column * 2)
                    create_checkbox(frame, name, row, column * 2 + 1)
                    row_count = max(row_count, row + 1)

        elif isinstance(items, list):
            for i, item in enumerate(items):
                row = i // num_columns
                column = i % num_columns
                create_label(frame, item, row, column * 2)
                create_checkbox(frame, item, row, column * 2 + 1)
                row_count = max(row_count, row + 1)
        else:
            print(f"Expected a dictionary or list but got {type(items)}")

        # Hinzufügen des "Speichern" Buttons am Ende der Liste
        #tk.Button(frame, text="Speichern", command=lambda: self.speichern(tab_name, items, berechnung_traglast=(item_type in ['nahkampf_waffe', 'fernkampf_waffe', 'ausruestung', 'ruestung']))).grid(row=row_count + 1, columnspan=num_columns * 2)
        tk.Button(frame, text="Speichern", command=lambda: self.speichern(tab_name, items, item_type, berechnung_traglast=(item_type in ['nahkampf_waffe', 'fernkampf_waffe', 'ausruestung', 'ruestung']))).grid(row=row_count + 1, columnspan=num_columns * 2)

    @Fehlerbehandlung.handle_errors
    def ausgabe_fenster(self, charakter_daten):
        # Use the frame from the 'Charakterbogen' tab
        tab = self.tabs['Charakterbogen'].scrollable_frame

        # Alte Inhalte des Tabs löschen
        for widget in tab.winfo_children():
            widget.destroy()

        # Create 5 columns
        columns = []
        for i in range(5):
            column_frame = tk.Frame(tab, bg='white')
            column_frame.grid(row=0, column=i, sticky='ns')
            columns.append(column_frame)
        
        tk.Label(columns[1], text="Charakterbogen", font=("Arial", 16, "bold"), bg='white', fg='black').grid(row=0, column=1, columnspan=5)

        # Column 0: Attribute 
        tk.Label(columns[0], text=" ", font=("Arial", 10, "bold"), bg='white', fg='black').grid(row=5, column=2, padx=5, pady=5, sticky='w')
        tk.Label(columns[0], text="Attribute:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=6, column=0, padx=5, pady=5, sticky='w')
        attr_frame = tk.Frame(columns[0], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        attr_frame.grid(row=7, column=0, sticky='nsew', padx=5, pady=5)
        for i, (attr, value) in enumerate(charakter_daten['Attribute'].items(), start=1):
            tk.Label(attr_frame, text=f"{attr}: {value}", bg='white', fg='black').grid(row=i, column=0, sticky='w')

        # Column 0: Fertigkeiten
        tk.Label(columns[0], text="Fertigkeiten:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=9, column=0, padx=5, pady=5, sticky='w')
        fertigkeiten_frame = tk.Frame(columns[0], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        fertigkeiten_frame.grid(row=10, column=0, sticky='nsew', padx=5, pady=5)
        for i, (fert, value) in enumerate(charakter_daten['Fertigkeiten'].items(), start=1):
            if self.model.fertigkeiten[fert].stufe > 0:
                tk.Label(fertigkeiten_frame, text=f"{fert}: {value}", bg='white', fg='black').grid(row=i, column=0, sticky='w')

        # Column 1: Konzept
        tk.Label(columns[1], text=" ", font=("Arial", 16, "bold"), bg='white', fg='black').grid(row=1, column=1, padx=5, pady=5, sticky='w')
        konzept_frame = tk.Frame(columns[1], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        konzept_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        for i, (key, value) in enumerate(charakter_daten['Konzept'].items(), start=1):
            tk.Label(konzept_frame, text=f"{key}: {value}", bg='white', fg='black').grid(row=i, column=1, sticky='w')

        # Column 1: Derived values
        tk.Label(columns[1], text="Abgeleitete Werte:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=4, column=1, padx=5, pady=5, sticky='w')
        derived_frame = tk.Frame(columns[1], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        derived_frame.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        for i, (key, value) in enumerate(charakter_daten['Abgeleitete Werte'].items(), start=1):
            tk.Label(derived_frame, text=f"{key}: {value}", bg='white', fg='black').grid(row=i, column=1, sticky='w')

        # Column 1: Talents & Handicaps
        tk.Label(columns[1], text="Handicaps:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=7, column=1, padx=5, pady=5, sticky='w')
        handicaps_frame = tk.Frame(columns[1], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        handicaps_frame.grid(row=8, column=1, sticky='ew', padx=5, pady=5)
        for i, (handicap, selected) in enumerate(charakter_daten['Handicaps'].items(), start=1):
            if selected:
                tk.Label(handicaps_frame, text=handicap, bg='white', fg='black').grid(row=i, column=0, padx=5, pady=2, sticky='w')
        tk.Label(columns[1], text="Talente:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=10, column=1, padx=5, pady=5, sticky='w')
        talents_frame = tk.Frame(columns[1], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        talents_frame.grid(row=11, column=1, sticky='ew', padx=5, pady=5)
        talent_kategorien = [
            'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente',
            'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente'
        ]
        row_counter = 0
        for kategorie in talent_kategorien:
            for talent, selected in charakter_daten.get(kategorie, {}).items():
                if selected:
                    tk.Label(talents_frame, text=talent, bg='white', fg='black').grid(row=row_counter, column=0, padx=5, pady=2, sticky='w')
                    row_counter += 1

        # Column 2: Wealth, equipment, and weapons
        tk.Label(columns[2], text=" ", font=("Arial", 10, "bold"), bg='white', fg='black').grid(row=2, column=2, padx=5, pady=5, sticky='w')
        tk.Label(columns[2], text="Ausrüstung:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=6, column=2, padx=5, pady=5, sticky='w')
        equipment_frame = tk.Frame(columns[2], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        equipment_frame.grid(row=7, column=2, columnspan=5, sticky='ew', padx=5, pady=5)
        tk.Label(equipment_frame, text=f"{self.model.vermoegen} Gold", bg='white', fg='black').grid(row=8, column=1, padx=5, pady=2, sticky='w')
        for i, (ausruest, details) in enumerate(charakter_daten['Ausrüstung'].items(), start=1):
            tk.Label(equipment_frame, text=ausruest, bg='white', fg='black').grid(row=i, column=1, padx=5, pady=2, sticky='w')

        # Column 2: Rüstung
        tk.Label(columns[2], text="Rüstung:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=9, column=2, padx=5, pady=5, sticky='w')
        ruest_frame = tk.Frame(columns[2], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        ruest_frame.grid(row=10, column=2, columnspan=5, sticky='nsew', padx=5, pady=5)
        for i, (ruest, details) in enumerate(charakter_daten['Rüstung'].items(), start=1):
            tk.Label(ruest_frame, text=f"{ruest} (Torso: {details['Torso']}, Arme: {details['Arme']}, Beine: {details['Beine']}, Kopf: {details['Kopf']})", bg='white', fg='black').grid(row=i, column=0, sticky='w')
        gesamt_ruestungsschutz = self.model.berechne_gesamt_ruestungsschutz()
        tk.Label(ruest_frame, text=f"Gesamt (Torso: {gesamt_ruestungsschutz['Torso']}, Arme: {gesamt_ruestungsschutz['Arme']}, Beine: {gesamt_ruestungsschutz['Beine']}, Kopf: {gesamt_ruestungsschutz['Kopf']})", bg='white', fg='black').grid(row=i+1, column=0, sticky='w')

        # Column 2: Waffen
        tk.Label(columns[2], text="Nahkampfwaffen:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=12, column=2, padx=5, pady=5, sticky='w')
        waffe_frame = tk.Frame(columns[2], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        waffe_frame.grid(row=13, column=2, columnspan=5, sticky='nsew', padx=5, pady=5)
        for i, (waffe, details) in enumerate(charakter_daten['Nahkampfwaffen'].items(), start=1):
            tk.Label(waffe_frame, text=f"{waffe} (Schaden: {details['Schaden']}, Reichweite: {details['Reichweite']}, PB: {details['PB']}, FR: {details['FR']}, Schuss: {details['Schuss']}, Mindeststärke: {details['Mindeststärke']})", bg='white', fg='black').grid(row=i, column=0, sticky='w')
        for i, (waffe, details) in enumerate(charakter_daten['Fernkampfwaffen'].items(), start=len(charakter_daten['Nahkampfwaffen'])+1):
            tk.Label(waffe_frame, text=f"{waffe} (Schaden: {details['Schaden']}, Reichweite: {details['Reichweite']}, PB: {details['PB']}, FR: {details['FR']}, Schuss: {details['Schuss']}, Mindeststärke: {details['Mindeststärke']})", bg='white', fg='black').grid(row=i, column=0, sticky='w')

        # Column 2: Powers
        tk.Label(columns[2], text="Mächte:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=15, column=2, padx=5, pady=5, sticky='w')
        powers_frame = tk.Frame(columns[2], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        powers_frame.grid(row=16, column=2, columnspan=5, sticky='nsew', padx=5, pady=5)
        for i, (macht, selected) in enumerate(charakter_daten['Mächte'].items(), start=1):
            if selected:
                tk.Label(powers_frame, text=macht, bg='white', fg='black').grid(row=i, column=0, sticky='w')

    @Fehlerbehandlung.handle_errors
    def speichern_in_datei(self):
        dateiname = filedialog.asksaveasfilename(defaultextension=".json")
        if dateiname:
            self.model.speichern_in_datei(dateiname)
            messagebox.showinfo("Erfolg", "Charakter gespeichert!")

    @Fehlerbehandlung.handle_errors
    def laden_aus_datei(self):
        dateiname = filedialog.askopenfilename(defaultextension=".json")
        if dateiname:
            self.model.laden_aus_datei(dateiname)
            self.ausgabe_fenster(self.model.charakter_daten)
            self.update_eingabe_felder()
            self.update_view()
            messagebox.showinfo("Erfolg", "Charakter geladen!")

    @Fehlerbehandlung.handle_errors
    def save_as_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return

        self.root.update_idletasks()  # Ensure the GUI is fully updated

        self.show_tab('Charakterbogen')

        # Funktion, die nach der Verzögerung ausgeführt wird
        def capture_image():
            tab = self.tabs['Charakterbogen'].scrollable_frame
            tab.update_idletasks()  # Ensure the frame is fully updated
            
            x = tab.winfo_rootx()+30
            y = tab.winfo_rooty()
            width = 1150
            height = 900

            print(f"Coordinates for image capture: ({x}, {y}, {x + width}, {y + height})")

            # Take screenshot and crop to the size of the 'Charakterbogen' frame
            ImageGrab.grab().crop((x, y, x + width, y + height)).save(file_path)
            messagebox.showinfo("Erfolg", "Charakter als PNG gespeichert!")

        # Verzögerung einbauen (500 Millisekunden)
        self.root.after(500, capture_image)

    @Fehlerbehandlung.handle_errors
    def drucken_als_pdf(self):
        dateiname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if dateiname:
            pdf = FPDF()
            pdf.add_page()
            # Setzen Sie die Schriftart und -größe für den Titel
            pdf.set_font("Arial", 'B', size=16)
            pdf.cell(200, 10, txt="Charakterbogen", ln=True, align='C')
            # Fügen Sie die Daten für jeden Abschnitt hinzu
            for kategorie, daten in self.model.charakter_daten.items():
                pdf.set_font("Arial", 'B', size=12)  # Setzen Sie die Schriftart auf fett für die Kategorie
                pdf.cell(200, 10, txt=kategorie, ln=True, align='L')
                pdf.set_font("Arial", size=12)  # Setzen Sie die Schriftart auf normal für die Daten
                for key, value in daten.items():
                    if isinstance(value, bool) and value:  # Drucken Sie nur die Schlüssel für Boolean-Werte, die True sind
                        pdf.cell(200, 10, txt=key, ln=True, align='L')
                    elif not isinstance(value, bool):  # Drucken Sie Schlüssel und Werte für Nicht-Boolean-Werte
                        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
                pdf.cell(200, 10, txt="", ln=True)  # Fügen Sie einen Abstand nach jeder Kategorie hinzu
            # Speichern Sie das PDF-Dokument
            pdf.output(dateiname)
            messagebox.showinfo("Erfolg", "Charakterbogen als PDF gespeichert!")

if __name__ == "__main__":

    # Set default window size to 1600x1400 pixels
    root = tk.Tk()
    root.geometry("1600x1400")
    root.title("Charaktererstellung Savage Worlds")
    model = CharakterModel()
    view = CharakterView(root, model)
    root.mainloop()
        
PyInstaller.__main__.run([
    os.path.join('my_package', '__main__.py'),
])