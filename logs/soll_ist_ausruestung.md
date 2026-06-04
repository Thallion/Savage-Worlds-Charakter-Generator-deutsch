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

- **🔴 FEHLT_KATALOG** (1): `potion of wall walking`
- **⚠ ZUVIEL** (1): `Trank: Geistige Stärke`

### Alchemist ↔ ALCHEMIST

- **🔴 FEHLT_KATALOG** (4): `bag of holding`, `goggles`, `sunrod`, `potion of environmental protection`

### Barbarin ↔ BARBARIAN

- **🔴 FEHLT_KATALOG** (1): `potion of growth`

### Barde ↔ BARD

- **🔴 FEHLT_KATALOG** (1): `adventurer’s lantern (lights on command, hovers near user)`

### Diebin ↔ THIEF

- **🔴 FEHLT_KATALOG** (2): `potion of darksight`, `potion of invisibility`

### Druidin ↔ DRUID

- **🔴 FEHLT_KATALOG** (1): `potion of invisibility`

### Hexe ↔ WITCH

- **🔴 FEHLT_KATALOG** (3): `two prepared powers in chicken bones`, `grave dust`, `hex bag`

### Krieger ↔ WARRIOR

- **🔴 FEHLT_KATALOG** (1): `potion of environmental protection`
- **⚠ ZUVIEL** (1): `Bronzehelm`

### Magier ↔ MAGE

- **🔴 FEHLT_KATALOG** (2): `Cloak of Protection (+2)`, `potion of wall walking`
- **⚠ ZUVIEL** (1): `Umhang mit Kapuze`

### Mönch ↔ MONK

- **🔴 FEHLT_KATALOG** (1): `Bite/claws (Str+d8)`

### Narr ↔ JESTER

- **🔴 FEHLT_KATALOG** (1): `potion of invisibility`

### Paladin ↔ PALADIN

- **🔴 FEHLT_KATALOG** (1): `potion of environmental protection`

### Ritter ↔ KNIGHT

- **🔴 FEHLT_KATALOG** (1): `war horse with padded barding`

### Verteidiger ↔ DEFENDER

- **⚠ ZUVIEL** (1): `Bolzen (10)`

### Waldläufer ↔ RANGER

- **⚠ ZUVIEL** (1): `Ledertunika`

### Zauberer ↔ SORCERER

- **🔴 FEHLT_KATALOG** (2): `bag of holding`, `potion of recharge (10 PP)`
- **⚠ ZUVIEL** (1): `Umhang mit Kapuze`

## SciFi Kompendium (36 Chars vs. 12 Bögen)

### Ambassador ↔ AMBASSADOR

- **⚠ ZUVIEL** (1): `Waffensperre`

### Commander ↔ COMMANDER

- **⚠ ZUVIEL** (1): `Waffensperre`

### Hacker ↔ HACKER

- **🔴 FEHLT_KATALOG** (1): `alter wear`

### Infiltrator ↔ INFILTRATOR

- **🔴 FEHLT_KATALOG** (2): `line projector`, `Cybernetic Implants: ×2 Hidden compartment (Concealed internal space that can hold up to two pounds of objects; finding it requires close examination and a Notice roll at –4).`
- **⚠ ZUVIEL** (1): `Cyberware: Verborgenes Fach`

### Influencer ↔ INFLUENCER

- **🔴 FEHLT_KATALOG** (1): `light slugthrower (Range 10/20/40, Damage 2d6)`

### Mercenary ↔ MERCENARY

- **🔴 FEHLT_KATALOG** (2): `muscle weave (+1 Toughness).`, `Cybernetic Implants: Adrenal surge (+2 to recover from Shaken or Stunned)`
- **⚠ ZUVIEL** (1): `Cyberware: Adrenalindrüse`

### Psyker ↔ PSYKER

- **⚠ ZUVIEL** (1): `Waffensperre`

### Roughneck ↔ ROUGHNECK

- **🔴 FEHLT_KATALOG** (1): `Cybernetic Implants: Replacement arm (ignore One Arm penalties)`
- **⚠ ZUVIEL** (1): `Cyberware: Ersatzgliedmaße`

### Surveyor ↔ SURVEYOR

- **⚠ ZUVIEL** (1): `Waffensperre`

---

## Zusammenfassung

| Setting | Chars | FEHLT_OFFEN (Schritt 1) | FEHLT_KATALOG (Schritt 2) |
|---|---|---|---|
| Fantasy Kompendium | 32 | **0** | **22** |
| SciFi Kompendium | 36 | **0** | **7** |
| **Gesamt** | – | **0** | **29** |

**Schritt 1 (offen):** Diese Items sind im Katalog vorhanden — Build-Skripte können sie per `s.kaufen(name)` einbauen.
**Schritt 2 (Katalog):** Diese Items fehlen im Katalog — User-Freigabe + Katalog-Erweiterung erforderlich.
