import logging
import re

Logger = logging.getLogger(__name__)

DEFAULT_EFFECTS = {
    'attribute_bonuses': {},
    'robustheit_bonus': 0,
    'groesse_modifikator': 0,
    'bewegungsweite_bonus': 0,
    'fertigkeits_startboni': {},
    'fertigkeits_startmalus': {},
    'fertigkeits_modifier_boni': {},
    'auto_talente': [],
    'auto_handicaps': [],
    'auto_mächte': [],
    'spezielle_effekte': {},
    'wahlmoeglichkeiten': {},
}


class Volk:
    def __init__(self, name, handicaps=None, talente=None, besonderheiten=None,
                 effects=None, custom=False):
        self.name = name
        self.handicaps = handicaps or []
        self.talente = talente or []
        self.besonderheiten = besonderheiten or []
        self.ausgewaehlt = False
        self.aktiv = True
        self.custom = custom
        self.effects = effects or dict(DEFAULT_EFFECTS)

    def get_attribut_bonus(self, attribut_name):
        return self.effects.get('attribute_bonuses', {}).get(attribut_name, 0)

    def get_fertigkeits_bonus(self, fertigkeits_name):
        return self.effects.get('fertigkeits_startboni', {}).get(fertigkeits_name, 0)

    def get_robustheit_bonus(self):
        return self.effects.get('robustheit_bonus', 0)

    def get_groesse_modifikator(self):
        return self.effects.get('groesse_modifikator', 0)

    def get_bewegungsweite_bonus(self):
        return self.effects.get('bewegungsweite_bonus', 0)

    def has_wahlmoeglichkeit(self, typ):
        return self.effects.get('wahlmoeglichkeiten', {}).get(typ, False)

    def has_spezialeffekt(self, effekt_name):
        spezielle_effekte = self.effects.get('spezielle_effekte', {})
        if isinstance(spezielle_effekte, list):
            return any(e.get('typ') == effekt_name and e.get('wert') for e in spezielle_effekte)
        return spezielle_effekte.get(effekt_name, False)

    def _iter_spezielle_effekte(self):
        spezielle = self.effects.get('spezielle_effekte', [])
        if isinstance(spezielle, list):
            for eintrag in spezielle:
                if isinstance(eintrag, dict):
                    yield eintrag.get('typ'), eintrag.get('wert')
        elif isinstance(spezielle, dict):
            for typ, wert in spezielle.items():
                yield typ, wert

    def _hat_spezialeffekt_typ(self, typ):
        for t, w in self._iter_spezielle_effekte():
            if t == typ and w:
                return True
        return False

    def apply_effects_to_charakter(self, charakter):
        try:
            Logger.info(f"=== Anwenden der Völker-Effekte für {self.name} ===")

            grundfertigkeiten = ["Allgemeinwissen", "Athletik", "Heimlichkeit", "Überreden", "Wahrnehmung"]

            for attr_name, bonus in self.effects.get('attribute_bonuses', {}).items():
                if attr_name in charakter.attribute:
                    attribut = charakter.attribute[attr_name]
                    if bonus > 0:
                        if attribut.wert == 4 and attribut.modifier == 0:
                            attribut.wuerfel.value = 4 + bonus
                    elif bonus < 0:
                        if attribut.modifier == 0:
                            attribut.wuerfel.modifier = bonus

            for fert_name, bonus in self.effects.get('fertigkeits_startboni', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    if fert_name in grundfertigkeiten:
                        if fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                            fertigkeit.wuerfel.value = 4 + bonus
                    else:
                        if fertigkeit.wert == 4 and fertigkeit.modifier == -2:
                            if bonus > 0:
                                fertigkeit.wuerfel.value = 4 + bonus
                                fertigkeit.wuerfel.modifier = 0

            for fert_name, malus in self.effects.get('fertigkeits_startmalus', {}).items():
                if fert_name in charakter.fertigkeiten:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    if fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                        fertigkeit.wuerfel.modifier = malus

            for fert_name, mod_bonus in self.effects.get('fertigkeits_modifier_boni', {}).items():
                if fert_name in charakter.fertigkeiten and mod_bonus != 0:
                    fertigkeit = charakter.fertigkeiten[fert_name]
                    fertigkeit.wuerfel.modifier += mod_bonus

            self._apply_spezialeffekt_stat_changes(charakter, grundfertigkeiten)

            for talent_name in self.effects.get('auto_talente', []):
                if talent_name in charakter.talente and not charakter.talente[talent_name].ausgewaehlt:
                    charakter.talente[talent_name].ausgewaehlt = True
                    if talent_name not in charakter.selected_talente:
                        charakter.selected_talente.append(talent_name)
                    talent = charakter.talente[talent_name]
                    if hasattr(talent, 'machtpunkte') and talent.machtpunkte > 0:
                        charakter.erhoehe_machtpunkte(talent.machtpunkte)
                    if hasattr(talent, 'neue_maechte') and talent.neue_maechte > 0:
                        charakter.verfuegbare_maechte += talent.neue_maechte
                        charakter.anzahl_maechte += talent.neue_maechte

            for handicap_name in self.effects.get('auto_handicaps', []):
                if handicap_name in charakter.handicaps and not charakter.handicaps[handicap_name].ausgewaehlt:
                    charakter.handicaps[handicap_name].ausgewaehlt = True
                    if handicap_name not in charakter.selected_handicaps:
                        charakter.selected_handicaps.append(handicap_name)

            for macht_name in self.effects.get('auto_mächte', []):
                if macht_name in charakter.maechte and not charakter.maechte[macht_name].ausgewaehlt:
                    charakter.maechte[macht_name].ausgewaehlt = True
                    if macht_name not in charakter.selected_maechte:
                        charakter.selected_maechte.append(macht_name)

            return True
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Völker-Effekte für {self.name}: {e}")
            return False

    def _apply_spezialeffekt_stat_changes(self, charakter, grundfertigkeiten):
        try:
            if self._hat_spezialeffekt_typ('wahrnehmung_w6'):
                fertigkeit = charakter.fertigkeiten.get('Wahrnehmung')
                if fertigkeit and fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                    fertigkeit.wuerfel.value = 6

            if self._hat_spezialeffekt_typ('wahrnehmung_w8'):
                fertigkeit = charakter.fertigkeiten.get('Wahrnehmung')
                if fertigkeit and fertigkeit.wert == 4 and fertigkeit.modifier == 0:
                    fertigkeit.wuerfel.value = 8

            if self._hat_spezialeffekt_typ('natuerlicher_kaempfer'):
                fertigkeit = charakter.fertigkeiten.get('Kämpfen')
                if fertigkeit and fertigkeit.wert == 4 and fertigkeit.modifier == -2:
                    fertigkeit.wuerfel.value = 6
                    fertigkeit.wuerfel.modifier = 0
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden von Spezialeffekt-Stat-Änderungen für {self.name}: {e}")

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            return True
        return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            return True
        return False

    def to_dict(self):
        return {
            'name': self.name,
            'handicaps': list(self.handicaps),
            'talente': list(self.talente),
            'besonderheiten': list(self.besonderheiten),
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom,
            'effects': self.effects,
        }

    @classmethod
    def from_dict(cls, data):
        volk = cls(
            name=data.get('name', ''),
            handicaps=data.get('handicaps', []),
            talente=data.get('talente', []),
            besonderheiten=data.get('besonderheiten', []),
            effects=data.get('effects', {}),
            custom=data.get('custom', False),
        )
        volk.ausgewaehlt = data.get('ausgewaehlt', False)
        volk.aktiv = data.get('aktiv', True)
        return volk

    @classmethod
    def from_setting_dict(cls, data):
        return cls.from_dict(data)
