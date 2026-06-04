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

- **🟢 FEHLT_OFFEN** (1): `bandolier` (→`Bandolier`)
- **🔴 FEHLT_KATALOG** (11): `potion of haste (ignore 2 points of Multi-Action penalties for 5 rounds)`, `Masterwork staff (Str+d4, AP 1, Parry +1, Reach 1, Two Hands)`, `studded leather armor (+2)`, `eight daggers (Range 3/6/12, Damage Str+d4, RoF 1)`, `thief’s pack`, `potion of healing`, ... +5
- **⚠ ZUVIEL** (8): `Bandolier`, `Krähenfüße`, `Stab (3,5 m)`, `Peitsche`, `Ledertunika`, `Diebespaket`, ... +2

### Alchemist ↔ ALCHEMIST

- **🟢 FEHLT_OFFEN** (1): `bandolier` (→`Bandolier`)
- **🔴 FEHLT_KATALOG** (14): `alchemist’s fire (Range 3/6/12, 2d4, SBT, RoF 1, Heavy Weapon, target might catch fire)`, `goggles`, `masterwork leather tunic (+2)`, `bag of holding`, `tindertwig`, `Dagger (Str+d4)`, ... +8

### Assassinin ↔ ASSASSIN

- **🟢 FEHLT_OFFEN** (1): `bandolier` (→`Bandolier`)
- **🔴 FEHLT_KATALOG** (12): `light cloak with hood`, `10 blowgun darts`, `Dagger (Str+d4)`, `sap (Str+d4, nonlethal)`, `blowgun (Range 3/6/12, Damage d4–2, AP 1, RoF 1)`, `assassin’s brew (lethal, ingested, –2 Notice to detect)`, ... +6
- **⚠ ZUVIEL** (8): `Bandolier`, `Diebespaket`, `Ledertunika`, `Blasrohr`, `Blasrohrpfeile (20)`, `Totschläger`, ... +2

### Barbarin ↔ BARBARIAN

- **🔴 FEHLT_KATALOG** (7): `Masterwork great axe (Str+d10, AP 4, Parry –1, Two Hands)`, `heavy boots`, `hide tunic (+2, torso)`, `heavy helm (+4, head)`, `potion of growth`, `adventurer’s pack`, ... +1
- **⚠ ZUVIEL** (5): `Zweihandaxt`, `Abenteurerpaket`, `Ledertunika`, `Stiefel, schwer`, `Schwerer Helm`

### Barde ↔ BARD

- **🟢 FEHLT_OFFEN** (1): `Masterwork rapier (Str+d4, Parry +1)` (→`Rapier`)
- **🔴 FEHLT_KATALOG** (8): `cloak with hood`, `potion of boost Trait (Vigor)`, `adventurer’s lantern (lights on command, hovers near user)`, `potion of healing`, `leather tunic (+2)`, `entertainer’s pack`, ... +2
- **⚠ ZUVIEL** (8): `Rapier`, `Rauchstab`, `Ledertunika`, `Trank: Attributsteigerung`, `Unterhalterpaket`, `Laterne`, ... +2

### Champion ↔ CHAMPION

- **🔴 FEHLT_KATALOG** (6): `3 vials of holy water`, `masterwork plate mail (+4, torso, arms, legs only)`, `20 bolts`, `light crossbow (Range 10/20/40, Damage 2d6, AP 2, RoF 1, Reload 1)`, `cleric’s pack`, `Heavy mace (Str+d8, AP 1)`
- **⚠ ZUVIEL** (2): `Keule, schwer`, `Leichte Armbrust`

### Diebin ↔ THIEF

- **🟢 FEHLT_OFFEN** (1): `Masterwork rapier (Str+d4, AP 1, Parry +1)` (→`Rapier`)
- **🔴 FEHLT_KATALOG** (13): `potion of boost Trait (Strength)`, `trapmaking kit`, `hand crossbow (Range 5/10/20, Damage 2d4, RoF 1)`, `sap (Str+d4, nonlethal)`, `5x daggers (Range 3/6/12, Damage Str+d4, AP 1)`, `potion of darksight`, ... +7
- **⚠ ZUVIEL** (11): `Rapier`, `Fallenherstellungsset`, `Rauchstab`, `Diebespaket`, `Ledertunika`, `Handarmbrust`, ... +5

### Druidin ↔ DRUID

