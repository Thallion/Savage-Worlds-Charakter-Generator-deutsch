# SOLL/IST Abweichungs-Analyse: Ausrüstung (Stand: 2026-06-04)

**Klassifizierung:**
- **FEHLT_OFFEN**: Bogen-Item ist im Katalog vorhanden, Char hat es nicht → **kann ergänzt werden** (Schritt 1)
- **FEHLT_KATALOG**: Bogen-Item ist im Katalog NICHT vorhanden → **muss ergänzt werden** (Schritt 2, Freigabe erforderlich)
- **ZUVIEL**: Char hat Item, das im Bogen nicht erwähnt wird (häufig: Approximation/Subsitution im Build)
- **OK**: SOLL vollständig gedeckt

**Wichtig:** 'OFFEN' bedeutet Item-Key existiert im Katalog. Im Build-Lauf kann `s.kaufen(item)` aufgerufen werden.

---

## Fantasy Kompendium (32 Chars vs. 32 Bögen)

### Akrobatin ↔ ACROBAT

- **🔴 FEHLT_KATALOG** (9): `potion of boost Trait (Spirit)`, `eight daggers (Range 3/6/12, Damage Str+d4, RoF 1)`, `thief’s pack`, `studded leather armor (+2)`, `potion of haste (ignore 2 points of Multi-Action penalties for 5 rounds)`, `smokestick`, ... +3
- **⚠ ZUVIEL** (4): `Diebespaket`, `Ledertunika`, `Krähenfüße`, `Dolch`

### Alchemist ↔ ALCHEMIST

- **🔴 FEHLT_KATALOG** (12): `tanglefoot bag`, `potion of environmental protection`, `thunderstone`, `goggles`, `smokestick`, `bag of holding`, ... +6
- **⚠ ZUVIEL** (3): `Alchemistenfeuer`, `Gegengift, Phiole`, `Alchemistenpaket`

### Assassinin ↔ ASSASSIN

- **🔴 FEHLT_KATALOG** (11): `sap (Str+d4, nonlethal)`, `assassin’s brew (lethal, ingested, –2 Notice to detect)`, `green slime extract (paralyzing, contact, +1 Notice to detect)`, `thief’s pack`, `studded leather armor (+2)`, `giant snake poison (lethal, injury)`, ... +5
- **⚠ ZUVIEL** (6): `Totschläger`, `Umhang mit Kapuze`, `Ledertunika`, `Blasrohrpfeile (20)`, `Diebespaket`, `Blasrohr`

### Barbarin ↔ BARBARIAN

- **🔴 FEHLT_KATALOG** (5): `adventurer’s pack`, `heavy boots`, `potion of growth`, `hide tunic (+2, torso)`, `potion of healing`
- **⚠ ZUVIEL** (4): `Stiefel, schwer`, `Ledertunika`, `Trank: Heilung`, `Abenteurerpaket`

### Barde ↔ BARD

- **🔴 FEHLT_KATALOG** (7): `potion of boost Trait (Vigor)`, `cloak with hood`, `entertainer’s pack`, `musical instrument`, `smokestick`, `adventurer’s lantern (lights on command, hovers near user)`, ... +1
- **⚠ ZUVIEL** (7): `Trank: Attributsteigerung`, `Umhang mit Kapuze`, `Laterne`, `Trank: Heilung`, `Rauchstab`, `Musikinstrument`, ... +1

### Champion ↔ CHAMPION

- **🔴 FEHLT_KATALOG** (4): `20 bolts`, `masterwork plate mail (+4, torso, arms, legs only)`, `cleric’s pack`, `3 vials of holy water`
- **⚠ ZUVIEL** (4): `Bolzen (10)`, `Heiliges Wasser`, `Klerikerpaket`, `Plattenbrustharnisch`

### Diebin ↔ THIEF

- **🔴 FEHLT_KATALOG** (12): `tanglefoot bag`, `20 bolts`, `5x daggers (Range 3/6/12, Damage Str+d4, AP 1)`, `sap (Str+d4, nonlethal)`, `thief’s pack`, `studded leather armor (+2)`, ... +6
- **⚠ ZUVIEL** (10): `Totschläger`, `Umhang mit Kapuze`, `Verstrickungsbeutel`, `Ledertunika`, `Trank: Attributsteigerung`, `Bolzen (10)`, ... +4

### Druidin ↔ DRUID

- **🔴 FEHLT_KATALOG** (3): `potion of invisibility`, `Heartwood staff (Str+d8. Parry +1, Reach 1, Two Hands)`, `natural armor (+2)`
- **⚠ ZUVIEL** (2): `Stab (3,5 m)`, `Hemd aus natürlicher Rüstung`

### Hexe ↔ WITCH

- **🔴 FEHLT_KATALOG** (6): `mage’s pack`, `potion of boost Trait (Vigor)`, `tunic (+1)`, `two prepared powers in chicken bones`, `hex bag`, `grave dust`
- **⚠ ZUVIEL** (3): `Tunika`, `Trank: Attributsteigerung`, `Magierpaket`

