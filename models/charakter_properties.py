#charakter_properties.py
"""
Eigenschaften und Properties für die Charakter-Klasse.
Definiert alle Kivy Properties, die von der Hauptklasse verwendet werden.
"""
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,
    ObjectProperty, DictProperty, ListProperty
)

from functions.charakter_migration import MIGRATIONS_IDS

class CharakterProperties:
    """Mixin-Klasse für alle Charakter Properties"""
    
    # Profil und Grunddaten
    profil_daten = DictProperty({})
    char_name = StringProperty("")
    active_setting_name = StringProperty("")
    
    # Charaktergenerierung
    verbleibende_attributsteigerungen = NumericProperty(5)
    verbleibende_fertigkeitssteigerungen = NumericProperty(12)
    maximale_attributsteigerungen = NumericProperty(5)
    maximale_fertigkeitssteigerungen = NumericProperty(12)
    verbleibende_handicap_punkte = NumericProperty(0)
    gesamt_handicap_punkte = NumericProperty(0)
    char_gen_completed = BooleanProperty(False)
    
    # Aufstieg und Rang
    verbleibende_aufstiege = NumericProperty(0)
    aufstiege_gesamt = NumericProperty(0)
    rang = StringProperty("Anfänger")
    
    # Mächte
    verfuegbare_maechte = NumericProperty(0)
    anzahl_maechte = NumericProperty(0)
    machtpunkte = NumericProperty(0)

    # Superkräfte (Superkräfte-Kompendium)
    superkraefte = DictProperty({})
    superkraft_punkte_gesamt = NumericProperty(0)
    superkraft_punkte_verbraucht = NumericProperty(0)
    machtstufe = StringProperty("III")
    kraftobergrenze = NumericProperty(15)
    selected_superkraefte = ListProperty([])
    
    # Vermögen
    vermoegen = NumericProperty(500)
    # Wie oft Handicap-Punkte in Startkapital umgewandelt wurden (für die Rücknahme)
    startgeld_einloesungen = NumericProperty(0)
    waehrungseinheit = StringProperty("Gold")
    vermoegen_text = StringProperty("Vermögen: 500 Gold")
    
    # Spielwerte
    erschoepfung = NumericProperty(0)
    wunden = NumericProperty(0)
    bennys = NumericProperty(3)
    entschlossenheit = NumericProperty(0)
    
    # Element-Container
    talente = DictProperty({})
    handicaps = DictProperty({})
    fertigkeiten_daten = DictProperty({})
    maechte = DictProperty({})
    ausruestung = DictProperty({})
    konzept = DictProperty({})
    details = DictProperty({})
    voelker = DictProperty({})
    voelker_selected = DictProperty({})
    # Pro-Volk Multi-Slot-Auswahlen (Listen pro Wahlmöglichkeit), persistiert.
    voelker_auswahlen = DictProperty({})
    
    # Settings
    settingregeln = ObjectProperty(None)
    
    # Traglast
    maximale_traglast = NumericProperty(40)
    # gesamtgewicht wird als Property in CharakterEquipment definiert
    
    # Ausgewählte Elemente
    selected_handicaps = ListProperty([])
    selected_talente = ListProperty([])
    selected_maechte = ListProperty([])
    selected_allgemeine_ausruestung = ListProperty([])
    selected_waffen = ListProperty([])
    selected_ruestungen = ListProperty([])
    selected_schilde = ListProperty([])
    # Kostenlos aus Abstammung/Talenten gestellte natürliche Waffen
    # (functions/natuerliche_waffen.py) — nur diese werden wieder eingesammelt
    natuerliche_waffen = ListProperty([])
    
    # Abgeleitete Werte
    bewegungsweite = NumericProperty(6)
    parade = NumericProperty(3)
    robustheit = NumericProperty(3)
    robustheit_basis = NumericProperty(3)
    robustheit_mit_ruestung = StringProperty("")
    groesse = NumericProperty(0)
    
    # Attribute und Fertigkeiten
    attribute = DictProperty({})
    fertigkeiten = DictProperty({})

    # Cyberware (SciFi-Settings)
    cyberware_verfuegbar = DictProperty({})
    cyberware_installationen = DictProperty({})
    cyberware_stress_aktuell = NumericProperty(0)
    cyberware_stresslimit = NumericProperty(0)
    cyberware_stress_maximum = NumericProperty(0)
    cyberware_budget = NumericProperty(0)
    cyberware_nebenwirkungen = ListProperty([])
    selected_cyberware = ListProperty([])

    # Bereits angewendete Datenmigrationen (siehe functions/charakter_migration.py).
    # Neue Charaktere haben nichts nachzuholen und tragen deshalb alle IDs;
    # beim Laden wird die Liste aus der Save-Datei übernommen.
    migrationen = ListProperty(list(MIGRATIONS_IDS))

    # Steigerungs-Journal (kein Kivy-Property, da keine UI-Bindung nötig)
    steigerungs_journal = None