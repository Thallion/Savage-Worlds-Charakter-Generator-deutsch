# models/volk.py - Erweiterte Version
import unittest, json
from kivy.properties import StringProperty, ListProperty, BooleanProperty, DictProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS

class Volk(EventDispatcher):
    name = StringProperty("")
    handicaps = ListProperty([])
    talente = ListProperty([])
    besonderheiten = ListProperty([])
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    custom = BooleanProperty(False)
    
    # Neue strukturierte Effekte
    effects = DictProperty({})

    def __init__(self, name, handicaps=None, talente=None, besonderheiten=None, 
                 effects=None, custom=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.handicaps = handicaps or []
        self.talente = talente or []
        self.besonderheiten = besonderheiten or []
        self.ausgewaehlt = False
        self.aktiv = True
        self.custom = custom
        
        # Strukturierte Effekte direkt setzen (kein Text-Parsing mehr nötig)
        self.effects = effects or {
            'attribute_bonuses': {},      # {'Stärke': 2} = W4 -> W6
            'robustheit_bonus': 0,        # +1 oder -1
            'bewegungsweite_bonus': 0,    # +1 oder -1
            'fertigkeits_startboni': {},   # {'Wahrnehmung': 2} = W4-2 -> W4+0
            'fertigkeits_startmalus': {}, # {'Allgemeinwissen': -2} = W4 -> W4-2
            'auto_talente': [],           # Automatisch erhaltene Talente
            'auto_handicaps': [],         # Automatisch erhaltene Handicaps
            'auto_mächte': [],            # Automatisch erhaltene Mächte
            'spezielle_effekte': {},      # Für komplexere Effekte
            'wahlmoeglichkeiten': {}      # Für Dropdown-Auswahl
        }

    def _parse_effects_from_text(self):
        """
        Parst Effekte aus den Besonderheiten und Handicaps und strukturiert sie.
        Dies ist eine Migrationshilfe für bestehende Daten.
        """
        if not self.effects:
            self.effects = {
                'attribute_bonuses': {},      # {'Stärke': 2} = W4 -> W6
                'robustheit_bonus': 0,        # +1 oder -1
                'bewegungsweite_bonus': 0,    # +1 oder -1
                'fertigkeits_startboni': {},   # {'Wahrnehmung': 2} = W4-2 -> W4+0
                'fertigkeits_startmalus': {},  # {'Allgemeinwissen': -2} = W4 -> W4-2
                'auto_talente': [],           # Automatisch erhaltene Talente
                'auto_handicaps': [],         # Automatisch erhaltene Handicaps
                'auto_mächte': [],            # Automatisch erhaltene Mächte
                'spezielle_effekte': {},      # Für komplexere Effekte
                'wahlmoeglichkeiten': {}      # Für Dropdown-Auswahl
            }
            
        # Parse aus Besonderheiten
        for besonderheit in self.besonderheiten:
            self._parse_einzeleffekt(besonderheit, ist_handicap=False)
            
        # Parse aus Handicaps  
        for handicap in self.handicaps:
            self._parse_einzeleffekt(handicap, ist_handicap=True)

    def _parse_einzeleffekt(self, text, ist_handicap=False):
        """Parst einen einzelnen Effekt aus dem Text."""
        text_lower = text.lower()
        
        # Attribut-Boni erkennen (auch in Klammern)
        attribute = ['stärke', 'geschicklichkeit', 'konstitution', 'verstand', 'willenskraft']
        for attr in attribute:
            if f"{attr} w6 statt w4" in text_lower:
                attr_name = attr.capitalize()
                self.effects['attribute_bonuses'][attr_name] = 2
                
        # Fertigkeits-Boni erkennen (auch in Klammern)
        fertigkeiten = ['wahrnehmung', 'athletik', 'einschüchtern', 'kämpfen']
        for fert in fertigkeiten:
            if f"{fert} w6 statt w4" in text_lower:
                fert_name = fert.capitalize()
                self.effects['fertigkeits_startboni'][fert_name] = 2
            elif f"beginnt mit w4 in {fert}" in text_lower:
                fert_name = fert.capitalize()
                self.effects['fertigkeits_startboni'][fert_name] = 0  # W4-2 -> W4

        # Robustheit-Effekte (verschiedene Formulierungen)
        if any(phrase in text_lower for phrase in [
            "robustheit um 1", "-1 robustheit", "(-1 robustheit", 
            "reduzierte robustheit um 1", "größe -1"
        ]):
            if ist_handicap or any(neg in text_lower for neg in ["-1", "reduzierte", "schlank"]):
                self.effects['robustheit_bonus'] -= 1
            else:
                self.effects['robustheit_bonus'] += 1
        elif any(phrase in text_lower for phrase in ["+1 robustheit", "orkische wildheit"]):
            self.effects['robustheit_bonus'] += 1

        # Bewegungsweite-Effekte (verschiedene Formulierungen)
        if any(phrase in text_lower for phrase in [
            "verringerte bewegungsweite", "-1 bewegungsweite", "bewegungsweite -1"
        ]):
            self.effects['bewegungsweite_bonus'] -= 1

        # Wahlmöglichkeiten erkennen
        if any(phrase in text_lower for phrase in ["freies talent", "anpassungsfähigkeit"]):
            self.effects['wahlmoeglichkeiten']['freies_talent'] = True
            
        if any(phrase in text_lower for phrase in [
            "w6 in einem attribut statt w4", "flexibilität"
        ]):
            self.effects['wahlmoeglichkeiten']['freies_attribut'] = True
            
        if any(phrase in text_lower for phrase in [
            "verstandsbasierten fertigkeit auf w4", "zwanghaft"
        ]):
            self.effects['wahlmoeglichkeiten']['freie_verstandsfertigkeit'] = True

        # Spezielle Effekte für komplexere Fälle
        spezial_effects_mapping = {
            'elfenmagie': ['elfenmagie'],
            'nachtsicht': ['nachtsicht', 'dunkelsicht'],
            'steingespür': ['steingespür'],
            'gnomenmagie': ['gnomenmagie'],
            'eiserne_konstitution': ['eiserne konstitution'],
            'geschaerfte_sinne': ['geschärfte sinne']
        }
        
        for effect_key, keywords in spezial_effects_mapping.items():
            if any(keyword in text_lower for keyword in keywords):
                self.effects['spezielle_effekte'][effect_key] = True

    def get_attribut_bonus(self, attribut_name):
        """Gibt den Bonus für ein spezifisches Attribut zurück."""
        return self.effects.get('attribute_bonuses', {}).get(attribut_name, 0)

    def get_fertigkeits_bonus(self, fertigkeits_name):
        """Gibt den Bonus für eine spezifische Fertigkeit zurück."""
        return self.effects.get('fertigkeits_startboni', {}).get(fertigkeits_name, 0)

    def get_robustheit_bonus(self):
        """Gibt den Robustheit-Bonus zurück."""
        return self.effects.get('robustheit_bonus', 0)

    def get_bewegungsweite_bonus(self):
        """Gibt den Bewegungsweite-Bonus zurück."""
        return self.effects.get('bewegungsweite_bonus', 0)

    def has_wahlmoeglichkeit(self, typ):
        """Prüft, ob das Volk eine bestimmte Wahlmöglichkeit hat."""
        return self.effects.get('wahlmoeglichkeiten', {}).get(typ, False)

    def has_spezialeffekt(self, effekt_name):
        """Prüft, ob das Volk einen spezifischen Spezialeffekt hat."""
        spezielle_effekte = self.effects.get('spezielle_effekte', {})
        if isinstance(spezielle_effekte, list):
            # Listen-Format vom Volksgenerator: [{'typ': 'nachtsicht', 'wert': True}]
            return any(e.get('typ') == effekt_name and e.get('wert') for e in spezielle_effekte)
        # Dict-Format von _parse_effects_from_text
        return spezielle_effekte.get(effekt_name, False)

    def apply_effects_to_charakter(self, charakter):
        """
        Wendet die Völker-Effekte auf einen Charakter an.
        KORRIGIERT: Unterscheidet zwischen Grundfertigkeiten (W4→W6) und Nicht-Grundfertigkeiten (W4-2→W4+0).
        """
        try:
            Logger.info(f"=== Anwenden der Völker-Effekte für {self.name} ===")
            
            # Liste der Grundfertigkeiten (starten mit W4+0)
            grundfertigkeiten = [
                "Allgemeinwissen",
                "Athletik", 
                "Heimlichkeit",
                "Überreden",
                "Wahrnehmung",
            ]
            
            # Attribut-Boni anwenden
            for attr_name, bonus in self.effects.get('attribute_bonuses', {}).items():
                if attr_name in charakter.attribute:
                    attribut = charakter.attribute[attr_name]
                    if bonus > 0:
                        # Positiver Bonus: Würfelwert erhöhen (W4 → W6)
                        if attribut.wert == 4 and attribut.modifier == 0:
                            alter_wert = attribut.wert
                            attribut.wuerfel.value = 4 + bonus
                            Logger.info(f"Volk {self.name}: {attr_name} von W{alter_wert} auf W{attribut.wert} erhöht")
                        else:
                            Logger.debug(f"Volk {self.name}: {attr_name} nicht angepasst (aktuell: W{attribut.wert}{attribut.modifier:+d})")
                    elif bonus < 0:
                        # Negativer Bonus (Attributsschwäche): Modifier setzen (W4 → W4-2)
                        if attribut.modifier == 0:
                            attribut.wuerfel.modifier = bonus
                            Logger.info(f"Volk {self.name}: {attr_name} Attributsschwäche W{attribut.wert}{bonus:+d}")
                        else:
                            Logger.debug(f"Volk {self.name}: {attr_name} Modifier bereits gesetzt ({attribut.modifier:+d})")

            # Fertigkeits-Startboni anwenden (unterschiedlich für Grund- und Nicht-Grundfertigkeiten)
            for fert_name, bonus in self.effects.get('fertigkeits_startboni', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    
                    if fert_name in grundfertigkeiten:
                        # GRUNDFERTIGKEIT: W4+0 → W6+0 (Würfelwert erhöhen)
                        if fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                            alter_wert = fertigkeit.wert
                            fertigkeit.wuerfel.value = 4 + bonus  # +2 = W6
                            Logger.info(f"Volk {self.name}: {fert_name} (Grundfertigkeit) von W{alter_wert} auf W{fertigkeit.wert} erhöht")
                        else:
                            Logger.debug(f"Volk {self.name}: {fert_name} (Grundfertigkeit) nicht angepasst (aktuell: W{fertigkeit.wert}{fertigkeit.modifier:+d})")
                    else:
                        # NICHT-GRUNDFERTIGKEIT: W4-2 → W6 (beim Rotvolk Kämpfen)
                        if fertigkeit.wert == 4 and fertigkeit.modifier == -2:
                            if bonus > 0:
                                # Würfel erhöhen und Modifier auf 0 setzen
                                fertigkeit.wuerfel.value = 4 + bonus  # +2 = W6
                                fertigkeit.wuerfel.modifier = 0
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) von W4-2 auf W6 erhöht")
                            else:
                                fertigkeit.wuerfel.modifier = -2 + bonus
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) Modifier auf {fertigkeit.modifier:+d} gesetzt")
                        else:
                            Logger.debug(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) nicht angepasst (aktuell: W{fertigkeit.wert}{fertigkeit.modifier:+d})")

            # Fertigkeits-Startmalus anwenden (z.B. Golem: W4 → W4-2)
            for fert_name, malus in self.effects.get('fertigkeits_startmalus', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    if fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                        fertigkeit.wuerfel.modifier = malus  # -2 → W4-2
                        Logger.info(f"Volk {self.name}: {fert_name} von W4 auf W4{malus:+d} reduziert")

            # Automatische Talente hinzufügen
            for talent_name in self.effects.get('auto_talente', []):
                if talent_name in charakter.talente and not charakter.talente[talent_name].ausgewaehlt:
                    charakter.talente[talent_name].ausgewaehlt = True
                    if talent_name not in charakter.selected_talente:
                        charakter.selected_talente.append(talent_name)
                    # Machtpunkte erhöhen falls Talent welche hat (z.B. AH (Begabt))
                    talent = charakter.talente[talent_name]
                    if hasattr(talent, 'machtpunkte') and talent.machtpunkte > 0:
                        charakter.erhoehe_machtpunkte(talent.machtpunkte)
                        Logger.info(f"Volk {self.name}: +{talent.machtpunkte} Machtpunkte durch Talent '{talent_name}'")
                    # Auch verfügbare Mächte erhöhen falls das Talent welche gewährt
                    if hasattr(talent, 'neue_maechte') and talent.neue_maechte > 0:
                        charakter.verfuegbare_maechte += talent.neue_maechte
                        charakter.anzahl_maechte += talent.neue_maechte
                        Logger.info(f"Volk {self.name}: +{talent.neue_maechte} verfügbare Mächte durch Talent '{talent_name}'")
                    Logger.info(f"Volk {self.name}: Automatisches Talent '{talent_name}' erhalten")

            # Automatische Handicaps hinzufügen
            for handicap_name in self.effects.get('auto_handicaps', []):
                if handicap_name in charakter.handicaps and not charakter.handicaps[handicap_name].ausgewaehlt:
                    charakter.handicaps[handicap_name].ausgewaehlt = True
                    if handicap_name not in charakter.selected_handicaps:
                        charakter.selected_handicaps.append(handicap_name)
                    Logger.info(f"Volk {self.name}: Automatisches Handicap '{handicap_name}' erhalten")

            # Automatische Mächte hinzufügen
            for macht_name in self.effects.get('auto_mächte', []):
                if macht_name in charakter.maechte and not charakter.maechte[macht_name].ausgewaehlt:
                    charakter.maechte[macht_name].ausgewaehlt = True
                    if macht_name not in charakter.selected_maechte:
                        charakter.selected_maechte.append(macht_name)
                    Logger.info(f"Volk {self.name}: Automatische Macht '{macht_name}' erhalten")

            # Macht-Volk-Effekte (macht_volk): AH (Begabt) aktivieren + Mächte hinzufügen
            spezielle_effekte = self.effects.get('spezielle_effekte', [])
            if isinstance(spezielle_effekte, list):
                macht_volk_effekte = [e for e in spezielle_effekte if e.get('typ') == 'macht_volk']
                if macht_volk_effekte:
                    ah_name = 'AH (Begabt)'
                    if ah_name in charakter.talente and not charakter.talente[ah_name].ausgewaehlt:
                        charakter.talente[ah_name].ausgewaehlt = True
                        if ah_name not in charakter.selected_talente:
                            charakter.selected_talente.append(ah_name)
                        talent = charakter.talente[ah_name]
                        if hasattr(talent, 'machtpunkte') and talent.machtpunkte > 0:
                            charakter.erhoehe_machtpunkte(talent.machtpunkte)
                            Logger.info(f"Volk {self.name}: +{talent.machtpunkte} Machtpunkte durch '{ah_name}'")
                        if hasattr(talent, 'neue_maechte') and talent.neue_maechte > 0:
                            charakter.verfuegbare_maechte += talent.neue_maechte
                            charakter.anzahl_maechte += talent.neue_maechte
                            Logger.info(f"Volk {self.name}: +{talent.neue_maechte} verfügbare Mächte durch '{ah_name}'")
                        Logger.info(f"Volk {self.name}: AH (Begabt) automatisch aktiviert (Macht-Volk)")
                    for mve in macht_volk_effekte:
                        macht_name = mve.get('wert')
                        if macht_name and macht_name in charakter.maechte and not charakter.maechte[macht_name].ausgewaehlt:
                            charakter.maechte[macht_name].ausgewaehlt = True
                            if macht_name not in charakter.selected_maechte:
                                charakter.selected_maechte.append(macht_name)
                            Logger.info(f"Volk {self.name}: Macht '{macht_name}' erhalten (Macht-Volk)")

            # Robustheit und Bewegungsweite werden in abgeleitete_werte.py berechnet
            robustheit_bonus = self.effects.get('robustheit_bonus', 0)
            bewegungsweite_bonus = self.effects.get('bewegungsweite_bonus', 0)
            
            if robustheit_bonus != 0:
                Logger.info(f"Volk {self.name}: Robustheit-Bonus {robustheit_bonus:+d}")
            if bewegungsweite_bonus != 0:
                Logger.info(f"Volk {self.name}: Bewegungsweite-Bonus {bewegungsweite_bonus:+d}")

            Logger.info(f"=== Völker-Effekte für {self.name} erfolgreich angewendet ===")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Völker-Effekte für {self.name}: {e}")
            return False

    def remove_effects_from_charakter(self, charakter):
        """
        Entfernt die Völker-Effekte von einem Charakter.
        ROBUST: Behandelt Edge Cases und unerwartete Zustände.
        """
        try:
            Logger.info(f"=== Entfernen der Völker-Effekte für {self.name} ===")
            
            # Liste der Grundfertigkeiten (starten mit W4+0)
            grundfertigkeiten = [
                "Allgemeinwissen",
                "Athletik", 
                "Heimlichkeit",
                "Überreden",
                "Wahrnehmung",
            ]
            
            # Attribut-Boni rückgängig machen
            for attr_name, bonus in self.effects.get('attribute_bonuses', {}).items():
                if attr_name in charakter.attribute:
                    attribut = charakter.attribute[attr_name]

                    if bonus > 0:
                        # Positiven Bonus rückgängig machen (Würfelwert reduzieren)
                        expected_boosted_value = 4 + bonus
                        if attribut.wert == expected_boosted_value:
                            attribut.wuerfel.value = 4
                            Logger.info(f"Volk {self.name}: {attr_name} von W{expected_boosted_value} auf W4 zurückgesetzt")
                        elif attribut.wert > 4:
                            new_value = max(4, attribut.wert - bonus)
                            attribut.wuerfel.value = new_value
                            Logger.info(f"Volk {self.name}: {attr_name} von W{attribut.wert} auf W{new_value} reduziert")
                        else:
                            Logger.debug(f"Volk {self.name}: {attr_name} bereits auf Basis-Niveau (W{attribut.wert})")
                    elif bonus < 0:
                        # Negativen Bonus (Attributsschwäche) rückgängig machen (Modifier auf 0)
                        if attribut.modifier == bonus:
                            attribut.wuerfel.modifier = 0
                            Logger.info(f"Volk {self.name}: {attr_name} Attributsschwäche entfernt (W{attribut.wert}{bonus:+d} → W{attribut.wert})")
                        elif attribut.modifier < 0:
                            new_modifier = min(0, attribut.modifier - bonus)
                            attribut.wuerfel.modifier = new_modifier
                            Logger.info(f"Volk {self.name}: {attr_name} Modifier von {attribut.modifier:+d} auf {new_modifier:+d} reduziert")
                        else:
                            Logger.debug(f"Volk {self.name}: {attr_name} Modifier bereits auf 0")

            # Fertigkeits-Boni rückgängig machen
            for fert_name, bonus in self.effects.get('fertigkeits_startboni', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    
                    if fert_name in grundfertigkeiten:
                        # GRUNDFERTIGKEIT: Zurück auf W4+0
                        expected_boosted_value = 4 + bonus
                        
                        if fertigkeit.wert == expected_boosted_value and fertigkeit.modifier == 0:
                            # Standard Fall: Fertigkeit hat den erwarteten Bonus-Wert
                            fertigkeit.wuerfel.value = 4
                            Logger.info(f"Volk {self.name}: {fert_name} (Grundfertigkeit) von W{expected_boosted_value} auf W4 zurückgesetzt")
                        elif fertigkeit.wert > 4:
                            # Edge Case: Fertigkeit wurde über den Basis-Bonus hinaus erhöht
                            new_value = max(4, fertigkeit.wert - bonus)
                            fertigkeit.wuerfel.value = new_value
                            Logger.info(f"Volk {self.name}: {fert_name} (Grundfertigkeit) von W{fertigkeit.wert} auf W{new_value} reduziert")
                        else:
                            Logger.debug(f"Volk {self.name}: {fert_name} (Grundfertigkeit) bereits auf Basis-Niveau")
                    else:
                        # NICHT-GRUNDFERTIGKEIT: Zurück auf W4-2
                        if bonus > 0:
                            # Bonus erhöht Würfelwert: W(4+bonus) → W4-2
                            expected_boosted_value = 4 + bonus
                            if fertigkeit.wert == expected_boosted_value and fertigkeit.modifier == 0:
                                fertigkeit.wuerfel.value = 4
                                fertigkeit.wuerfel.modifier = -2
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) von W{expected_boosted_value} auf W4-2 zurückgesetzt")
                            elif fertigkeit.wert > expected_boosted_value:
                                new_value = max(4, fertigkeit.wert - bonus)
                                fertigkeit.wuerfel.value = new_value
                                fertigkeit.wuerfel.modifier = -2
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) von W{fertigkeit.wert} auf W{new_value}-2 reduziert")
                            else:
                                Logger.debug(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) bereits auf Basis-Niveau")
                        else:
                            # Bonus erhöhte Modifier: W4-2 → W4+0
                            expected_boosted_modifier = -2 + bonus
                            if fertigkeit.wert == 4 and fertigkeit.modifier == expected_boosted_modifier:
                                fertigkeit.wuerfel.modifier = -2
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) von W4{expected_boosted_modifier:+d} auf W4-2 zurückgesetzt")
                            elif fertigkeit.modifier > -2:
                                new_modifier = max(-2, fertigkeit.modifier - abs(bonus))
                                fertigkeit.wuerfel.modifier = new_modifier
                                Logger.info(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) Modifier von {fertigkeit.modifier:+d} auf {new_modifier:+d} reduziert")
                            else:
                                Logger.debug(f"Volk {self.name}: {fert_name} (Nicht-Grundfertigkeit) bereits auf Basis-Niveau")

            # Fertigkeits-Startmalus rückgängig machen
            for fert_name, malus in self.effects.get('fertigkeits_startmalus', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    if fertigkeit.wert == 4 and fertigkeit.modifier == malus:
                        fertigkeit.wuerfel.modifier = 0
                        Logger.info(f"Volk {self.name}: {fert_name} von W4{malus:+d} auf W4 zurückgesetzt")

            # Automatische Talente entfernen (nur die von diesem Volk hinzugefügten)
            for talent_name in self.effects.get('auto_talente', []):
                if talent_name in charakter.selected_talente:
                    charakter.selected_talente.remove(talent_name)
                    Logger.info(f"Volk {self.name}: '{talent_name}' aus selected_talente entfernt")

                if talent_name in charakter.talente and charakter.talente[talent_name].ausgewaehlt:
                    talent = charakter.talente[talent_name]
                    # Machtpunkte reduzieren falls Talent welche hatte
                    if hasattr(talent, 'machtpunkte') and talent.machtpunkte > 0:
                        charakter.senke_machtpunkte(talent.machtpunkte)
                        Logger.info(f"Volk {self.name}: -{talent.machtpunkte} Machtpunkte durch Talent '{talent_name}'")
                    # Verfügbare Mächte reduzieren falls das Talent welche gewährt hatte
                    if hasattr(talent, 'neue_maechte') and talent.neue_maechte > 0:
                        charakter.verfuegbare_maechte -= talent.neue_maechte
                        charakter.anzahl_maechte -= talent.neue_maechte
                        charakter.verfuegbare_maechte = max(charakter.verfuegbare_maechte, 0)
                        Logger.info(f"Volk {self.name}: -{talent.neue_maechte} verfügbare Mächte durch Talent '{talent_name}'")
                    talent.ausgewaehlt = False
                    Logger.info(f"Volk {self.name}: Automatisches Talent '{talent_name}' deaktiviert")

            # Automatische Handicaps entfernen (nur die von diesem Volk hinzugefügten)
            for handicap_name in self.effects.get('auto_handicaps', []):
                if handicap_name in charakter.selected_handicaps:
                    charakter.selected_handicaps.remove(handicap_name)
                    Logger.info(f"Volk {self.name}: '{handicap_name}' aus selected_handicaps entfernt")

                if handicap_name in charakter.handicaps and charakter.handicaps[handicap_name].ausgewaehlt:
                    charakter.handicaps[handicap_name].ausgewaehlt = False
                    Logger.info(f"Volk {self.name}: Automatisches Handicap '{handicap_name}' deaktiviert")

            # Automatische Mächte entfernen (nur die von diesem Volk hinzugefügten)
            for macht_name in self.effects.get('auto_mächte', []):
                if macht_name in charakter.selected_maechte:
                    charakter.selected_maechte.remove(macht_name)
                    Logger.info(f"Volk {self.name}: '{macht_name}' aus selected_maechte entfernt")

                if macht_name in charakter.maechte and charakter.maechte[macht_name].ausgewaehlt:
                    charakter.maechte[macht_name].ausgewaehlt = False
                    Logger.info(f"Volk {self.name}: Automatische Macht '{macht_name}' deaktiviert")

            # Macht-Volk-Effekte entfernen: Mächte abwählen + AH (Begabt) deaktivieren
            spezielle_effekte = self.effects.get('spezielle_effekte', [])
            if isinstance(spezielle_effekte, list):
                macht_volk_effekte = [e for e in spezielle_effekte if e.get('typ') == 'macht_volk']
                if macht_volk_effekte:
                    for mve in macht_volk_effekte:
                        macht_name = mve.get('wert')
                        if macht_name:
                            if macht_name in charakter.selected_maechte:
                                charakter.selected_maechte.remove(macht_name)
                                Logger.info(f"Volk {self.name}: '{macht_name}' aus selected_maechte entfernt")
                            if macht_name in charakter.maechte and charakter.maechte[macht_name].ausgewaehlt:
                                charakter.maechte[macht_name].ausgewaehlt = False
                                Logger.info(f"Volk {self.name}: Macht '{macht_name}' deaktiviert")
                    ah_name = 'AH (Begabt)'
                    if ah_name in charakter.talente and charakter.talente[ah_name].ausgewaehlt:
                        talent = charakter.talente[ah_name]
                        if hasattr(talent, 'machtpunkte') and talent.machtpunkte > 0:
                            charakter.senke_machtpunkte(talent.machtpunkte)
                            Logger.info(f"Volk {self.name}: -{talent.machtpunkte} Machtpunkte durch '{ah_name}'")
                        if hasattr(talent, 'neue_maechte') and talent.neue_maechte > 0:
                            charakter.verfuegbare_maechte -= talent.neue_maechte
                            charakter.anzahl_maechte -= talent.neue_maechte
                            charakter.verfuegbare_maechte = max(charakter.verfuegbare_maechte, 0)
                            Logger.info(f"Volk {self.name}: -{talent.neue_maechte} verfügbare Mächte durch '{ah_name}'")
                        charakter.talente[ah_name].ausgewaehlt = False
                        if ah_name in charakter.selected_talente:
                            charakter.selected_talente.remove(ah_name)
                        Logger.info(f"Volk {self.name}: AH (Begabt) deaktiviert (Macht-Volk)")

            Logger.info(f"=== Völker-Effekte für {self.name} erfolgreich entfernt ===")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen der Völker-Effekte für {self.name}: {e}")
            return False

    def __str__(self):
        return f"{self.name} (Handicaps: {', '.join(self.handicaps)}, Talente: {', '.join(self.talente)}, Besonderheiten: {', '.join(self.besonderheiten)})"

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            Logger.debug(f"Volk '{self.name}' wurde ausgewählt.")
            return True
        else:
            Logger.warning(f"Volk '{self.name}' ist bereits ausgewählt.")
            return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            Logger.debug(f"Volk '{self.name}' wurde abgewählt.")
            return True
        else:
            Logger.warning(f"Volk '{self.name}' ist nicht ausgewählt.")
            return False

    def to_dict(self):
        return {
            'name': self.name,
            'handicaps': self.handicaps,
            'talente': self.talente,
            'besonderheiten': self.besonderheiten,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom,
            'effects': self.effects  # Neue strukturierte Effekte
        }

    def to_setting_dict(self):
        return {
            'name': self.name,
            'handicaps': self.handicaps,
            'talente': self.talente,
            'besonderheiten': self.besonderheiten,
            'aktiv': self.aktiv,
            'custom': self.custom,
            'effects': self.effects  # Neue strukturierte Effekte
        }

    @classmethod
    def from_dict(cls, data):
        volk = cls(
            name=data.get('name', ''),
            handicaps=data.get('handicaps', []),
            talente=data.get('talente', []),
            besonderheiten=data.get('besonderheiten', []),
            effects=data.get('effects', {}),  # Strukturierte Effekte laden
            custom=data.get('custom', False)
        )
        volk.ausgewaehlt = data.get('ausgewaehlt', False)
        volk.aktiv = data.get('aktiv', True)
        return volk

    @classmethod
    def from_setting_dict(cls, data):
        """Factory method für Setting-Daten (entspricht from_dict)."""
        return cls.from_dict(data)