### Klerikerin ↔ CLERIC

- **🔴 FEHLT_KATALOG** (3): `20 bolts`, `two vials of holy water`, `cleric’s pack`
- **⚠ ZUVIEL** (3): `Bolzen (10)`, `Heiliges Wasser`, `Klerikerpaket`

### Krieger ↔ WARRIOR

- **🔴 FEHLT_KATALOG** (6): `20 bolts`, `potion of environmental protection`, `weighted net (Range 3/6/12, target is Entangled with successful hit, Hardness 10)`, `mercenary’s pack`, `potion of haste (ignore 2 points of MultiAction penalties for 5 rounds)`, `bronze armor and helmet (+3)`
- **⚠ ZUVIEL** (6): `Trank: Beschleunigung`, `Bolzen (10)`, `Bronzebrustpanzer`, `Bronzehelm`, `Söldnerpaket`, `Netz (beschwert)`

### Loremaster ↔ LOREMASTER

- **🔴 FEHLT_KATALOG** (9): `mage’s pack`, `scroll of mind link`, `scroll of summon ally (attendant)`, `scroll of arcane protection`, `scroll of boost Trait (Strength)`, `scroll of invisibility`, ... +3
- **⚠ ZUVIEL** (9): `Schriftrolle: Schutz`, `Buch`, `Magierpaket`, `Schriftrolle: Arkaner Schutz`, `Schriftrolle: Eigenschaft erhöhen/senken`, `Schriftrolle: Gedankenverbindung`, ... +3

### Magier ↔ MAGE

- **🔴 FEHLT_KATALOG** (4): `mage’s pack`, `Cloak of Protection (+2)`, `potion of wall walking`, `potion of healing`
- **⚠ ZUVIEL** (3): `Umhang mit Kapuze`, `Magierpaket`, `Trank: Heilung`

### Mönch ↔ MONK

- **🔴 FEHLT_KATALOG** (3): `cleric’s pack`, `Bite/claws (Str+d8)`, `potion of healing`
- **⚠ ZUVIEL** (2): `Klerikerpaket`, `Trank: Heilung`

### Narr ↔ JESTER

- **🔴 FEHLT_KATALOG** (4): `sap (Str+d4, nonlethal)`, `potion of boost Trait (Vigor)`, `entertainer’s pack`, `potion of invisibility`
- **⚠ ZUVIEL** (3): `Totschläger`, `Trank: Attributsteigerung`, `Unterhalterpaket`

### Paladin ↔ PALADIN

- **🔴 FEHLT_KATALOG** (4): `potion of environmental protection`, `cleric’s pack`, `plate mail (+3)`, `Flail (Str+d6, Ignores Shield Bonus)`
- **⚠ ZUVIEL** (2): `Klerikerpaket`, `Plattenbrustharnisch`

### Ritter ↔ KNIGHT

- **🔴 FEHLT_KATALOG** (7): `riding tack`, `20 bolts`, `mercenary’s pack`, `masterwork plate mail (+4)`, `war horse with padded barding`, `enclosed heavy helm (+4, head only, –1 to vision-based Notice rolls)`, ... +1
- **⚠ ZUVIEL** (6): `Bolzen (10)`, `Plattenbrustharnisch`, `Schwerer geschlossener Helm`, `Söldnerpaket`, `Bastardschwert`, `Reitbedarf`

### Rüpel ↔ BRUTE

- **🔴 FEHLT_KATALOG** (5): `three potions of healing`, `mercenary’s pack`, `potion of haste (ignore 2 points of Multi-Action penalties for 5 rounds)`, `heavy boots`, `enclosed heavy helm (+4, head only, –1 to vision-based Notice rolls)`
- **⚠ ZUVIEL** (3): `Stiefel, schwer`, `Schwerer geschlossener Helm`, `Söldnerpaket`

### Schamane ↔ SHAMAN

- **🔴 FEHLT_KATALOG** (2): `Fetish staff (Str+d4, Parry +1, Reach 1, Two Hands)`, `chalk of spirit warding`
- **⚠ ZUVIEL** (1): `Stab (3,5 m)`

### Verteidiger ↔ DEFENDER

- **🔴 FEHLT_KATALOG** (6): `locked gauntlets (+1 Strength roll vs. Disarm attempts)`, `armor spikes (+1 damage when Crushing or Grappling)`, `dungeoneer’s pack`, `spiked tower shield (Parry +2, Cover –4, +1 damage when attacking with shield, –1 Pace)`, `Masterwork bastard sword (Str+d8, AP 2, +1 damage if used with Two Hands)`, `two potions of healing`
- **⚠ ZUVIEL** (4): `Bolzen (10)`, `Bastardschwert`, `Großer Schild`, `Gewölbeforscherpaket`

### Waldläufer ↔ RANGER

