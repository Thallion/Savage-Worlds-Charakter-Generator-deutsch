# Plan: Android-Performance-Optimierung

## Context

Die App läuft auf Desktop flüssig, fühlt sich auf Android aber träge an. Ursachen laut Code-Analyse:

- **Startup** blockiert ~1–2 s: Alle 13 Screens + 10 Services werden synchron instanziiert, kein Presplash sichtbar.
- **UI-Rendering** wird bei jeder Änderung verworfen und neu gebaut — besonders `CharakterbogenWidget.update_overview()` zerstört 80–150 Widgets pro Refresh.
- **Android-spezifische Risiken**: `threading.Thread` in `html_manager.py` kann auf Android crashen (kein Looper), Backup-ZIP läuft synchron im Main-Thread.
- **Cascading `Clock.schedule_once`-Ketten** (z. B. `volk_funktionen.py` 0.05s + 0.2s + 0.1s) summieren sich zu sichtbarem Lag.
- **Keine Profiling-Infrastruktur** — ohne Messpunkte ist Optimierung Raten.

Ziel: Messbar schnellerer Kaltstart, flüssigere Tab-Wechsel, kein Freeze bei Charakter-Updates, keine Thread-Crashes auf Android. Änderungen sollen Desktop-Verhalten nicht verschlechtern.

**Vorgehen:** Wir arbeiten diesen Plan Schritt für Schritt ab. Jeder Schritt wird einzeln implementiert, getestet und bestätigt, bevor der nächste begonnen wird. **Jeder Schritt bekommt einen eigenen PR** und — wo sinnvoll — passendes Logging sowie einen Unit-Test.

---

## Checkliste

- [x] **Schritt 1** — Presplash in `buildozer.spec` aktivieren
- [x] **Schritt 2** — Tab-Screens lazy instanziieren (`main.py`)
- [ ] **Schritt 3** — Nicht-kritische Services lazy (`service_container.py`)
- [ ] **Schritt 4** — `BackupService` in Hintergrund-Thread
- [ ] **Schritt 5** — `threading.Thread`-Gebrauch für Android absichern
- [ ] **Schritt 6** — `Clock.schedule_once`-Ketten konsolidieren
- [ ] **Schritt 7** — `CharakterbogenWidget` Update-in-Place
- [ ] **Schritt 8** — Dialog-Wiederverwendung
- [ ] **Schritt 9** — Binding-Lifecycle prüfen
- [ ] **Schritt 10** — Theme-Color-Caching
- [ ] **Schritt 11** — Debug-Build-Profil arm64-only
- [ ] **Schritt 12** — `no-byte-compile-python` prüfen
- [ ] **Schritt 13** — Release-Logging-Level reduzieren
- [ ] **Schritt 14** — Startup-Timing-Logs in `main.py`
- [ ] **Schritt 15** — On-Device-Profiling

---

## Prioritäten

**P0 = sofort / hoher Impact · P1 = mittelfristig · P2 = Feinschliff**

---

## P0 — Startup sichtbar beschleunigen

### 1. Presplash aktivieren (`buildozer.spec:52, 89`)
Aktuell: blanker schwarzer Screen für 1–2 s.
- `presplash.filename = %(source.dir)s/assets/icon_512.png` oder dediziertes Presplash-PNG
- `android.presplash_color = #FFFFFF` (oder Theme-Farbe)
- Kein Code-Change nötig — rein Config.

### 2. Tab-Screens lazy instanziieren (`main.py:889–936`, `views/screens.py`)
Aktuell: `build_tabs_and_screens_immediate()` baut alle 13 Screens bei `on_start`. Nur Tab 0 ist sofort sichtbar.
- Tabs als leere `Screen`-Hüllen registrieren, Content (`EinstellungenWidget`, `VoelkerWidget`, …) erst beim ersten Tab-Switch instanziieren.
- Hook: Kivy `ScreenManager.current` bzw. `MDTabsPrimary.on_tab_switch` → Lazy-Init-Flag pro Screen.
- Erwarteter Gewinn: ~400–600 ms Startup auf Android.

### 3. Nicht-kritische Services verzögern (`services/service_container.py:44–82`)
- `BackupService` (synchrones ZIP, blockt), `TutorialService`, `HTMLService`, `PDFService` erst bei erstem Gebrauch initialisieren (Lazy-Property im `ServiceContainer`).
- Kernservices bleiben eager: `ConfigService`, `EventService`, `ThemeService`, `DialogService`.

