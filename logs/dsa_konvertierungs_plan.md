 # Plan: Savage Aventurien — Konvertierung zu DSA (Das Schwarze Auge)

**Stand:** 2026-06-03
**Quell-Setting:** `settings/Savage Aventurien.json` (Kombination aus Savage Pathfinder + Fantasy Kompendium)
**Ziel-Setting:** Repräsentation von "Das Schwarze Auge 5" als SW-Setting
**Strategie:** Convert the Setting, not the Rules — SW-Kern behalten, DSA-Flair über Völker, Mächte (mit Trappings) und Settingregeln

---

## 1. Ausgangslage

| Element | Aktueller Stand | Anmerkung |
|---------|----------------|-----------|
| `name` | "Savage Aventurien" | ggf. ergänzen / Versionierung |
| `voelker` | 10 Völker | +2 neue (Holberker, Nachtalb) → 12 |
| `voelker_selected` | 15 Einträge (Standard-SW-Rassen) | reduzieren auf 12 DSA-Spezies |
| `attribute` | 5 Attribute (Standard SW) | unverändert |
| `fertigkeiten_daten` | 31 Fertigkeiten | evtl. 1-2 DSA-spezifische ergänzen |
| `talente` | 488 Talente | ca. 50-80 ersatzlos streichen, ~20-30 DSA-spezifisch ergänzen |
| `handicaps` | 162 Handicaps | ca. 30 streichen, DSA-Vor-/Nachteile ergänzen |
| `maechte` | 73 Mächte (flache Liste) | beibehalten + DSA-Trappings ergänzen, evtl. ~5-10 neue Mächte |
| `ausruestung` | 449 Items | DSA-spezifisch erweitern, preislich in DSA-Münzen (S/D/H/K) |
| `settingregeln` | 25 Regeln (alle FALSE) | DSA-Regeln aktivieren |
| `startgeld` | 300 GM | DSA-Startwerte |
| `waehrung` | "GM" | auf "DSA" (S/D/H/K) umstellen |

---

## 2. Die 5 Kategorien (Legende)

Für jedes Element wird eine Konvertierungs-Entscheidung getroffen:

| # | Status | Bedeutung |
|---|--------|-----------|
| **1** | Wird aus Savage Worlds übernommen | keine Änderung |
| **2** | Savage Worlds Regel muss angepasst werden | Beschreibung / Mechanik ändern |
| **3** | Wird gelöscht, da nicht im Setting vorgesehen | komplett entfernen |
| **4** | Fehlt im DSA-Regelwiki und wird ergänzt | neu hinzufügen |
| **5** | Fehlt im DSA-Regelwiki und wird NICHT ergänzt | bewusst weglassen |

---

## 3. Völker (Spezies) — 10 bestehende + 2 neue = 12

Quelle: https://dsa.ulisses-regelwiki.de/spezies.html

### 3.1 Konvertierungstabelle

| Spezies | Status | Aktion | Begründung |
|---------|:------:|--------|------------|
| **Mensch** | 2 | DSA-typische Anpassung | LE=5, GS=8, KE=5, +1 Attribut frei. Mittelländer, Thorwaler, Nivesen, Tulamiden, Waldmenschen als Kultur-Wahl. |
| **Elf** | 2 | DSA-typische Anpassung | LE=5, SK variabel, Zä variabel, GS=8. Niedrige Zähigkeit (Wald+Stadt-Aversion), Elfenwuchs-Wahl (Lang/Groß). |
| **Halbelf** | 2 | DSA-typische Anpassung | Mischung Mensch+Elf, beide Kulturen. Eingeschränkte Immunität gegen Wundübel. |
| **Zwerg** | 2 | DSA-typische Anpassung | LE=8 (Variabel), SK=5, Zä=5, GS=6. Zäher Hund, Tradition, Hob-Füße. |
| **Ork** | 2 | DSA-typische Anpassung | LE=10, SK variabel, Zä=5, GS=8. Hitze-Resistenz, Nachtsicht, Blutrausch. |
| **Halbork** | 2 | DSA-typische Anpassung | Mischung wie Halbelf, etwas weniger extreme Werte. |
| **Goblin** | 2 | DSA-typische Anpassung | LE=8, SK=5, Zä=5, GS=6. Schlitzohrig, Fieser Trick, Verrückte Wissenschaft (statt nur "Flink"). |
| **Achaz** | 2 | DSA-typische Anpassung | LE=10, SK=5, Zä=5, GS=8. Hitzeresistenz, Kältempfindlich, Schuppenhaut. |
| **Necker** | 2 | DSA-typische Anpassung | LE=8, SK=5, Zä=5, GS=6/Schwimmen 8. Amphibisch, Lauerer. |
| **Drachling** | 2 | DSA-typische Anpassung | LE=10, SK=5, Zä=5, GS=6. Odem-Waffe, Panzerung +2, Elementar-Wahl. |
| **Holberker** 🆕 | 4 | NEU | Verwilderte Menschen, LE=5, SK variabel, Zä=5, GS=8. Tierempathie, Wildnis-Vorteile. |
| **Nachtalb** 🆕 | 4 | NEU | Albino-Nachkommen der Elfen, LE=5, SK=5, Zä=5, GS=8. Nachtsicht, Aberglaube-Umfeld. |

### 3.2 `voelker_selected` — Update

**Aktuell (15):** Elf, Gnom, Halbelf, Halbling, Halbork, Ifrits, Mensch, Oreads, Zwerg, Android, Aquarianer, Avionen, Halbelfe, Rakashaner, Saurianer

**Neu (12):** Elf, Halbelf, Zwerg, Ork, Halbork, Goblin, Achaz, Necker, Drachling, Holberker, Nachtalb, Mensch

Achtung: aktuell ist "Mensch" als einziges auf `True`. Wir setzen alle 12 DSA-Spezies auf `True` (User-Default, im UI abwählbar).

---

## 4. Mächte — SW-Basis beibehalten + DSA-Trappings

Quelle: https://dsa.ulisses-regelwiki.de/zauberauswahl.html (263), https://dsa.ulisses-regelwiki.de/ritualauswahl.html (74), https://dsa.ulisses-regelwiki.de/liturgieauswahl.html (199), https://dsa.ulisses-regelwiki.de/zeremonieauswahl.html (138), https://dsa.ulisses-regelwiki.de/segenauswahl.html (12)

### 4.1 Strategie

- **Bleibt:** Die 73 bestehenden SW-Mächte
- **Ergänzt pro Macht:** `dsa_trappings: ["DSA-Zaubername 1", "DSA-Zaubername 2", …]`
- **Neu (Status 4):** ~5-10 Mächte für DSA-typische Effekte (z.B. "Leib aus Eichenholz", "Sturmwand" als Variante, "Zauberklinge")
- **Gelöscht (Status 3):** Falls welche sich als redundant erweisen (z.B. "Chaos" wirkt zu SW-typisch)

### 4.2 Konvertierungstabelle (Beispiele)

| SW-Macht | Status | DSA-Trapping(s) | Bemerkung |
|----------|:------:|-----------------|-----------|
| **Heilung** | 1 | Balsam Salabunde, Hexenspeichel, Salander, Heilungsbann | Kernzauber Gildenmagier + Heilung Liturgie |
| **Elementarmanipulation** | 1 | Ignifaxius, Aquasphaero, Humuspfeil, Orcanofaxius, Fulminictus | Elementarzauber |
| **Blenden** | 1 | Blendung, Blindheit, Obarans Blendung | |
| **Betäuben** | 1 | Paralyse, Schmerzen lindern (umgekehrt) | |
| **Furcht** | 1 | Angst auslösen, Horriphobus, Panik überkomme euch, Furcht | |
| **Tarnung** (im Setting: Geräusch/Stille?) | 1 | Silentium, Nebelwand, Schleier der Unwissenheit | |
| **Gedankenlesen** | 1 | Blick in die Gedanken, Seelentier erkennen, Offenlegung des Geistes | |
| **Eigenschaft erhöhen/senken** | 1 | Attributo (KU/CH/GE/etc.), Stärke/Schwäche | |
| **Böswillige Verwandlung** | 1 | Alpgestalt, Chamaelioni, Serpentialis, Tiergestalt | |
| **Gegenstand beschwören** | 1 | Objectovoco, Objectofixo, Heiliger Befehl, Invocatio Minima | |
| **Ebenenwechsel** | 1 | Transversalis, Körperlose Reise, Sphärenbann, Planastrale | |
| **Marionette** | 1 | Bannbaladin, Dominion, Impersona, Zwingtanz | |
| **Bannen** (im Setting: Aufheben?) | 1 | Dämonenbann, Elementarbann, Verwandlungsbann, Temporalbann, Bannzone | |
| **Schutz** (Arkaner Schutz) | 1 | Armatrutz, Schimmernder Schild, Magieschutz, Paravantio | |
| **Schaden (Geschoss)** | 1 | Eispfeil, Erzpfeil, Feuerpfeil, Luftpfeil, Wasserpfeil, Humuspfeil | |
| **Wall / Barriere** | 1 | Flammenwand, Eichenleib, Eiswand, Dornenwand, Granit und Marmor, Standfest, Wellenwand | |
| **Fliegen** | 1 | Adlerschwinge, Aerofugo, Firmlauf, Wipfellauf, Wolkenwand | |
| **Tiere kontrollieren** (im Setting: Beschwören oder Tiermeister?) | 1 | Herr über das Tierreich, Tiere besprechen, Tiergedanken, Seelentier erkennen | |
| **Gestaltwandeln** | 1 | Metamorphose (Frosch, Echse etc.), Animalia, Wandler, Chimärenform | |
| **Licht / Dunkelheit** | 1 | Dunkelheit, Licht (Auge des Limbus), Oculus Astralis | |
| **Heilung entfernen / Fluch** | 1 | Böser Blick, Mal der Erschöpfung, Pestodem, Schleichende Fäulnis, Fluch der Schwäche | |
| **Erkennen / Scannen** | 1 | Analys Arkanstruktur, Magieanalyse, Magiesicht, Arcanovi, Pectetinzzel, Odem Arcanum | |

### 4.3 Neue Mächte (Status 4)

| Neue Macht | DSA-Name | Reichweite | MP | Bemerkung |
|------------|----------|------------|----|-----------|
| **Heiliger Boden** | Bodenweihe, Weihe des Bodens, Ortsweihe (Sanctum) | Zone | 3+ | Götterwirken-Schutzkreis |
| **Zeremonie (Liturgien-Boost)** | Weihe des Heims, Göttliche Erkenntnis | Berührung | 2 | Boost für Liturgien |
| **Ritualplatz** | Dschinnenruf, Invocatio Maior, Invocatio Maxima, Standhafter Wächter | Zone | 5+ | Mächtige Rituale |
| **Liturgieschild** | Liturgieschild, Bann der Dunkelheit, Bann des Lichts | Selbst | 2 | Kleriker-Schutz |
| **Geisterruf** | Geisterruf, Geisterbeschwörung, Totes handle, Blick in die Flammen | Zone | 3+ | Schamanen / Geoden |
| **Elfenlied** | Verzerrtes Elfenlied, Elfenstimme | Selbst / Zone | 2 | Elfen-Magie |
| **Zaubermelodie** | Bannlied, Klagelied, Zaubermelodie | Selbst | 2 | Barden-Magie |
| **Hexenknoten** | Hexenkrallen, Hexengalle, Hexenholz | Berührung | 2 | Hexen-Fluch |

### 4.4 Status 3 (zu löschen)

| Macht | Begründung |
|-------|------------|
| Chaos (Magie) | Zu generisch, nicht DSA-typisch |
| Bindender Ruf (V) | Ersetzt durch "Bannbaladin" / "Zwingtanz" |

> **Hinweis:** Die Lösch-Liste ist vorläufig und sollte mit dem User in der Review-Session abgestimmt werden.

### 4.5 Vollständige DSA → SW-Macht Zuordnungs-Liste

**Legende:**

| Kürzel | Bedeutung |
|:------:|-----------|
| `H:X` | existierende SW-Macht `X` (Status 1, direkt zuweisen) |
| `B:X` | existierende SW-Macht `X` (Status 2, DSA-Beschreibung anpassen) |
| `N:X` | neue SW-Macht `X` nötig (Status 4, muss neu angelegt werden) |
| `×`   | kein passendes SW-Äquivalent — nur als DSA-Trapping in Beschreibung führen |

**Quellen:**
- 263 Zauber → https://dsa.ulisses-regelwiki.de/zauberauswahl.html
- 74 Rituale → https://dsa.ulisses-regelwiki.de/ritualauswahl.html
- 199 Liturgien → https://dsa.ulisses-regelwiki.de/liturgieauswahl.html
- 138 Zeremonien → https://dsa.ulisses-regelwiki.de/zeremonieauswahl.html
- 12 Segen → https://dsa.ulisses-regelwiki.de/segenauswahl.html

#### 4.5.1 Zauber (263) → SW-Macht

