import tkinter as tk
import math,json,traceback,inspect, sys
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from Savage_Char_Datenbasis_0_7 import *

class Fehlerbehandlung:
    @staticmethod
    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                _, _, tb = sys.exc_info()
                filename, lineno, _, _ = traceback.extract_tb(tb)[-1]
                print(f"Fehler in Zeile {lineno}: Datei nicht gefunden: {str(e)}")
            except json.JSONDecodeError as e:
                _, _, tb = sys.exc_info()
                filename, lineno, _, _ = traceback.extract_tb(tb)[-1]
                print(f"Fehler in Zeile {lineno}: JSON-Fehler: {str(e)}")
            except KeyError as e:
                _, _, tb = sys.exc_info()
                filename, lineno, _, _ = traceback.extract_tb(tb)[-1]
                print(f"Fehler in Zeile {lineno}: Schlüssel-Fehler: {str(e)}")
            except Exception as e:
                _, _, tb = sys.exc_info()
                filename, lineno, _, _ = traceback.extract_tb(tb)[-1]
                print(f"Fehler in Zeile {lineno}: Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
        return wrapper

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
        self.vermoegen = 1000
        self.attribute = {attr: Würfel(4) for attr in ['Geschicklichkeit', 'Verstand', 'Willenskraft', 'Stärke', 'Konstitution']}
        self.fertigkeiten = {fert: Würfel(4 if fert in grundfertigkeiten else 0) for fert in fertigkeiten}              
        self.maechte = maechte.copy()
        self.hintergrund_talente = hintergrund_talente.copy()
        self.kampf_talente = kampf_talente.copy()
        self.handicaps = handicaps.copy()
        self.nahkampf_waffe = nahkampf_waffe.copy()
        self.ausruestung = ausruestung.copy()
        self.ruestung = ruestung.copy()
        self.grundfertigkeiten = grundfertigkeiten.copy()
        self.charakter_daten = {
            'Konzept': self.konzept,
            'Attribute': {attr: str(wuerfel) for attr, wuerfel in self.attribute.items()},
            'Fertigkeiten': {fert: str(wuerfel) for fert, wuerfel in self.fertigkeiten.items()},
            'Mächte': {},
            'Abgeleitete Werte': {},
            'Handicaps': {},
            'Hintergrund Talente': {},
            'Kampf Talente': {},
            'Ausrüstung': {},
            'Rüstung': {},
            'Nahkampfwaffen': {}
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

    @Fehlerbehandlung.handle_errors
    def update_model_from_data(self):
        self.konzept.update(self.charakter_daten['Konzept'])
        self.attribute.update({attr: Würfel.von_stufe(int(wuerfel[1:])) for attr, wuerfel in self.charakter_daten['Attribute'].items()})
        self.fertigkeiten.update({fert: Würfel.von_stufe(int(wuerfel[1:])) for fert, wuerfel in self.charakter_daten['Fertigkeiten'].items()})

    @Fehlerbehandlung.handle_errors
    def berechne_abgeleitete_werte(self):
        # Bewegungsweite ist standardmäßig 6
        bewegungsweite = "6\""
        # Parade ist 2 plus der halbe Kämpfen-Würfel
        kaempfen_wuerfel = self.charakter_daten['Fertigkeiten'].get('Kämpfen', 'd4')
        parade = 2 + math.ceil(int(kaempfen_wuerfel[1:].split('+')[0]) / 2)
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
    def __init__(self, root, model):
        self.root = root
        self.model = model

        # Frame für die vertikalen Tabs erstellen
        self.tab_frame = ttk.Frame(root)
        self.tab_frame.pack(side='left', fill='y')

        # Frame für das horizontale Tab-Display erstellen
        self.display_frame = ttk.Frame(root)
        self.display_frame.pack(side='right', expand=True, fill='both')

        # Tabs erstellen
        self.tabs = {}
        self.tab_buttons = {}
        for name in ['Settings', 'Konzept', 'Volk', 'Attribute', 'Fertigkeiten', 'Mächte', 'Hintergrund Talente', 'Kampf Talente', 'Handicaps', 'Ausrüstung', 'Rüstung', 'Nahkampfwaffen', 'Notizen', 'Charakterbogen', 'Export']:
            tab = ttk.Frame(self.display_frame)
            self.tabs[name] = tab

            # Button für jeden Tab im vertikalen Tab-Bereich
            button = ttk.Button(self.tab_frame, text=name, command=lambda n=name: self.show_tab(n))
            button.pack(fill='x')
            self.tab_buttons[name] = button

        self.charakter_daten_values_attribute = {}
        self.charakter_daten_values_fertigkeiten = {}
        self.charakter_daten_selected_fertigkeiten = {}

        self.eingabe_konzept()
        self.eingabe_attribute()
        self.eingabe_fertigkeiten()
        self.eingabe_eigenschaften('Mächte', self.model.maechte)
        self.eingabe_eigenschaften('Hintergrund Talente', self.model.hintergrund_talente)
        self.eingabe_eigenschaften('Kampf Talente', self.model.kampf_talente)
        self.eingabe_eigenschaften('Handicaps', self.model.handicaps)
        self.eingabe_ausruestung()
        self.eingabe_ruestung()
        self.eingabe_nahkampf_waffe()
        self.eingabe_export()
        self.ausgabe_fenster(self.model.charakter_daten)

        # Standardmäßig das erste Tab anzeigen
        self.show_tab('Settings')

    @Fehlerbehandlung.handle_errors
    def show_tab(self, tab_name):
        # Alle Tabs verstecken
        for tab in self.tabs.values():
            tab.pack_forget()

        # Das ausgewählte Tab anzeigen
        self.tabs[tab_name].pack(expand=True, fill='both')

    @Fehlerbehandlung.handle_errors
    def steigerung_senkung(self, name, art, richtung):
        if art == 'Attribute':
            current_stufe = self.model.attribute[name].stufe
        elif art == 'Fertigkeiten':
            current_stufe = self.model.fertigkeiten[name].stufe

        neue_stufe = current_stufe + (1 if richtung == '+' else -1)

        if art == 'Attribute' and 1 <= neue_stufe <= 7:
            self.model.attribute[name] = Würfel.von_stufe(neue_stufe)
        elif art == 'Fertigkeiten' and 0 <= neue_stufe <= 7:
            self.model.fertigkeiten[name] = Würfel.von_stufe(neue_stufe)

        self.update_view()

    @Fehlerbehandlung.handle_errors
    def update_view(self):
        for tab_name in ['Attribute', 'Fertigkeiten']:
            for widget in self.tabs[tab_name].winfo_children():
                widget.destroy()
        self.eingabe_attribute()
        self.eingabe_fertigkeiten()

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
            messagebox.showinfo("Erfolg", "Charakter geladen!")

    @Fehlerbehandlung.handle_errors
    def update_eingabe_felder(self):
        # Update Attribute
        tab = self.tabs['Attribute']
        for i, (name, wuerfel) in enumerate(self.model.attribute.items()):
            current_value = self.model.charakter_daten['Attribute'].get(name, 'd4')
            label_list = tab.grid_slaves(row=i, column=1)
            if label_list:
                label_list[0].config(text=current_value)  # Update the Label displaying the attribute value

        # Update Fertigkeiten
        frame = self.tabs['Fertigkeiten'].winfo_children()[0]  # Assuming the frame is the first child in the tab
        for i, (name, wuerfel) in enumerate(self.model.fertigkeiten.items()):
            current_value = self.model.charakter_daten['Fertigkeiten'].get(name, 'd4')
            label_list = frame.grid_slaves(row=i, column=1)
            if label_list:
                label_list[0].config(text=current_value)  # Update the Label displaying the skill value

        # Update Mächte, Talente, Handicaps, Ausrüstung und Nahkampfwaffen
        for category, model_items, data_key in [
            ('Mächte', self.model.maechte, 'Mächte'),
            ('Hintergrund Talente', self.model.hintergrund_talente, 'Hintergrund Talente'),
            ('Kampf Talente', self.model.kampf_talente, 'Kampf Talente'),         
            ('Handicaps', self.model.handicaps, 'Handicaps'),
            ('Ausrüstung', self.model.ausruestung, 'Ausrüstung'),
            ('Rüstung', self.model.ruestung, 'Rüstung'),
            ('Nahkampfwaffen', self.model.nahkampf_waffe, 'Nahkampfwaffen')
        ]:
            for item in model_items:
                if item in self.charakter_daten_selected_fertigkeiten:
                    self.charakter_daten_selected_fertigkeiten[item].set(item in self.model.charakter_daten[data_key])

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
    def eingabe_konzept(self):
        tab = self.tabs['Konzept']
        labels = ['Charakter Name', 'Spieler Name', 'Geschlecht', 'Alter', 'Profession', 'Beschreibung', 'Hintergund', 'Sprachen']
        for i, label in enumerate(labels):
            tk.Label(tab, text=label).grid(row=i, column=0, sticky='w')
            tk.Entry(tab).grid(row=i, column=1, sticky='w')

        
    @Fehlerbehandlung.handle_errors
    def eingabe_attribute(self):
        tab = self.tabs['Attribute']
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

    @Fehlerbehandlung.handle_errors
    def add_scrollbar_to_tab(self, tab_name):
        tab = self.tabs[tab_name]

        # Create a canvas and a vertical scrollbar for scrolling it
        canvas = tk.Canvas(tab)
        scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Bind the scrollbar to the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Create a window inside the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configure the canvas and scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame

    def eingabe_fertigkeiten(self):
        frame = self.add_scrollbar_to_tab('Fertigkeiten')

        for i, (name, wuerfel) in enumerate(self.model.fertigkeiten.items()):
            # Erhalte das verknüpfte Attribut für die Fertigkeit
            attribut = next(iter(fertigkeiten.get(name, {'Unbekannt'})))

            # Create and grid the skill name label with the attribute
            skill_name_label = tk.Label(frame, text=f"{name} ({attribut})")
            skill_name_label.grid(row=i, column=0, sticky='w')

            # Create and grid the skill value label
            value_text = str(wuerfel)
            if "+" not in value_text and wuerfel.modifikator > 0:
                value_text += f"+{wuerfel.modifikator}"
            elif "+" in value_text and wuerfel.modifikator < 0:
                value_text += f"{wuerfel.modifikator}"
            skill_value_label = tk.Label(frame, text=value_text)
            skill_value_label.grid(row=i, column=1, sticky='w')

            # Create and grid the skill increase and decrease buttons
            button_steigerung = tk.Button(frame, text='+', command=lambda n=name: self.steigerung_senkung(n, 'Fertigkeiten', '+'))
            button_steigerung.grid(row=i, column=2, sticky='w')
            button_senkung = tk.Button(frame, text='-', command=lambda n=name: self.steigerung_senkung(n, 'Fertigkeiten', '-'))
            button_senkung.grid(row=i, column=3, sticky='w')

        # Add the "Speichern" button
        tk.Button(frame, text="Speichern", command=self.speichern_fertigkeiten).grid(row=len(self.model.fertigkeiten), column=0)

    @Fehlerbehandlung.handle_errors
    def speichern_fertigkeiten(self):
        self.model.charakter_daten['Fertigkeiten'] = {fert: str(wuerfel) for fert, wuerfel in self.model.fertigkeiten.items()}
        self.model.speichern()
        self.ausgabe_fenster(self.model.charakter_daten)
        messagebox.showinfo("Erfolg", "Fertigkeiten gespeichert!")

    @Fehlerbehandlung.handle_errors
    def eingabe_eigenschaften(self, tab_name, eigenschaften):
        frame = self.add_scrollbar_to_tab(tab_name)

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
    def kaufe_waffe(self, waffe):
        kosten = self.model.nahkampf_waffe[waffe]['Kosten']
        if self.model.vermoegen >= kosten:
            self.model.vermoegen -= kosten
            return True, f"{waffe} wurde zum Charakterbogen hinzugefügt."
        else:
            return False, "Du hast nicht genug Gold, um diese Rüstung zu kaufen."

    @Fehlerbehandlung.handle_errors
    def eingabe_ausruestung(self):
        frame = self.add_scrollbar_to_tab('Ausrüstung')

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
    def eingabe_ruestung(self):
        frame = self.add_scrollbar_to_tab('Rüstung')

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
    def eingabe_nahkampf_waffe(self):
        frame = self.add_scrollbar_to_tab('Nahkampfwaffen')

        for i, (waffe, details) in enumerate(self.model.nahkampf_waffe.items()):
            label = tk.Label(frame, text=f"{waffe} ")
            label.grid(row=i, column=0, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Schaden: {details['Schaden']}, Mindeststärke: {details['Mindeststärke']})")
            label.grid(row=i, column=1, sticky='w', padx=15, pady=0)
            label = tk.Label(frame, text=f"(Kosten: {details['Kosten']}, Gewicht: {details['Gewicht']})")
            label.grid(row=i, column=2, sticky='w', padx=15, pady=0)
            selected = tk.BooleanVar(value=False)
            self.charakter_daten_selected_fertigkeiten[waffe] = selected
            checkbox = tk.Checkbutton(frame, variable=selected, command=lambda a=waffe: self.kaufe_waffe(a))
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
    def ausgabe_fenster(self, charakter_daten):
        tab = self.tabs['Charakterbogen']

        # Alte Inhalte des Tabs löschen
        for widget in tab.winfo_children():
            widget.destroy()

        # Scrollbar für das Eingabefenster
        scrollbar = tk.Scrollbar(tab)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas für das Eingabefenster
        canvas = tk.Canvas(tab, yscrollcommand=scrollbar.set, bg='white')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        # Frame im Canvas erstellen, um die Widgets zu halten
        frame = tk.Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=frame, anchor='nw')

        tk.Label(frame, text="Charakterbogen", font=("Arial", 16), bg='white').pack()

        # Create 5 columns
        columns = []
        for i in range(5):
            column_frame = tk.Frame(frame, bg='white')
            column_frame.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
            columns.append(column_frame)

        # Column 1: Attribute and derived values
        tk.Label(columns[0], text="Attribute:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        attr_frame = tk.Frame(columns[0], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        attr_frame.pack(fill='x', padx=5, pady=5)
        for attr, value in charakter_daten['Attribute'].items():
            tk.Label(attr_frame, text=f"{attr}: {value}", bg='#F0F0F0').pack(anchor='w')
        
        tk.Label(columns[0], text="Abgeleitete Werte:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        derived_frame = tk.Frame(columns[0], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        derived_frame.pack(fill='x', padx=5, pady=5)
        for key, value in charakter_daten['Abgeleitete Werte'].items():
            tk.Label(derived_frame, text=f"{key}: {value}", bg='#F0F0F0').pack(anchor='w')

        # Column 1 : Rüstung
        tk.Label(columns[0], text="Rüstung:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        ruest_frame = tk.Frame(columns[0], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        ruest_frame.pack(fill='x', padx=5, pady=5)
        for ruest, details in charakter_daten['Rüstung'].items():
            tk.Label(ruest_frame, text=f"{ruest} (Torso: {details['Torso']}, Arme: {details['Arme']}, Beine: {details['Beine']}, Kopf: {details['Kopf']})", bg='#F0F0F0').pack(anchor='w')          
        gesamt_ruestungsschutz = self.berechne_gesamt_ruestungsschutz()
        tk.Label(ruest_frame, text=f"Gesamt (Torso: {gesamt_ruestungsschutz['Torso']}, Arme: {gesamt_ruestungsschutz['Arme']}, Beine: {gesamt_ruestungsschutz['Beine']}, Kopf: {gesamt_ruestungsschutz['Kopf']})", bg='#F0F0F0').pack(anchor='w')

        # Column 1 : Waffen
        tk.Label(columns[0], text="Waffen:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        waffe_frame = tk.Frame(columns[0], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        waffe_frame.pack(fill='x', padx=5, pady=5)
        for waffe, details in charakter_daten['Nahkampfwaffen'].items():
            tk.Label(waffe_frame, text=f"{waffe} (Schaden: {details['Schaden']}, Mindeststärke: {details['Mindeststärke']})", bg='#F0F0F0').pack(anchor='w')
              
        # Column 2: Fertigkeiten
        tk.Label(columns[1], text="Fertigkeiten:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        fertigkeiten_frame = tk.Frame(columns[1], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        fertigkeiten_frame.pack(fill='x', padx=5, pady=5)
        for fert, value in charakter_daten['Fertigkeiten'].items():
            if self.model.fertigkeiten[fert].stufe > 0:  # Nur Fertigkeiten mit Würfelstufe > 0 anzeigen
                tk.Label(fertigkeiten_frame, text=f"{fert}: {value}", bg='#F0F0F0').pack(anchor='w')

        # Column 3: Talents & Handicaps
        tk.Label(columns[2], text="Handicaps:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        handicaps_frame = tk.Frame(columns[2], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        handicaps_frame.pack(fill='x', padx=5, pady=5)
        for handicap, selected in charakter_daten['Handicaps'].items():
            if selected:
                tk.Label(handicaps_frame, text=handicap, bg='#F0F0F0').pack(anchor='w')
        
        tk.Label(columns[2], text="Talente:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        talents_frame = tk.Frame(columns[2], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        talents_frame.pack(fill='x', padx=5, pady=5)
        for talent, selected in charakter_daten['Hintergrund Talente'].items():
            if selected:
                tk.Label(talents_frame, text=talent, bg='#F0F0F0').pack(anchor='w')
        for talent, selected in charakter_daten['Kampf Talente'].items():
            if selected:
                tk.Label(talents_frame, text=talent, bg='#F0F0F0').pack(anchor='w')

        # Column 4: Powers
        tk.Label(columns[3], text="Mächte:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        powers_frame = tk.Frame(columns[3], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        powers_frame.pack(fill='x', padx=5, pady=5)
        for macht, selected in charakter_daten['Mächte'].items():
            if selected:
                tk.Label(powers_frame, text=macht, bg='#F0F0F0').pack(anchor='w')

        # Column 5: Wealth, equipment, and weapons
        tk.Label(columns[4], text="Ausrüstung:", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')
        equipment_frame = tk.Frame(columns[4], bg='#F0F0F0', bd=1, relief='solid')  # Gray frame
        equipment_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(equipment_frame, text=f"{self.model.vermoegen} Gold", bg='#F0F0F0').pack(anchor='w')
        for ausruest, details in charakter_daten['Ausrüstung'].items():
            tk.Label(equipment_frame, text=ausruest, bg='#F0F0F0').pack(anchor='w')

        # Frame-Größe aktualisieren und Scrollregion setzen
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

    @Fehlerbehandlung.handle_errors
    def eingabe_export(self):
        # Inhalt für das Export-Tab
        tab = self.tabs['Export']
        tk.Button(tab, text="Speichern in Datei", command=self.speichern_in_datei).pack(pady=5)
        tk.Button(tab, text="Laden aus Datei", command=self.laden_aus_datei).pack(pady=5)
        tk.Button(tab, text="Drucken als PDF", command=self.drucken_als_pdf).pack(pady=5)

if __name__ == "__main__":
    # Set default window size to 640x480 pixels
    root = tk.Tk()
    root.geometry("1024x640")
    root.title("Charaktererstellung Savage Worlds")
    model = CharakterModel()
    view = CharakterView(root, model)
    root.mainloop()
