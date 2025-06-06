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
        
        # Strukturierte Effekte setzen
        self.effects = effects or {}
        self._parse_effects_from_text()

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
                'fertigkeits_startboni': {},  # {'Wahrnehmung': 2} = W4 -> W6
                'auto_talente': [],           # Automatisch erhaltene Talente
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
        
        # Attribut-Boni erkennen
        attribute = ['stärke', 'geschicklichkeit', 'konstitution', 'verstand', 'willenskraft']
        for attr in attribute:
            if f"{attr} w6 statt w4" in text_lower:
                attr_name = attr.capitalize()
                self.effects['attribute_bonuses'][attr_name] = 2
                
        # Fertigkeits-Boni erkennen
        fertigkeiten = ['wahrnehmung', 'athletik', 'einschüchtern']
        for fert in fertigkeiten:
            if f"{fert} w6 statt w4" in text_lower:
                fert_name = fert.capitalize()
                self.effects['fertigkeits_startboni'][fert_name] = 2
            elif f"beginnt mit w4 in {fert}" in text_lower:
                fert_name = fert.capitalize()
                self.effects['fertigkeits_startboni'][fert_name] = 0  # W4-2 -> W4

        # Robustheit-Effekte
        if "robustheit um 1" in text_lower:
            if ist_handicap or "reduzierte robustheit" in text_lower:
                self.effects['robustheit_bonus'] -= 1
            else:
                self.effects['robustheit_bonus'] += 1
        elif "+1 robustheit" in text_lower:
            self.effects['robustheit_bonus'] += 1

        # Bewegungsweite-Effekte
        if "bewegungsweite" in text_lower and ("-1" in text or "verringerte" in text_lower):
            self.effects['bewegungsweite_bonus'] -= 1

        # Wahlmöglichkeiten erkennen
        if "freies talent" in text_lower:
            self.effects['wahlmoeglichkeiten']['freies_talent'] = True
            
        if "w6 in einem attribut statt w4" in text_lower:
            self.effects['wahlmoeglichkeiten']['freies_attribut'] = True
            
        if "verstandsbasierten fertigkeit auf w4" in text_lower:
            self.effects['wahlmoeglichkeiten']['freie_verstandsfertigkeit'] = True

        # Spezielle Effekte für komplexere Fälle
        if "elfenmagie" in text_lower:
            self.effects['spezielle_effekte']['elfenmagie'] = True
            
        if "nachtsicht" in text_lower or "dunkelsicht" in text_lower:
            self.effects['spezielle_effekte']['nachtsicht'] = True
            
        if "steingespür" in text_lower:
            self.effects['spezielle_effekte']['steingespür'] = True

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
        return self.effects.get('spezielle_effekte', {}).get(effekt_name, False)

    def apply_effects_to_charakter(self, charakter):
        """
        Wendet die Völker-Effekte auf einen Charakter an.
        """
        try:
            # Attribut-Boni anwenden
            for attr_name, bonus in self.effects.get('attribute_bonuses', {}).items():
                if attr_name in charakter.attribute:
                    attribut = charakter.attribute[attr_name]
                    if attribut.wert == 4 and attribut.modifier == 0:  # Nur von W4 auf W6
                        attribut.wuerfel.value = 4 + bonus  # +2 = W6
                        Logger.info(f"Volk {self.name}: {attr_name} von W4 auf W{4+bonus} erhöht")

            # Fertigkeits-Startboni anwenden
            for fert_name, bonus in self.effects.get('fertigkeits_startboni', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    if fertigkeit.wert == 4 and fertigkeit.modifier == -2:  # Standard W4-2
                        fertigkeit.wuerfel.value = 4
                        fertigkeit.wuerfel.modifier = fertigkeit.modifier + bonus
                        Logger.info(f"Volk {self.name}: {fert_name} Startbonus +{bonus}")

            # Automatische Talente hinzufügen
            for talent_name in self.effects.get('auto_talente', []):
                if talent_name in charakter.talente and not charakter.talente[talent_name].ausgewaehlt:
                    charakter.talente[talent_name].ausgewaehlt = True
                    if talent_name not in charakter.selected_talente:
                        charakter.selected_talente.append(talent_name)
                    Logger.info(f"Volk {self.name}: Automatisches Talent {talent_name} erhalten")

            Logger.debug(f"Völker-Effekte für {self.name} angewendet")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Völker-Effekte für {self.name}: {e}")
            return False

    def remove_effects_from_charakter(self, charakter):
        """
        Entfernt die Völker-Effekte von einem Charakter.
        """
        try:
            # Attribut-Boni rückgängig machen
            for attr_name, bonus in self.effects.get('attribute_bonuses', {}).items():
                if attr_name in charakter.attribute:
                    attribut = charakter.attribute[attr_name]
                    if attribut.wert == 4 + bonus:  # Nur wenn der Bonus aktiv war
                        attribut.wuerfel.value = 4
                        Logger.info(f"Volk {self.name}: {attr_name} auf W4 zurückgesetzt")

            # Fertigkeits-Boni rückgängig machen
            for fert_name, bonus in self.effects.get('fertigkeits_startboni', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    fertigkeit.wuerfel.value = 4
                    fertigkeit.wuerfel.modifier = -2  # Standard zurücksetzen
                    Logger.info(f"Volk {self.name}: {fert_name} auf Standard zurückgesetzt")

            # Automatische Talente entfernen
            for talent_name in self.effects.get('auto_talente', []):
                if talent_name in charakter.selected_talente:
                    charakter.selected_talente.remove(talent_name)
                    if talent_name in charakter.talente:
                        charakter.talente[talent_name].ausgewaehlt = False
                    Logger.info(f"Volk {self.name}: Automatisches Talent {talent_name} entfernt")

            Logger.debug(f"Völker-Effekte für {self.name} entfernt")
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