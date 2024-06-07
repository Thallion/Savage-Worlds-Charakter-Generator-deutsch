import tkinter as tk
import math,json,traceback,inspect, sys 
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
        self.vermoegen = 1000
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
        self.eingabe_attribute()
        self.eingabe_fertigkeiten(self.tabs['Fertigkeiten'].scrollable_frame)  
        self.eingabe_eigenschaften('Mächte', self.model.maechte)
        self.eingabe_eigenschaften('Hintergrund Talente', self.model.hintergrund_talente)
        self.eingabe_eigenschaften('Kampf Talente', self.model.kampf_talente)
        self.eingabe_eigenschaften('Anführer Talente', self.model.anfuehrer_talente)
        self.eingabe_eigenschaften('Macht Talente', self.model.macht_talente)
        self.eingabe_eigenschaften('Experten Talente', self.model.experten_talente)
        self.eingabe_eigenschaften('Sozial Talente', self.model.sozial_talente)
        self.eingabe_eigenschaften('Übersinnliche Talente', self.model.uebersinnliche_talente)
        self.eingabe_eigenschaften('Legendäre Talente', self.model.legendaere_talente)
        self.eingabe_eigenschaften('Handicaps', self.model.handicaps)
        self.eingabe_ausruestung('Ausrüstung')
        self.eingabe_ruestung('Rüstung')
        #self.eingabe_schilde()
        self.eingabe_nahkampf_waffe('Nahkampfwaffen')
        self.eingabe_fernkampf_waffe('Fernkampfwaffen')
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
            else:
                self.model.gesamt_attributsteigerungen -= 1
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
        self.eingabe_attribute()
        self.eingabe_fertigkeiten(self.tabs['Fertigkeiten'].scrollable_frame)
        self.eingabe_konzept()
        self.display_gesamtsteigerungen()

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
        tk.Button(tab, text="Speichern", command=self.speichern_konzept).grid(row=len(labels), column=0)

    @Fehlerbehandlung.handle_errors
    def speichern_konzept(self):
        try:
            self.model.charakter_daten['Konzept']
            self.model.speichern()
            self.ausgabe_fenster(self.model.charakter_daten)
            messagebox.showinfo("Erfolg", "Konzept gespeichert!")
        except Exception as e:
            print(f"An error occurred: {e}")
            messagebox.showerror("Fehler", "Beim Speichern des Konzepts ist ein Fehler aufgetreten.")
     
    @Fehlerbehandlung.handle_errors
    def eingabe_attribute(self):
        tab = self.tabs['Attribute'].scrollable_frame
        for i, (name, wuerfel) in enumerate(self.model.attribute.items()):
            tk.Label(tab, text=name).grid(row=i, column=0, sticky='w')
            tk.Label(tab, text=str(wuerfel)).grid(row=i, column=1, sticky='w')
            for j, richtung in enumerate(['+', '-']):
                tk.Button(tab, text=richtung.capitalize(), command=lambda n=name, r=richtung: self.steigerung_senkung(n, 'Attribute', r)).grid(row=i, column=2 + j, sticky='w')
        tk.Button(tab, text="Speichern", command=self.speichern_attribute).grid(row=len(self.model.attribute), column=0)

    @Fehlerbehandlung.handle_errors
    def speichern_attribute(self):
        self.model.charakter_daten['Attribute'] = {attr: str(wuerfel) for attr, wuerfel in self.model.attribute.items()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        messagebox.showinfo("Erfolg", "Attribute gespeichert!")

    def eingabe_fertigkeiten(self, frame):
        for i, (name, wuerfel) in enumerate(self.model.fertigkeiten.items()):
            # Prüfen, ob die Fertigkeit in den Grundfertigkeiten enthalten ist
            attribut = 'Unbekannt'
            if name in self.model.grundfertigkeiten:
                attribut = 'Grundfertigkeit'

            # Erstellen und platzieren des Labels für den Fertigkeitsnamen mit Attribut
            skill_name_label = tk.Label(frame, text=f"{name} ({attribut})")
            skill_name_label.grid(row=i, column=0, sticky='w')

            # Erstellen und platzieren des Labels für den Fertigkeitswert
            value_text = str(wuerfel)
            if "+" not in value_text and wuerfel.modifikator > 0:
                value_text += f"+{wuerfel.modifikator}"
            elif "+" in value_text and wuerfel.modifikator < 0:
                value_text += f"{wuerfel.modifikator}"
            skill_value_label = tk.Label(frame, text=value_text)
            skill_value_label.grid(row=i, column=1, sticky='w')

            # Erstellen und platzieren der Buttons für das Steigern und Senken der Fertigkeit
            button_steigerung = tk.Button(frame, text='+', command=lambda n=name: self.steigerung_senkung(n, 'Fertigkeiten', '+'))
            button_steigerung.grid(row=i, column=2, sticky='w')
            button_senkung = tk.Button(frame, text='-', command=lambda n=name: self.steigerung_senkung(n, 'Fertigkeiten', '-'))
            button_senkung.grid(row=i, column=3, sticky='w')

        # Hinzufügen des "Speichern" Buttons
        tk.Button(frame, text="Speichern", command=self.speichern_fertigkeiten).grid(row=len(self.model.fertigkeiten), column=0)

    @Fehlerbehandlung.handle_errors
    def speichern_fertigkeiten(self):
        self.model.charakter_daten['Fertigkeiten'] = {fert: str(wuerfel) for fert, wuerfel in self.model.fertigkeiten.items()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        messagebox.showinfo("Erfolg", "Fertigkeiten gespeichert!")

    @Fehlerbehandlung.handle_errors
    def eingabe_eigenschaften(self, tab_name, eigenschaften):
        frame = self.tabs[tab_name].scrollable_frame  # Frame des entsprechenden Tabs
        num_eigenschaften = len(eigenschaften)
        num_columns = 3  # Anzahl der Spalten
        for i, eigenschaft in enumerate(eigenschaften):
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[eigenschaft] = selected
            # Berechnung der Zeile und Spalte basierend auf dem Index
            row = i // num_columns
            column = i % num_columns
            checkbox = tk.Checkbutton(frame, text=eigenschaft, variable=selected)
            checkbox.grid(row=row, column=column, sticky='w')
        # Button an das Ende der letzten Zeile platzieren
        tk.Button(frame, text="Speichern", command=lambda: self.speichern_eigenschaften(tab_name, eigenschaften)).grid(row=(num_eigenschaften // num_columns) + 1, column=0, columnspan=num_columns)

    @Fehlerbehandlung.handle_errors
    def speichern_eigenschaften(self, tab_name, eigenschaften):
        self.model.charakter_daten[tab_name] = {eigenschaft: True for eigenschaft in eigenschaften if self.charakter_daten_selected_fertigkeiten[eigenschaft].get()}

        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        messagebox.showinfo("Erfolg", f"{tab_name} gespeichert!")

    @Fehlerbehandlung.handle_errors

   # Funktion zum Berechnen der Traglast basierend auf der Stärke

    def berechne_traglast(self, staerke_wuerfel):
        wuerfelstufen_gewicht = {
            'd4': 10,
            'd6': 20,
            'd8': 30,
            'd10': 40,
            'd12': 50,
            'd12+1': 60,
            'd12+2': 70
        }
        return wuerfelstufen_gewicht.get(staerke_wuerfel, 0)

    @Fehlerbehandlung.handle_errors

    # Funktion zum Berechnen der Traglast basierend auf der Würfelstufe
    def berechne_traglast(self, wuerfel):
        wuerfelstufen_gewicht = {
            1: 10,
            2: 20,
            3: 30,
            4: 40,
            5: 50,
            6: 60,
            7: 70
        }
        return wuerfelstufen_gewicht.get(wuerfel.stufe, 0)

    @Fehlerbehandlung.handle_errors

    # Funktion zum Aktualisieren der Traglast im ausruestung_tab, ruestung_tab
    def aktualisiere_traglast(self):
        staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        maximale_traglast = self.berechne_traglast(staerke_wuerfel)
        gesamtgewicht = sum(self.model.ausruestung[ausruest]['Gewicht'] for ausruest, selected in self.model.charakter_daten['Ausrüstung'].items() if selected)
        gesamtgewicht = sum(self.model.ruestung[ruest]['Gewicht'] for ruest, selected in self.model.charakter_daten['Rüstung'].items() if selected)

        # Labels für die Anzeige der Traglast und des Gesamtgewichts
        traglast_label = tk.Label(self.tabs['Ausrüstung'], text=f"Maximale Traglast: {maximale_traglast} kg")
        traglast_label.grid(row=len(self.model.ausruestung)+1, column=0, sticky='w')
        gesamtgewicht_label = tk.Label(self.tabs['Ausrüstung'], text=f"Gesamtgewicht der Ausrüstung: {gesamtgewicht} kg")
        gesamtgewicht_label.grid(row=len(self.model.ausruestung)+2, column=0, sticky='w')
        traglast_label = tk.Label(self.tabs['Rüstung'], text=f"Maximale Traglast: {maximale_traglast} kg")
        traglast_label.grid(row=len(self.model.ruestung)+1, column=0, sticky='w')
        gesamtgewicht_label = tk.Label(self.tabs['Rüstung'], text=f"Gesamtgewicht der Rüstung: {gesamtgewicht} kg")
        gesamtgewicht_label.grid(row=len(self.model.ruestung)+2, column=0, sticky='w')
     
        return maximale_traglast, gesamtgewicht
  
    @Fehlerbehandlung.handle_errors
    def kaufe_ausruestung(self, ausruest):
        kosten = self.model.ausruestung[ausruest]['Kosten']
        if self.model.vermoegen >= kosten:
            self.model.vermoegen -= kosten
            return True, f"{ausruest} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diese Ausrüstung zu kaufen."

    @Fehlerbehandlung.handle_errors
    def kaufe_ruestung(self, ruest):
        kosten = self.model.ruestung[ruest]['Kosten']
        if self.model.vermoegen >= kosten:
            self.model.vermoegen -= kosten
            return True, f"{ruest} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diese Rüstung zu kaufen."

    @Fehlerbehandlung.handle_errors
    def kaufe_nahkampfwaffe(self, waffe):
        kosten = self.model.nahkampf_waffe[waffe]['Kosten']
        if self.model.vermoegen >= kosten:
            self.model.vermoegen -= kosten
            return True, f"{waffe} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diese Rüstung zu kaufen."

    @Fehlerbehandlung.handle_errors
    def kaufe_fernkampfwaffe(self, waffe):
        kosten = self.model.fernkampf_waffe[waffe]['Kosten']
        if self.model.vermoegen >= kosten:
            self.model.vermoegen -= kosten
            return True, f"{waffe} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diese Rüstung zu kaufen."

    @Fehlerbehandlung.handle_errors
    def eingabe_ausruestung(self, frame):
        frame = self.tabs['Ausrüstung'].scrollable_frame  # Frame des entsprechenden Tabs
        for i, (ausruest, details) in enumerate(self.model.ausruestung.items()):
            label = tk.Label(frame, text=f"{ausruest} (Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})")
            label.grid(row=i, column=0, sticky='w')
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[ausruest] = selected
            checkbox = tk.Checkbutton(frame, variable=selected, command=lambda a=ausruest: self.kaufe_ausruestung(a))
            checkbox.grid(row=i, column=1, sticky='w')
        tk.Button(frame, text="Speichern", command=self.speichern_ausruestung).grid(row=len(self.model.ausruestung), columnspan=2)
          
    @Fehlerbehandlung.handle_errors
    def speichern_ausruestung(self):
        self.model.charakter_daten['Ausrüstung'] = {ausruest: details for ausruest, details in self.model.ausruestung.items() if self.charakter_daten_selected_fertigkeiten[ausruest].get()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)

        # Berechnung der Traglast für die Messagebox
        staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        maximale_traglast = self.berechne_traglast(staerke_wuerfel)
        gesamtgewicht = sum(self.model.ausruestung[ausruest]['Gewicht'] for ausruest, selected in self.model.charakter_daten['Ausrüstung'].items() if selected)

        messagebox.showinfo("Erfolg", f"Ausrüstung gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg\nVerbleibendes Vermögen: {self.model.vermoegen} Gold")
        #messagebox.showinfo("Erfolg", f"Ausrüstung gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg")            

    @Fehlerbehandlung.handle_errors
    def berechne_gesamt_ruestungsschutz(self):
        gesamt_torso = sum(details['Torso'] for ruest, details in self.model.ruestung.items() if self.charakter_daten_selected_fertigkeiten[ruest].get())
        gesamt_arme = sum(details['Arme'] for ruest, details in self.model.ruestung.items() if self.charakter_daten_selected_fertigkeiten[ruest].get())
        gesamt_beine = sum(details['Beine'] for ruest, details in self.model.ruestung.items() if self.charakter_daten_selected_fertigkeiten[ruest].get())
        gesamt_kopf = sum(details['Kopf'] for ruest, details in self.model.ruestung.items() if self.charakter_daten_selected_fertigkeiten[ruest].get())
        return {
            'Torso': gesamt_torso,
            'Arme': gesamt_arme,
            'Beine': gesamt_beine,
            'Kopf': gesamt_kopf
        }

    @Fehlerbehandlung.handle_errors
    def eingabe_ruestung(self, frame):
        frame = self.tabs['Rüstung'].scrollable_frame  # Frame des entsprechenden Tabs
        for i, (ruest, details) in enumerate(self.model.ruestung.items()):
            label = tk.Label(frame, text=f"{ruest} ")
            label.grid(row=i, column=0, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Torso: {details['Torso']}, Arme: {details['Arme']}, Beine: {details['Beine']}, Kopf: {details['Kopf']})")
            label.grid(row=i, column=1, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})")
            label.grid(row=i, column=2, sticky='w', padx=15, pady=0)
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[ruest] = selected
            checkbox = tk.Checkbutton(frame, variable=selected, command=lambda a=ruest: self.kaufe_ruestung(a))
            checkbox.grid(row=i, column=3, sticky='w')
        tk.Button(frame, text="Speichern", command=self.speichern_ruestung).grid(row=len(self.model.ruestung), columnspan=2)
          
    @Fehlerbehandlung.handle_errors
    def speichern_ruestung(self):
        self.model.charakter_daten['Rüstung'] = {ruest: details for ruest, details in self.model.ruestung.items() if self.charakter_daten_selected_fertigkeiten[ruest].get()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        # Berechnung der Traglast für die Messagebox
        staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        maximale_traglast = self.berechne_traglast(staerke_wuerfel)
        gesamtgewicht = sum(self.model.ruestung[ruest]['Gewicht'] for ruest, selected in self.model.charakter_daten['Rüstung'].items() if selected)
        messagebox.showinfo("Erfolg", f"Rüstung gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg\nVerbleibendes Vermögen: {self.model.vermoegen} Gold")

    @Fehlerbehandlung.handle_errors
    def eingabe_nahkampf_waffe(self, frame):
        frame = self.tabs['Nahkampfwaffen'].scrollable_frame  # Frame des entsprechenden Tabs
        for i, (waffe, details) in enumerate(self.model.nahkampf_waffe.items()):
            label = tk.Label(frame, text=f"{waffe} ")
            label.grid(row=i, column=0, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Schaden: {details['Schaden']}, Mindeststärke: {details['Mindeststärke']})")
            label.grid(row=i, column=1, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})")
            label.grid(row=i, column=2, sticky='w', padx=15, pady=0)
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[waffe] = selected
            checkbox = tk.Checkbutton(frame, variable=selected, command=lambda a=waffe: self.kaufe_nahkampfwaffe(a))
            checkbox.grid(row=i, column=3, sticky='w')
        tk.Button(frame, text="Speichern", command=self.speichern_nahkampf_waffe).grid(row=len(self.model.nahkampf_waffe), columnspan=2)

    @Fehlerbehandlung.handle_errors
    def speichern_nahkampf_waffe(self):
        self.model.charakter_daten['Nahkampfwaffen'] = {waffe: details for waffe, details in self.model.nahkampf_waffe.items() if self.charakter_daten_selected_fertigkeiten[waffe].get()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        # Berechnung der Traglast für die Messagebox
        staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        maximale_traglast = self.berechne_traglast(staerke_wuerfel)
        gesamtgewicht = sum(details['Gewicht'] for details in self.model.charakter_daten['Nahkampfwaffen'].values())
        messagebox.showinfo("Erfolg", f"Nahkampfwaffen gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg\nVerbleibendes Vermögen: {self.model.vermoegen} Gold")

    @Fehlerbehandlung.handle_errors
    def eingabe_fernkampf_waffe(self, frame):
        frame = self.tabs['Fernkampfwaffen'].scrollable_frame  # Frame des entsprechenden Tabs
        for i, (waffe, details) in enumerate(self.model.fernkampf_waffe.items()):
            label = tk.Label(frame, text=f"{waffe} ")
            label.grid(row=i, column=0, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Schaden: {details['Schaden']}, Mindeststärke: {details['Mindeststärke']})")
            label.grid(row=i, column=1, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})")
            label.grid(row=i, column=2, sticky='w', padx=15, pady=0)
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[waffe] = selected
            checkbox = tk.Checkbutton(frame, variable=selected, command=lambda a=waffe: self.kaufe_fernkampfwaffe(a))
            checkbox.grid(row=i, column=3, sticky='w')
        tk.Button(frame, text="Speichern", command=self.speichern_fernkampf_waffe).grid(row=len(self.model.fernkampf_waffe), columnspan=2)

    @Fehlerbehandlung.handle_errors
    def speichern_fernkampf_waffe(self):
        self.model.charakter_daten['Fernkampfwaffen'] = {waffe: details for waffe, details in self.model.fernkampf_waffe.items() if self.charakter_daten_selected_fertigkeiten[waffe].get()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        # Berechnung der Traglast für die Messagebox
        staerke_wuerfel_daten = self.model.charakter_daten['Attribute'].get('Stärke', 'd4')
        seiten, modifikator = map(int, staerke_wuerfel_daten[1:].split('+')) if '+' in staerke_wuerfel_daten else (int(staerke_wuerfel_daten[1:]), 0)
        staerke_wuerfel = Würfel(seiten, modifikator)
        maximale_traglast = self.berechne_traglast(staerke_wuerfel)
        gesamtgewicht = sum(details['Gewicht'] for details in self.model.charakter_daten['Fernkampfwaffen'].values())
        messagebox.showinfo("Erfolg", f"Fernkampfwaffen gespeichert!\nMaximale Traglast: {maximale_traglast} kg\nAktuelle Traglast: {gesamtgewicht} kg\nVerbleibendes Vermögen: {self.model.vermoegen} Gold")
    
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
        for handicap, selected in charakter_daten['Handicaps'].items():
            if selected:
                tk.Label(handicaps_frame, text=handicap, bg='white', fg='black').grid(row=len(charakter_daten['Handicaps']) - 1, column=0, padx=5, pady=2, sticky='w')
        tk.Label(columns[1], text="Talente:", font=("Arial", 14, "bold"), bg='white', fg='black').grid(row=10, column=1, padx=5, pady=5, sticky='w')
        talents_frame = tk.Frame(columns[1], bg='white', bd=1, relief='solid', highlightbackground='black', highlightthickness=1)
        talents_frame.grid(row=11, column=1, sticky='ew', padx=5, pady=5)
        talent_kategorien = [
            'Hintergrund Talente', 'Kampf Talente', 'Anführer Talente', 'Macht Talente',
            'Experten Talente', 'Sozial Talente', 'Übersinnliche Talente', 'Legendäre Talente'
        ]
        for kategorie in talent_kategorien:
            for talent, selected in charakter_daten.get(kategorie, {}).items():
                if selected:
                    tk.Label(talents_frame, text=talent, bg='white', fg='black').grid(row=talents_frame.grid_size()[1] - len(charakter_daten.get(kategorie, {})) + 1, column=0, padx=5, pady=2, sticky='w')

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
        gesamt_ruestungsschutz = self.berechne_gesamt_ruestungsschutz()
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

if __name__ == "__main__":

    # Set default window size to 1600x1400 pixels
    root = tk.Tk()
    root.geometry("1600x1400")
    root.title("Charaktererstellung Savage Worlds")
    model = CharakterModel()
    view = CharakterView(root, model)
    root.mainloop()