- **🟢 FEHLT_OFFEN** (1): `wilderness pack` (→`Wildnispaket`)
- **🔴 FEHLT_KATALOG** (3): `Heartwood staff (Str+d8. Parry +1, Reach 1, Two Hands)`, `potion of invisibility`, `natural armor (+2)`
- **⚠ ZUVIEL** (3): `Hemd aus natürlicher Rüstung`, `Stab (3,5 m)`, `Wildnispaket`

### Hexe ↔ WITCH

- **🔴 FEHLT_KATALOG** (7): `potion of boost Trait (Vigor)`, `two prepared powers in chicken bones`, `Dagger (Str+d4)`, `grave dust`, `hex bag`, `tunic (+1)`, ... +1
- **⚠ ZUVIEL** (4): `Magierpaket`, `Dolch`, `Trank: Attributsteigerung`, `Tunika`

### Klerikerin ↔ CLERIC

- **🔴 FEHLT_KATALOG** (6): `mithral chain shirt (+3)`, `two vials of holy water`, `Light mace (Str+d6)`, `light crossbow (Range 10/20/40, Damage 2d6, AP 2, RoF 1)`, `20 bolts`, `cleric’s pack`
- **⚠ ZUVIEL** (6): `Streitkolben, leicht`, `Heiliges Wasser`, `Leichte Armbrust`, `Klerikerpaket`, `Kettenhemd`, `Bolzen (10)`

### Krieger ↔ WARRIOR

- **🔴 FEHLT_KATALOG** (10): `mercenary’s pack`, `potion of haste (ignore 2 points of Multi- Action penalties for 5 rounds)`, `light crossbow (Range 10/20/40, Damage 2d6, AP 2, RoF 1)`, `bronze armor and helmet (+3)`, `weighted net (Range 3/6/12, target is Entangled with successful hit, Hardness 10)`, `20 bolts`, ... +4
- **⚠ ZUVIEL** (4): `Schwert, Langschwert`, `Dolch`, `Netz (beschwert)`, `Leichte Armbrust`

### Loremaster ↔ LOREMASTER

- **🔴 FEHLT_KATALOG** (11): `scroll of protection`, `scroll of boost Trait (Strength)`, `scroll of summon ally (attendant)`, `scroll of teleport`, `Masterwork dagger (Str+d4, AP 1)`, `scroll of mind link`, ... +5
- **⚠ ZUVIEL** (7): `Magierpaket`, `Buch`, `Schriftrolle: Arkaner Schutz`, `Schriftrolle: Schutz`, `Schriftrolle: Verbündeten beschwören`, `Dolch`, ... +1

### Magier ↔ MAGE

- **🟢 FEHLT_OFFEN** (1): `potion of speed` (→`Trank: Beschleunigung`)
- **🔴 FEHLT_KATALOG** (6): `Masterwork staff (Str+d4, Parry +1, Reach 1, AP 1, Two Hands)`, `dagger (Str+d4)`, `Cloak of Protection (+2)`, `potion of healing`, `potion of wall walking`, `mage’s pack`
- **⚠ ZUVIEL** (5): `Magierpaket`, `Stab (3,5 m)`, `Umhang mit Kapuze`, `Dolch`, `Trank: Heilung`

### Mönch ↔ MONK

- **🟢 FEHLT_OFFEN** (1): `masterwork meteor hammer (Str+d6, AP 1, Reach 2, Ignore Shield Bonus, Two Hands)` (→`Hammer`)
- **🔴 FEHLT_KATALOG** (5): `knife (Str+d4, Range 3/6/12)`, `cloth tunic (+1)`, `cleric’s pack`, `Bite/claws (Str+d8)`, `potion of healing`
- **⚠ ZUVIEL** (4): `Klerikerpaket`, `Dolch`, `Meteorhammer`, `Tunika`

### Narr ↔ JESTER

- **🔴 FEHLT_KATALOG** (6): `potion of boost Trait (Vigor)`, `Masterwork knife (Range 3/6/12, Damage Str+d4, AP 1, RoF 1, Parry +1)`, `sap (Str+d4, nonlethal)`, `leather tunic (+2)`, `potion of invisibility`, `entertainer’s pack`
- **⚠ ZUVIEL** (5): `Dolch/Messer`, `Ledertunika`, `Trank: Attributsteigerung`, `Unterhalterpaket`, `Totschläger`

### Paladin ↔ PALADIN

- **🟢 FEHLT_OFFEN** (1): `holy water` (→`Heiliges Wasser`)
- **🔴 FEHLT_KATALOG** (5): `Flail (Str+d6, Ignores Shield Bonus)`, `plate mail (+3)`, `medium shield (Parry +2, Cover –2)`, `cleric’s pack`, `potion of environmental protection`
- **⚠ ZUVIEL** (2): `Mittlerer Schild`, `Streitflegel`