| # | DSA-Zauber | → SW-Macht | Bemerkung |
|--:|------------|:----------:|-----------|
| 1 | Ablativum | N:Schutzrüstung | absorbiert Schaden, Schild-Zauber |
| 2 | Abvenenum | N:Gegengift | entfernt Gift |
| 3 | Adlerauge | H:Fernsicht | Sicht verbessern, Weitsicht |
| 4 | Adlerschwinge | H:Fliegen | Flug, kurz |
| 5 | Aeolito | H:Wetterkontrolle | Wind |
| 6 | Aerofugo | H:Fliegen | Wind, Flug |
| 7 | Affenarme | H:Eigenschaft erhöhen | Kletterarme |
| 8 | Affenruf | N:Tierruf | Affe |
| 9 | Alpgestalt | H:Böswillige Verwandlung | Alp-Gestalt |
| 10 | Altisonus | N:Schallverstärkung | Donner, Laut |
| 11 | Analys Arkanstruktur | H:Arkanes entdecken | Magie analysieren |
| 12 | Angst auslösen | H:Furcht | |
| 13 | Aquafaxius | H:Geschoss | Wasserpfeil |
| 14 | Aquaqueris | N:Wasserreinigung | Quellensuche |
| 15 | Aquasphaero | H:Flächenschlag | Wasser-Sphäre |
| 16 | Arachnea | N:Spinnennetz | Spinnenfäden-Netz |
| 17 | Archofaxius | H:Geschoss | archaisch Eis-Pfeil |
| 18 | Archosphaero | H:Flächenschlag | archaisch Eis-Sphäre |
| 19 | Armatrutz | H:Schutz | Panzerung |
| 20 | Aromatis Illusionis | N:Duftzauber | Geruchs-Illusion |
| 21 | Atemnot | H:Lähmung | Atem lähmen |
| 22 | Attributo (Charisma) | H:Eigenschaft erhöhen | CH |
| 23 | Attributo (Fingerfertigkeit) | H:Eigenschaft erhöhen | FF |
| 24 | Attributo (Gewandtheit) | H:Eigenschaft erhöhen | GE |
| 25 | Attributo (Intuition) | H:Eigenschaft erhöhen | IN |
| 26 | Attributo (Klugheit) | H:Eigenschaft erhöhen | KL |
| 27 | Attributo (Konstitution) | H:Eigenschaft erhöhen | KO |
| 28 | Attributo (Körperkraft) | H:Eigenschaft erhöhen | KK |
| 29 | Attributo (Mut) | H:Eigenschaft erhöhen | MU |
| 30 | Aufwecken | H:Heilung | Bewusstlose wecken |
| 31 | Auge des Limbus | H:Fernsicht | Übersinnlich |
| 32 | Aura der Erschöpfung | H:Schwächung | Aura-Erschöpfung |
| 33 | Aureolus | N:Heiliger Schein | Licht, Schutz vor Untoten |
| 34 | Auris Illusionis | H:Illusion | Geräusch-Illusion |
| 35 | Avilea | N:Regenruf | Wetter |
| 36 | Axxeleratus | H:Geschwindigkeit | Bewegung beschleunigen |
| 37 | Ängste Lindern | H:Empathie | Furcht lindern |
| 38 | Balsam Salabunde | H:Heilung | Wundheilung, Klassiker |
| 39 | Band und Fessel | H:Lähmung | Fesselzauber |
| 40 | Bannbaladin | B:Marionette | Willenskontrolle, Barde |
| 41 | Basaltleib | B:Schutz | Stein-Panzerung |
| 42 | Blick aufs Wesen | H:Arkanes entdecken | Wesen erkennen |
| 43 | Blick in die Gedanken | H:Gedankenlesen | |
| 44 | Blindheit | H:Blenden | |
| 45 | Blitz dich find | N:Blitzruf | Teleportation |
| 46 | Blitzball | H:Geschoss | Elektrizität |
| 47 | Böser Blick | H:Fluch | Schwächender Blick |
| 48 | Brandungsleib | B:Schutz | Wasser-Panzerung |
| 49 | Brennender Hass | H:Marionette | Hass anfachen |
| 50 | Chamaelioni | H:Böswillige Verwandlung | Farbwechsel |
| 51 | Claudibus | H:Lähmung | Kälte-Lähmung |
| 52 | Corpofesso | H:Spurlos | Kälte-Tarnung |
| 53 | Corpofrigo | H:Geschoss | Kälte-Pfeil |
| 54 | Cryptographo | N:Verschlüsselung | Geheimschrift |
| 55 | Dämonenbann | H:Aufheben | Bann |
| 56 | Dämonenschild | H:Arkaner Schutz | |
| 57 | Dämonisches Vergessen | H:Gedankenleere | Gedächtnis löschen |
| 58 | Debilitatio | H:Schwächung | |
| 59 | Desintegratus | H:Verwirrung | Stärke senken |
| 60 | Disruptivo | H:Magie bannen | Magie stören |
| 61 | Dornenwand | H:Barriere | Dornen |
| 62 | Drachenleib | B:Schutz | Drachen-Panzerung |
| 63 | Dunkelheit | H:Dunkelsicht | Gegenteilig |
| 64 | Duplicatus | N:Doppelgänger | Ebenbild |
| 65 | Ecliptifactus | N:Finsternis | Sonne/Mond |
| 66 | Eichenleib | B:Schutz | Eichen-Panzerung |
| 67 | Eigene Ängste | H:Furcht | |
| 68 | Eigene Dummheit | H:Verwirrung | |
| 69 | Einflussbann | H:Magie bannen | |
| 70 | Eisenrost | N:Rost | Waffen rosten |
| 71 | Eiseskälte Kämpferherz | B:Hauch | Kälte-Berserker |
| 72 | Eispfeil | H:Geschoss | Kälte |
| 73 | Eiswand | H:Barriere | Eis |
| 74 | Elementarbann | H:Magie bannen | Elementarmagie |
| 75 | Elfenstimme | H:Empathie | Stimme, Bonus |
| 76 | Erinnerung verlasse dich | H:Gedankenleere | |
| 77 | Erschöpfungen lindern | H:Heilung | Müdigkeit heilen |
| 78 | Erzpfeil | H:Geschoss | Metall |
| 79 | Eulenruf | N:Tierruf | Eule |
| 80 | Exposami | N:Explosion | Druckwelle |
| 81 | Falkenauge | H:Fernsicht | |
| 82 | Favilludo | N:Funkenregen | Funken-Schaden |
| 83 | Federleib | H:Geschwindigkeit | Leichtigkeit, Sturz |
| 84 | Feenstaub | H:Verwirrung | Wahrnehmung stören |
| 85 | Fesselfeld | H:Barriere | Käfig |
| 86 | Feuerpfeil | H:Geschoss | Feuer |
| 87 | Firnlauf | H:Geschwindigkeit | Schnee/Eis |
| 88 | Fischflosse | N:Flossen | Unterwasser |
| 89 | Flammenwand | H:Barriere | Feuer |
| 90 | Fledermausruf | N:Tierruf | Fledermaus |
| 91 | Flim Flam | N:Feuerwerk | Schaden + Licht |
| 92 | Foramen | H:Gegenstand beschwören | Schloss öffnen |
| 93 | Fortifex | B:Schutz | Strukturen stärken |
| 94 | Frigifaxius | H:Geschoss | Kälte |
| 95 | Frigisphaero | H:Flächenschlag | Kälte |
| 96 | Frostleib | B:Schutz | Kälte-Panzerung |
| 97 | Fulminictus | H:Geschoss | Blitzschlag |
| 98 | Gardianum | H:Arkaner Schutz | Schutz vor Bösem |
| 99 | Gedankenbilder | H:Illusion | |
| 100 | Gefunden | H:Aufspüren | Gegenstand |
| 101 | Geisteressenz | H:Gegenstand beschwören | Geist rufen, kurz |
| 102 | Gifthaut | H:Schwächung | Gift aus Haut |
| 103 | Glutlauf | H:Geschwindigkeit | Feuer-Glut |
| 104 | Granit und Marmor | H:Barriere | Stein |
| 105 | Große Gier | H:Marionette | Gier auslösen |
| 106 | Große Verwirrung | H:Verwirrung | |
| 107 | Halluzination | H:Illusion | |
| 108 | Harmlose Gestalt | H:Tarnung | Böses tarnen |
| 109 | Haselbusch | N:Busch | Tarnung, Hecke |
| 110 | Heilungsbann | B:Heilung | göttliche Heilung |
| 111 | Hellsichtbann | H:Magie bannen | Magie brechen |
| 112 | Heptagramma | H:Barriere | Sieben-Punkt-Schutz |
| 113 | Herr über das Tierreich | H:Sprechen mit Tieren | Tiere kontrollieren |
| 114 | Herzschlag ruhe | H:Lähmung | langsam |
| 115 | Hexagramma | H:Barriere | Schutzkreis |
| 116 | Hexengalle | H:Schwächung | Fluch |
| 117 | Hexenholz | N:Holz | Magisches Holz |
| 118 | Hexenknoten | N:Hexenbande | Person binden |
| 119 | Hexenkrallen | B:Geschoss | Krallen, Nahkampf |
| 120 | Hexenspeichel | H:Heilung | Speziell, Heilung |
| 121 | Hilfreiche Pfote | N:Tierhilfe | Tier zu Hilfe |
| 122 | Hilfreiche Schwinge | N:Tierhilfe | Vogel zu Hilfe |
| 123 | Hilfreiche Tatze | N:Tierhilfe | Raubtier zu Hilfe |
| 124 | Himmelslauf | H:Fliegen | Himmel laufen |
| 125 | Höllenpein | H:Schwächung | Höllenqual |
| 126 | Hornissenruf | N:Tierruf | Hornissen |
| 127 | Horriphobus | H:Furcht | Schreckensvisionen |
| 128 | Humofaxius | H:Geschoss | Erde |
| 129 | Humosphaero | H:Flächenschlag | Erde |
| 130 | Humuspfeil | H:Geschoss | Erde-Pfeil |
| 131 | Ignifaxius | H:Geschoss | Feuer-Pfeil, Klassiker |
| 132 | Ignisphaero | H:Flächenschlag | Feuer-Sphäre |
| 133 | Ignorantia | H:Verwirrung | Dummheit |
| 134 | Illusionsbann | H:Magie bannen | |
| 135 | Imperavi | H:Marionette | Befehl |
| 136 | Impersona | H:Böswillige Verwandlung | Person imitieren |
| 137 | Incendio | N:Brand | Feuer, Rauch |
| 138 | Invercano | N:Hülle | Rüstung aufheben |
| 139 | Invinculo | H:Lähmung | Fessel |
| 140 | Invocatio Minima | H:Gegenstand beschwören | Dämon rufen, klein |
| 141 | Karnifilo | B:Geschoss | Schmerz-Klinge |
| 142 | Katzenaugen | H:Fernsicht | Nachtsicht |
| 143 | Katzenruf | N:Tierruf | Katze |
| 144 | Klarum Purum | H:Arkanes entdecken | Magie neutralisieren |
| 145 | Krabbelnder Schrecken | H:Furcht | Insekten |
| 146 | Kraft des Humus | H:Schutz | Erde-Kraft |
| 147 | Kraft des Tieres | H:Eigenschaft erhöhen | Tierstärke |
| 148 | Krähenruf | N:Tierruf | Krähe |
| 149 | Krötenruf | N:Tierruf | Kröte |
| 150 | Krötensprung | H:Geschwindigkeit | Hüpfen |
| 151 | Kulminatio | H:Stärke | Kraft-Verstärkung |
| 152 | Kusch | H:Lähmung | Schlaf |
| 153 | Last des Alters | H:Schwächung | Alter |
| 154 | Levthans Feuer | B:Flächenschlag | Meer-Feuer |
| 155 | Luftpfeil | H:Geschoss | Luft |
| 156 | Lunge des Leviatan | H:Schutz | Unterwasser-Atmung |
| 157 | Mal der Erschöpfung | H:Schwächung | |
| 158 | Mal der Schwäche | H:Schwächung | |
| 159 | Manifesto | H:Gegenstand beschwören | Objekt erscheint |
| 160 | Manus Illusionis | H:Illusion | Trugbild-Hand |
| 161 | Manus Miracula | H:Heilung | Wunderheilung |
| 162 | Memorans | H:Gedankenlesen | Gedächtnis lesen |
| 163 | Menetekel | H:Furcht | Schrift an Wand |
| 164 | Minimus Reductibus | B:Schwächung | Schrumpfen |
| 165 | Motoricus | H:Böswillige Verwandlung | Tier-Motorik |
| 166 | Nebelform | H:Tarnung | Nebel-Gestalt |
| 167 | Nebelwand | H:Barriere | Nebel |
| 168 | Nuntiovolo | N:Botenruf | Bote, fliegend |
| 169 | Objectobscuro | H:Illusion | Objekt verbergen |
| 170 | Objectofixo | H:Lähmung | Objekt fixieren |
| 171 | Objectovoco | H:Gegenstand beschwören | Objekt rufen |
| 172 | Objektbann | H:Magie bannen | |
| 173 | Oculus Astralis | H:Fernsicht | Astrale Sicht |
| 174 | Oculus Illusionis | H:Illusion | Trugbild-Augen |
| 175 | Odem Arcanum | H:Fluch | magischer Atem |
| 176 | Oktagramma | H:Barriere | Schutzkreis |
| 177 | Orcanofaxius | H:Geschoss | Wasser/Orkan |
| 178 | Orcanosphaero | H:Flächenschlag | Wasser/Orkan |
| 179 | Pandaemonium | H:Verwirrung | Chaos, Höllenlärm |
| 180 | Panik überkomme euch | H:Furcht | |
| 181 | Papageienruf | N:Tierruf | Papagei |
| 182 | Paralysis | H:Lähmung | |
| 183 | Penetrizzel | H:Geschoss | durchdringend |
| 184 | Pentagramma | H:Barriere | Schutzkreis |
| 185 | Pestilenz erspüren | H:Aufspüren | Krankheit |
| 186 | Pestodem | H:Fluch | Pest-Hauch |
| 187 | Physiostabilis | H:Heilung | Körper stabilisieren |
| 188 | Plumbumbarum | B:Geschoss | Blei, schwer |
| 189 | Projectimago | H:Illusion | Bild projizieren |
| 190 | Protectionis | H:Schutz | |
| 191 | Psychostabilis | H:Heilung | Geist stabilisieren |
| 192 | Radau | N:Lärm | Lärm, Schaden |
| 193 | Reflectimago | H:Illusion | Spiegelbild |
| 194 | Regeneratio | H:Heilung | Regeneration |
| 195 | Reptilea | H:Böswillige Verwandlung | Reptil |
| 196 | Respondami | H:Arkanes entdecken | Antwort |
| 197 | Salander | H:Heilung | Balsam speziell |
| 198 | Sanfter Fall | H:Geschwindigkeit | Sturz |
| 199 | Sanftmut | H:Empathie | Emotion beruhigen |
| 200 | Sapefacta | H:Böswillige Verwandlung | Sapay-Affe |
| 201 | Satuarias Herrlichkeit | H:Heilung | spezielle Heilung |
| 202 | Schimmernder Schild | H:Schutz | |
| 203 | Schlangenruf | N:Tierruf | Schlange |
| 204 | Schlechte Ausstrahlung | H:Fluch | Charisma senken |
| 205 | Schleier der Unwissenheit | H:Gedankenleere | Gedächtnis blockieren |
| 206 | Schmerzen lindern | H:Heilung | |
| 207 | Schuppenhaut | B:Schutz | Schuppen-Panzerung |
| 208 | Schwarz und Rot | H:Verwirrung | Farbblitz |
| 209 | Schwarzer Schrecken | H:Furcht | Todesfurcht |
| 210 | Seelentier erkennen | H:Aufspüren | Seelentier |
| 211 | Seidenzunge | H:Empathie | Charisma-Sprache |
| 212 | Sensattacco | H:Eigenschaft erhöhen | Sinne schärfen |
| 213 | Sensibar | H:Fernsicht | Weitsicht |
| 214 | Serpentialis | H:Böswillige Verwandlung | Schlange |
| 215 | Silentium | H:Geräusch/Stille | |
| 216 | Sinesigil | N:Schutzkreis | Schutz, Siegel |
| 217 | Skelettarius | H:Gegenstand beschwören | Skelett rufen |
| 218 | Solidirid | H:Arkaner Schutz | Solidität |
| 219 | Somnigravis | H:Lähmung | Schlaf |
| 220 | Sphärenbann | H:Magie bannen | Sphären-Magie |
| 221 | Spinnenlauf | H:Geschwindigkeit | Spinnenklettern |
| 222 | Spinnenruf | N:Tierruf | Spinne |
| 223 | Spurlos | H:Spurlos | |
| 224 | Standfest | B:Schutz | Stabilität |
| 225 | Steinwand | H:Barriere | Stein |
| 226 | Stillstand | H:Lähmung | kurze Erstarrung |
| 227 | Sturm der Verunsicherung | H:Verwirrung | |
| 228 | Sturmwand | H:Barriere | Sturm/Wind |
| 229 | Sumpfstrudel | H:Geschwindigkeit | Sumpf, langsam |
| 230 | Sumus Elixiere | H:Heilung | Elixier |
| 231 | Taubheit | H:Verwirrung | Taub |
| 232 | Telekinesebann | H:Magie bannen | |
| 233 | Temporalbann | H:Magie bannen | Zeit-Magie |
| 234 | Tempus Stasis | H:Lähmung | Zeit einfrieren |
| 235 | Tiere besprechen | H:Sprechen mit Tieren | |
| 236 | Tiergedanken | H:Sprechen mit Tieren | |
| 237 | Transversalis | H:Ebenenwechsel | Ortsreise |
| 238 | Unentflammbarkeit | H:Schutz | Feuer-Immunität |
| 239 | Ungeschickt | H:Schwächung | GE senken |
| 240 | Verunsicherung | H:Verwirrung | |
| 241 | Verwandlungsbann | H:Magie bannen | |
| 242 | Vipernblick | H:Blenden | Viper |
| 243 | Visibili | H:Arkanes entdecken | Sichtbarmachen |
| 244 | Vogelzwitschern | N:Tierruf | Vogel |
| 245 | Warmes gefriere | H:Lähmung | Kälte |
| 246 | Wasseratem | H:Schutz | Unterwasser-Atmung |
| 247 | Wasserpfeil | H:Geschoss | Wasser |
| 248 | Welle der Reinigung | H:Heilung | Krankheit, Gift |
| 249 | Welle des Schmerzes | H:Schwächung | Schmerz |
| 250 | Wellenlauf | H:Geschwindigkeit | Wasser bewegen |
| 251 | Wellenwand | H:Barriere | Wasser |
| 252 | Windhose | H:Wetterkontrolle | |
| 253 | Windstille | H:Wetterkontrolle | Wind stillen |
| 254 | Wipfellauf | H:Geschwindigkeit | Baumkronen |
| 255 | Woge der Versteinerung | H:Lähmung | Versteinerung |
| 256 | Wolfstatze | N:Wolfsform | Tierform Wolf |
| 257 | Wüstenlauf | H:Geschwindigkeit | Wüste |
| 258 | Zauberpferd herbeirufen | H:Gegenstand beschwören | Pferd |
| 259 | Zitterfinger | H:Schwächung | Zittern |
| 260 | Zorn der Elemente | H:Wetterkontrolle | Elemente-Wut |
| 261 | Zunge betäuben | H:Zunge lähmen | |
| 262 | Zweifel schüren | H:Verwirrung | |
| 263 | Zwingtanz | B:Marionette | Tanz, Willen unterwerfen |

