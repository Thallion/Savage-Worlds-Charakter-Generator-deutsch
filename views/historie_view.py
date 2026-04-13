"""
historie_view.py: Widget für die Anzeige der Charakter-Historie und Logs.
Orientiert sich am Auto Character Generator Log-System.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty

from utils.platform_utils import is_mobile_layout

_mobile = is_mobile_layout()

from kivymd.uix.boxlayout import MDBoxLayout

from services.service_container import service_container


# PyInstaller-kompatibles Laden der KV-Datei (mit Mobile-Unterstützung)
def load_kv_file():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))

    kv_name = 'historie_view_mobile.kv' if _mobile else 'historie_view.kv'
    kv_path = os.path.join(base_path, 'views', kv_name)

    # Fallback auf Desktop-KV wenn Mobile-KV nicht existiert
    if not os.path.exists(kv_path):
        kv_path = os.path.join(base_path, 'views', 'historie_view.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
        Logger.info(f"historie_view: KV-Datei geladen: {os.path.basename(kv_path)}")
    else:
        Logger.error(f"historie_view: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()


class CharakterHistorie:
    """
    Klasse zur Verwaltung der Charakter-Historie.
    Speichert alle Änderungen und Steigerungen eines Charakters.
    """
    
    def __init__(self):
        self.entries = []
        self.session_start = datetime.now()
    
    def add_entry(self, entry_type: str, details: Dict[str, Any], rang: str = "") -> None:
        """
        Fügt einen neuen Eintrag zur Historie hinzu.

        Args:
            entry_type: Art der Änderung (attribut_steigerung, fertigkeit_steigerung, etc.)
            details: Details zur Änderung
            rang: Aktueller Rang des Charakters (z.B. "Anfänger", "Veteran")
        """
        current_time = datetime.now()
        timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Prüfe auf Duplikate (gleicher Typ, Name und Zeitstempel innerhalb von 2 Sekunden)
        for existing_entry in reversed(self.entries[-5:]):  # Prüfe nur die letzten 5 Einträge
            if (existing_entry['type'] == entry_type and 
                existing_entry['details'].get('name') == details.get('name')):
                
                # Parse existierenden Zeitstempel
                existing_time = datetime.strptime(existing_entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                time_diff = abs((current_time - existing_time).total_seconds())
                
                # Wenn innerhalb von 2 Sekunden und gleiche Werte, ignoriere als Duplikat
                if time_diff <= 2:
                    if entry_type in ['attribut_steigerung', 'fertigkeit_steigerung']:
                        if (existing_entry['details'].get('von') == details.get('von') and
                            existing_entry['details'].get('nach') == details.get('nach')):
                            Logger.debug(f"Duplikat ignoriert: {entry_type} - {details.get('name')} (Zeitdiff: {time_diff}s)")
                            return
                    elif entry_type in ['talent_hinzugefuegt', 'handicap_hinzugefuegt', 'macht_hinzugefuegt']:
                        Logger.debug(f"Duplikat ignoriert: {entry_type} - {details.get('name')} (Zeitdiff: {time_diff}s)")
                        return
        
        entry = {
            'timestamp': timestamp_str,
            'type': entry_type,
            'rang': rang,
            'details': details
        }
        self.entries.append(entry)
    
    def get_formatted_log(self) -> str:
        """
        Gibt die Historie als formatierten String zurück.
        
        Returns:
            Formatierter Log-String
        """
        log_lines = []
        log_lines.append("=" * 80)
        log_lines.append("CHARAKTER-HISTORIE")
        log_lines.append(f"Session gestartet: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        log_lines.append("=" * 80)
        log_lines.append("")
        
        # Gruppiere Einträge nach Typ
        grouped = {}
        for entry in self.entries:
            entry_type = entry['type']
            if entry_type not in grouped:
                grouped[entry_type] = []
            grouped[entry_type].append(entry)
        
        # Zeige gruppierte Einträge
        for entry_type, entries in grouped.items():
            log_lines.append(f"\n{entry_type.upper().replace('_', ' ')}:")
            log_lines.append("-" * 40)
            
            for entry in entries:
                details = entry['details']
                timestamp = entry['timestamp']
                rang_text = f" [{entry['rang']}]" if entry.get('rang') else ""

                if entry_type == 'attribut_steigerung':
                    kosten_typ = details.get('kosten_typ', 'Punkte')
                    kosten = details['kosten']
                    
                    # Korrekte Aufstiegs-Darstellung: 1 Attributsteigerung = 1 Aufstieg
                    if 'aufstieg' in kosten_typ.lower():
                        kosten_text = f"1 Aufstieg"
                    elif 'handicap' in kosten_typ.lower():
                        kosten_text = f"2 Handicap-Punkte"  # Attribut kostet immer 2 Handicap-Punkte
                    else:
                        kosten_text = f"{kosten} {kosten_typ}"
                        
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']}: W{details['von']} → W{details['nach']} ({kosten_text})")

                elif entry_type == 'fertigkeit_steigerung':
                    kosten_typ = details.get('kosten_typ', 'Punkte')
                    kosten = details['kosten']
                    
                    # Korrekte Aufstiegs-Darstellung basierend auf tatsächlichen Kosten
                    if 'aufstieg' in kosten_typ.lower():
                        if kosten == 1:
                            kosten_text = f"1 Aufstieg"  # Fertigkeit über Attribut
                        else:
                            kosten_text = f"0.5 Aufstiege"  # Normale Fertigkeit
                    else:
                        kosten_text = f"{kosten} {kosten_typ}"
                        
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']}: W{details['von']} → W{details['nach']} ({kosten_text})")
                elif entry_type == 'talent_hinzugefuegt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} (Kosten: {details.get('kosten', 0)})")
                elif entry_type == 'talent_entfernt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} entfernt")
                elif entry_type == 'handicap_hinzugefuegt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} ({details.get('stufe', '')} - Punkte: {details.get('punkte', 0)})")
                elif entry_type == 'handicap_entfernt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} entfernt")
                elif entry_type == 'handicap_reduziert':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} von schwer zu leicht reduziert")
                elif entry_type == 'macht_hinzugefuegt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} (Rang: {details.get('rang', 'Anfänger')})")
                elif entry_type == 'macht_entfernt':
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} entfernt")
                elif entry_type == 'ausruestung_hinzugefuegt':
                    custom_marker = " [Custom]" if details.get('custom', False) else ""
                    auto_marker = " [Auto-Gen]" if details.get('auto_generated', False) else ""
                    log_lines.append(f"  [{timestamp}]{rang_text} {details['name']} hinzugefügt{custom_marker}{auto_marker}")
                elif entry_type == 'auto_character_generated':
                    template_name = details.get('template', 'Unbekannt')
                    setting = details.get('setting', 'SWAE')
                    auto_points = details.get('total_auto_points', 0)
                    log_lines.append(f"  [{timestamp}]{rang_text} Auto-Generierung abgeschlossen:")
                    log_lines.append(f"    Template: {template_name} (Setting: {setting})")
                    if auto_points > 0:
                        log_lines.append(f"    Zusätzliche Punkte: {auto_points}")
                else:
                    log_lines.append(f"  [{timestamp}]{rang_text} {details}")
        
        # Zeige Statistiken pro Pool (berechnet aus Entries)
        log_lines.append("")
        log_lines.append("=" * 80)
        log_lines.append("STATISTIK:")
        log_lines.append("-" * 40)

        # Zähle Steigerungen (nur exakte Typen, keine Substring-Matches)
        attribut_steigerungen = len([e for e in self.entries if e['type'] == 'attribut_steigerung'])
        fertigkeits_steigerungen = len([e for e in self.entries if e['type'] == 'fertigkeit_steigerung'])
        talente_hinzugefuegt = len([e for e in self.entries if e['type'] == 'talent_hinzugefuegt'])
        talente_entfernt = len([e for e in self.entries if e['type'] == 'talent_entfernt'])
        handicaps_hinzugefuegt = len([e for e in self.entries if e['type'] == 'handicap_hinzugefuegt'])
        handicaps_entfernt = len([e for e in self.entries if e['type'] == 'handicap_entfernt'])
        maechte_hinzugefuegt = len([e for e in self.entries if e['type'] == 'macht_hinzugefuegt'])
        maechte_entfernt = len([e for e in self.entries if e['type'] == 'macht_entfernt'])

        # Berechne Punkte pro Pool aus Entries (nicht aus total_kosten)
        # Attributpunkte: nur Chargen-Attributsteigerungen (nicht Aufstiege/Handicap)
        attr_punkte = sum(e['details'].get('kosten', 0) for e in self.entries
                         if e['type'] == 'attribut_steigerung'
                         and 'aufstieg' not in e['details'].get('kosten_typ', '').lower()
                         and 'handicap' not in e['details'].get('kosten_typ', '').lower())

        # Fertigkeitspunkte: nur Chargen-Fertigkeitssteigerungen
        fert_punkte = sum(e['details'].get('kosten', 0) for e in self.entries
                         if e['type'] == 'fertigkeit_steigerung'
                         and 'aufstieg' not in e['details'].get('kosten_typ', '').lower()
                         and 'handicap' not in e['details'].get('kosten_typ', '').lower())

        # Talentpunkte: nur Chargen-Talente (nicht Aufstiege/Handicap)
        talent_punkte = sum(e['details'].get('kosten', 0) for e in self.entries
                           if e['type'] == 'talent_hinzugefuegt'
                           and 'aufstieg' not in e['details'].get('kosten_typ', '').lower()
                           and 'handicap' not in e['details'].get('kosten_typ', '').lower())

        # Handicap-Punkte: erhalten vs. verwendet
        handicap_punkte_erhalten = sum(e['details'].get('punkte', 0) for e in self.entries if e['type'] == 'handicap_hinzugefuegt')
        handicap_punkte_entfernt = sum(e['details'].get('punkte', 0) for e in self.entries if e['type'] == 'handicap_entfernt')

        handicap_punkte_fuer_attribute = sum(2 for e in self.entries
                                           if e['type'] == 'attribut_steigerung' and 'handicap' in e['details'].get('kosten_typ', '').lower())
        handicap_punkte_fuer_fertigkeiten = sum(e['details'].get('kosten', 0) for e in self.entries
                                               if e['type'] == 'fertigkeit_steigerung' and 'handicap' in e['details'].get('kosten_typ', '').lower())
        handicap_punkte_fuer_talente = sum(2 for e in self.entries
                                         if e['type'] == 'talent_hinzugefuegt' and 'handicap' in e['details'].get('kosten_typ', '').lower())

        handicap_punkte_verwendet = handicap_punkte_fuer_attribute + handicap_punkte_fuer_fertigkeiten + handicap_punkte_fuer_talente
        handicap_punkte_verfuegbar = handicap_punkte_erhalten - handicap_punkte_entfernt - handicap_punkte_verwendet

        # Aufstiege: alle Steigerungen die via Aufstieg bezahlt wurden
        aufstiege_verwendet = sum(e['details'].get('kosten', 0) for e in self.entries
                                 if 'aufstieg' in e['details'].get('kosten_typ', '').lower())

        log_lines.append(f"  Attribute:     {attr_punkte} Punkte ({attribut_steigerungen} Steigerungen)")
        log_lines.append(f"  Fertigkeiten:  {fert_punkte} Punkte ({fertigkeits_steigerungen} Steigerungen)")
        log_lines.append(f"  Talente:       {talent_punkte} Punkte ({talente_hinzugefuegt} hinzugefügt, {talente_entfernt} entfernt)")
        log_lines.append(f"  Handicaps:     +{handicap_punkte_erhalten} erhalten, {handicap_punkte_verwendet} verwendet, {handicap_punkte_verfuegbar} verfügbar ({handicaps_hinzugefuegt} hinzugefügt, {handicaps_entfernt} entfernt)")
        log_lines.append(f"  Mächte:        {maechte_hinzugefuegt} hinzugefügt, {maechte_entfernt} entfernt")
        log_lines.append(f"  Aufstiege:     {aufstiege_verwendet} verwendet")
        log_lines.append("=" * 80)
        
        return "\n".join(log_lines)
    
    def save_to_file(self, char_name: str, output_dir: Optional[Path] = None) -> Path:
        """
        Speichert die Historie in einer Datei.
        
        Args:
            char_name: Name des Charakters
            output_dir: Ausgabeverzeichnis (optional)
            
        Returns:
            Path zur gespeicherten Datei
        """
        # Standard-Ausgabeverzeichnis
        if output_dir is None:
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "chars" / "manual_logs"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_historie_{timestamp}.txt"
        filepath = output_dir / filename
        
        # Log schreiben
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.get_formatted_log())
        
        Logger.info(f"Historie gespeichert: {filepath}")
        return filepath
    
    def to_dict(self) -> Dict:
        """Konvertiert die Historie zu einem Dictionary."""
        return {
            'session_start': self.session_start.isoformat(),
            'entries': self.entries
        }

    def from_dict(self, data: Dict) -> None:
        """Lädt die Historie aus einem Dictionary."""
        self.session_start = datetime.fromisoformat(data['session_start'])
        self.entries = data.get('entries', [])


class HistorieWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung der Charakter-Historie.
    Zeigt alle Änderungen und Steigerungen des aktuellen Charakters an.

    Mobile: Layout wird dynamisch in Python aufgebaut und reagiert
    auf Orientierungswechsel (Portrait/Landscape).
    Desktop: Layout kommt aus historie_view.kv.
    """

    charakter_controller = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Historie-Manager - wird bei App-Start als neue Session gestartet
        self.historie = CharakterHistorie()

        # Service References
        self.charakter_controller = None
        self._dialog_service = None

        # Widget-Referenzen
        self.auto_log_switch = None
        self.log_display = None
        self.stats_text = None
        self.stats_card = None
        self.filter_input = None

        # Mobile-State
        self._stats_collapsed = False
        self._current_orientation = None  # 'portrait' oder 'landscape'
        self._debounce_resize_event = None

        if _mobile:
            # Mobile: Layout dynamisch aufbauen
            Clock.schedule_once(self._build_mobile_layout, 0)
        else:
            # Desktop: Widget-Referenzen aus KV-IDs
            Clock.schedule_once(self._init_widget_refs_desktop, 0)

        # Services initialisieren
        Clock.schedule_once(self._init_services, 0.1)

        # Event-Listener registrieren
        Clock.schedule_once(self._register_event_listeners, 0.2)

    # ── Desktop: KV-basierte Widget-Refs ──────────────────────────

    def _init_widget_refs_desktop(self, dt):
        """Setzt Widget-Referenzen aus KV-IDs (Desktop)."""
        self.auto_log_switch = self.ids.auto_log_switch
        self.log_display = self.ids.log_display
        self.stats_text = self.ids.stats_text
        self.stats_card = self.ids.stats_card
        self.filter_input = self.ids.filter_input
        self.filter_input.bind(text=self._apply_filter)

    # ── Mobile: Dynamisches Layout ────────────────────────────────

    def _build_mobile_layout(self, dt):
        """Baut das Mobile-Layout dynamisch auf und bindet Orientierungswechsel."""
        from kivy.core.window import Window

        # Orientierung bestimmen und Layout aufbauen
        self._rebuild_for_orientation()

        # Auf Größenänderungen reagieren (Orientierungswechsel)
        Window.bind(on_resize=self._on_window_resize)

    def _on_window_resize(self, window, width, height):
        """Reagiert auf Fenster-/Orientierungswechsel."""
        new_orientation = 'landscape' if width > height else 'portrait'
        if new_orientation != self._current_orientation:
            # Debounce: Verzögert rebuilden um mehrfache resize-Events zu vermeiden
            if self._debounce_resize_event:
                self._debounce_resize_event.cancel()
            self._debounce_resize_event = Clock.schedule_once(
                lambda dt: self._rebuild_for_orientation(), 0.15
            )

    def _rebuild_for_orientation(self):
        """Baut das Layout passend zur aktuellen Orientierung neu auf."""
        from kivy.core.window import Window
        from kivy.metrics import dp

        is_landscape = Window.width > Window.height
        new_orientation = 'landscape' if is_landscape else 'portrait'

        # Aktuellen Log-Text sichern
        current_text = ""
        if self.log_display:
            current_text = self.log_display.text

        # Alte Widgets entfernen
        self.clear_widgets()

        if is_landscape:
            self._build_landscape_layout()
        else:
            self._build_portrait_layout()

        # Log-Text wiederherstellen
        if current_text and self.log_display:
            self.log_display.text = current_text

        self._current_orientation = new_orientation

        # Display aktualisieren falls Historie vorhanden
        if self.historie.entries:
            self._update_display()

    def _build_portrait_layout(self):
        """Baut das Portrait-Layout auf (vertikal gestapelt)."""
        from kivy.metrics import dp
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.card import MDCard
        from kivymd.uix.divider import MDDivider
        from kivymd.uix.selectioncontrol import MDSwitch
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.scrollview import MDScrollView
        from views.ui_components import ReadonlyTextDisplay

        self.orientation = 'vertical'
        self.padding = dp(6)
        self.spacing = dp(6)

        # ── Header: Titel + Auto-Log Switch ──
        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(8))

        title = MDLabel(text="[b]Charakter-Historie[/b]", markup=True, font_size="18sp", size_hint_x=1)
        header.add_widget(title)

        switch_box = MDBoxLayout(orientation='horizontal', size_hint_x=None, width=dp(110), spacing=dp(4))
        switch_label = MDLabel(text="Auto-Log:", size_hint_x=None, width=dp(65), font_size="13sp")
        self.auto_log_switch = MDSwitch()
        self.auto_log_switch.active = True
        switch_box.add_widget(switch_label)
        switch_box.add_widget(self.auto_log_switch)
        header.add_widget(switch_box)

        self.add_widget(header)

        # ── Buttons ──
        btn_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))

        btn_save = MDButton(style="tonal", size_hint_x=1, on_release=self._save_history)
        btn_save.add_widget(MDButtonText(text="Speichern"))
        btn_row.add_widget(btn_save)

        btn_clear = MDButton(style="tonal", size_hint_x=1, on_release=self._clear_history)
        btn_clear.add_widget(MDButtonText(text="Löschen"))
        btn_row.add_widget(btn_clear)

        btn_export = MDButton(style="tonal", size_hint_x=1, on_release=self._export_full_history)
        btn_export.add_widget(MDButtonText(text="Exportieren"))
        btn_row.add_widget(btn_export)

        self.add_widget(btn_row)

        # ── Divider ──
        self.add_widget(MDDivider())

        # ── Statistik-Karte (klappbar) ──
        self.stats_card = MDCard(
            orientation='vertical', padding=dp(8),
            size_hint_y=None, height=dp(110),
            md_bg_color=(0.1, 0.1, 0.1, 1)
        )
        self.stats_card.bind(on_release=self._toggle_stats)

        stats_header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(24))
        stats_title = MDLabel(
            text="[b]Session-Statistik:[/b]", markup=True,
            size_hint_x=1, font_size="14sp"
        )
        self._stats_chevron = MDLabel(
            text="▲", size_hint_x=None, width=dp(24),
            font_size="14sp", halign="center"
        )
        stats_header.add_widget(stats_title)
        stats_header.add_widget(self._stats_chevron)
        self.stats_card.add_widget(stats_header)

        self.stats_text = MDLabel(
            text="Keine Daten verfügbar",
            size_hint_y=None, height=dp(70), font_size="13sp"
        )
        self.stats_card.add_widget(self.stats_text)

        self._stats_collapsed = False
        self.add_widget(self.stats_card)

        # ── Log-Anzeige (ScrollView) ──
        scroll = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False, do_scroll_y=True,
            bar_width=dp(24), bar_margin=dp(12),
            scroll_type=['bars', 'content']
        )
        scroll.scroll_wheel_distance = dp(114)

        self.log_display = ReadonlyTextDisplay(
            text="", readonly=True, multiline=True,
            font_size="12sp",
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[dp(8), dp(8), dp(40), dp(8)],
            size_hint_y=None
        )
        self.log_display.bind(minimum_height=self.log_display.setter('height'))
        scroll.add_widget(self.log_display)

        self.add_widget(scroll)

        # ── Filter-Zeile ──
        filter_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(6))
        self.filter_input = MDTextField(mode="outlined", size_hint_x=1)
        self.filter_input.hint_text = "Suche in Historie..."
        self.filter_input.bind(text=self._apply_filter)
        filter_row.add_widget(self.filter_input)

        self.add_widget(filter_row)

    def _build_landscape_layout(self):
        """Baut das Landscape-Layout auf (zwei Spalten: Controls links, Log rechts)."""
        from kivy.metrics import dp
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.card import MDCard
        from kivymd.uix.divider import MDDivider
        from kivymd.uix.selectioncontrol import MDSwitch
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.scrollview import MDScrollView
        from views.ui_components import ReadonlyTextDisplay

        self.orientation = 'horizontal'
        self.padding = dp(6)
        self.spacing = dp(8)

        # ═══ Linke Spalte: Controls + Stats ═══
        left_col = MDBoxLayout(
            orientation='vertical', size_hint_x=None, width=dp(200),
            spacing=dp(6), padding=[0, 0, dp(4), 0]
        )

        # Titel
        title = MDLabel(
            text="[b]Charakter-\nHistorie[/b]", markup=True,
            font_size="16sp", size_hint_y=None, height=dp(44)
        )
        left_col.add_widget(title)

        # Auto-Log Switch
        switch_box = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(4)
        )
        switch_label = MDLabel(text="Auto-Log:", font_size="12sp", size_hint_x=None, width=dp(65))
        self.auto_log_switch = MDSwitch()
        self.auto_log_switch.active = True
        switch_box.add_widget(switch_label)
        switch_box.add_widget(self.auto_log_switch)
        left_col.add_widget(switch_box)

        left_col.add_widget(MDDivider())

        # Buttons (vertikal gestapelt)
        btn_save = MDButton(style="tonal", size_hint_x=1, size_hint_y=None, height=dp(36),
                            on_release=self._save_history)
        btn_save.add_widget(MDButtonText(text="Speichern", font_size="12sp"))
        left_col.add_widget(btn_save)

        btn_clear = MDButton(style="tonal", size_hint_x=1, size_hint_y=None, height=dp(36),
                             on_release=self._clear_history)
        btn_clear.add_widget(MDButtonText(text="Löschen", font_size="12sp"))
        left_col.add_widget(btn_clear)

        btn_export = MDButton(style="tonal", size_hint_x=1, size_hint_y=None, height=dp(36),
                              on_release=self._export_full_history)
        btn_export.add_widget(MDButtonText(text="Exportieren", font_size="12sp"))
        left_col.add_widget(btn_export)

        left_col.add_widget(MDDivider())

        # Kompakte Statistik
        self.stats_card = MDCard(
            orientation='vertical', padding=dp(6),
            size_hint_y=None, height=dp(100),
            md_bg_color=(0.1, 0.1, 0.1, 1)
        )
        stats_title = MDLabel(
            text="[b]Statistik:[/b]", markup=True,
            size_hint_y=None, height=dp(20), font_size="12sp"
        )
        self.stats_card.add_widget(stats_title)

        self.stats_text = MDLabel(
            text="Keine Daten", size_hint_y=None, height=dp(70), font_size="11sp"
        )
        self.stats_card.add_widget(self.stats_text)
        left_col.add_widget(self.stats_card)

        # Filter
        self.filter_input = MDTextField(mode="outlined", size_hint_y=None, height=dp(40))
        self.filter_input.hint_text = "Suche..."
        self.filter_input.bind(text=self._apply_filter)
        left_col.add_widget(self.filter_input)

        # Spacer unten
        left_col.add_widget(MDBoxLayout(size_hint_y=1))

        self.add_widget(left_col)

        # ═══ Rechte Spalte: Log-Anzeige (volle Höhe) ═══
        scroll = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False, do_scroll_y=True,
            bar_width=dp(20), bar_margin=dp(8),
            scroll_type=['bars', 'content']
        )
        scroll.scroll_wheel_distance = dp(114)

        self.log_display = ReadonlyTextDisplay(
            text="", readonly=True, multiline=True,
            font_size="11sp",
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[dp(8), dp(8), dp(30), dp(8)],
            size_hint_y=None
        )
        self.log_display.bind(minimum_height=self.log_display.setter('height'))
        scroll.add_widget(self.log_display)

        self.add_widget(scroll)

    def _toggle_stats(self, *args):
        """Klappt die Statistik-Karte ein/aus (nur Portrait)."""
        from kivy.metrics import dp
        from kivy.animation import Animation

        if self._stats_collapsed:
            # Aufklappen
            anim = Animation(height=dp(110), duration=0.2)
            anim.start(self.stats_card)
            if self.stats_text:
                self.stats_text.opacity = 1
            if hasattr(self, '_stats_chevron'):
                self._stats_chevron.text = "▲"
            self._stats_collapsed = False
        else:
            # Zuklappen
            anim = Animation(height=dp(30), duration=0.2)
            anim.start(self.stats_card)
            if self.stats_text:
                self.stats_text.opacity = 0
            if hasattr(self, '_stats_chevron'):
                self._stats_chevron.text = "▼"
            self._stats_collapsed = True
    
    def _init_services(self, dt):
        """Initialisiert die Service-Referenzen."""
        try:
            self.charakter_controller = service_container.get_charakter_controller()
            self._dialog_service = service_container.get_dialog_service()
            
            # Bei App-Start KEINE existierende Historie laden - immer mit leerer Historie starten
            # Historie wird nur geladen wenn ein Charakter explizit geladen wird (character_loaded event)
            
            Logger.info("HistorieWidget Services initialisiert - Historie bleibt leer bei App-Start")
        except Exception as e:
            Logger.error(f"Fehler bei Service-Initialisierung: {str(e)}")
    
    def _register_event_listeners(self, dt):
        """Registriert Event-Listener für Charakter-Änderungen."""
        try:
            event_service = service_container.get_event_service()
            if event_service:
                # Registriere Listener für verschiedene Änderungen
                event_service.subscribe('attribute_changed', self._on_attribute_changed)
                event_service.subscribe('skill_changed', self._on_skill_changed)
                event_service.subscribe('talent_added', self._on_talent_added)
                event_service.subscribe('talent_removed', self._on_talent_removed)
                event_service.subscribe('handicap_added', self._on_handicap_added)
                event_service.subscribe('handicap_removed', self._on_handicap_removed)
                event_service.subscribe('handicap_reduced', self._on_handicap_reduced)
                event_service.subscribe('macht_added', self._on_macht_added)
                event_service.subscribe('macht_removed', self._on_macht_removed)
                event_service.subscribe('character_loaded', self._on_character_loaded)
                event_service.subscribe('character_saved', self._on_character_saved)
                event_service.subscribe('character_created', self._on_character_created)
                Logger.info("Historie Event-Listener registriert")

            # Zusätzlich Kivy-Event vom Controller binden (wird beim regulären Laden ausgelöst)
            if self.charakter_controller:
                self.charakter_controller.bind(on_charakter_loaded=self._on_kivy_charakter_loaded)
                Logger.info("Historie Kivy-Event on_charakter_loaded gebunden")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Registrierung: {str(e)}")
    
    def _get_charakter_rang(self) -> str:
        """Gibt den aktuellen Rang des Charakters zurück."""
        try:
            if self.charakter_controller and self.charakter_controller.charakter:
                return getattr(self.charakter_controller.charakter, 'rang', '')
        except Exception:
            pass
        return ''

    def _sync_journal_to_charakter(self):
        """Synchronisiert die aktuelle Historie ins Charakter-Objekt."""
        try:
            if self.charakter_controller and self.charakter_controller.charakter:
                self.charakter_controller.charakter.steigerungs_journal = self.historie.to_dict()
        except Exception as e:
            Logger.error(f"Fehler bei Journal-Synchronisation: {e}")

    def _update_display(self):
        """Aktualisiert die Anzeige der Historie."""
        try:
            if not self.log_display or not self.stats_text:
                return

            # Log-Text aktualisieren
            self.log_display.text = self.historie.get_formatted_log()

            # Statistik aktualisieren (exakte Typ-Matches)
            stats_text = []
            stats_text.append(f"Attribute gesteigert: {len([e for e in self.historie.entries if e['type'] == 'attribut_steigerung'])} mal")
            stats_text.append(f"Fertigkeiten gesteigert: {len([e for e in self.historie.entries if e['type'] == 'fertigkeit_steigerung'])} mal")
            talente_add = len([e for e in self.historie.entries if e['type'] == 'talent_hinzugefuegt'])
            talente_del = len([e for e in self.historie.entries if e['type'] == 'talent_entfernt'])
            stats_text.append(f"Talente: {talente_add} erworben, {talente_del} entfernt")

            self.stats_text.text = "\n".join(stats_text)

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Historie-Anzeige: {str(e)}")
    
    def _on_attribute_changed(self, event_data):
        """Handler für Attribut-Änderungen."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            # Handle sowohl dict als auch Event-Objekt
            if hasattr(event_data, 'data'):
                data = event_data.data
            else:
                data = event_data
                
            if not isinstance(data, dict):
                Logger.warning(f"Unerwarteter Datentyp für Attribut-Event: {type(data)}")
                return
                
            details = {
                'name': data.get('attribute_name', 'Unbekannt'),
                'von': data.get('old_value', 4),
                'nach': data.get('new_value', 6),
                'kosten': data.get('cost', 1),
                'kosten_typ': data.get('cost_type', 'Attributspunkte')
            }
            self.historie.add_entry('attribut_steigerung', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Attribut-Logging: {str(e)}")
    
    def _on_skill_changed(self, event_data):
        """Handler für Fertigkeits-Änderungen."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            # Handle sowohl dict als auch Event-Objekt
            if hasattr(event_data, 'data'):
                data = event_data.data
            else:
                data = event_data
                
            if not isinstance(data, dict):
                Logger.warning(f"Unerwarteter Datentyp für Fertigkeits-Event: {type(data)}")
                return
                
            details = {
                'name': data.get('skill_name', 'Unbekannt'),
                'von': data.get('old_value', 0),
                'nach': data.get('new_value', 4),
                'kosten': data.get('cost', 1),
                'kosten_typ': data.get('cost_type', 'Fertigkeitspunkte')
            }
            self.historie.add_entry('fertigkeit_steigerung', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Fertigkeits-Logging: {str(e)}")
    
    def _on_talent_added(self, event_data):
        """Handler für neue Talente."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            # Handle sowohl dict als auch Event-Objekt
            if hasattr(event_data, 'data'):
                data = event_data.data
            else:
                data = event_data
                
            if not isinstance(data, dict):
                Logger.warning(f"Unerwarteter Datentyp für Talent-Event: {type(data)}")
                return
                
            details = {
                'name': data.get('talent_name', 'Unbekannt'),
                'kosten': data.get('cost', 1),
                'voraussetzungen': data.get('requirements', '')
            }
            self.historie.add_entry('talent_hinzugefuegt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Talent-Logging: {str(e)}")
    
    def _on_handicap_added(self, event_data):
        """Handler für neue Handicaps."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            # Handle sowohl dict als auch Event-Objekt
            if hasattr(event_data, 'data'):
                data = event_data.data
            else:
                data = event_data
                
            if not isinstance(data, dict):
                Logger.warning(f"Unerwarteter Datentyp für Handicap-Event: {type(data)}")
                return
                
            details = {
                'name': data.get('handicap_name', 'Unbekannt'),
                'stufe': data.get('stufe', 'Leicht'),
                'punkte': data.get('points', 1)
            }
            self.historie.add_entry('handicap_hinzugefuegt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Handicap-Logging: {str(e)}")
    
    def _on_macht_added(self, event_data):
        """Handler für neue Mächte."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            # Handle sowohl dict als auch Event-Objekt
            if hasattr(event_data, 'data'):
                data = event_data.data
            else:
                data = event_data
                
            if not isinstance(data, dict):
                Logger.warning(f"Unerwarteter Datentyp für Macht-Event: {type(data)}")
                return
                
            details = {
                'name': data.get('macht_name', 'Unbekannt'),
                'rang': data.get('rang', 'Anfänger'),
                'kosten': data.get('cost', 1)
            }
            self.historie.add_entry('macht_hinzugefuegt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Macht-Logging: {str(e)}")
    
    def _on_talent_removed(self, event_data):
        """Handler für entfernte Talente."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            details = {
                'name': event_data.get('talent_name', 'Unbekannt'),
                'action': event_data.get('action', 'removed')
            }
            self.historie.add_entry('talent_entfernt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Talent-Entfernung-Logging: {str(e)}")
    
    def _on_handicap_removed(self, event_data):
        """Handler für entfernte Handicaps."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            details = {
                'name': event_data.get('handicap_name', 'Unbekannt'),
                'action': event_data.get('action', 'removed')
            }
            self.historie.add_entry('handicap_entfernt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Handicap-Entfernung-Logging: {str(e)}")
    
    def _on_handicap_reduced(self, event_data):
        """Handler für reduzierte Handicaps."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            details = {
                'name': event_data.get('handicap_name', 'Unbekannt'),
                'action': event_data.get('action', 'reduced')
            }
            self.historie.add_entry('handicap_reduziert', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Handicap-Reduzierung-Logging: {str(e)}")
    
    def _on_macht_removed(self, event_data):
        """Handler für entfernte Mächte."""
        if not self.auto_log_switch or not self.auto_log_switch.active:
            return
            
        try:
            details = {
                'name': event_data.get('macht_name', 'Unbekannt'),
                'action': event_data.get('action', 'removed')
            }
            self.historie.add_entry('macht_entfernt', details, rang=self._get_charakter_rang())
            self._sync_journal_to_charakter()
            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler bei Macht-Entfernung-Logging: {str(e)}")
    
    def _on_kivy_charakter_loaded(self, *args):
        """Callback für Kivy-Event on_charakter_loaded vom Controller (reguläres Laden)."""
        try:
            char_name = 'Unbekannt'
            if self.charakter_controller and self.charakter_controller.charakter:
                char_name = getattr(self.charakter_controller.charakter, 'char_name', 'Unbekannt')
            self._on_character_loaded({'character_name': char_name})
        except Exception as e:
            Logger.error(f"Fehler bei Kivy on_charakter_loaded: {str(e)}")

    def _on_character_loaded(self, event_data):
        """Handler für geladene Charaktere. Lädt Journal aus Charakter-JSON falls vorhanden."""
        try:
            char_name = event_data.get('character_name', 'Unbekannt')
            self.historie = CharakterHistorie()  # Neue Historie starten

            # Versuche Journal aus dem Charakter-Objekt zu laden
            journal_loaded = False
            if self.charakter_controller and self.charakter_controller.charakter:
                journal = self.charakter_controller.charakter.steigerungs_journal
                if journal and isinstance(journal, dict) and journal.get('entries'):
                    self.historie.from_dict(journal)
                    journal_loaded = True
                    Logger.info(f"Steigerungs-Journal aus Charakter-JSON geladen ({len(journal.get('entries', []))} Einträge)")

            if not journal_loaded:
                # Fallback: Aus Log-Dateien laden (Kompatibilität mit alten Charakteren)
                self.historie.add_entry('charakter_geladen', {'name': char_name})
                self._load_existing_history()

            self._update_display()
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Historie: {str(e)}")
    
    def _on_character_saved(self, event_data):
        """Handler für gespeicherte Charaktere. Synchronisiert Journal ins Charakter-Objekt."""
        try:
            # Journal immer ins Charakter-Objekt schreiben, damit es im JSON landet
            self._sync_journal_to_charakter()
            if self.auto_log_switch and self.auto_log_switch.active:
                self._save_history(None)
        except Exception as e:
            Logger.error(f"Fehler beim Auto-Speichern der Historie: {str(e)}")
    
    def _on_character_created(self, event_data):
        """Handler für neu erstellte Charaktere."""
        try:
            char_name = event_data.get('character_name', 'Neuer Charakter')
            # Leere Historie bei neuem Charakter
            self.historie = CharakterHistorie()
            self.historie.add_entry('charakter_erstellt', {'name': char_name})
            self._sync_journal_to_charakter()
            self._update_display()
            Logger.info(f"Historie zurückgesetzt für neuen Charakter: {char_name}")
        except Exception as e:
            Logger.error(f"Fehler beim Zurücksetzen der Historie: {str(e)}")
    
    def _save_history(self, instance):
        """Speichert die aktuelle Historie in einer Datei."""
        try:
            if not self.charakter_controller or not self.charakter_controller.charakter:
                if self._dialog_service:
                    self._dialog_service.show_error_dialog("Kein Charakter geladen!")
                return
            
            char_name = getattr(self.charakter_controller.charakter, 'char_name', 'Unbekannt')
            filepath = self.historie.save_to_file(char_name)
            
            if self._dialog_service:
                self._dialog_service.show_info_dialog(
                    "Historie gespeichert",
                    f"Die Historie wurde erfolgreich gespeichert:\n{filepath}"
                )
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Historie: {str(e)}")
            if self._dialog_service:
                self._dialog_service.show_error_dialog(f"Fehler beim Speichern: {str(e)}")
    
    def _clear_history(self, instance):
        """Löscht die aktuelle Historie."""
        try:
            if self._dialog_service:
                def confirm_clear():
                    self.historie = CharakterHistorie()
                    self._update_display()
                    Logger.info("Historie gelöscht")
                
                self._dialog_service.show_confirmation_dialog(
                    "Historie löschen?",
                    "Möchten Sie die gesamte Historie wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.",
                    confirm_clear
                )
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Historie: {str(e)}")
    
    def _apply_filter(self, instance, value):
        """Wendet einen Filter auf die Log-Anzeige an."""
        try:
            if not value:
                # Kein Filter - zeige alles
                self.log_display.text = self.historie.get_formatted_log()
            else:
                # Filter anwenden
                full_log = self.historie.get_formatted_log()
                filtered_lines = []
                for line in full_log.split('\n'):
                    if value.lower() in line.lower():
                        filtered_lines.append(line)
                self.log_display.text = '\n'.join(filtered_lines)
        except Exception as e:
            Logger.error(f"Fehler beim Filtern: {str(e)}")
    
    def _export_full_history(self, instance):
        """Exportiert die vollständige Historie mit allen Details."""
        try:
            if not self.charakter_controller or not self.charakter_controller.charakter:
                if self._dialog_service:
                    self._dialog_service.show_error_dialog("Kein Charakter geladen!")
                return
            
            # Erweiterte Historie mit JSON-Export
            char_name = getattr(self.charakter_controller.charakter, 'char_name', 'Unbekannt')
            
            # JSON-Export
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "chars" / "manual_logs"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            json_filename = f"{safe_name}_historie_{timestamp}.json"
            json_filepath = output_dir / json_filename
            
            # JSON speichern
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.historie.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Auch als Text speichern
            text_filepath = self.historie.save_to_file(char_name, output_dir)
            
            if self._dialog_service:
                self._dialog_service.show_info_dialog(
                    "Export erfolgreich",
                    f"Historie exportiert:\n- Text: {text_filepath}\n- JSON: {json_filepath}"
                )
        except Exception as e:
            Logger.error(f"Fehler beim Export: {str(e)}")
            if self._dialog_service:
                self._dialog_service.show_error_dialog(f"Export fehlgeschlagen: {str(e)}")
    
    def _load_existing_history(self):
        """Lädt existierende Historie-Dateien für den aktuellen Charakter."""
        try:
            if not self.charakter_controller or not self.charakter_controller.charakter:
                return
            
            char_name = getattr(self.charakter_controller.charakter, 'char_name', 'Unbekannt')
            
            # Suche nach existierenden Log-Dateien
            from pathlib import Path
            from utils.path_utils import get_chars_path
            
            chars_root = Path(get_chars_path())
            log_dirs = [
                chars_root / "manual_logs",
                chars_root / "auto_generated" / "logs"
            ]
            
            found_logs = []
            for log_dir in log_dirs:
                if log_dir.exists():
                    # Suche nach passenden Dateien
                    pattern = f"{char_name}*historie*.json"
                    for file in log_dir.glob(pattern):
                        found_logs.append(file)
            
            if found_logs:
                # Lade die neueste Datei
                latest_log = max(found_logs, key=lambda f: f.stat().st_mtime)
                with open(latest_log, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.historie.from_dict(data)
                Logger.info(f"Historie geladen aus: {latest_log}")
                self._update_display()
        except Exception as e:
            Logger.error(f"Fehler beim Laden existierender Historie: {str(e)}")
    
    def refresh_widget(self):
        """Aktualisiert das Widget (wird vom Tab-System aufgerufen)."""
        try:
            self._update_display()
            Logger.info("HistorieWidget aktualisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Widget-Refresh: {str(e)}")