### Ritter ↔ KNIGHT

- **🔴 FEHLT_KATALOG** (10): `lance (Str+d8, AP 2 when charging, Reach 2, mounted combat only)`, `mercenary’s pack`, `heavy crossbow (Range 15/30/60, Damage 2d8, AP 2, RoF 1, Reload 2)`, `medium shield (Parry +2, Cover –2)`, `20 bolts`, `enclosed heavy helm (+4, head only, –1 to vision-based Notice rolls)`, ... +4
- **⚠ ZUVIEL** (3): `Schwere Armbrust`, `Bastardschwert`, `Lanze`

### Rüpel ↔ BRUTE

- **🟢 FEHLT_OFFEN** (1): `spiked chain (Str+d6, AP 1, ignores shield bonus, Two Hands)` (→`Pike`)
- **🔴 FEHLT_KATALOG** (8): `three potions of healing`, `mercenary’s pack`, `potion of haste (ignore 2 points of Multi-Action penalties for 5 rounds)`, `heavy boots`, `medium shield (Parry +2, Cover –2)`, `enclosed heavy helm (+4, head only, –1 to vision-based Notice rolls)`, ... +2
- **⚠ ZUVIEL** (7): `Morgenstern`, `Stiefel, schwer`, `Stachelkette`, `Mittlerer Schild`, `Schwerer geschlossener Helm`, `Söldnerpaket`, ... +1

### Schamane ↔ SHAMAN

- **🟢 FEHLT_OFFEN** (1): `wilderness pack` (→`Wildnispaket`)
- **🔴 FEHLT_KATALOG** (4): `chalk of spirit warding`, `light leather tunic (+1)`, `dagger (Str+d4)`, `Fetish staff (Str+d4, Parry +1, Reach 1, Two Hands)`
- **⚠ ZUVIEL** (4): `Stab (3,5 m)`, `Wildnispaket`, `Ledertunika`, `Dolch`

### Verteidiger ↔ DEFENDER

- **🟢 FEHLT_OFFEN** (2): `armor spikes (+1 damage when Crushing or Grappling)` (→`Pike`), `spiked tower shield (Parry +2, Cover –4, +1 damage when attacking with shield, –1 Pace)` (→`Pike`)
- **🔴 FEHLT_KATALOG** (5): `masterwork heavy crossbow (Range 15/30/60, Damage 2d8, AP 3, RoF 1, Reload 2)`, `dungeoneer’s pack`, `Masterwork bastard sword (Str+d8, AP 2, +1 damage if used with Two Hands)`, `locked gauntlets (+1 Strength roll vs. Disarm attempts)`, `two potions of healing`
- **⚠ ZUVIEL** (5): `Großer Schild`, `Schwere Armbrust`, `Bastardschwert`, `Bolzen (10)`, `Gewölbeforscherpaket`

### Waldläufer ↔ RANGER

- **🟢 FEHLT_OFFEN** (2): `wilderness pack` (→`Wildnispaket`), `potion of speed` (→`Trank: Beschleunigung`)
- **🔴 FEHLT_KATALOG** (8): `trapmaking kit`, `masterwork composite bow (Range 12/24/48, Damage Str+d6, AP 2, RoF 1)`, `Hand axe (Str+d6)`, `potion of boost Trait (Stealth)`, `masterwork scale shirt (+3, torso and arms)`, `30 arrows`, ... +2
- **⚠ ZUVIEL** (6): `Handaxt`, `Fallenherstellungsset`, `Ledertunika`, `Kompositbogen`, `Pfeile (20)`, `Wildnispaket`

### Zauberer ↔ SORCERER

- **🔴 FEHLT_KATALOG** (7): `potion of recharge (10 PP)`, `mage’s pack`, `bag of holding`, `tunic and heavy hooded cloak (+1)`, `potion of healing`, `Dark metal dagger (Str+d4, AP 1, –2 Vigor to Soak)`, ... +1
- **⚠ ZUVIEL** (6): `Magierpaket`, `Buch`, `Dolch`, `Umhang mit Kapuze`, `Tunika`, `Trank: Heilung`

## SciFi Kompendium (36 Chars vs. 12 Bögen)

### Ambassador ↔ AMBASSADOR

