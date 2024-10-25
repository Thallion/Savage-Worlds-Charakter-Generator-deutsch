class TestHandicaps(unittest.TestCase):
    def setUp(self):
        print("setUp wird aufgerufen")
        # logging.disable(logging.CRITICAL)
        try:
            # Verwenden Sie die vollständige Handicap-Liste
            self.handicap_liste = handicap_liste
            self.charakter = Charakter(name="Testcharakter")
            self.charakter.initialisiere_handicaps(self.handicap_liste)
            print("setUp - Charakter mit Handicaps initialisiert")
        except Exception as e:
            print(f"Fehler in setUp: {e}")
    
    def tearDown(self):
        print("tearDown wird aufgerufen")
        logging.disable(logging.NOTSET)
    
    def test_initialisierung_handicaps(self):
        print("test_initialisierung_handicaps")
        # Überprüfe, ob alle Handicaps korrekt initialisiert wurden
        anzahl_handicaps = len(self.handicap_liste)
        self.assertEqual(len(self.charakter.handicaps), anzahl_handicaps)
        
        print("Schlüssel in self.charakter.handicaps:")
        for key in self.charakter.handicaps.keys():
            print(key)
        
        for daten in self.handicap_liste:
            name = daten.get('Name', '')
            stufe = daten.get('Stufe', '').lower()
            name_key = f"{name} ({stufe})"
            self.assertIn(name_key, self.charakter.handicaps)
            handicap = self.charakter.handicaps[name_key]
            self.assertEqual(handicap.name, name)
            self.assertEqual(handicap.stufe, stufe)
            self.assertEqual(handicap.beschreibung, ' ')
            self.assertFalse(handicap.ausgewaehlt)
            self.assertTrue(handicap.aktiv)
        print(f"Alle {anzahl_handicaps} Handicaps wurden korrekt initialisiert.")

        
    def test_waehle_handicap(self):
        print("test_waehle_handicap")
        # Wähle einige Handicaps aus, ohne das Limit von 4 Punkten zu überschreiten
        self.charakter.waehle_handicap("Analphabet (leicht)")
        self.assertTrue(self.charakter.handicaps["Analphabet (leicht)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 1)
        
        self.charakter.waehle_handicap("Angetrieben (schwer)")
        self.assertTrue(self.charakter.handicaps["Angetrieben (schwer)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 3)
        
        # Versuch, ein Handicap zu wählen, das das Limit überschreiten würde
        self.charakter.waehle_handicap("Alt (schwer)")
        self.assertFalse(self.charakter.handicaps["Alt (schwer)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 3)
        print("Handicap 'Alt (schwer)' konnte nicht gewählt werden, da es das Punktelimit überschreiten würde.")
        
        # Wähle ein weiteres leichtes Handicap
        self.charakter.waehle_handicap("Angewohnheit (leicht)")
        self.assertTrue(self.charakter.handicaps["Angewohnheit (leicht)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 4)
        print("Handicap 'Angewohnheit (leicht)' wurde erfolgreich gewählt.")
        
        # Überprüfe die Anzahl der zusätzlichen Talente
        self.assertEqual(self.charakter.zusaetzliche_talente, 2)
        print(f"Zusätzliche Talente: {self.charakter.zusaetzliche_talente}")
    
    def test_entferne_handicap(self):
        print("test_entferne_handicap")
        # Wähle einige Handicaps aus
        self.charakter.waehle_handicap("Analphabet (leicht)")
        self.charakter.waehle_handicap("Angetrieben (schwer)")
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 3)
        self.assertEqual(self.charakter.zusaetzliche_talente, 1)
        
        # Entferne ein Handicap
        self.charakter.entferne_handicap("Angetrieben (schwer)")
        self.assertFalse(self.charakter.handicaps["Angetrieben (schwer)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 1)
        self.assertEqual(self.charakter.zusaetzliche_talente, 0)
        print("Handicap 'Angetrieben (schwer)' wurde entfernt.")
        
        # Versuche nun, ein schweres Handicap zu wählen
        self.charakter.waehle_handicap("Alt (schwer)")
        self.assertTrue(self.charakter.handicaps["Alt (schwer)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 3)
        print("Handicap 'Alt (schwer)' wurde erfolgreich gewählt.")
    
    def test_ueberschreite_punktelimit(self):
        print("test_ueberschreite_punktelimit")
        # Wähle Handicaps bis zum Limit
        self.charakter.waehle_handicap("Analphabet (leicht)")  # 1 Punkt
        self.charakter.waehle_handicap("Angewohnheit (leicht)")  # 1 Punkt, Gesamt: 2
        self.charakter.waehle_handicap("Angetrieben (schwer)")  # 2 Punkte, Gesamt: 4
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 4)
        self.assertEqual(self.charakter.zusaetzliche_talente, 2)
        
        # Versuch, ein existierendes Handicap zu wählen, das das Limit überschreiten würde
        self.charakter.waehle_handicap("Feind (leicht)")
        self.assertFalse(self.charakter.handicaps["Feind (leicht)"].ausgewaehlt)
        print("Handicap 'Feind (leicht)' konnte nicht gewählt werden, da es das Punktelimit überschreiten würde.")
        
        # Versuch, ein nicht existierendes Handicap zu wählen
        self.charakter.waehle_handicap("Nicht existent (leicht)")
        self.assertNotIn("Nicht existent (leicht)", self.charakter.handicaps)
        print("Handicap 'Nicht existent (leicht)' existiert nicht und konnte nicht gewählt werden.")
    
    def test_berechne_zusaetzliche_talente(self):
        print("test_berechne_zusaetzliche_talente")
        # Keine Handicaps ausgewählt
        self.assertEqual(self.charakter.zusaetzliche_talente, 0)
        
        # Wähle Handicaps im Wert von 3 Punkten
        self.charakter.waehle_handicap("Analphabet (leicht)")  # 1 Punkt
        self.charakter.waehle_handicap("Angetrieben (schwer)")  # 2 Punkte
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 3)  # Sollte jetzt korrekt sein
        self.assertEqual(self.charakter.zusaetzliche_talente, 1)
        print(f"Gesamt Handicappunkte: {self.charakter.gesamt_handicap_punkte}, Zusätzliche Talente: {self.charakter.zusaetzliche_talente}")
        
        # Wähle ein weiteres leichtes Handicap
        self.charakter.waehle_handicap("Angewohnheit (leicht)")  # 1 Punkt, Gesamt: 4
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 4)
        self.assertEqual(self.charakter.zusaetzliche_talente, 2)
        print(f"Gesamt Handicappunkte: {self.charakter.gesamt_handicap_punkte}, Zusätzliche Talente: {self.charakter.zusaetzliche_talente}")
    
    def test_handicap_auswaehlen_und_entfernen(self):
        print("test_handicap_auswaehlen_und_entfernen")
        # Wähle ein Handicap
        self.charakter.waehle_handicap("Angewohnheit (leicht)")
        self.assertTrue(self.charakter.handicaps["Angewohnheit (leicht)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 1)
        
        # Entferne das Handicap
        self.charakter.entferne_handicap("Angewohnheit (leicht)")
        self.assertFalse(self.charakter.handicaps["Angewohnheit (leicht)"].ausgewaehlt)
        self.assertEqual(self.charakter.gesamt_handicap_punkte, 0)
        print("Handicap 'Angewohnheit (leicht)' wurde erfolgreich entfernt.")
        
        # Versuch, ein nicht ausgewähltes Handicap zu entfernen
        self.charakter.entferne_handicap("Angewohnheit (leicht)")
        print("Handicap 'Angewohnheit (leicht)' war bereits nicht ausgewählt.")
        
        # Versuch, ein nicht existierendes Handicap zu entfernen
        self.charakter.entferne_handicap("Nicht existent (leicht)")
        print("Handicap 'Nicht existent (leicht)' existiert nicht und konnte nicht entfernt werden.")

if __name__ == '__main__':
    print("Unittest wird gestartet")
    unittest.main(verbosity=2)