#### 4.5.2 Rituale (74) → SW-Macht

| # | DSA-Ritual | → SW-Macht | Bemerkung |
|--:|------------|:----------:|-----------|
| 1 | Accuratum | H:Schutz | Ziel-Magie |
| 2 | Adamantium | B:Schutz | Härte, Adamantium |
| 3 | Animatio | H:Gegenstand beschwören | Belebung |
| 4 | Applicatus | N:Zauber verstärken | Zauber auf Objekt |
| 5 | Arcanovi | H:Arkanes entdecken | |
| 6 | Aurum Argentor | H:Gegenstand beschwören | Gold |
| 7 | Band der Freundschaft | N:Freundschaft | Empathie |
| 8 | Bärenruhe | N:Bärenkraft | Stärke |
| 9 | Blick durch fremde Augen | H:Fernsicht | |
| 10 | Blick in die Vergangenheit | H:Aufspüren | Vergangenheit |
| 11 | Brandform | H:Böswillige Verwandlung | Feuergestalt |
| 12 | Caldofrigo | B:Schutz | heiß+kalt zugleich |
| 13 | Chimaeroform | H:Böswillige Verwandlung | Chimäre |
| 14 | Chronoklassis | H:Lähmung | Zeit klassifizieren |
| 15 | Chrononautos | H:Ebenenwechsel | Zeitreise |
| 16 | Custodosigil | H:Schutz | Wächtersiegel |
| 17 | Dämonenpakt beenden | H:Aufheben | Pakt brechen |
| 18 | Destructibo | H:Verwirrung | Zerstörung |
| 19 | Dschinnenruf | H:Gegenstand beschwören | Dschinn |
| 20 | Eins mit der Natur | H:Empathie | Naturverbunden |
| 21 | Elementarer Diener | H:Gegenstand beschwören | Elementar |
| 22 | Ergebenheit der Wogen | H:Marionette | Wogen, Willen |
| 23 | Erhabenheit des Marmors | B:Schutz | Marmor-Härte |
| 24 | Felsenform | H:Böswillige Verwandlung | Stein |
| 25 | Freiheit der Wolken | H:Geschwindigkeit | Wolke, fliegen |
| 26 | Gefäß der Jahre | H:Heilung | Verjüngung |
| 27 | Geisterbeschwörung | H:Gegenstand beschwören | Geist rufen |
| 28 | Geisterruf | N:Geisterruf | Schamanen |
| 29 | Gletscherform | H:Böswillige Verwandlung | Gletscher |
| 30 | Hagelschlag und Sturmgebrüll | H:Flächenschlag | Hagel, Sturm |
| 31 | Hartes schmelze | B:Verwirrung | Material verändern |
| 32 | Immortalis Lebenszeit | H:Heilung | langes Leben |
| 33 | Infinitum Immerdar | H:Heilung | ewiges Leben |
| 34 | Invocatio Maior | H:Gegenstand beschwören | Dämon, mittel |
| 35 | Invocatio Maxima | H:Gegenstand beschwören | Dämon, groß |
| 36 | Invocatio Minor | H:Gegenstand beschwören | Dämon, klein |
| 37 | Klarheit des Eises | B:Verwirrung | Klarheit, Wahrnehmung |
| 38 | Körperlose Reise | H:Ebenenwechsel | Astralreise |
| 39 | Lawinenfall und Trümmerfeld | H:Flächenschlag | Lawine |
| 40 | Leidensbund | N:Leidensbund | Schmerzen teilen |
| 41 | Madas Spiegel | H:Illusion | Spiegel, Trugbild |
| 42 | Magischer Raub | H:Spionage | Magie stehlen |
| 43 | Meister der Elemente | N:Elementar-Meister | Elemente stärken |
| 44 | Memorabia Falsifir | H:Gedankenleere | Gedächtnis löschen |
| 45 | Movimento | H:Geschwindigkeit | Mobilität |
| 46 | Nekropathia | H:Gegenstand beschwören | Untote kontaktieren |
| 47 | Nihilogravo | H:Schwächung | Schwerelosigkeit |
| 48 | Pflanzenform | H:Böswillige Verwandlung | Pflanze |
| 49 | Planastrale | H:Ebenenwechsel | Astralebene |
| 50 | Reinheit der Lohe | N:Reinigung | Feuer-Reinigung |
| 51 | Riesengestalt | H:Eigenschaft erhöhen | Riesenstärke |
| 52 | Ruf der Feenwesen | H:Gegenstand beschwören | Feen |
| 53 | Ruhe Körper | H:Lähmung | Körper stillen |
| 54 | Seelenwanderung | H:Ebenenwechsel | Seele wandert |
| 55 | Standhafter Wächter | H:Gegenstand beschwören | Wächter rufen |
| 56 | Staub wandle | H:Böswillige Verwandlung | Staub |
| 57 | Stein wandle | H:Böswillige Verwandlung | Stein |
| 58 | Totes handle | H:Gegenstand beschwören | Tote kontaktieren |
| 59 | Transformatio | H:Böswillige Verwandlung | Transformation |
| 60 | Transmutare | H:Böswillige Verwandlung | Umwandlung |
| 61 | Traumgestalt | H:Böswillige Verwandlung | Traumform |
| 62 | Überlegener Krieger | H:Stärke | Krieger stärken |
| 63 | Unberührt von Satinav | H:Schutz | Satinav abwehren |
| 64 | Weiches erstarre | B:Lähmung | weich zu hart |
| 65 | Weisheit der Bäume | H:Empathie | Baum-Weisheit |
| 66 | Widerwille | H:Schutz | Widerstand |
| 67 | Wirbelform | H:Böswillige Verwandlung | Wirbel |
| 68 | Wogenform | H:Böswillige Verwandlung | Woge |
| 69 | Xenographus | H:Arkanes entdecken | Fremde Schrift |
| 70 | Zauberklinge Geisterspeer | H:Geschoss | Geist-Klinge |
| 71 | Zaubernahrung | H:Heilung | Nahrung herstellen |
| 72 | Zauberschnurren | N:Schnurren | Katzen-Magie |
| 73 | Zauberwesen der Natur | H:Gegenstand beschwören | Naturwesen |
| 74 | Zauberzwang | H:Marionette | Willen zwingen |

#### 4.5.3 Liturgien (199) → SW-Macht

