# fertigkeiten_funktionen.py

from models.fertigkeit import Fertigkeit
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from kivy.logger import Logger, LOG_LEVELS

def initialisiere_fertigkeiten(self):
    """Initialisiert die Fertigkeiten des Charakters."""

    self.initialisiere_attribute()

    grundfertigkeiten = [
        "Allgemeinwissen",
        "Athletik",
        "Heimlichkeit",
        "Überreden",
        "Wahrnehmung",
    ]
    
    # Erstellen einer Menge der Fertigkeitenamen aus fertigkeiten_daten
    fertigkeiten_namen_in_daten = set(self.fertigkeiten_daten.keys())
    # Erstellen einer Liste der aktuellen Fertigkeitenamen
    fertigkeiten_namen_aktuell = set(self.fertigkeiten.keys())

    # Aktualisieren oder Erstellen von Fertigkeiten
    for fertigkeit_name, attribut_set in self.fertigkeiten_daten.items():
        if isinstance(attribut_set, set) and len(attribut_set) == 1:
            attribut_name = next(iter(attribut_set))
        else:
            Logger.error(f"Fertigkeit '{fertigkeit_name}' hat eine ungültige Attribut-Zuweisung.")
            continue

        attribut_obj = self.attribute.get(attribut_name)
        if attribut_obj is None:
            Logger.error(f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' nicht gefunden.")
            continue

        ist_grundfertigkeit = fertigkeit_name in grundfertigkeiten

        if fertigkeit_name in self.fertigkeiten:
            # Bestehende Fertigkeit aktualisieren
            fertigkeit = self.fertigkeiten[fertigkeit_name]
            fertigkeit.attribut = attribut_obj
            fertigkeit.grundfertigkeit = ist_grundfertigkeit
        else:
            # Neue Fertigkeit erstellen
            fertigkeit = Fertigkeit(
                fertigkeit_name=fertigkeit_name,
                attribut=attribut_obj,
                grundfertigkeit=ist_grundfertigkeit,
            )
            fertigkeit.bind(wert=self.on_fertigkeit_wert_change)
            fertigkeit.bind(wert=self.on_fertigkeit_modifier_change)
            self.fertigkeiten[fertigkeit_name] = fertigkeit

    # Entfernen von Fertigkeiten, die nicht mehr in fertigkeiten_daten vorhanden sind
    fertigkeiten_zu_entfernen = fertigkeiten_namen_aktuell - fertigkeiten_namen_in_daten
    for fertigkeit_name in fertigkeiten_zu_entfernen:
        del self.fertigkeiten[fertigkeit_name]
        Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde entfernt, da sie nicht im geladenen Setting vorhanden ist.")

def steigere_fertigkeit(self, fertigkeit_name):
    fertigkeit = self.fertigkeiten.get(fertigkeit_name)
    if fertigkeit:
        zugehoeriges_attribut = fertigkeit.attribut
        aktueller_total_value = fertigkeit.wuerfel.value + fertigkeit.wuerfel.modifier
        attribut_total_value = zugehoeriges_attribut.wuerfel.value + zugehoeriges_attribut.wuerfel.modifier

        # Bestimme den neuen Wert und Modifier nach der Steigerung
        if fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == -2:
            neuer_wert = fertigkeit.wuerfel.value
            neuer_modifier = fertigkeit.wuerfel.modifier + 2
        elif fertigkeit.wuerfel.value < 12:
            neuer_wert = fertigkeit.wuerfel.value + 2
            neuer_modifier = fertigkeit.wuerfel.modifier
        elif fertigkeit.wuerfel.value == 12 and fertigkeit.wuerfel.modifier < 2:
            neuer_wert = fertigkeit.wuerfel.value
            neuer_modifier = fertigkeit.wuerfel.modifier + 1
        else:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
            return False

        neuer_total_value = neuer_wert + neuer_modifier

    # Bestimme die Kosten
    if self.char_gen_completed:
        if neuer_total_value > attribut_total_value:
            kosten = 1
        else:
            kosten = 0.5
    else:            
        if neuer_total_value > attribut_total_value:
            kosten = 2
        else:
            kosten = 1

    def steigern():
        erfolg = fertigkeit.wuerfel.increase()
        if erfolg:
            fertigkeit.ausgewaehlt = True
            Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesteigert auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
            self.rang = self.get_rang(self.aufstiege_gesamt)                
            return True                
        else:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
            return False            

    if self.char_gen_completed:
        if self.verbleibende_aufstiege >= kosten:
            self.verbleibende_aufstiege -= kosten
            steigern()
        else:
            Logger.warning("Nicht genügend verbleibende Aufstiege.")
            return False
    else:
        if self.verbleibende_fertigkeitssteigerungen >= kosten:
            self.verbleibende_fertigkeitssteigerungen -= kosten
            steigern()
        else:
            if self.verbleibende_handicap_punkte > 0.5:
                steigern()
                self.verbleibende_handicap_punkte -= 1
                Logger.info("Fertigkeit mit Handicap-Punkten gesteigert.")
            else:
                Logger.warning("Nicht genügend verbleibende Fertigkeitssteigerungen.")
                return False

def senke_fertigkeit(self, fertigkeit_name):
    """
    Senkt eine Fertigkeit um eine Stufe und gibt die entsprechenden Steigerungen zurück.
    Grundfertigkeiten dürfen nicht von W4+0 auf W4-2 gesenkt werden.
    """
    grundfertigkeiten = [
        "Allgemeinwissen",
        "Athletik",
        "Heimlichkeit",
        "Überreden",
        "Wahrnehmung",
    ]

    def senken():
        fertigkeit.wuerfel.decrease()
        Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesenkt auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
        self.update_char_gen_status()  # Aktualisiere den Status
        self.rang = self.get_rang(self.aufstiege_gesamt)

    fertigkeit = self.fertigkeiten.get(fertigkeit_name)
    if fertigkeit:
        # Überprüfung, ob die Fertigkeit eine Grundfertigkeit ist und ob sie bereits den Mindestmodifier hat
        if fertigkeit_name in grundfertigkeiten and fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == 0:
            Logger.warning(f"Grundfertigkeit '{fertigkeit_name}' kann nicht von W4+0 auf W4-2 gesenkt werden.")
            return False

        zugehoeriges_attribut = fertigkeit.attribut

    # Bestimme die Kosten
    if self.char_gen_completed: 
        kosten = 0.5
        if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
            kosten = 1
    else:
        kosten = 1
        if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
            kosten = 2                 

    vorheriger_wert = fertigkeit.wuerfel.value
    vorheriger_modifier = fertigkeit.wuerfel.modifier

    if self.char_gen_completed:
        if self.verbleibende_aufstiege < self.aufstiege_gesamt:
            #Logger.debug(f"Verbleibende Aufstiege vor Gutschrift: {self.verbleibende_aufstiege}")
            self.verbleibende_aufstiege += kosten
            #Logger.debug(f"{kosten} `verbleibende_aufstiege` gutgeschrieben. Neuer Wert: {self.verbleibende_aufstiege}")
            senken()
        else:
            Logger.debug("Maximum Aufstiege erreicht.")
            return False
    else:
        if self.verbleibende_handicap_punkte < self.gesamt_handicap_punkte:
            self.verbleibende_handicap_punkte += kosten
            senken()
        else:
            if self.verbleibende_fertigkeitssteigerungen < self.maximale_fertigkeitssteigerungen:
                #Logger.debug(f"Verbleibende Fertigkeitssteigerungen vor Gutschrift: {self.verbleibende_fertigkeitssteigerungen}")
                self.verbleibende_fertigkeitssteigerungen += kosten
                #Logger.debug(f"{kosten} `Verbleibende Fertigkeitssteigerungen` gutgeschrieben. Neuer Wert: {self.verbleibende_fertigkeitssteigerungen}")
                senken()
            else:
                Logger.warning("Maximum Fertigkeitspunkte erreicht.")
                return False