### 4. `BackupService` Hintergrund-Init (`services/backup_service.py:40–80`)
- Backup-Durchlauf (ZIP + Hash-Check) in `threading.Thread` nach App-Ready, nicht im `__init__`.
- Wichtig: I/O-Thread OK auf Android, nur JVM-/UI-Calls müssen auf UI-Thread.

---

## P0 — Android-spezifische Risiken beheben

### 5. `threading.Thread`-Gebrauch für Android absichern
Kritische Stellen:
- `manager/html_manager.py:483–529` — HTTP-Server-Thread. Auf Android prüfen und deaktivieren bzw. über `Clock`-basierten Scheduler ersetzen (Android-Print-Path nutzt ohnehin `android_print_utils.py`).
- `views/eigenschaften_view.py:10, 242, 530` — Hintergrund-Loader. Wenn keine JNI-Calls → OK, sonst auf `Clock.schedule_once` umstellen.
- `views/screens.py:336` — Update-Check-Daemon. Auf Android überspringen (Play-Store-Policy verbietet externe Update-Checks ohnehin).
- Pattern: `if platform == 'android': Clock.schedule_once(...) else: Thread(...)`.

### 6. `Clock.schedule_once`-Ketten konsolidieren
- `functions/volk_funktionen.py` — kaskadierte 0.05+0.2+0.1 s-Delays auf eine einzige `schedule_once(..., 0)` mit sequenzieller Logik reduzieren.
- `controllers/template_handler.py:36–37` — Template-Load nur triggern, wenn Template-Dialog erstmals geöffnet wird (komplett rauswerfen aus `__init__`).

---

## P1 — Rendering-Hotspots entschärfen

### 7. `CharakterbogenWidget` — Update-in-Place (`views/charakterbogen_view.py:194–217`)
Aktuell: 12 `_update_*_section()` rufen `clear_widgets()` + Rebuild (80–150 Widgets pro Refresh).
- Labels einmal anlegen, per Kivy-Binding an `Charakter`-Properties koppeln → nur Textinhalt ändert sich.
- Für dynamische Listen (Talente, Waffen): `RecycleView` wie in `talente_view.py:107–125` nutzen (Pattern existiert bereits).
- Betroffene Methoden: `_update_profil_section` (230), `_update_attribute_section` (331), `_update_fertigkeiten_section` (358), …
- Alternative (minimal-invasiv): Debounce per `Clock.schedule_once(update, 0)` gegen mehrfache Updates pro Frame.

### 8. Dialog-Wiederverwendung
- Häufig wiederkehrende Dialoge (z. B. `talente_view.py:255–349` Pathfinder-Kostenlos-Dialog, `ausruestung_view.py:244–387`) einmal als `self._xxx_dialog` cachen, nur Inhalt aktualisieren.
- Nicht wiederverwendbar: Dialoge mit dynamischer Struktur (Setting-Assistent) — unverändert lassen.

### 9. Binding-Lifecycle (`views/` — 257 `.bind()`-Calls)
- In Screens mit `on_enter`/`on_leave` prüfen, ob Bindings beim Verlassen explizit entfernt werden sollten (Memory-Leak + CPU-Overhead über Session).
- Fokus: `views/pointbar_view.py` (30+ Bindings), `charakterbogen_view.py`.
- Pragmatisch: nur dort anfassen, wo ein Profiler erhöhten CPU-Verbrauch zeigt.

### 10. Theme-Color-Caching
- `views/talente_view.py:664–676`, `handicaps_view.py:682–706`, `ausruestung_view.py:87–109`: `_get_background_color()` fragt pro ListItem `theme_cls` ab.
- Farben bei Theme-Wechsel cachen (via `EventService.on_theme_changed`), nicht pro `on_index`.

---

## P1 — Build- und APK-Optimierung

### 11. Debug-Builds schlanker (`buildozer.spec:298`)
- Neues Profil `[app@debug] android.archs = arm64-v8a` (nur 64-Bit für Tests).
- Release-Build bleibt `arm64-v8a, armeabi-v7a` für Play Store.
- Nutzen: ~50 % kleinere APK, schnellere Build-Iteration.