| # | DSA-Liturgie | → SW-Macht | Bemerkung |
|--:|--------------|:----------:|-----------|
| 1 | Angriffslust | H:Stärke | Angriffslust |
| 2 | Angriffswelle | H:Flächenschlag | Welle von Angriffen |
| 3 | Auge des Jägers | H:Fernsicht | |
| 4 | Ausnüchtern | H:Heilung | klarer Kopf |
| 5 | Bann der Dunkelheit | H:Licht | |
| 6 | Bann der Furcht | N:Mutbann | Furcht bannen |
| 7 | Bann der göttlichen Gaben | H:Magie bannen | |
| 8 | Bann des Lichts | H:Dunkelsicht | |
| 9 | Bann wider Untote | H:Schutz | Untote fern |
| 10 | Bannstrahl | H:Geschoss | Heiliger Strahl |
| 11 | Bannzone | H:Barriere | Heilige Zone |
| 12 | Bärenhaut | B:Schutz | Bären-Panzer |
| 13 | Befehl des Schamanen | H:Marionette | |
| 14 | Befreiung des Geistes | H:Heilung | Geist befreien |
| 15 | Begnadeter Reiter | N:Reiter-Segen | Reiten |
| 16 | Berauschen | H:Verwirrung | |
| 17 | Besänftigung | H:Empathie | Emotion |
| 18 | Bescheidenheit | H:Empathie | Demut |
| 19 | Beschwörung der gemeinen Diener des Rattenkindes | H:Gegenstand beschwören | Ratten |
| 20 | Blendstrahl | H:Blenden | Heilig |
| 21 | Blendung | H:Blenden | |
| 22 | Blick auf den Meeresgrund | H:Fernsicht | |
| 23 | Blick des Heilers | H:Heilung | |
| 24 | Blitzschlag | H:Geschoss | göttlich |
| 25 | Blutiger Zorn | H:Stärke | Berserker |
| 26 | Blutiges Siegel | N:Blut-Siegel | Verfolgung blockieren |
| 27 | Blutzoll | H:Fluch | Blut-Schwächung |
| 28 | Bodenweihe | N:Heiliger Boden | Boden weihen |
| 29 | Botschaft aus der Tiefe | H:Telepathie | |
| 30 | Brazoraghs Krieger | H:Gegenstand beschwören | Krieger |
| 31 | Büchersuche | H:Aufspüren | Buch finden |
| 32 | Dämonenwall | H:Barriere | Dämonen abwehren |
| 33 | Delphinruf | N:Tierruf | Delphin |
| 34 | Des Einen bezaubernder Sphärenklang | H:Empathie | göttlich |
| 35 | Doppelgänger | H:Böswillige Verwandlung | Ebenbild |
| 36 | Ehrenhaftigkeit | H:Empathie | Ehre |
| 37 | Ehrlicher Vertrag | N:Vertragszauber | bindet |
| 38 | Eisbärenruf | N:Tierruf | Eisbär |
| 39 | Entfesselung | H:Befreiung | Fesseln lösen |
| 40 | Entstelltes Antlitz | H:Böswillige Verwandlung | Entstellung |
| 41 | Entzifferung | H:Arkanes entdecken | |
| 42 | Erdbeben | H:Flächenschlag | |
| 43 | Ermutigung | H:Empathie | Mut |
| 44 | Ernüchterung | H:Heilung | Nüchtern |
| 45 | Erregender Rausch | H:Verwirrung | Charisma |
| 46 | Ertrinken | H:Schwächung | Wasser |
| 47 | Erwachen | H:Heilung | erwecken |
| 48 | Erzene Opfergabe | H:Gegenstand beschwören | Erz-Opfer |
| 49 | Fall ins Nichts | H:Lähmung | Sturz |
| 50 | Fesselndes Band | H:Lähmung | Band |
| 51 | Feuerwall | H:Barriere | Feuer |
| 52 | Flugechsenruf | N:Tierruf | Flugechse |
| 53 | Freundschaftliches Auftreten | H:Empathie | freundlich |
| 54 | Friedfertigkeit | H:Empathie | Frieden |
| 55 | Friedvolle Aura | H:Schutz | Aura |
| 56 | Friedvoller Rausch | H:Empathie | Frieden |
| 57 | Froststurm | H:Flächenschlag | Frost |
| 58 | Furchteinflößende Tiergeister | H:Furcht | Tier-Furcht |
| 59 | Furchtresistenz | H:Schutz | Furcht-Widerstand |
| 60 | Gebieter der Flammen | N:Feuergebiet | Flammen befehligen |
| 61 | Gefühlskälte | H:Empathie | Kühlen |
| 62 | Geist des Strategen | N:Strategie | Taktik |
| 63 | Geisterblick | H:Arkanes entdecken | |
| 64 | Geisterfalle | H:Falle | Geist fangen |
| 65 | Geldwechsel | N:Geldzauber | Geld vermehren |
| 66 | Gesegneter Rausch | H:Empathie | gesegnet |
| 67 | Gespür für das Göttliche | H:Fernsicht | göttlich spüren |
| 68 | Getreidewachstum | H:Pflanzenzauber | Wachstum |
| 69 | Giftbann | H:Heilung | Gift bannen |
| 70 | Gnadenstoß | H:Stärke | Mitleid |
| 71 | Goldene Hand | H:Heilung | Hand-Aura |
| 72 | Goldene Rüstung | H:Schutz | |
| 73 | Göttliche Klinge | H:Geschoss | göttlich |
| 74 | Göttliche Verständigung | H:Telepathie | |
| 75 | Göttlicher Fingerzeig | H:Fernsicht | Hinweis |
| 76 | Göttlicher Rausch | H:Stärke | göttlich |
| 77 | Göttliches Zeichen | N:Göttliches Zeichen | Omen |
| 78 | Hairuf | H:Gegenstand beschwören | Achaz-Geist |
| 79 | Hauch des Elements | H:Geschoss | Element-Hauch |
| 80 | Heiliger Befehl | H:Marionette | |
| 81 | Heiliges Liebesspiel | H:Empathie | Liebe, Heilung |
| 82 | Heilsame Quelle | H:Heilung | Quelle |
| 83 | Heilsegen | H:Heilung | |
| 84 | Heldenkraft | H:Stärke | |
| 85 | Helfende Hand | H:Heilung | Hilfe |
| 86 | Herbeirufung der Heerscharen des Rattenkindes (Ratten) | H:Gegenstand beschwören | Ratten |
| 87 | Herbeirufung der Heerscharen des Rattenkindes (Schakale) | H:Gegenstand beschwören | Schakale |
| 88 | Herbeirufung der Heerscharen des Rattenkindes (Vampirfledermäuse) | H:Gegenstand beschwören | Fledermäuse |
| 89 | Herbeirufung der Heerscharen des Rattenkindes (Wolfsspinnen) | H:Gegenstand beschwören | Spinnen |
| 90 | Herbeirufung von Tairachs Dienern (Nebelkrähen) | H:Gegenstand beschwören | Krähen |
| 91 | Herr der Flammen | N:Feuerherr | Flammen |
| 92 | Hilfreiche Seele | H:Empathie | Hilfe |
| 93 | Innere Ruhe | H:Empathie | Ruhe |
| 94 | Jaguarruf | N:Tierruf | Jaguar |
| 95 | Kälteexplosion | H:Flächenschlag | Kälte |
| 96 | Kampfgeschick | H:Eigenschaft erhöhen | Kampf, GE |
| 97 | Klarer Geist | H:Heilung | Klarheit |
| 98 | Kleidungschamäleon | H:Tarnung | Kleidung tarnen |
| 99 | Kleine Windhose | H:Wetterkontrolle | |
| 100 | Kleiner Bann wider Untote | H:Schutz | Untote |
| 101 | Kleiner Bannstrahl | H:Geschoss | heilig, klein |
| 102 | Kraftvoller Körper | H:Stärke | |
| 103 | Krankheiten vorbeugen | H:Heilung | Krankheit |
| 104 | Krankheitsbann | H:Heilung | |
| 105 | Kriegsfarben | H:Stärke | Kriegs-Ermutigung |
| 106 | Lautlos | H:Geräusch/Stille | |
| 107 | Lebensschutz | H:Schutz | Leben |
| 108 | Levthanischer Liebhaber | H:Empathie | Efferd-Liebe |
| 109 | Liturgieschild | N:Liturgieschild | Kleriker |
| 110 | Lust erzeugen | H:Empathie | Lust |
| 111 | Macht des Levthan | H:Wetterkontrolle | Wasser |
| 112 | Mächtiger Angriff | H:Stärke | Angriff |
| 113 | Magieanalyse | H:Arkanes entdecken | |
| 114 | Magiebann | H:Magie bannen | |
| 115 | Magieschutz | H:Schutz | |
| 116 | Magiesicht | H:Fernsicht | Magie sehen |
| 117 | Magiespiegel | H:Schutz | Magie reflektieren |
| 118 | Mammutruf | N:Tierruf | Mammut |
| 119 | Maske | H:Böswillige Verwandlung | Maske |
| 120 | Mauereinsturz | H:Flächenschlag | Mauer |
| 121 | Meeresungeheuer vertreiben | H:Furcht | Ungeheuer |
| 122 | Mit Dummheit schlagen | H:Verwirrung | Dumm |
| 123 | Mondsicht | H:Fernsicht | Nachtsicht |
| 124 | Mondsilberzunge | H:Empathie | Sprache |
| 125 | Motivation | H:Empathie | Motivation |
| 126 | Namenlose Kälte | H:Schwächung | Kälte, Namenlos |
| 127 | Namenlose Raserei | H:Stärke | Raserei |
| 128 | Namenlose Zweifel | H:Verwirrung | Zweifel |
| 129 | Namenloses Vergessen | H:Gedankenleere | |
| 130 | Nebelkrähenschwarm | H:Gegenstand beschwören | Krähen |
| 131 | Numinorus Fesseln | H:Lähmung | Fessel |
| 132 | Obarans Blendung | H:Blenden | Praios |
| 133 | Objektsegen | H:Schutz | Objekt |
| 134 | Obsession | H:Marionette | |
| 135 | Offenlegung des Geistes | H:Gedankenlesen | |
| 136 | Ogerruf | N:Tierruf | Oger |
| 137 | Opfergang | H:Schutz | Opfer |
| 138 | Ort der Ruhe | H:Schutz | Heiliger Ort |
| 139 | Pech und Schwefel | H:Schwächung | Pech, Schwefel |
| 140 | Peraines Gnade | H:Heilung | Peraine |
| 141 | Pflanzenwuchs | H:Pflanzenzauber | Wachstum |
| 142 | Quallenhaut | H:Schutz | Quallen |
| 143 | Quallenruf | N:Tierruf | Qualle |
| 144 | Rabenruf | N:Tierruf | Rabe |
| 145 | Rattenschwarm | H:Gegenstand beschwören | Ratten |
| 146 | Regenbogenbrücke | H:Ebenenwechsel | Regenbogen |
| 147 | Reinigung des Bösen | H:Heilung | Böses reinigen |
| 148 | Rinderruf | N:Tierruf | Rind |
| 149 | Ruf der Heimat | H:Empathie | Heimat |
| 150 | Schattenfessel | H:Lähmung | Schatten |
| 151 | Schiffsgespür | H:Fernsicht | Schiff |
| 152 | Schlaf | H:Lähmung | |
| 153 | Schlangenruf | N:Tierruf | Schlange |
| 154 | Schlangenstab | H:Gegenstand beschwören | Schlangenstab |
| 155 | Schlangenzunge | H:Empathie | Sprache, Schlau |
| 156 | Schleichende Fäulnis | H:Fluch | Fäulnis |
| 157 | Schleichende Fäulnis (Pflanzen) | H:Fluch | Pflanzenfäule |
| 158 | Schlingerruf | N:Tierruf | Schlinger |
| 159 | Schmerzresistenz | H:Schutz | Schmerz |
| 160 | Schonfrist | H:Heilung | Wunde, Zeit |
| 161 | Schutz der Hornissenkönigin | H:Schutz | |
| 162 | Schutz der Wehrlosen | H:Schutz | |
| 163 | Schutzsegen | H:Schutz | |
| 164 | Schwindende Zauberkraft | H:Schwächung | Zauberkraft |
| 165 | Seelenschatten | H:Illusion | Seelen-Schatten |
| 166 | Seevogelsprache | H:Sprechen mit Tieren | Vogel |
| 167 | Sicherer Weg | H:Schutz | Weg |
| 168 | Sicht in der Dunkelheit | H:Fernsicht | Nachtsicht |
| 169 | Speer des Athleten | H:Geschoss | Athlet, göttlich |
| 170 | Sprache des Tapams | H:Sprechen mit Tieren | Tapam |
| 171 | Steinhaut | H:Schutz | Stein |
| 172 | Sternenglanz | H:Licht | Sterne |
| 173 | Sturmruf | H:Wetterkontrolle | Sturm |
| 174 | Talismanruf | H:Gegenstand beschwören | Talisman |
| 175 | Tierbeherrschung | H:Sprechen mit Tieren | |
| 176 | Tiere beruhigen | H:Empathie | Tiere |
| 177 | Tierleid lindern | H:Heilung | Tiere |
| 178 | Tiersprache | H:Sprechen mit Tieren | |
| 179 | Trankfluch | H:Fluch | Trank |
| 180 | Treuer Begleiter | H:Empathie | Begleiter |
| 181 | Tsas Gedankenspiel | H:Gedankenlesen | Tsa |
| 182 | Unsichtbare Flut | H:Tarnung | Wasser |
| 183 | Unterwasseratmung | H:Schutz | Atmung |
| 184 | Untotenerhebung | H:Gegenstand beschwören | Untote |
| 185 | Vampirische Kräfte | H:Schwächung | Blut |
| 186 | Verstecktes Begehren | H:Empathie | Begehren |
| 187 | Versteinerung | H:Lähmung | Versteinerung |
| 188 | Wahrheit | H:Empathie | Wahrheit |
| 189 | Wand wider Dämonen | H:Barriere | Dämonen |
| 190 | Wasserlauf | H:Geschwindigkeit | Wasser |
| 191 | Weihe des Bodens | N:Heiliger Boden | |
| 192 | Wieselflink | H:Geschwindigkeit | |
| 193 | Windhose | H:Wetterkontrolle | |
| 194 | Windruf | H:Wetterkontrolle | Wind |
| 195 | Wolfsruf | N:Tierruf | Wolf |
| 196 | Wundersame Verständigung | H:Telepathie | wundersam |
| 197 | Zähe Haut | H:Schutz | zäh |
| 198 | Zauberschutz | H:Schutz | |
| 199 | Zwergenmacht | H:Stärke | Zwerg |

#### 4.5.4 Zeremonien (138) → SW-Macht