- **🟢 FEHLT_OFFEN** (3): `personal data device` (→`Persönliche Datenassistenz`), `universal battery` (→`Batterie, Universal-`), `biolink` (→`Biolink`)
- **🔴 FEHLT_KATALOG** (3): `language translator`, `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `Body armor (+4, –4 bullet damage, Torso, Arms, Legs)`
- **⚠ ZUVIEL** (6): `Batterie, Universal-`, `Infanteriekampfanzug`, `Laserpistole`, `Taschencomputer`, `Waffensperre`, `Universalübersetzer`

### Commander ↔ COMMANDER

- **🟢 FEHLT_OFFEN** (3): `personal data device` (→`Persönliche Datenassistenz`), `universal battery` (→`Batterie, Universal-`), `biolink` (→`Biolink`)
- **🔴 FEHLT_KATALOG** (3): `molecular knife (Str+d4+2, AP 2)`, `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `Body armor (+4, –4 bullet damage, Torso, Arms, Legs)`
- **⚠ ZUVIEL** (6): `Batterie, Universal-`, `Infanteriekampfanzug`, `Molekularmesser`, `Laserpistole`, `Taschencomputer`, `Waffensperre`

### Hacker ↔ HACKER

- **🟢 FEHLT_OFFEN** (4): `personal data device` (→`Persönliche Datenassistenz`), `cyberdeck` (→`Cyberdeck`), `commlink (50)` (→`Commlink`), `backpack` (→`Rucksack`)
- **🔴 FEHLT_KATALOG** (4): `goggles`, `language translator`, `Kevlar jacket (+2, Torso, Arms)`, `alter wear`
- **⚠ ZUVIEL** (5): `Rucksack`, `Taschencomputer`, `Cyberdeck`, `Universalübersetzer`, `Kevlarweste`

### Infiltrator ↔ INFILTRATOR

- **🟢 FEHLT_OFFEN** (3): `personal data device` (→`Persönliche Datenassistenz`), `camouflage suit` (→`Tarnanzug`), `cyberdeck` (→`Cyberdeck`)
- **🔴 FEHLT_KATALOG** (11): `line projector`, `language translator`, `stun baton (Str+d4, Non- Lethal, Stun)`, `rebreather`, `Cybernetic Implants: ×2 Hidden compartment (Concealed internal space that can hold up to two pounds of objects; finding it requires close examination and a Notice roll at –4).`, `×4 stun grenade (Range 5/10/20, MBT, Stun)`, ... +5
- **⚠ ZUVIEL** (11): `Molekularschwert`, `Infanteriekampfanzug`, `Tarnkleidung`, `Direktionales Mikrofon`, `Kreislaufatemgerät`, `Taschencomputer`, ... +5

### Influencer ↔ INFLUENCER

- **🟢 FEHLT_OFFEN** (1): `personal data device` (→`Persönliche Datenassistenz`)
- **🔴 FEHLT_KATALOG** (5): `switchblade (Str+d4)`, `Kevlar jacket (+2, Torso, Arms)`, `commercial drone (Pace 12, Toughness 3)`, `formal clothing`, `light slugthrower (Range 10/20/40, Damage 2d6)`
- **⚠ ZUVIEL** (5): `Kevlarweste`, `Taschencomputer`, `Springmesser`, `Kleidung, formell`, `Drohne, Kommerziell`

### Mercenary ↔ MERCENARY

- **🟢 FEHLT_OFFEN** (2): `commlink` (→`Commlink`), `personal data device` (→`Persönliche Datenassistenz`)
- **🔴 FEHLT_KATALOG** (6): `automatic shotgun (Range 12/24/48, Damage 1–3d6, RoF 3, Shotgun)`, `muscle weave (+1 Toughness).`, `Cybernetic Implants: Adrenal surge (+2 to recover from Shaken or Stunned)`, `molecular sword (Str+d8+2, AP 4)`, `cybernetic eyes (Negate 4 points of illumination penalties, +2 Notice as an action)`, `Body armor (+4, –4 bullet damage, Body, Arms, Legs)`
- **⚠ ZUVIEL** (6): `Molekularschwert`, `Cyberware: Adrenalindrüse`, `Infanteriekampfanzug`, `Taschencomputer`, `Komlink`, `Cyberware: Verbesserte Sicht`

### Morpher ↔ MORPHER

- **🟢 FEHLT_OFFEN** (3): `commlink` (→`Commlink`), `personal data device` (→`Persönliche Datenassistenz`), `nanowear` (→`Nanowear`)
- **🔴 FEHLT_KATALOG** (2): `electronic lockpick (1 minute to use Electronics d10)`, `Laser pistol (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`
- **⚠ ZUVIEL** (4): `Nanowear`, `Laserpistole`, `Taschencomputer`, `Komlink`