### 12. `android.no-byte-compile-python = True` prüfen
- Setzt voraus: `*.pyc` wird im APK mitgeliefert — schnellerer Import-Pfad beim Start.
- Testen, ob p4a das korrekt handhabt (nicht alle Versionen tun es).

### 13. Logging-Level in Release reduzieren
- `utils/logging_setup.py` — in Release-Builds standardmäßig `WARNING` statt `DEBUG`/`INFO`.
- Laufzeit-Gewinn klein, aber Log-I/O ist auf langsamen Android-Speichern spürbar.

---

## P2 — Profiling & Messbarkeit

### 14. Startup-Timing-Logs
- In `main.py` an 5–6 Schlüsselstellen `time.monotonic()`-Deltas loggen: Import-Ende, `build()`, Services init, Tab-Registrierung, `on_start`-Ende, erstes Frame.
- Einmalig per `adb logcat -s python` auslesen → Hotspots identifizieren, bevor P1-Rendering-Arbeiten starten.

### 15. On-Device-Profiling-Checkliste
- `adb shell dumpsys gfxinfo com.github.thallion.savageworlds` → Frame-Times
- `adb logcat | grep -i "choreographer"` → Skipped Frames
- Vorher/Nachher-Vergleich auf mindestens einem Low-End-Gerät (z. B. Android 9, 3 GB RAM).

---

## Kritische Dateien

| Datei | Zweck |
|---|---|
| `buildozer.spec` | Presplash, Arch-Split, Build-Profile |
| `main.py` (889–936) | Tab-/Screen-Registrierung → lazy |
| `services/service_container.py` (44–82) | Lazy-Services |
| `services/backup_service.py` (40–80) | Backup in Thread |
| `manager/html_manager.py` (483–529) | Thread-Guard für Android |
| `views/charakterbogen_view.py` (194–386) | Update-in-Place |
| `functions/volk_funktionen.py` | Clock-Kaskaden konsolidieren |
| `controllers/template_handler.py` (36–37) | Template-Load weiter verzögern |

**Wiederverwendbare existierende Patterns:**
- `views/talente_view.py:107–125` → `MDRecycleView` als Referenz für Charakterbogen-Listen
- `utils/platform_utils.py:14, 40–74` → bereits vorhandenes `_mobile_layout_cache`
- `utils/android_print_utils.py` → korrektes UI-Thread-Handling als Vorlage für Thread-Guards

---

## Verifikation pro Schritt

Für jeden einzelnen Schritt:

1. Änderung implementieren.
2. `python "test units/run_all_tests.py"` grün.
3. Desktop-Smoke-Test: `python main.py` startet, relevanter Flow funktioniert.
4. Git-Commit mit klarem Message (`perf(android): step X — …`).
5. User bestätigt → nächster Schritt.

## Gesamt-Verifikation nach Abschluss

1. **Startup-Messung** (vor/nach P0): `adb logcat -s python:I` — Zeit von `on_start` bis erstes Frame auf Testgerät. Ziel: −30 % (≈ 1.5 s → 1 s).
2. **Tab-Wechsel**: Manuell durch alle 13 Tabs swipen, auf Ruckler achten. Ziel: < 100 ms Verzögerung bis Content sichtbar.
3. **Charakter-Bogen-Stress**: Bestehenden Charakter laden (`test units/test_hesindian_magier.py`-Fixture), Attribut ändern, Refresh-Zeit des Charakterbogens mit `time.monotonic()` messen. Ziel: < 50 ms.
4. **Thread-Safety**: App auf Android Device starten, HTML-Export + Share-Intent + Backup parallel triggern — kein JVM-Crash im logcat.
5. **Regression-Tests**: `python "test units/run_all_tests.py"` — alle bestehenden Tests müssen grün bleiben.
6. **APK-Größen-Diff**: `ls -la bin/*.aab` vor/nach — sollte nicht wachsen (P1-Build-Profil sogar kleiner).

---

## Nicht im Scope

- Komplett-Umstellung auf neues UI-Framework.
- Migration weg von KivyMD 2.0.1 master.
- Python-Version-Downgrade (3.11 → 3.10) — wäre Nutzen/Risiko-grenzwertig, separat evaluieren.
- Kompression der Setting-JSONs (3.1 MB gesamt — Plattengröße, nicht Runtime).