| # | DSA-Zeremonie | → SW-Macht | Bemerkung |
|--:|---------------|:----------:|-----------|
| 1 | Ächtung (Exkommunikation) | H:Marionette | Ausschluss |
| 2 | Ackersegen | H:Heilung | Wachstum |
| 3 | Arcanum Interdictum | H:Magie bannen | Interdikt |
| 4 | Aufnahme (Initiation) | H:Empathie | Aufnahme |
| 5 | Ausbrennen (Purgation) | H:Heilung | Böses ausbrennen |
| 6 | Bannfluch (Anathema) | H:Fluch | |
| 7 | Berauschender Wein | H:Empathie | Wein, Rausch |
| 8 | Beschwörung der hohen Diener des Rattenkindes | H:Gegenstand beschwören | hoch |
| 9 | Beschwörung der machtvollen Diener des Rattenkindes | H:Gegenstand beschwören | mächtig |
| 10 | Bild für die Ewigkeit | H:Illusion | Bild, Ewigkeit |
| 11 | Blick in die Flammen | H:Fernsicht | Flammen |
| 12 | Dämonenpakt brechen | H:Aufheben | |
| 13 | Das Löschen des Lichts | H:Dunkelsicht | Licht löschen |
| 14 | Delphingestalt | H:Böswillige Verwandlung | Delphin |
| 15 | Diener der Erde | H:Gegenstand beschwören | Erde |
| 16 | Diener der Flammen | H:Gegenstand beschwören | Feuer |
| 17 | Diener der Kälte | H:Gegenstand beschwören | Kälte |
| 18 | Diener der Wellen | H:Gegenstand beschwören | Wasser |
| 19 | Diener der Wolken | H:Gegenstand beschwören | Luft |
| 20 | Diener des Erzes | H:Gegenstand beschwören | Erz |
| 21 | Eidechsengestalt | H:Böswillige Verwandlung | Eidechse |
| 22 | Eidechsenregeneration | H:Heilung | Regeneration |
| 23 | Einflüsterung | H:Empathie | Einflüstern |
| 24 | Eingeschworene Mannschaft | H:Empathie | Mannschaft |
| 25 | Einhorngestalt (Mächtige Tiergestalt) | H:Böswillige Verwandlung | Einhorn |
| 26 | Eisbärengestalt | H:Böswillige Verwandlung | Eisbär |
| 27 | Elsterngestalt | H:Böswillige Verwandlung | Elster |
| 28 | Empfängnis des Korsmals | H:Empathie | Korsmal |
| 29 | Erfolgreiche Pflanzensuche | H:Aufspüren | Pflanze |
| 30 | Erinnern | H:Gedankenleere | umgekehrt |
| 31 | Erschaffung von Nachtkindern | H:Gegenstand beschwören | Nachtkinder |
| 32 | Exorzismus | H:Aufheben | Exorzismus |
| 33 | Falkengestalt | H:Böswillige Verwandlung | Falke |
| 34 | Fest der Freude | H:Empathie | Freude |
| 35 | Flugechsengestalt | H:Böswillige Verwandlung | Flugechse |
| 36 | Freie Seelenfahrt | H:Ebenenwechsel | Seele |
| 37 | Frostschutz | H:Schutz | Frost |
| 38 | Fruchtbarkeit | H:Heilung | Fruchtbarkeit |
| 39 | Fuchsgestalt | H:Böswillige Verwandlung | Fuchs |
| 40 | Gänsegestalt | H:Böswillige Verwandlung | Gans |
| 41 | Geiergestalt | H:Böswillige Verwandlung | Geier |
| 42 | Geistersprache | H:Telepathie | Geist |
| 43 | Geistheilung | H:Heilung | |
| 44 | Geschlechterwechsel | H:Böswillige Verwandlung | Geschlecht |
| 45 | Geschwinder Schritt | H:Geschwindigkeit | |
| 46 | Gespräch mit den Toten | H:Gegenstand beschwören | Tote |
| 47 | Geweihter Panzer | H:Schutz | Panzer, geweiht |
| 48 | Gnade des Vergessens | H:Gedankenleere | Vergessen, Gnade |
| 49 | Göttliche Erkenntnis | H:Arkanes entdecken | göttlich |
| 50 | Göttliche Präzision | H:Geschoss | präzise, göttlich |
| 51 | Greifenruf | N:Tierruf | Greif |
| 52 | Große Waffenweihe | H:Schutz | Waffe, geweiht |
| 53 | Guter Fang | H:Geschicklichkeit | Fang |
| 54 | Häutung | H:Heilung | Häutung, Schlange |
| 55 | Heiliger Schwur | H:Empathie | Schwur |
| 56 | Heilschlaf | H:Heilung | Schlaf, Heilung |
| 57 | Heilung von Seelenkranken | H:Heilung | Seele |
| 58 | Herr der Meere | H:Wetterkontrolle | Meer |
| 59 | Hilfe in der Not | H:Heilung | Hilfe |
| 60 | Himmlische Schatzkammer | H:Gegenstand beschwören | Schatz |
| 61 | Hundegestalt | H:Böswillige Verwandlung | Hund |
| 62 | Inspiration | H:Empathie | Inspiration |
| 63 | Jagdglück | H:Glück | Jagd |
| 64 | Jaguargestalt | H:Böswillige Verwandlung | Jaguar |
| 65 | Jugendlichkeit | H:Heilung | Jugend |
| 66 | Kleine Moralstärkung | H:Empathie | Moral |
| 67 | Kriegszustand | H:Stärke | Krieg |
| 68 | Läuterung des Erzes | H:Heilung | Läuterung |
| 69 | Lebenstausch | H:Heilung | Leben, Tausch |
| 70 | Leichtfüssig | H:Geschwindigkeit | |
| 71 | Leitende Strömung | H:Fernsicht | Strömung |
| 72 | Liebestätowierung | H:Empathie | Liebe, Tattoo |
| 73 | Liturgieabsorption | H:Schutz | Liturgie absorbieren |
| 74 | Löwengestalt | H:Böswillige Verwandlung | Löwe |
| 75 | Luchsgestalt | H:Böswillige Verwandlung | Luchs |
| 76 | Machtvoller Exorzismus | H:Aufheben | Exorzismus, mächtig |
| 77 | Makelloser Leib | H:Heilung | Leib, makellos |
| 78 | Marbidenmacht | H:Schwächung | Marbide |
| 79 | Metallerhitzung | H:Geschoss | Metall, Hitze |
| 80 | Moralstärkung | H:Empathie | Moral |
| 81 | Mungogestalt | H:Böswillige Verwandlung | Mungo |
| 82 | Nahrungsreinigung | H:Heilung | Nahrung |
| 83 | Nebelleib | H:Tarnung | Nebel |
| 84 | Nebelschwaden | H:Tarnung | Nebel |
| 85 | Numinorus Fluch | H:Fluch | Numinoru |
| 86 | Objektweihe | H:Schutz | Objekt |
| 87 | Ogerbindung | H:Lähmung | Oger |
| 88 | Ortsweihe (Sanctum) | N:Heiliger Boden | Ort |
| 89 | Panthergestalt | H:Böswillige Verwandlung | Panther |
| 90 | Paradiesvogelgestalt | H:Böswillige Verwandlung | Paradiesvogel |
| 91 | Pferdegestalt | H:Böswillige Verwandlung | Pferd |
| 92 | Pflanzenkraft | H:Pflanzenzauber | Pflanze, Kraft |
| 93 | Priesterweihe (Ordination) | H:Heilung | Weihe, Priester |
| 94 | Rabengestalt | H:Böswillige Verwandlung | Rabe |
| 95 | Rat der Ahnen | H:Telepathie | Ahnen |
| 96 | Regenkontrolle | H:Wetterkontrolle | Regen |
| 97 | Reisesegen | H:Schutz | Reise |
| 98 | Sättigung | H:Heilung | Sättigung |
| 99 | Schaffenskraft | H:Stärke | Schaffen |
| 100 | Schattenrochengestalt | H:Böswillige Verwandlung | Schattenrochen |
| 101 | Schlangenfluch | H:Fluch | Schlange |
| 102 | Schlangengestalt | H:Böswillige Verwandlung | Schlange |
| 103 | Schmetterlingsgestalt | H:Böswillige Verwandlung | Schmetterling |
| 104 | Schwanengestalt | H:Böswillige Verwandlung | Schwan |
| 105 | Seelenbannung | H:Lähmung | Seele |
| 106 | Seelenprüfung | H:Arkanes entdecken | Seele |
| 107 | Seemonsterruf | N:Tierruf | Seemonster |
| 108 | Segnung des Heims | H:Schutz | Heim |
| 109 | Selbstopferung | H:Heilung | Opfer |
| 110 | Sicherer Tritt | H:Geschwindigkeit | Tritt |
| 111 | Sippenbann | H:Schutz | Sippe |
| 112 | Speisung | H:Heilung | Speisung |
| 113 | Stärkung der Wildnis | H:Pflanzenzauber | Wildnis |
| 114 | Staub und Schimmel | H:Schwächung | Staub, Schimmel |
| 115 | Storchengestalt | H:Böswillige Verwandlung | Storch |
| 116 | Tabu-Zone | H:Barriere | Tabu |
| 117 | Tairachs machtvolle Erhebung von Untoten | H:Gegenstand beschwören | Untote, mächtig |
| 118 | Talismanverankerung | H:Schutz | Talisman |
| 119 | Taubengestalt | H:Böswillige Verwandlung | Taube |
| 120 | Tempelweihe (Konsekration) | H:Schutz | Tempel |
| 121 | Traumbild | H:Illusion | Traum |
| 122 | Traumgesicht | H:Fernsicht | Traum |
| 123 | Travias Wachgänse | H:Gegenstand beschwören | Gänse |
| 124 | Unbeschwerte Wanderung | H:Geschwindigkeit | |
| 125 | Untote erschaffen | H:Gegenstand beschwören | Untote |
| 126 | Verblassende Erinnerung | H:Gedankenleere | Erinnerung verblassen |
| 127 | Vergessen | H:Gedankenleere | |
| 128 | Waffenfluch | H:Fluch | Waffe |
| 129 | Wegweiser | H:Fernsicht | Weg |
| 130 | Weihe des Heims | H:Schutz | Heim, Weihe |
| 131 | Widdergestalt | H:Böswillige Verwandlung | Widder |
| 132 | Wiederherstellung | H:Heilung | Wiederherstellung |
| 133 | Winterschlaf | H:Lähmung | Winterschlaf |
| 134 | Wolfsfluch | H:Fluch | Wolf |
| 135 | Wolfsgestalt | H:Böswillige Verwandlung | Wolf |
| 136 | Zuflucht | H:Schutz | Zuflucht |
| 137 | Zwergische Verbrüderung | H:Empathie | Brüderlichkeit |
| 138 | Zwergwalgestalt | H:Böswillige Verwandlung | Zwergwal |

#### 4.5.5 Segen (12) → SW-Macht

| # | DSA-Segen | → SW-Macht | Bemerkung |
|--:|-----------|:----------:|-----------|
| 1 | Eidsegen | H:Empathie | Eid |
| 2 | Feuersegen | H:Schutz | Feuer |
| 3 | Geburtssegen | H:Heilung | Geburt |
| 4 | Glückssegen | H:Glück | |
| 5 | Grabsegen | H:Heilung | Grab |
| 6 | Harmoniesegen | H:Empathie | Harmonie |
| 7 | Kleiner Heilsegen | H:Heilung | klein |
| 8 | Kleiner Schutzsegen | H:Schutz | klein |
| 9 | Speisesegen | H:Heilung | Speise |
| 10 | Stärkungssegen | H:Heilung | Stärkung |
| 11 | Tranksegen | H:Heilung | Trank |
| 12 | Weisheitssegen | H:Empathie | Weisheit |

#### 4.5.6 Zusammenfassung — SW-Macht → Anzahl DSA-Einträge

Diese Tabelle zeigt, welche SW-Mächte am häufigsten als DSA-Trapping dienen (für Implementierungs-Priorisierung):

| SW-Macht (existierend) | Anzahl DSA | Hauptquelle |
|------------------------|-----------:|-------------|
| `Heilung` | 51 | Zauber, Liturgien, Zeremonien, Segen |
| `Schutz` | 47 | Zauber, Liturgien, Zeremonien |
| `Böswillige Verwandlung` | 45 | Zauber, Zeremonien (Tiergestalten) |
| `Gegenstand beschwören` | 34 | Zauber, Liturgien, Zeremonien |
| `H:Geschoss` | 28 | Zauber (Elementarpfeile) |
| `Empathie` | 27 | Liturgien, Zeremonien, Segen |
| `Heiliger Boden` / `Heiliger Boden` (N) | 24 | Liturgien, Zeremonien |
| `Fernsicht` | 23 | Zauber, Liturgien |
| `Lähmung` | 22 | Zauber, Liturgien, Zeremonien |
| `Schwächung` | 19 | Zauber, Liturgien, Zeremonien |
| `Verwirrung` | 16 | Zauber, Liturgien |
| `Flächenschlag` | 15 | Zauber, Liturgien |
| `Barriere` | 14 | Zauber, Liturgien |
| `Geschwindigkeit` | 14 | Zauber, Rituale |
| `Heilig` (N) | 14 | Liturgien, Zeremonien |
| `Stärke` | 12 | Liturgien, Zeremonien |
| `Illusion` | 12 | Zauber |
| `Tierruf` (N) | 12 | Zauber, Liturgien, Zeremonien |
| `Magie bannen` | 11 | Zauber, Liturgien, Zeremonien |
| `Gedankenleere` | 9 | Zauber, Rituale, Zeremonien |
| `Arkanes entdecken/verbergen` | 9 | Zauber, Rituale, Liturgien |
| `Wetterkontrolle` | 8 | Zauber, Liturgien, Zeremonien |
| `Furcht` | 8 | Zauber, Liturgien |
| `Telepathie` | 7 | Liturgien, Zeremonien |
| `Marionette` | 7 | Zauber, Liturgien, Zeremonien |
| `Heilig` (N) | 7 | Liturgien, Zeremonien |
| `Eigenschaft erhöhen` | 6 | Zauber, Rituale |
| `Fluch` | 6 | Zauber, Liturgien, Zeremonien |
| `Tarnung` | 6 | Zauber, Liturgien |
| `Dunkelsicht` | 4 | Zauber, Liturgien, Zeremonien |
| `Aufheben` | 4 | Zauber, Rituale, Zeremonien |
| `Sprechen mit Tieren` | 5 | Zauber, Liturgien |
| `Blenden` | 5 | Zauber, Liturgien |
| `Gedankenlesen` | 4 | Zauber, Liturgien |
| `Aufspüren` | 4 | Zauber, Rituale, Liturgien |
| `Licht` | 2 | Liturgien |
| `Ebenenwechsel` | 6 | Zauber, Rituale, Liturgien |
| `Heilig` (N) | – | – |
| `Fliegen` | 3 | Zauber |
| `Pflanzenzauber` | 4 | Liturgien, Zeremonien |
| `Glück` | 2 | Zeremonien, Segen |
| `Heiliger Boden` (N) | 3 | Liturgien, Zeremonien |
| `Elementar-Meister` (N) | 1 | Ritual |
| `Geisterruf` (N) | 2 | Ritual, Liturgie |
| `Spionage` | 1 | Ritual |
| `Befreiung` | 1 | Liturgie |
| `Falle` | 1 | Liturgie |
| `Geschicklichkeit` | 1 | Zeremonie |

#### 4.5.7 Neue SW-Mächte (alle N: aus 4.5.1-4.5.5 zusammengefasst)

Diese Mächte müssen **neu im Setting** angelegt werden (Phase 6 der Konvertierung):

| Neue Macht | Beschreibung | Anzahl DSA-Trappings |
|------------|--------------|---------------------:|
| `Heiliger Boden` | Zone weihen, Schutz vor Bösem | 3 |
| `Liturgieschild` | göttlicher Schutz, Kleriker | 1 |
| `Geisterruf` | Geist rufen, Schamanen-spezifisch | 1 |
| `Elementar-Meister` | Elementar-Magie verstärken | 1 |
| `Schutzrüstung` | absorbiert Schaden, Schild-Zauber | 1 |
| `Gegengift` | entfernt Gift | 1 |
| `Schallverstärkung` | Donner, Laut | 1 |
| `Duftzauber` | Geruchs-Illusion | 1 |
| `Wasserreinigung` | Quellensuche, Wasser klären | 1 |
| `Spinnennetz` | Fesselfeld-Netz | 1 |
| `Regenruf` | Wetter, Regen | 1 |
| `Blitzruf` | Teleportation | 1 |
| `Verschlüsselung` | Geheimschrift | 1 |
| `Rost` | Waffen rosten | 1 |
| `Explosion` | Druckwelle | 1 |
| `Funkenregen` | Funken-Schaden | 1 |
| `Flossen` | Unterwasser-Anpassung | 1 |
| `Busch` | Tarnung, Hecke | 1 |
| `Tierhilfe` | Tier zu Hilfe rufen (Pfote/Schwinge/Tatze) | 3 |
| `Wolfsform` | Tierform Wolf | 1 |
| `Botenruf` | Bote, fliegend | 1 |
| `Doppelgänger` | Ebenbild erschaffen | 1 |
| `Finsternis` | Sonne/Mond verdecken | 1 |
| `Brand` | Feuer, Rauch | 1 |
| `Hülle` | Rüstung aufheben | 1 |
| `Zauber verstärken` | Applicatus | 1 |
| `Freundschaft` | Empathie, Band | 1 |
| `Bärenkraft` | Stärke | 1 |
| `Leidensbund` | Schmerzen teilen | 1 |
| `Reinigung` | Feuer-Reinigung | 1 |
| `Schnurren` | Katzen-Magie | 1 |
| `Mutbann` | Furcht bannen (göttlich) | 1 |
| `Reiter-Segen` | Reiten verbessern | 1 |
| `Blut-Siegel` | Verfolgung blockieren | 1 |
| `Vertragszauber` | bindet | 1 |
| `Strategie` | Taktik-Bonus | 1 |
| `Geldzauber` | Geld vermehren | 1 |
| `Feuergebiet` | Flammen befehligen | 1 |
| `Feuerherr` | Flammen-Meister | 1 |
| `Göttliches Zeichen` | Omen, Wunder | 1 |

> **Gesamt:** ~40 neue SW-Mächte müssen für die vollständige DSA-Abdeckung angelegt werden.

---

## 5. Magische Handlungen / Sonderformen

Quelle: https://dsa.ulisses-regelwiki.de/Z_MagHandlungen.html

In DSA gibt es 14 Sonderformen. Diese werden **nicht** als eigene Mächte umgesetzt, sondern als DSA-Trapping-Listen geführt:

| Sonderform | Umsetzung |
|------------|-----------|
| **Animistenkräfte** | Trapping für Schamanen-Mächte |
| **Bannzeichen** | Trapping für Kleriker (Vor Zauberern) |
| **Elfenlieder** | Eigene Macht "Elfenlied" |
| **Geodenrituale** | Trapping für Elementar-Magier |
| **Goblinrituale** | Eigene Trapping-Kategorie |
| **Herrschaftsrituale** | Trapping für Druiden |
| **Hexenflüche** | Trapping für Hexen-Magie |
| **Schelmenstreiche** | Trapping für Schurken/Schelm-Zauber |
| **Verzerrte Elfenlieder** | Trapping (gegenteilig zu Elfenliedern) |
| **Zaubermelodien** | Eigene Macht "Zaubermelodie" |
| **Zauberrunen** | Trapping für Magier-Zauber |
| **Zaubertänze** | Eigene Macht "Zaubertanz" |
| **Zibiljarituale** | Trapping (selten, Achaz-Kult) |

**Vorschlag:** In der UI unter jeder Macht ein Aufklapp-Menü "DSA-Verbreitung" mit den Sonderformen anzeigen.

---

## 6. Fertigkeiten — behalten (alle 31 bleiben vorerst)

> **Stand 2026-06-02:** Phase 3 (Fertigkeiten löschen) wurde vom User **NICHT genehmigt** und aus dem Plan entfernt. Alle 31 Fertigkeiten bleiben unverändert.

Aktuell 31 Fertigkeiten. Vergleich mit DSA:

| SW-Fertigkeit | DSA-Analogon | Status |
|---------------|--------------|:------:|
| Allgemeinwissen | Allgemeinwissen | 1 |
| Athletik | Körperbeherrschung | 1 |
| Heimlichkeit | Schleichen | 1 |
| Überreden | Überreden | 1 |
| Wahrnehmung | Sinnesschärfe | 1 |
| Kämpfen | Nahkampf (geteilt) | 1 |
| Schießen | Fernkampf | 1 |
| Diebeskunst | Taschendiebstahl / Schlösser | 1 |
| Überleben | Wildnisleben | 1 |
| Reiten | Reiten | 1 |
| Fahren | Fahren | 1 |
| Seefahrt | Seefahrt | 1 |
| Pilot | – | 1 (vorerst behalten) |
| Darbietung | Singen/Tanzen/Schauspielerei | 1 |
| Einschüchtern | Einschüchtern | 1 |
| Glaube | Götterwirken/Religion | 1 |
| Heilen | Heilkunde | 1 |
| Provozieren | – | 1 (vorerst behalten) |
| Reparieren | Handwerk | 1 |
| Glücksspiel | Glücksspiel | 1 |
| Kriegskunst | Kriegskunst | 1 |
| Okkultismus | Mythenkunde | 1 |
| Geisteswissenschaften | Mythenkunde (Spez.) | 1 |
| Naturwissenschaften | – | 1 (vorerst behalten) |
| Zaubern | Magiekunde (Basis) | 1 |
| Verrückte Wissenschaft | Alchemie | 1 |
| Alchemie | Alchemie | 1 |
| Sprache | Sprachen | 1 |
| Recherche | – | 1 (vorerst behalten) |
| Zaubern (Zauberer) | – | bereits aktiv |
| Fokus | – | bereits inaktiv |

**Hinweis:** Die ursprünglich vorgesehenen Löschungen (Pilot, Provozieren, Naturwissenschaften, Recherche) wurden verworfen, weil Textverweise in 6 Talenten, 4 Handicaps und 1 Macht sonst zu dangling references würden. Bei zukünftiger Genehmigung müssten auch die Talent-Voraussetzungen und Beschreibungstexte mit-aktualisiert werden.

---

## 7. Talente — Auswahl (488 → ca. 380-400)

### 7.1 SW-Klassen (bleiben — Status 1)

Alle 22 Klassen bleiben erhalten: Barbar, Kämpfer, Mönch, Paladin, Schurke, Waldläufer, Zauberer (6 Blutlinien), Hexenmeister, Alchemist, Kavalier, Inquisitor, Orakel, Hexe, Revolverheld, Magus, Ninja, Wandler, AH (Barde/Druide/Kleriker/Magier/Beschwörer/Diabolist/Elementarist/Illusionist/Nekromant/Schamane/Tüftler/Hexer/Hexe)

### 7.2 Zu löschende Talente (Status 3)

Diese Talente passen nicht in die Aventurien-Welt:

| Talent | Begründung |
|--------|------------|
| **AH (Diabolist)** | In DSA gibt es keine Dämonenbeschwörer als positive Klasse (nur als "Schwarzmagier" in der Verbotenen Liste) |
| **Beschwörung (Diabolist)** | Dämonen eher Feinde als Verbündete |
| **Rüstung des Abgrunds** | Dämonen-Thematik, unpassend |
| **Bluttrinker** | Vampir-Thematik (in DSA selten, nur als "Untoter") |
| **AH (Orakel)** | Evtl. behalten, da Orakel in DSA als Götterdiener existieren |
| **Erzfeind** (als generisches Talent) | Bleibt, evtl. anpassen |
| **Glücklicher Halbling** | Halblinge sind nicht in DSA-Setting |
| **Gnomenmagie** | Gnome nicht in DSA-Setting |
| **Flügel der Luft** | Oreads/Ifrits nicht in DSA |
| **Kudzu-Ringer** | Pflanzenkreatur-Thema, exotisch |
| **Engelsschwingen** | Aasimar-Thema (Aventurien kennt keine Aasimar) |
| **Himmlischer Diener** | Wie oben |
| **Versengende Waffe** (als Ifrit) | Ifrits nicht in DSA |
| **Oread-Gräber** | Oreads nicht in DSA |
| **Wasserabstammung** (als Ifrit) | Ifrits nicht in DSA |
| **Klingenzahn** (als Orc-Variante) | Evtl. anpassen |
| **Tiefblick** (Dunkelelf) | Dunkelelfen → Nachtalb-Variante |
| **AH (Tüftler)** | Ersetzen durch Schelm / Mechanikus |
| **Magus** | In DSA eher "Alchemist" oder "Hexer" |
| **Ninja** | Kulturfremd, evtl. entfernen |
| **Kranich-Stil** (Mönch) | Bleibt, evtl. DSA-Stil ergänzen |
| **AH (Hexer/Hexe)** | Bleibt |

### 7.3 Neue Talente (Status 4) — DSA-spezifisch

| Neues Talent | Kategorie | Voraussetzung | Beschreibung |
|--------------|-----------|---------------|--------------|
| **Schnell (Schnellzauber)** | Macht | Zauberer | Kann Zauber in halber Aktionszeit wirken |
| **Hauszauber** | Macht | Zauberer | Erlernt einen zusätzlichen Hauszauber |
| **Meister der Elemente** | Macht | Zauberer | Ignoriert Modifikator bei elementaren Zaubern |
| **Magischer Fokus** | Macht | Zauberer | +1 auf Zauberproben mit Fokusgegenstand |
| **Liturgiemeister** | Kleriker | – | Vergünstigte Liturgie-Steigerung |
| **Prediger** | Sozial | – | +2 auf Überreden bei Göttergläubigen |
| **Gebieter der Flammen** | Liturgie | Rondra, Praios, Ingerimm | +1 auf Bannstrahl / Flammenwand |
| **Gebieter des Wassers** | Liturgie | Efferd, Peraine | +1 auf Aquasphaero / Wellenwand |
| **Heiler der Wunden** | Kleriker | Peraine, Travia | Heilt +1 Wunde extra |
| **Kampfprediger** | Kampf | Rondra | +1 auf Angriffswurf in erster Runde |
| **Tierekenner** | Waldläufer | – | +2 auf Tierkunde-Proben |
| **Alchemist (DSA-Variante)** | Alchemist | – | Trankherstellung mit Rezepten |
| **Söldner** | Klasse | – | Ersetzt/ergänzt Kämpfer |
| **Streuner** | Klasse | – | Ersetzt Schurke |
| **Wüstensohn** | Volkstalent | Tulamide | +2 auf Hitzeresistenz |
| **Waldmensch** | Volkstalent | Waldmensch | +2 auf Waldnavigation |
| **Thorwaler Seemann** | Volkstalent | Thorwaler | +2 auf Seefahrt |
| **Zwergischer Schmied** | Volkstalent | Zwerg | +2 auf Reparieren (Waffen) |

### 7.4 Status 2 (anpassen)

| Talent | Anpassung |
|--------|-----------|
| **AH (Druide)** | Auf "Herrschaftsrituale"-Magie umstellen |
| **AH (Kleriker)** | Liturgie-Wirken statt Magie |
| **AH (Schamane)** | Animistenkräfte + Geisterruf |
| **AH (Magier)** | Magie (Gildenmagier) + Zauberrunen |
| **AH (Barde)** | Zaubermelodien + Darbietung |
| **AH (Hexe)** | Hexenflüche statt "Hexerei" |
| **AH (Beschwörer)** | Elementar-/Dämonenbeschwörung anpassen |
| **AH (Alchemist)** | Tränke und Elixiere |
| **Naturbursche** | Auf "Wildnisleben"-Fertigkeit umstellen |
| **Waldläufer** | Erzfeind + Bevorzugtes Gelände wie DSA |
| **Priesterweihe** | Status 4 — neues Talent |

---

## 8. Handicaps (162 → ca. 130)

### 8.1 Status 3 (löschen)

| Handicap | Begründung |
|----------|------------|
| **Ahnen-Schwäche** (alle Stufen) | SW-typische Blutlinien-Mechanik, in DSA nicht relevant |
| **Bevorzugte Klasse** | Klassen-Konzept bleibt, aber Handicap entfällt |
| **Rüstungsbeschränkung_*** | Bleibt (generisch) |
| **Erbstück** | Bleibt |
| **Heldisch** | DSA-typisch behalten? — JA |
| **Gesucht** | Bleibt |
| **Ehrenkodex** | Bleibt (DSA: Ehrgefühl) |
| **Arrogant** | Bleibt |
| **Blutrünstig** | Bleibt (DSA: Blutrausch der Thorwaler/Orks) |
| **Feengeraubt** | Bleibt |
| **Ahnungslos** | Bleibt |
| **Geheimnis_*** | Bleibt |
| **Angewohnheit_*** | Bleibt |

**Eigentlich zu streichen:**
| Handicap | Begründung |
|----------|------------|
| **Junge** | Bleibt, in DSA oft relevant (Anfänger) |
| **Befleckter Geist** | Bleibt |
| **Heldentum** | Bleibt |
| **Auserkoren** | Bleibt |
| **Feind (leicht/schwer)** | Bleibt |
| **Fies** | Bleibt (DSA: Fieser Dieb) |
| **Hässlich_*** | Bleibt |
| **Fettleibig** | Bleibt |
| **Kränklich** | Bleibt |
| **Pech** | Bleibt |
| **Tollpatschig** | Bleibt |
| **Neugierig** | Bleibt |

> **Fazit:** Die meisten Handicaps bleiben (1), nur wenige müssen gelöscht werden (3).

### 8.2 Status 4 (ergänzen — DSA-Vor-/Nachteile)

| Neues Handicap | Stufe | Beschreibung |
|----------------|-------|--------------|
| **Niedrige Seelenkraft** | schwer | -1 auf Willenskraft-basierte Proben |
| **Blutrausch** (leicht/schwer) | – | Bei Wunde: muss angreifen |
| **Kälteempfindlich** | leicht | -4 bei Kälte |
| **Hitzeempfindlich** | leicht | -4 bei Hitze |
| **Niedrige Zähigkeit** | schwer | -1 Robustheit |
| **Zäher Hund** (VORTEIL!) | VORTEIL | +1 Robustheit |
| **Schlechte Eigenschaft** | – | Angst vor etwas Spezifischem |
| **Immunität gegen [Gift]** | VORTEIL | Wie Waldmenschen |
| **Hitze-/Kälte-Resistenz** | VORTEIL | +4 auf Resistenz-Probe |
| **Angenehmer Geruch** | VORTEIL | +2 auf Darbietung |
| **Entfernungssinn** | VORTEIL | +2 auf Wahrnehmung (Entfernung) |
| **Aberglaube** | leicht | -1 gegen Götterwirken |
| **Goldgier** | leicht | Bei Reichtum: Selbstbeherrschungs-Probe |
| **Streitsucht** | leicht | Muss auf Provokation reagieren |
| **Eidvergessen** | schwer | Verliert Karma bei Eidbruch |
| **Zwergischer Starrsinn** | leicht | -2 auf Überreden |
| **Elfischer Hochmut** | leicht | -2 auf Umgang mit "Kurzläuffigen" |
| **Orkischer Blutdurst** | leicht | Wie Blutrausch |
| **Niedrige Seelenkraft** (Variante) | – | – |

> **Wichtig:** In DSA sind VOR- und NACHTEILE ein Schlüsselkonzept. Wir sollten eine Trennung einführen: `ist_vorteil: true/false` (analog zu DSA).

### 8.3 Status 2 (anpassen)

| Handicap | Anpassung |
|----------|-----------|
| **Behindernde Rüstung_*** | Auf DSA-Panzerung anpassen (Beine, Arme, Helm) |
| **Hinterhältiger Angriff** | Wird Talent (Schurke) |
| **Berüchtigt** | Auf "Berüchtigt in [Stadt]" anpassen |

---

## 8.5 Wildes Aventurien — DSA-Talente & Handicaps (Fan-Konversion)

**Stand:** 2026-06-03 — ✅ implementiert
**Quellen:** `Texte/Wildes-Aventurien-V2.3.pdf` (50 S.) + `Texte/Wildes_Aventurien.pdf` (Ver. 3.0, 20 S.)
**Skript:** `scripts/dsa_add_wildes_aventurien.py` (idempotent)
**Backup:** `backup/settings/Savage Aventurien_vor_wildes_aventurien_20260603.json`
**Abgleich-Doku:** `logs/wildes_aventurien_abgleich.md`

Durch das integrierte Fantasy Kompendium ist vieles bereits abgedeckt. Übernommen wurden nur die **DSA-spezifischen** Elemente ohne FK-Äquivalent.

### 8.5.1 Neue Talente (16 hinzugefügt)

