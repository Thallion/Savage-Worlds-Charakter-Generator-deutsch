if __name__ == '__main__':
    # Initialisiere den Charakter
    charakter = Charakter(name="Maximus")

    # Steigere die Attribute auf das Maximum mit den verfügbaren Punkten
    charakter.steigere_attribut('Stärke')         # W4 -> W6
    charakter.steigere_attribut('Stärke')         # W6 -> W8
    charakter.steigere_attribut('Geschicklichkeit')  # W4 -> W6
    charakter.steigere_attribut('Konstitution')      # W4 -> W6
    charakter.steigere_attribut('Verstand')          # W4 -> W6
    charakter.steigere_attribut('Verstand')          # W6 -> W8

    # Steigere die Fertigkeiten mit den verfügbaren Punkten
    charakter.steigere_fertigkeit('Kämpfen')      # W4 -> W6
    charakter.steigere_fertigkeit('Kämpfen')      # W6 -> W8
    charakter.steigere_fertigkeit('Schießen')     # W4 -> W6
    charakter.steigere_fertigkeit('Schießen')     # W6 -> W8
    charakter.steigere_fertigkeit('Athletik')     # W4 -> W6
    charakter.steigere_fertigkeit('Athletik')     # W6 -> W8
    charakter.steigere_fertigkeit('Wahrnehmung')  # W4 -> W6
    charakter.steigere_fertigkeit('Überleben')    # W4 -> W6
    charakter.steigere_fertigkeit('Heimlichkeit') # W4 -> W6
    charakter.steigere_fertigkeit('Heimlichkeit') # W6 -> W8
    charakter.steigere_fertigkeit('Heimlichkeit') # W8 -> W10

    # Initialisiere die Handicaps
    charakter.initialisiere_handicaps(handicap_liste)

    # Wähle Handicaps aus
    charakter.waehle_handicap("Analphabet (leicht)")
    charakter.waehle_handicap("Beschämt (leicht)")
    charakter.waehle_handicap("Blind (schwer)")

    # Berechne zusätzliche Talente
    zusaetzliche_talente = charakter.berechne_zusaetzliche_talente()
    print(f"Zusätzliche Talente durch Handicaps: {zusaetzliche_talente}")

    # Initialisiere die Talente
    charakter.initialisiere_talente(talent_daten)

    # Wähle Talente aus
    charakter.waehle_talent("Arkaner Hintergrund")
    charakter.waehle_talent("Machtpunkte")
    charakter.waehle_talent("Neue Mächte")

    print(f"Verfügbare Mächte: {charakter.verfuegbare_maechte}")
    print(f"Machtpunkte: {charakter.machtpunkte}")

    # Initialisiere die Mächte
    charakter.initialisiere_maechte(maechte_daten)

    # Wähle Mächte aus
    charakter.waehle_macht("Gedankenleere")
    charakter.waehle_macht("Heilung")

    # Initialisiere Ausrüstung, Rüstungen und Waffen
    charakter.initialisiere_ausruestung(ausruestung_daten)
    charakter.initialisiere_ruestungen(ruestung_daten)
    charakter.initialisiere_waffen(waffen_daten)

    # Kaufe Rüstung
    jacke = charakter.ruestungen["Jacke (dick)"]
    charakter.kaufen(jacke)
    jacke.anlegen(charakter)

    # Überprüfen, ob die Rüstung angelegt ist
    print(f"Jacke (dick) angelegt: {jacke.angelegt}")  # Sollte True sein

    # Kaufe Rüstung
    jacke = charakter.ruestungen["Jacke (dünn)"]
    charakter.kaufen(jacke)
    jacke.anlegen(charakter)

    # Überprüfen, ob die Rüstung angelegt ist
    print(f"Jacke (dick) angelegt: {jacke.angelegt}")  # Sollte True sein   

    abgeleitete_werte = charakter.berechne_abgeleitete_werte()
    print("Abgeleitete Werte nach Anlegen der Rüstung:")
    for key, value in abgeleitete_werte.items():
        print(f"{key}: {value}")

    # Kaufe Nahkampfwaffe
    langschwert = charakter.waffen_daten["Laserschwert"]
    charakter.kaufen(langschwert)
    langschwert.anlegen(charakter)

    # Kaufe Fernkampfwaffe
    langbogen = charakter.waffen_daten["Gatling (.45)"]
    charakter.kaufen(langbogen)
    langbogen.anlegen(charakter)

    # Kaufe Ausrüstung
    seil = charakter.ausruestung_daten["Werkzeugkoffer"]
    charakter.kaufen(seil, anzahl=1)

    print(f"Verbleibendes Vermögen: {charakter.vermoegen} Münzen")

    abgeleitete_werte = charakter.berechne_abgeleitete_werte()
    print("Abgeleitete Werte:")
    for key, value in abgeleitete_werte.items():
        print(f"{key}: {value}")

    print("\nCharakterübersicht:")
    print(f"Name: {charakter.name}")
    print("Attribute:")
    for attribut in charakter.attribute.values():
        print(f"{attribut.name}: W{attribut.wert}")

    print("\nFertigkeiten:")
    for fertigkeit in charakter.fertigkeiten.values():
        if fertigkeit.wert > 4:
            print(f"{fertigkeit.name}: W{fertigkeit.wert}")

    print("\nHandicaps:")
    for handicap in charakter.ausgewaehlte_handicaps():
        print(f"{handicap.name} ({handicap.stufe}): {handicap.beschreibung}")

    print("\nTalente:")
    for talent in charakter.ausgewaehlte_talente():
        print(f"{talent.name}{talent.beschreibung}")

    print("\nMächte:")
    for macht in charakter.ausgewaehlte_maechte():
        print(f"{macht.name}, Rang: {macht.rang}, 'Machtpunkte' {macht.machtpunkte}, 'Reichweite': {macht.reichweite}, 'Dauer': {macht.dauer}, Effekt: {macht.effekt}")

    print("\nAusrüstung:")
    for item in charakter.ausruestung_daten.values():
        if item.menge > 0:
            print(f"{item.name} x{item.menge}")

    print("\nWaffen:") 
    for waffe in charakter.waffen_daten.values():
        if waffe.menge > 0:
            status = "Angelegt" if waffe.angelegt else "Nicht angelegt"
            # Formatieren der Eigenschaften als Schlüssel=Wert
            eigenschaften = ', '.join(f"{k}={v}" for k, v in waffe.eigenschaften.items()) if waffe.eigenschaften else 'Keine'
            print(f"{waffe.name}: {eigenschaften}")

    print("\nRüstungen:")
    for ruestung in charakter.ruestungen.values():
        if ruestung.angelegt:
            status = "Angelegt"
            print(f"{ruestung.name}: Torso={ruestung.torso}, Arme={ruestung.arme}, Beine={ruestung.beine}, Kopf={ruestung.kopf}, Status={status}")
        else:
            status = "Nicht angelegt"
       