- **🔴 FEHLT_KATALOG** (6): `masterwork scale shirt (+3, torso and arms)`, `trapmaking kit`, `3 flammable arrows`, `potion of boost Trait (Stealth)`, `potion of healing`, `masterwork composite bow (Range 12/24/48, Damage Str+d6, AP 2, RoF 1)`
- **⚠ ZUVIEL** (3): `Kompositbogen`, `Ledertunika`, `Fallenherstellungsset`

### Zauberer ↔ SORCERER

- **🔴 FEHLT_KATALOG** (6): `mage’s pack`, `potion of recharge (10 PP)`, `tunic and heavy hooded cloak (+1)`, `bag of holding`, `book`, `potion of healing`
- **⚠ ZUVIEL** (5): `Umhang mit Kapuze`, `Buch`, `Magierpaket`, `Trank: Heilung`, `Tunika`

## SciFi Kompendium (36 Chars vs. 12 Bögen)

### Ambassador ↔ AMBASSADOR

- **🔴 FEHLT_KATALOG** (2): `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `language translator`
- **⚠ ZUVIEL** (3): `Universalübersetzer`, `Waffensperre`, `Laserpistole`

### Commander ↔ COMMANDER

- **🔴 FEHLT_KATALOG** (1): `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`
- **⚠ ZUVIEL** (2): `Waffensperre`, `Laserpistole`

### Hacker ↔ HACKER

- **🔴 FEHLT_KATALOG** (4): `Kevlar jacket (+2, Torso, Arms)`, `goggles`, `language translator`, `alter wear`
- **⚠ ZUVIEL** (2): `Universalübersetzer`, `Kevlarweste`

### Infiltrator ↔ INFILTRATOR

- **🔴 FEHLT_KATALOG** (9): `Cybernetic Implants: ×2 Hidden compartment (Concealed internal space that can hold up to two pounds of objects; finding it requires close examination and a Notice roll at –4).`, `×4 stun grenade (Range 5/10/20, MBT, Stun)`, `language translator`, `directional microphone`, `electronic lockpick`, `rebreather`, ... +3
- **⚠ ZUVIEL** (6): `Direktionales Mikrofon`, `Universalübersetzer`, `Betäubungsschlagstock`, `Kreislaufatemgerät`, `EMP-Granate`, `Cyberware: Verborgenes Fach`

### Influencer ↔ INFLUENCER

- **🔴 FEHLT_KATALOG** (5): `formal clothing`, `Kevlar jacket (+2, Torso, Arms)`, `commercial drone (Pace 12, Toughness 3)`, `light slugthrower (Range 10/20/40, Damage 2d6)`, `switchblade (Str+d4)`
- **⚠ ZUVIEL** (4): `Drohne, Kommerziell`, `Kleidung, formell`, `Kevlarweste`, `Springmesser`

### Mercenary ↔ MERCENARY

- **🔴 FEHLT_KATALOG** (4): `automatic shotgun (Range 12/24/48, Damage 1–3d6, RoF 3, Shotgun)`, `muscle weave (+1 Toughness).`, `Cybernetic Implants: Adrenal surge (+2 to recover from Shaken or Stunned)`, `cybernetic eyes (Negate 4 points of illumination penalties, +2 Notice as an action)`
- **⚠ ZUVIEL** (2): `Cyberware: Verbesserte Sicht`, `Cyberware: Adrenalindrüse`

### Morpher ↔ MORPHER

- **🔴 FEHLT_KATALOG** (1): `electronic lockpick (1 minute to use Electronics d10)`

### Psyker ↔ PSYKER

- **🔴 FEHLT_KATALOG** (1): `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`
- **⚠ ZUVIEL** (2): `Waffensperre`, `Laserpistole`

### Roughneck ↔ ROUGHNECK

- **🔴 FEHLT_KATALOG** (5): `toolkit`, `claws (Str+d4 damage).`, `flashlight`, `Cybernetic Implants: Replacement arm (ignore One Arm penalties)`, `welding goggles`
- **⚠ ZUVIEL** (4): `Werkzeugkoffer`, `Cyberware: Ersatzgliedmaße`, `Taschenlampe (10" Strahl)`, `Cyberware: Klauen`

### Surveyor ↔ SURVEYOR

- **🔴 FEHLT_KATALOG** (3): `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `flashlight`, `hand axe (Str+d6)`
- **⚠ ZUVIEL** (3): `Taschenlampe (10" Strahl)`, `Waffensperre`, `Laserpistole`

---

## Zusammenfassung

| Setting | Chars | FEHLT_OFFEN (Schritt 1) | FEHLT_KATALOG (Schritt 2) |
|---|---|---|---|
| Fantasy Kompendium | 32 | **0** | **134** |
| SciFi Kompendium | 36 | **0** | **35** |
| **Gesamt** | – | **0** | **169** |

**Schritt 1 (offen):** Diese Items sind im Katalog vorhanden — Build-Skripte können sie per `s.kaufen(name)` einbauen.
**Schritt 2 (Katalog):** Diese Items fehlen im Katalog — User-Freigabe + Katalog-Erweiterung erforderlich.