| Talent | Kategorie | Rang | Quelle |
|--------|-----------|:----:|--------|
| Kraftlinienmagie | Magier | H | DSA-Kernkonzept (Ley-Linien) |
| Kugelzauber | Magier | A | Kristallkugel |
| Mirakel | Kleriker | A | Geweihten-Bennie |
| Magischer Alltag | Macht | A | ≈ Prestidigitation |
| Knochenkeule | Schamane | F | Schamanen-Fokuswaffe |
| Elfenlieder | Macht | A | Elfen-Magie (DSA: AH Fey) |
| Hexenflüche | Hexe | A | Hexen-Fluchmechanik |
| Dolch des Druiden | Druide | A | Vulkanglasdolch |
| Bindung des Stabes | Magier | A | Stab-Baum (Ver. 3.0) |
| Fokus des Stabes | Magier | F | Stab-Baum, benötigt Bindung |
| Flammenschwert | Magier | V | Stab-Baum, benötigt Fokus |
| Zauberspeicher | Magier | V | MP-Speicher im Stab |
| Kraftfokus | Magier | V | W8 Wild Die mit Stab |
| Eisenaffine Aura | Hintergrund | A | „Bann des Eisens" |
| Schelm | Hintergrund | A | Kobold-erzogener Trickster |
| Prophezeien | Experte | A | ≈ Macht Weissagung |

### 8.5.2 Neue Handicaps (6 Einträge / 4 Konzepte)

| Handicap (Key) | Stufe | Punkte |
|----------------|-------|:------:|
| Artefaktgebunden_leicht | leicht | 1 |
| Novize_leicht / Novize_schwer | leicht/schwer | 1 / 2 |
| Stigma_leicht / Stigma_schwer | leicht/schwer | 1 / 2 |
| Laestige_Mindergeister_leicht | leicht | 1 |

### 8.5.3 Bewusst NICHT übernommen (bereits durch FK abgedeckt)

| PDF-Element | FK-Äquivalent |
|-------------|---------------|
| Vertrauter | `Vertrauter` ✅ |
| Alchemist / Meisteralchemist | identisch ✅ |
| Beschwörer | `AH (Beschwörer)` ✅ |
| Artefaktbauer | `Artefakterschaffer` + `Meisterlicher Artefakterschaffer` ✅ |

### 8.5.4 Offene Punkte / Review-Notizen

- **Prophezeien** verweist mechanisch auf die Macht **Weissagung**, die im Setting (noch) fehlt → ggf. in Phase 6.2 als neue Macht ergänzen, oder Beschreibung bleibt selbsterklärend.
- **Elfenlieder** nutzt DSA-Voraussetzung „AH (Fey)", die es im Setting nicht gibt → ersetzt durch `Zaubern W6` + „Elf oder Halbelf".
- **Artefaktgebunden**: Wert −4 (Ver. 3.0) statt −6 (V2.3) übernommen.
- Die PDF nennt zwei **gestrichene SW-Talente** (`Analphabet`, `Elan`) — noch nicht aus dem Setting entfernt (Status 3, optional in einer späteren Phase).
- ⚠️ **Review (Phase 9.R):** Balancing & Voraussetzungs-Ketten gegen FK gegenprüfen.

---

## 8.6 DSA-Regelwiki „Nachteile" — Lücken-Abgleich

**Stand:** 2026-06-03 — ✅ implementiert
**Quelle:** https://dsa.ulisses-regelwiki.de/nachteilauswahl.html (81 Nachteile)
**Skript:** `scripts/dsa_add_nachteile_wiki.py` (idempotent)
**Backup:** `backup/settings/Savage Aventurien_vor_nachteile_wiki_20260603.json`
**Abgleich-Doku:** `logs/dsa_nachteile_abgleich.md`

Inhaltlicher Abgleich aller 81 Wiki-Nachteile gegen die bestehenden Handicaps. Ergebnis:

### 8.6.1 Neu ergänzt (8)

| Handicap | Stufe | DSA-Vorlage |
|----------|:-----:|-------------|
| Hitzeempfindlich | leicht | Hitzeempfindlich I-II |
| Kälteempfindlich | leicht | Kälteempfindlich / Kältestarre |
| Farbenblind | leicht | Farbenblind |
| Schlafwandler | leicht | Schlafwandler |
| Giftanfällig | leicht | Giftanfällig I-II |
| Unverträglichkeit gegenüber Alkohol | leicht | Unverträglichkeit gegenüber Alkohol |
| Strenger Körpergeruch | leicht | konsolidiert Ork-/Raubtier-/Jagdwildgeruch |
| Empfindlichkeit gegen Eisen | leicht | Empfindlichkeit (unedle Metalle) |

### 8.6.2 Bereits abgedeckt (Beispiele)

`Niedrige Zähigkeit` → `Verringerte Vitalität` · `Niedrige Seelenkraft` → `Selbstzweifel` ·
`Nachtblind` → `Gewöhnliche Sicht` · `Instabiler Zauberer`/`Wilde Magie` → `Magischer Tollpatsch` ·
`Gläsern` → `Zerbrechlich` · `Taub` → `Schwerhörig` · `Behäbig` → `Langsam`. Vollständige
Tabelle in der Abgleich-Doku.

### 8.6.3 Bewusst NICHT übernommen

- **DSA-Ressourcen-Mechanik** (kein SW-Pendant): Niedrige Astral-/Karmalkraft, Schwache
  Zaubermelodien/-tänze, Limbus-Medium, Wenige Predigten/Visionen, Schlechte Regeneration,
  Kein Vertrauter, Keine Flugsalbe, Wahrer Name, …
- **Zu generisch / Namens-Mechanik:** Unfähig, Lernfaul, Verweichlicht, Böser Namensvetter,
  Lächerlicher Name, Schurkenname, Unpassender Name.

### 8.6.4 Offene Folge-Aufgabe

- ⚠️ **Phase 4 (Völker):** `Hitzeempfindlich`/`Kälteempfindlich`/`Strenger Körpergeruch`/
  `Empfindlichkeit gegen Eisen` bei den passenden Völkern (Achaz, Ork, Waldmensch, Elf)
  als Volks-Handicap hinterlegen.

---

## 9. Ausrüstung (449 Items)

### 9.1 Status 1 (beibehalten)

Alle generischen Items (Beutel, Fackel, Seil, Kerze, etc.) bleiben.

### 9.2 Status 2 (anpassen — DSA-Währung & DSA-Namen)

- Währung: **Dukaten (D), Silbertaler (S), Heller (H), Kreuzer (K)**
- 1 Dukaten = 10 Silbertaler = 100 Heller = 1000 Kreuzer
- Aktuelle Preise in GM (Goldmünzen) umrechnen oder neu setzen
- Startgeld: Variabel je nach Kultur (10-50 Dukaten)

**Beispiel-Items, die anzupassen sind:**

| Item | Anpassung |
|------|-----------|
| **Langschwert** | W6+4 statt W6+1, Preis: 25 D |
| **Kurzschwert** | W6+1, Preis: 12 D |
| **Streitaxt** | W6+4 (oder mehr), Preis: 20 D |
| **Plattenrüstung** | Rüstung +6, Preis: 80 D |
| **Kettenrüstung** | Rüstung +5, Preis: 50 D |
| **Lederrüstung** | Rüstung +2, Preis: 8 D |
| **Arbalest (schwere Armbrust)** | 2W6, Preis: 50 D |
| **Hellebarde** | W6+4 (Reichweite 1), Preis: 30 D |
| **Wurfaxt** | W6+2, Preis: 1 D |

### 9.3 Status 4 (ergänzen — DSA-spezifisch)

| Neues Item | Beschreibung | Preis |
|------------|--------------|-------|
| **Bornland-Langschwert** | DSA-typische Waffe | 28 D |
| **Holzfälleraxt** | Standard-Axt der Thorwaler | 8 D |
| **Schuppenhemd** | DSA-Rüstung (Zwerg) | 12 D |
| **Watvogel** | Tuchrüstung (kein Abzug) | 6 D |
| **Zwergischer Rundschild** | +2 Parierwaffe | 10 D |
| **Alchemistenschere** | DSA-Werkzeug | 0,5 D |
| **Wundsalbe** | Heilt 1 Wunde, einmal pro Tag | 1 D |
| **Heiltrank (Balsam)** | Heilt 1W6+2 SP, einmal | 5 D |
| **Schlaftrunk** | Lässt Ziel 1W6 Runden schlafen | 4 D |
| **Wurara-Gift** | Kontaktgift | 2 D pro Dosis |
| **Sturmharpune** | Achaz-Waffe | 8 D |
| **Aventurische Münzen** | D, S, H, K | – |
| **Efferdbann-Zeichen** | Kultgegenstand | 5 D |
| **Praios-Amulett** | Licht-Schutz | 30 D |
| **Rondra-Schwert** | Kultgegenstand | 100+ D |
| **Phex-Hand** | Diebeswerkzeug | 20 D |
| **Peraine-Kraut** | Heilkraut | 0,5 D |
| **Borbarad-Bannschwert** | Legendär | 500+ D |
| **Magierstab** | Fokus | 20-200 D |
| **Zauberbuch** | Magier-Inventar | 50+ D |

---

## 10. Settingregeln (25 Regeln)

### 10.1 Status 2 (Aktivieren — DSA-Regeln)

| Regel | Status | Aktion |
|-------|:------:|--------|
| **helden_sterben_nie** | → 2 | Anpassen: "Helden sterben nie" in DSA-Lite (Bennies äquivalent) |
| **schnelle_genesung** | → 2 | Anpassen: Heilung in DSA erfolgt langsamer (Tage/Wochen) |
| **schwere_entscheidungen** | → 2 | Anpassen: "Schwere Entscheidungen" — Karma-System |
| **ungepanzerter_held** | → 2 | Anpassen: In Aventurien sehr relevant (Panzerung hemmt) |
| **mehr_fertigkeitspunkte** | → 2 | Anpassen: Proben-Spezialisierung |
| **geborener_held** | → 2 | Anpassen: DSA hat "AP" (Abenteuerpunkte) |
| **wundobergrenze** | → 2 | Anpassen: Keine Wund-Obergrenze in SW-Standard |
| **kreativer_kampf** | → 2 | Anpassen: Kampfstil, Manöver |
| **keine_machtpunkte** | → 2 | Anpassen: Magie-Punkte ähneln DSA-AsP/KaP |
| **narrenglueck** | → 2 | Anpassen: Glückspunkt-System (Schelm) |
| **riesige_feinde** | → 2 | Anpassen: Riesige Feinde in DSA sehr häufig |
| **riesige_feinde,** | – | Bug: doppelter Key — entfernen |
| **fertigkeitsspezialisierungen** | → 2 | Anpassen: DSA-Spezialisierungen (z.B. "Schleichen: Wälder") |
| **fieser_schaden** | → 2 | Anpassen: "Fieser Schaden" — Hinterhältiger Angriff |
| **dynamischer_rueckschlag** | → 2 | Anpassen: "Dynamischer Rückschlag" (Bennies/Patzer) |
| **entschlossenheit** | → 2 | Anpassen: Entschlossenheit gegen Furcht |
| **fanatiker** | → 2 | Anpassen: Fanatiker (Boron, Praios, etc.) |
| **freizeit** | → 2 | Anpassen: Freizeit-Aktivitäten |
| **grosse_abenteuer** | → 2 | Anpassen: "Große Abenteuer" — Reisen, Götterwirken |
| **mehr_sprachen** | → 2 | Anpassen: Sprachen in DSA sehr wichtig (Garethi, Thorwalsch, Tulamidya) |
| **schurkische_entschlossenheit** | → 2 | Anpassen: "Schurkische Entschlossenheit" (Schurken) |
| **schwierige_heilung** | → 2 | Anpassen: "Schwierige Heilung" (Wunden heilen langsam) |
| **strahlschablone** | → 2 | Anpassen: Strahlschablonen für Linienzauber |
| **grosse_hoehen** | → 2 | Anpassen: "Große Höhen" (Riesige Wesen) |
| **verrat** | → 2 | Anpassen: "Verrat" (Verräter-Konzepte) |

### 10.2 Bug: doppelter Key

`riesige_feinde,` (mit Komma) ist ein Duplikat von `riesige_feinde`. **Entfernen.**

---

## 11. Währung & Startgeld

| Element | Alt | Neu |
|---------|-----|-----|
| `waehrung` | "GM" | "DSA" (D/S/H/K) |
| `startgeld` | 300 | Kulturabhängig (Empfehlung: 25 Dukaten Standard) |

**Währungs-Umrechnung in der UI:**
- 1 GM ≈ 1 Dukaten
- 1 SP = 1 Silbertaler
- 1 HP = 1 Heller
- 1 CP = 1 Kreuzer

---

## 12. Konvertierungs-Reihenfolge (Vorschlag)

> **Stand 2026-06-02:** Phase 3 wurde vom User verworfen. Reihenfolge entsprechend angepasst.

| Phase | Schritt | Aufwand | Status |
|-------|---------|---------|:------:|
| 0 | MD-Plan mit User abnicken | 30 min | ✅ |
| 1 | Bugfix `riesige_feinde,` | 1 min | ✅ 2026-06-02 |
| 2 | `waehrung` + `startgeld` + `attribute` | 5 min | ⏳ auf User-Genehmigung |
| ~~3~~ | ~~`fertigkeiten_daten` (4 löschen)~~ | ~~10 min~~ | ❌ abgelehnt 2026-06-02 |
| 4 | `voelker` (10 anpassen + 2 neu) | 60 min | ⬜ offen |
| 5 | `voelker_selected` auf 12 DSA-Spezies | 5 min | ⬜ offen (abh. von 4) |
| 6.1 | `maechte`: bestehende 73 um `dsa_trappings` erweitert | 30 min | ✅ 2026-06-02 |
| 6.1.1 | `maechte`: DSA-Zauber als Trappings in der Machtbeschreibung angezeigt | 30 min | ✅ 2026-06-03 |
| 6.2 | `maechte`: neue Mächte (genehmigte Auswahl) | 60 min | ⏳ auf User-Genehmigung (siehe `logs/dsa_neue_maechte_diskussion.md`) |
| 6.3 | `maechte`: Duplikate + Status 3 (`Chaos`, `Bindender Ruf`) | 5 min | ⬜ offen |
| 6.R | **Review: Mächte-Trappings QA** — inhaltliche Prüfung aller 759 Trappings | 60 min | ⬜ offen |
| 7 | `talente`: Status 3 löschen (~20-30), Status 4 ergänzen (~20) | 180 min | ⬜ offen |
| 8 | `handicaps`: Status 4 ergänzen (~15), Status 3 löschen (~5) | 90 min | ⬜ offen |
| 8.5 | **Wildes Aventurien: DSA-Talente + Handicaps** (16 Talente, 6 Handicaps) | 60 min | ✅ 2026-06-03 |
| 8.6 | **DSA-Regelwiki Nachteile: Lücken-Abgleich** (8 Handicaps ergänzt) | 45 min | ✅ 2026-06-03 |
| 9 | `ausruestung`: Preise in D/S/H/K, DSA-Items ergänzen (~20-30) | 120 min | ⬜ offen |
| 9.R | **Review: Inhalte komplett** — Völker, Talente, Handicaps, Ausrüstung prüfen | 60 min | ⬜ offen |
| 10 | `settingregeln`: 24 Regeln anpassen/aktivieren | 60 min | ⬜ offen |
| 11 | Validierung: Charakter-Generierung testen | 60 min | ⬜ offen |
| 12 | Test-Archetypen: Mittelländer Magier, Thorwaler Krieger, Zwergischer Schmied, Elfen-Beschwörer | 120 min | ⬜ offen |
| 13 | **Final Review: Gesamtabnahme** — Setting, Code, Tests, PDF-Export | 60 min | ⬜ offen |

