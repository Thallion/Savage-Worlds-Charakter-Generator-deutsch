class SettingRegeln:
    FELDER = [
        'dynamischer_rueckschlag', 'entschlossenheit', 'fanatiker',
        'fertigkeitsspezialisierungen', 'fieser_schaden', 'geborener_held',
        'grosse_abenteuer', 'helden_sterben_nie', 'keine_machtpunkte',
        'kreativer_kampf', 'mehr_fertigkeitspunkte', 'mehr_sprachen',
        'narrenglueck', 'schnelle_genesung', 'schwere_entscheidungen',
        'ungepanzerter_held', 'wundobergrenze', 'strahlschablone',
        'große_hoehen', 'verrat', 'schwierige_heilung', 'freizeit',
        'riesige_feinde', 'schurkische_entschlossenheit',
    ]

    def __init__(self):
        for feld in self.FELDER:
            setattr(self, feld, False)

    def to_dict(self):
        result = {}
        for feld in self.FELDER:
            result[feld] = getattr(self, feld, False)
        return result

    def from_dict(self, data):
        for feld in self.FELDER:
            key = feld
            if key == 'riesige_feinde':
                value = data.get('riesige_feinde,', data.get('riesige_feinde', False))
            else:
                value = data.get(key, False)
            setattr(self, feld, value)