### Mystic ↔ MYSTIC

- **🟢 FEHLT_OFFEN** (1): `personal data device` (→`Persönliche Datenassistenz`)
- **🔴 FEHLT_KATALOG** (2): `2× universal battery`, `Plasma rifle (Range 10/20/40, 2d10, Cauterize, Heavy Weapon, Plasma)`
- **⚠ ZUVIEL** (3): `Batterie, Universal-`, `Plasmagewehr`, `Taschencomputer`

### Psyker ↔ PSYKER

- **🟢 FEHLT_OFFEN** (4): `personal data device` (→`Persönliche Datenassistenz`), `universal battery` (→`Batterie, Universal-`), `Scanner (25"/50 yards)` (→`Scanner`), `biolink` (→`Biolink`)
- **🔴 FEHLT_KATALOG** (2): `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `Body armor (+4, –4 bullet damage, Torso, Arms, Legs)`
- **⚠ ZUVIEL** (6): `Batterie, Universal-`, `Infanteriekampfanzug`, `Laserpistole`, `Taschencomputer`, `Waffensperre`, `Scanner`

### Roughneck ↔ ROUGHNECK

- **🟢 FEHLT_OFFEN** (3): `personal data device` (→`Persönliche Datenassistenz`), `universal battery` (→`Batterie, Universal-`), `backpack` (→`Rucksack`)
- **🔴 FEHLT_KATALOG** (7): `plasma pistol (Range 5/10/20, 2d10, Cauterize, Heavy Weapon, Plasma)`, `claws (Str+d4 damage).`, `toolkit`, `Cybernetic Implants: Replacement arm (ignore One Arm penalties)`, `flashlight`, `welding goggles`, ... +1
- **⚠ ZUVIEL** (8): `Batterie, Universal-`, `Infanteriekampfanzug`, `Rucksack`, `Taschencomputer`, `Cyberware: Klauen`, `Werkzeugkoffer`, ... +2

### Spacer ↔ SPACER

- **🟢 FEHLT_OFFEN** (2): `commlink` (→`Commlink`), `universal battery` (→`Batterie, Universal-`)
- **🔴 FEHLT_KATALOG** (6): `heavy blaster pistol (Range 10/20/40, 3d6, AP 2)`, `×3 adhesive patches`, `red dot sight (+1 to Shooting at Short/Medium range)`, `molecular knife (Str+d4+2, AP 2)`, `spacesuit (+1, Sealed)`, `Body armor (+4, –4 bullet damage, Torso, Arms, Legs)`
- **⚠ ZUVIEL** (8): `Batterie, Universal-`, `Infanteriekampfanzug`, `Molekularmesser`, `Raumanzug`, `Schwere Blasterpistole`, `Komlink`, ... +2

### Surveyor ↔ SURVEYOR

- **🟢 FEHLT_OFFEN** (4): `×2 medi-gel (+2 Healing to stabilize or within the Golden Hour)` (→`Medi-Gel`), `universal battery` (→`Batterie, Universal-`), `backpack` (→`Rucksack`), `scanner (25"/50 yards)` (→`Scanner`)
- **🔴 FEHLT_KATALOG** (5): `hand axe (Str+d6)`, `flashlight`, `laser pistol with weapon lock (Range 15/30/60, Damage 2d6, AP 2, Cauterize, Overcharge)`, `Body armor (+4, –4 bullet damage, Torso, Arms, Legs)`, `environment wear (Negate Vigor rolls for hot or cold climate)`
- **⚠ ZUVIEL** (9): `Batterie, Universal-`, `Infanteriekampfanzug`, `Rucksack`, `Laserpistole`, `Waffensperre`, `Medi-Gel`, ... +3

---

## Zusammenfassung

| Setting | Chars | FEHLT_OFFEN (Schritt 1) | FEHLT_KATALOG (Schritt 2) |
|---|---|---|---|
| Fantasy Kompendium | 32 | **15** | **172** |
| SciFi Kompendium | 36 | **33** | **56** |
| **Gesamt** | – | **48** | **228** |

**Schritt 1 (offen):** Diese Items sind im Katalog vorhanden — Build-Skripte können sie per `s.kaufen(name)` einbauen.
**Schritt 2 (Katalog):** Diese Items fehlen im Katalog — User-Freigabe + Katalog-Erweiterung erforderlich.