**Gesamt-Aufwand:** ca. 14-18 Stunden

---

## 13. Offene Entscheidungsfragen für den User

1. **Bugfix:** Soll der doppelte Key `riesige_feinde,` sofort entfernt werden?
2. **Völker-Defaults:** Soll die `voelker_selected`-Liste die 12 neuen Völker als Default aktiviert haben, oder soll der User sie erst auswählen?
3. **DSA-Magie-Vokabular:** Soll die App optional eine "DSA-Magie-Ansicht" bekommen, in der die Mächte nach Sonderformen gruppiert sind?
4. **Startgeld:** Soll es kulturabhängig sein (Mensch Mittelländer: 25 D, Zwerg: 30 D, Ork: 10 D), oder ein einheitliches "Standard" sein?
5. **Ausrüstung-Währung:** Alle 449 Items in DSA-Währung umrechnen, oder nur die DSA-neuen in D/S/H/K und die alten in "GM" lassen?
6. **Talente "AH (Diabolist)" komplett entfernen, oder als "Schwarzmagier" umbenennen?**
7. **"Ninja" löschen oder als "Ninja aus dem Fernen Osten" behalten?**
8. **Mächte-Erweiterung:** Soll die Macht-Liste (73) um 5-10 DSA-spezifische erweitert werden, oder reichen die 73 + Trappings?
9. **"Magier"/"Zauberer"-Unterscheidung:** In DSA streng (Gildenmagier vs. Hexer), in SW unscharf. Beibehalten?
10. **Pflanzenwelt/Flora:** Soll das Herbarium (DSA-typisch) als eigenes Item-Cluster aufgenommen werden?

---

## 14. Validierungs-Kriterien (nach Konvertierung)

- [ ] `python main.py` startet ohne Fehler
- [ ] Setting "Savage Aventurien" ist in der Dropdown-Liste wählbar
- [ ] Neuer Charakter → Auswahl aller 12 Völker möglich
- [ ] Mächte-Anzeige zeigt DSA-Trappings als Tooltip/Detail
- [ ] Beispiel-Charakter: Mittelländer Magier mit Hauszauber "Ignifaxius" speicherbar
- [ ] Beispiel-Charakter: Thorwaler Krieger mit Kult-Blut "Swafnir"
- [ ] Beispiel-Charakter: Zwergischer Schmied mit Runen-Axt
- [ ] Beispiel-Charakter: Hexe aus dem Süden mit Hexenflüchen
- [ ] Währung zeigt D/S/H/K korrekt
- [ ] Startgeld variiert nach Kultur
- [ ] PDF-Export zeigt DSA-Bezeichnungen
- [ ] Tests laufen: `python "test units/run_all_tests.py"`

---

## 15. Datei-Ablage

- **MD-Plan:** `logs/dsa_konvertierungs_plan.md` (dieses Dokument)
- **Aktualisiertes Setting:** `settings/Savage Aventurien.json`
- **Backup des Originals:** `backup/settings/Savage Aventurien_original_<datum>.json`
- **Log-Datei:** `logs/dsa_konvertierung_<datum>.log`
- **Konvertierungs-Skript:** `scripts/convert_to_dsa.py` (für reproduzierbare Konvertierung)

---

## 16. Fortschritts-Tracking (Phase 6: Mächte)

**Stand:** 2026-06-03 — Phase 6.1 + 6.1.1 abgeschlossen, Phase 6.2 wartet auf User-Genehmigung

### 16.1 Erledigte Schritte

- [x] **Sektion 4.5: Vollständige DSA → SW-Macht Zuordnungs-Liste erstellt** (686 DSA-Einträge)
- [x] **Phase 1: Bugfix `riesige_feinde,`** — Duplikat entfernt, 24 Settingregeln übrig
- [x] **Phase 6.1: Bestehende 73 SW-Mächte um `dsa_trappings` erweitert** (70/73 erweitert, 2 ohne Mapping, 1 Duplikat)
- [x] **Phase 6.1.1: DSA-Zauber als Trappings in der Machtbeschreibung** — Trapping-Namen werden in der UI-Beschreibung jeder Macht angezeigt ✅ 2026-06-03
- [x] **Backup des Originals erstellt:** `backup/settings/Savage Aventurien_original_20260602.json`
- [x] **Konvertierungs-Skript erstellt:** `scripts/dsa_add_trappings.py`
- [x] **Log-Datei erstellt:** `logs/dsa_konvertierung_20260602_125934.log`
- [x] **Phase 3 ABGELEHNT:** 4 Fertigkeiten löschen — User möchte vorerst alle 31 behalten
- [ ] **Phase 6.2: 40 neue SW-Mächte (Status 4)** — **WARTET AUF USER-GENEHMIGUNG**, siehe `logs/dsa_neue_maechte_diskussion.md`

### 16.2 Statistik Phase 6.1

| Kennzahl | Wert |
|----------|-----:|
| Mächte gesamt (unverändert) | 73 |
| Mächte mit DSA-Trappings | 70 / 73 (96 %) |
| DSA-Trappings gesamt | 759 |
| Ø Trappings pro Macht | 10,8 |
| Neue Mächte hinzugefügt | **0** (warten auf Einzel-Genehmigung) |

**Hinweis:** In einer früheren Iteration wurden 40 neue Mächte versehentlich direkt hinzugefügt. Nach User-Hinweis wurden sie rückgängig gemacht und in eine separate Diskussions-Liste ausgelagert.

### 16.3 Beispiel: `Heilung` (vorher / nachher)

**Vorher (73 Mächte, ohne DSA-Bezug):**
```json
{
  "name": "Heilung",
  "rang": "A",
  "machtpunkte": 3,
  "beschreibung": "Stellt Wunden wieder her, die weniger als eine Stunde alt sind."
}
```

**Nachher (mit 53 DSA-Trappings):**
```json
{
  "name": "Heilung",
  "rang": "A",
  "machtpunkte": 3,
  "beschreibung": "Stellt Wunden wieder her, die weniger als eine Stunde alt sind.",
  "dsa_trappings": [
    "Balsam Salabunde",
    "Hexenspeichel",
    "Manus Miracula",
    "Physiostabilis",
    "Psychostabilis",
    "Regeneratio",
    "Salander",
    "Satuarias Herrlichkeit",
    "Schmerzen lindern",
    "Sumus Elixiere",
    "Welle der Reinigung",
    "Aufwecken",
    "Erwachen",
    "Erschöpfungen lindern",
    "Gifthaut heilen",
    "Zaubernahrung",
    "Ausnüchtern (Liturgie)",
    "Befreiung des Geistes (Liturgie)",
    "Blick des Heilers (Liturgie)",
    "Giftbann (Liturgie)",
    "Goldene Hand (Liturgie)",
    "Heilsame Quelle (Liturgie)",
    "Heilsegen (Liturgie)",
    "Helfende Hand (Liturgie)",
    "Klarer Geist (Liturgie)",
    "Krankheitsbann (Liturgie)",
    "Krankheiten vorbeugen (Liturgie)",
    "Peraines Gnade (Liturgie)",
    "Reinigung des Bösen (Liturgie)",
    "Schonfrist (Liturgie)",
    "Tierleid lindern (Liturgie)",
    "Ackersegen (Zeremonie)",
    "Ausbrennen (Purgation) (Zeremonie)",
    "Eidechsenregeneration (Zeremonie)",
    "Fruchtbarkeit (Zeremonie)",
    "Geistheilung (Zeremonie)",
    "Häutung (Zeremonie)",
    "Heilschlaf (Zeremonie)",
    "Heilung von Seelenkranken (Zeremonie)",
    "Hilfe in der Not (Zeremonie)",
    "Jugendlichkeit (Zeremonie)",
    "Läuterung des Erzes (Zeremonie)",
    "Lebenstausch (Zeremonie)",
    "Makelloser Leib (Zeremonie)",
    "Nahrungsreinigung (Zeremonie)",
    "Priesterweihe (Ordination) (Zeremonie)",
    "Sättigung (Zeremonie)",
    "Selbstopferung (Zeremonie)",
    "Speisung (Zeremonie)",
    "Wiederherstellung (Zeremonie)",
    "Geburtssegen (Segen)",
    "Grabsegen (Segen)",
    "Kleiner Heilsegen (Segen)",
    "Speisesegen (Segen)",
    "Stärkungssegen (Segen)",
    "Tranksegen (Segen)",
    "Gefäß der Jahre (Ritual)",
    "Immortalis Lebenszeit (Ritual)",
    "Infinitum Immerdar (Ritual)"
  ]
}
```

### 16.4 Phase 6.2: Neue Mächte — Einzelabstimmung erforderlich

**40 vorgeschlagene neue Mächte** wurden **NICHT** ins Setting übernommen.

→ Vollständige Diskussions-Liste mit Einzelabstimmung: **`logs/dsa_neue_maechte_diskussion.md`**

**Empfehlung zur Konsolidierung** (siehe Diskussions-Datei):
- 11 der 40 Mächte könnten als **Variante/Trapping** zu bestehenden Mächten geführt werden
- Konsolidierung würde Anzahl auf ca. **15-20 echte neue Mächte** reduzieren

**Vorgeschlagene Konsolidierungen:**

| Neue Macht | Stattdessen Variante von… |
|------------|--------------------------|
| Heiliger Boden | `Schutz` (Zonen-Variante) |
| Liturgieschild | `Schutz` (göttliche Variante) |
| Gegengift | `Heilung` (Trapping) |
| Spinnennetz | `Verstricken` |
| Regenruf | `Wetterkontrolle` |
| Blitzruf | `Teleportation` |
| Wolfsform | `Böswillige Verwandlung` |
| Finsternis | `Licht/Dunkelheit` |
| Schnurren | (entfernen) |
| Göttliches Zeichen | `Mystisches Eingreifen` (existiert!) |
| Botenruf | `Gedankenverbindung` |

### 16.5 Status der Konvertierungs-Phasen

| Phase | Schritt | Status |
|------:|---------|:------:|
| 0 | MD-Plan mit User abnicken | ✅ |
| 1 | Bugfix `riesige_feinde,` | ✅ 2026-06-02 |
| 2 | `waehrung` + `startgeld` + `attribute` | ⏳ auf User-Genehmigung |
| ~~3~~ | ~~`fertigkeiten_daten`~~ | ❌ abgelehnt 2026-06-02 |
| 4 | `voelker` (10 anpassen + 2 neu) | ⬜ offen |
| 5 | `voelker_selected` auf 12 DSA-Spezies | ⬜ offen (abh. von 4) |
| **6.1** | **`maechte`: Bestehende 73 um `dsa_trappings` erweitern** | **✅ 2026-06-02** |
| **6.1.1** | **DSA-Zauber als Trappings in der Machtbeschreibung** | **✅ 2026-06-03** |
| **6.2** | **`maechte`: 40 neue Mächte anlegen** | **⏳ auf User-Genehmigung** |
| **6.R** | **Review: Mächte-Trappings QA** | **⬜ offen** |
| 7 | `talente` | ⬜ offen |
| 8 | `handicaps` | ⬜ offen |
| 9 | `ausruestung` | ⬜ offen |
| 10 | `settingregeln` | ⬜ offen |
| 11 | Validierung | ⬜ offen |
| 12 | Test-Archetypen | ⬜ offen |

### 16.6 Nächste Schritte

**Sofort:**
- [ ] **User-Entscheidung:** Einzelabstimmung der 40 neuen Mächte in `logs/dsa_neue_maechte_diskussion.md`
  - Option A: Einzelabstimmung
  - Option B: Block-Abstimmung nach Rang
  - Option C: Top-X-Prioritäten

**Nach Genehmigung:**
- [ ] Die 2 übersprungenen Mächte prüfen:
  - `Objekt auslesen` — kein DSA-Mapping gefunden, evtl. zu löschen (Status 3)
  - `Schlummer` — entspricht `Kusch` (Zauber) / `Schlaf` (Liturgie), kann zu `Lähmung` konsolidiert werden
- [x] **UI-Anpassung: DSA-Zauber als Trappings in der Machtbeschreibung** ✅ 2026-06-03
- [ ] Filter-Funktion: "Zeige nur Mächte mit DSA-Trappings"
- [ ] Doppelten Key `Gegenstand Beschwören` (capital B) auflösen
- [ ] Zu löschende Mächte entfernen (Phase 6.3): `Chaos`, `Bindender Ruf`, ggf. `Objekt auslesen`, `Schlummer`
- [ ] Validierung: `python main.py` startet ohne Fehler
- [ ] Test: Charakter-Generierung mit DSA-Macht

### 16.7 Offene Entscheidungsfragen (Phase 6)

1. **Neue Mächte:** Welche der 40 vorgeschlagenen Mächte werden genehmigt? (siehe Diskussions-Liste)
2. **Konsolidierung:** Welche der 11 vorgeschlagenen Konsolidierungen werden umgesetzt?
3. **UI-Anzeige:** Wie sollen DSA-Trappings angezeigt werden? (Tooltip / Detail-Button / Spalte?)
4. **Sortierung:** Mächte alphabetisch oder nach DSA-Original (Zauber, Liturgien, …)?
5. **Löschung:** Soll `Chaos` und `Bindender Ruf` jetzt entfernt werden, oder als deprecated markiert bleiben?
6. **Duplikate:** `Gegenstand Beschwören` (capital B) — automatisch löschen oder als Alias behalten?
7. **dsa_neu Flag:** Soll das Flag in der App sichtbar sein (z.B. als "NEU" Badge)?
8. **Trapping-Typen:** Soll in `dsa_trappings` zwischen `(Zauber)`, `(Ritual)`, `(Liturgie)`, `(Zeremonie)`, `(Segen)` unterschieden werden? **Aktuell: JA, bei komplexen Zuordnungen**
