class TestTalente(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        # Initialisiere den Charakter
        self.charakter = Charakter(name="Testcharakter")
        # Füge zusätzliche Talente hinzu
        self.charakter.zusaetzliche_talente = 2  # Beispielhaft 2 zusätzliche Talente durch Handicaps
        # Initialisiere die Talente
        talent_daten = {
            'Hintergrund': hintergrund_talente,
            'Kampf': kampf_talente,
            'Anführer': anfuehrer_talente,
            'Macht': macht_talente,
            'Experte': experten_talente,
            'Sozial': sozial_talente,
            'Übersinnlich': uebersinnliche_talente,
            'Legendär': legendaere_talente
        }
        self.charakter.initialisiere_talente(talent_daten)
        print("setUp - Charakter mit Talenten initialisiert")
    
    def tearDown(self):
        logging.disable(logging.NOTSET)
    
    def test_talent_auswaehlen(self):
        print("test_talent_auswaehlen")
        # Wähle ein Talent aus
        self.charakter.waehle_talent("Aristokrat")
        self.assertTrue(self.charakter.talente["Aristokrat"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 1)
        print("Talent 'Aristokrat' wurde erfolgreich ausgewählt.")
        
        # Wähle ein weiteres Talent aus
        self.charakter.waehle_talent("Attraktiv")
        self.assertTrue(self.charakter.talente["Attraktiv"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 2)
        print("Talent 'Attraktiv' wurde erfolgreich ausgewählt.")
        
        # Überprüfe die maximale Anzahl an Talenten
        self.charakter.waehle_talent("Glück")
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 3)
        print("Talent 'Glück' wurde erfolgreich ausgewählt.")
        
        # Versuch, ein weiteres Talent zu wählen (Limit sollte erreicht sein)
        self.charakter.waehle_talent("Flink")
        self.assertFalse(self.charakter.talente["Flink"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 3)
        print("Maximale Anzahl an Talenten erreicht. Talent 'Flink' konnte nicht ausgewählt werden.")
    
    def test_talent_entfernen(self):
        print("test_talent_entfernen")
        # Wähle ein Talent aus
        self.charakter.waehle_talent("Aristokrat")
        self.assertTrue(self.charakter.talente["Aristokrat"].ausgewaehlt)
        
        # Entferne das Talent
        self.charakter.entferne_talent("Aristokrat")
        self.assertFalse(self.charakter.talente["Aristokrat"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 0)
        print("Talent 'Aristokrat' wurde erfolgreich entfernt.")
        
        # Versuch, ein nicht ausgewähltes Talent zu entfernen
        self.charakter.entferne_talent("Attraktiv")
        self.assertFalse(self.charakter.talente["Attraktiv"].ausgewaehlt)
        print("Talent 'Attraktiv' war nicht ausgewählt und konnte nicht entfernt werden.")
    
    def test_verfuegbare_maechte_und_machtpunkte(self):
        print("test_verfuegbare_maechte_und_machtpunkte")
        # Initial Machtpunkte und verfügbare Mächte sollten 0 sein
        self.assertEqual(self.charakter.verfuegbare_maechte, 0)
        self.assertEqual(self.charakter.machtpunkte, 0)
        
        # Wähle ein Talent, das neue Mächte und Machtpunkte gewährt
        self.charakter.talente["Arkaner Hintergrund"].neue_maechte = 2
        self.charakter.talente["Arkaner Hintergrund"].machtpunkte = 10
        self.charakter.waehle_talent("Arkaner Hintergrund")
        self.assertTrue(self.charakter.talente["Arkaner Hintergrund"].ausgewaehlt)
        self.assertEqual(self.charakter.verfuegbare_maechte, 2)
        self.assertEqual(self.charakter.machtpunkte, 10)
        print("Talent 'Arkaner Hintergrund' wurde ausgewählt. Verfügbare Mächte und Machtpunkte aktualisiert.")
        print("Machtpunkte", self.charakter.machtpunkte)    
        print("Verfügbare Mächte", self.charakter.verfuegbare_maechte)    
        
        # Entferne das Talent und prüfe die Aktualisierung
        self.charakter.entferne_talent("Arkaner Hintergrund")
        self.assertFalse(self.charakter.talente["Arkaner Hintergrund"].ausgewaehlt)
        self.assertEqual(self.charakter.verfuegbare_maechte, 0)
        self.assertEqual(self.charakter.machtpunkte, 0)
        print("Talent 'Arkaner Hintergrund' wurde entfernt. Verfügbare Mächte und Machtpunkte zurückgesetzt.")
    
    def test_talent_bereits_ausgewaehlt(self):
        print("test_talent_bereits_ausgewaehlt")
        # Wähle ein Talent aus
        self.charakter.waehle_talent("Aristokrat")
        self.assertTrue(self.charakter.talente["Aristokrat"].ausgewaehlt)
        
        # Versuch, das gleiche Talent erneut zu wählen
        self.charakter.waehle_talent("Aristokrat")
        self.assertTrue(self.charakter.talente["Aristokrat"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 1)
        print("Talent 'Aristokrat' war bereits ausgewählt und konnte nicht erneut gewählt werden.")
    
    def test_talent_existiert_nicht(self):
        print("test_talent_existiert_nicht")
        # Versuch, ein nicht existierendes Talent zu wählen
        self.charakter.waehle_talent("Nicht existent")
        self.assertNotIn("Nicht existent", self.charakter.talente)
        print("Talent 'Nicht existent' existiert nicht und konnte nicht gewählt werden.")
    
    def test_maximale_talente(self):
        print("test_maximale_talente")
        # Setze die maximale Anzahl an Talenten auf 1
        self.charakter.zusaetzliche_talente = 0  # Nur 1 Talent erlaubt
        self.charakter.waehle_talent("Aristokrat")
        self.assertTrue(self.charakter.talente["Aristokrat"].ausgewaehlt)
        
        # Versuch, ein weiteres Talent zu wählen
        self.charakter.waehle_talent("Attraktiv")
        self.assertFalse(self.charakter.talente["Attraktiv"].ausgewaehlt)
        self.assertEqual(len(self.charakter.ausgewaehlte_talente()), 1)
        print("Maximale Anzahl an Talenten erreicht. Talent 'Attraktiv' konnte nicht ausgewählt werden.")

if __name__ == '__main__':
    print("Unittest wird gestartet")
    unittest.main(verbosity=2)