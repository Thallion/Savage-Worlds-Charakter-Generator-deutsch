# views/voelker_view.py - MDCard Lösung gegen Textüberschneidung
"""
View-Komponente für Völker nach dem MVC-Pattern.
MDCard-LÖSUNG: Jedes Volk in eigener Card mit strukturiertem Layout
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivy.properties import ObjectProperty, DictProperty
from kivy.metrics import dp
import logging

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# Konstanten
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_ATTRIBUT_TEXT = 'Wähle ein Attribut'  
DEFAULT_FERTIGKEIT_TEXT = 'Wähle eine Fertigkeit'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'
NO_ATTRIBUT_AVAILABLE_TEXT = 'Keine Attribute verfügbar'
NO_FERTIGKEIT_AVAILABLE_TEXT = 'Keine Fertigkeiten verfügbar'

# KV-String mit MDCard-Layout
KV_STRING = '''
<VoelkerWidget>:
    orientation: 'vertical'
    padding: [dp(20), dp(15), dp(20), dp(15)]
    spacing: dp(15)
    md_bg_color: self.theme_cls.backgroundColor

    MDLabel:
        text: "Völker"
        size_hint_y: None
        height: dp(50)
        halign: 'left'
        font_style: "Headline"
        theme_text_color: "Primary"

    ScrollView:
        size_hint: (1, 1)
        do_scroll_x: False
        do_scroll_y: True
        bar_width: dp(12)

        MDBoxLayout:
            id: voelker_content_container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(20)
            padding: [0, dp(10), 0, dp(20)]
'''

Builder.load_string(KV_STRING)


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    Verwendet MDCard für saubere Struktur ohne Textüberschneidung.
    """
    controller = ObjectProperty(None)
    voelker_auswahlen = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voelker_auswahlen = {}
        self.dropdown_menu = None
        
        # Controller aus der App initialisieren
        Clock.schedule_once(self._initialize_controller, 0)
        Clock.schedule_once(self.aktualisiere_ui, 0.1)

    def set_controller(self, controller):
        """Setzt den Controller für das Widget."""
        self.controller = controller
        if controller and hasattr(controller, 'charakter'):
            controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
            self.aktualisiere_ui()

    def _initialize_controller(self, dt=None):
        """Initialisiert die Verbindung zum Controller aus der App."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                self.controller = app.controller
                Logger.debug(f"VoelkerWidget: Controller erfolgreich initialisiert")
                
                # Event-Bindung für Charakteränderungen
                if hasattr(self.controller, 'charakter'):
                    self.controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
                    Logger.debug("VoelkerWidget: Event-Bindung erstellt")
            else:
                Logger.error("VoelkerWidget: App-Controller nicht verfügbar")
                
        except Exception as e:
            Logger.error(f"VoelkerWidget: Controller-Initialisierung fehlgeschlagen: {e}")

    def aktualisiere_ui(self, *args):
        """Aktualisiert die UI basierend auf dem aktuellen Zustand des Charakters."""
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        try:
            # Controller-Verfügbarkeit prüfen
            if not self.controller:
                self._initialize_controller()
                
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("VoelkerWidget: Controller nicht verfügbar - Retry in 1s")
                Clock.schedule_once(self.aktualisiere_ui, 1.0)
                return
                
            # UI-Container prüfen
            if not hasattr(self, 'ids') or 'voelker_content_container' not in self.ids:
                Logger.debug("VoelkerWidget: UI-Container noch nicht verfügbar")
                Clock.schedule_once(self.aktualisiere_ui, 0.5)
                return
                
            container = self.ids.voelker_content_container
            container.clear_widgets()

            charakter = self.controller.charakter
            
            # Völker-Daten prüfen
            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                placeholder = MDLabel(
                    text="Keine Völker-Daten verfügbar",
                    halign='center',
                    theme_text_color="Secondary",
                    font_style="Body",
                    size_hint_y=None,
                    height=dp(100)
                )
                container.add_widget(placeholder)
                return
            
            # Sicherstellen, dass voelker_selected existiert
            if not hasattr(charakter, 'voelker_selected'):
                charakter.voelker_selected = {}
                
            for volk_name in charakter.voelker:
                if volk_name not in charakter.voelker_selected:
                    charakter.voelker_selected[volk_name] = False
            
            # Völker als Cards anzeigen
            for volk_name, volk in charakter.voelker.items():
                volk_card = self._create_volk_card(volk_name, volk)
                container.add_widget(volk_card)
                
            Logger.debug(f"VoelkerWidget: UI erfolgreich aktualisiert mit {len(charakter.voelker)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _create_volk_card(self, volk_name, volk):
        """Erstellt eine MDCard für ein Volk - verhindert Textüberschneidung komplett."""
        
        # Höhe der Card basierend auf Inhalt berechnen
        card_height = self._calculate_card_height(volk_name, volk)
        
        # Hauptcard für das Volk
        card = MDCard(
            size_hint_y=None,
            height=card_height,
            padding=dp(20),
            spacing=dp(12),
            elevation=3,
            radius=[8],
            md_bg_color=self.theme_cls.surfaceContainerColor,
            style="elevated"
        )
        
        # Hauptcontainer innerhalb der Card
        card_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card_height - dp(60),  # Mehr Abzug für Card-Padding + Sicherheitspuffer
            spacing=dp(12)
        )
        
        # 1. Header-Bereich (Name + Checkbox)
        header_section = self._create_header_section(volk_name)
        card_content.add_widget(header_section)
        
        # 2. Auswahl-Bereich (falls vorhanden)
        auswahl_section = self._create_auswahl_section(volk_name, volk)
        if auswahl_section:
            card_content.add_widget(auswahl_section)
        
        # 3. Detail-Bereich (Handicaps, Talente, etc.)
        detail_section = self._create_detail_section(volk)
        if detail_section:
            card_content.add_widget(detail_section)
        
        # Content zur Card hinzufügen
        card.add_widget(card_content)
        
        return card

    def _calculate_card_height(self, volk_name, volk):
        """Berechnet die notwendige Höhe für eine Volk-Card basierend auf dem Inhalt."""
        
        base_height = dp(120)  # Grundhöhe (Header + Padding) - erhöht
        
        # Auswahl-Optionen zählen
        auswahl_count = 0
        if self._hat_freies_talent(volk_name, volk):
            auswahl_count += 1
        if self._hat_freies_attribut(volk_name, volk):
            auswahl_count += 1
        if self._hat_freie_fertigkeit(volk_name, volk):
            auswahl_count += 1
        
        auswahl_height = auswahl_count * dp(85)  # Jede Auswahl braucht 85dp - erhöht
        
        # Detail-Items zählen und Textlänge berücksichtigen
        detail_height = 0
        kategorien = [
            ('Handicaps', getattr(volk, 'handicaps', [])),
            ('Talente', getattr(volk, 'talente', [])),
            ('Besonderheiten', getattr(volk, 'besonderheiten', []))
        ]
        
        for kategorie, items in kategorien:
            if items:
                detail_height += dp(35)  # Kategorie-Header
                for item in items:
                    # Geschätzte Höhe basierend auf Textlänge
                    text_length = len(item)
                    if text_length > 100:  # Sehr langer Text
                        detail_height += dp(70)  # Doppelte Höhe
                    elif text_length > 50:  # Mittellanger Text
                        detail_height += dp(50)  # 1.5x Höhe
                    else:  # Kurzer Text
                        detail_height += dp(35)  # Normale Höhe
        
        # Gesamthöhe berechnen
        total_height = base_height + auswahl_height + detail_height + dp(80)  # Größerer Buffer
        
        # Mindesthöhe sicherstellen
        return max(total_height, dp(250))  # Mindesthöhe erhöht

    def _create_header_section(self, volk_name):
        """Erstellt den Header-Bereich mit Name und Checkbox."""
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),  # Feste Höhe für Header
            spacing=dp(15)
        )
        
        # Volk-Name Label - mit ausreichend Platz
        name_label = MDLabel(
            text=volk_name,
            font_style="Title",
            theme_text_color="Primary",
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(60),  # Feste Höhe für bessere Lesbarkeit
            halign='left',
            valign='center'
        )
        # Wichtig: Text-Wrapping aktivieren
        name_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
        
        # Checkbox
        is_active = self.controller.charakter.voelker_selected.get(volk_name, False)
        checkbox = MDCheckbox(
            active=is_active,
            size_hint_x=None,
            width=dp(50),
            selected_color=self.theme_cls.primary_color
        )
        checkbox.bind(active=lambda instance, value, volk_name=volk_name: 
                    self._on_checkbox_active(instance, value, volk_name))
        
        header.add_widget(name_label)
        header.add_widget(checkbox)
        
        return header

    def _create_auswahl_section(self, volk_name, volk):
        """Erstellt den Auswahl-Bereich für völker-spezifische Optionen."""
        is_active = self.controller.charakter.voelker_selected.get(volk_name, False)
        auswahl = self.voelker_auswahlen.get(volk_name, {})
        
        # Anzahl der Auswahl-Optionen zählen
        auswahl_count = 0
        if self._hat_freies_talent(volk_name, volk):
            auswahl_count += 1
        if self._hat_freies_attribut(volk_name, volk):
            auswahl_count += 1
        if self._hat_freie_fertigkeit(volk_name, volk):
            auswahl_count += 1
        
        if auswahl_count == 0:
            return None
        
        # Container für alle Auswahl-Optionen mit berechneter Höhe
        auswahl_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=auswahl_count * dp(85),  # Feste Höhe basierend auf Anzahl - erhöht
            spacing=dp(10)
        )
        
        # Freies Talent
        if self._hat_freies_talent(volk_name, volk):
            talent_section = self._create_single_auswahl(
                "Freies Talent",
                auswahl.get('talent', DEFAULT_TALENT_TEXT),
                lambda: self.show_talent_search_dialog(None, volk_name),
                is_active
            )
            auswahl_container.add_widget(talent_section)
        
        # Freies Attribut
        if self._hat_freies_attribut(volk_name, volk):
            attribut_section = self._create_single_auswahl(
                "Freies Attribut",
                auswahl.get('attribut', DEFAULT_ATTRIBUT_TEXT),
                lambda: self.show_attribut_search_dialog(None, volk_name),
                is_active
            )
            auswahl_container.add_widget(attribut_section)
        
        # Freie Fertigkeit
        if self._hat_freie_fertigkeit(volk_name, volk):
            fertigkeit_section = self._create_single_auswahl(
                "Freie Fertigkeit",
                auswahl.get('fertigkeit', DEFAULT_FERTIGKEIT_TEXT),
                lambda: self.show_fertigkeit_search_dialog(None, volk_name),
                is_active
            )
            auswahl_container.add_widget(fertigkeit_section)
        
        return auswahl_container

    def _create_single_auswahl(self, titel, auswahl_text, callback, is_active):
        """Erstellt eine einzelne Auswahl-Option innerhalb der Card."""
        
        # Container für eine Auswahl-Option mit fester Höhe
        auswahl_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),  # Feste Höhe für jede Auswahl - angepasst an Berechnung
            spacing=dp(5)
        )
        
        # Titel der Auswahl
        titel_label = MDLabel(
            text=f"{titel}:",
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30),  # Erhöht für bessere Lesbarkeit
            halign='left',
            valign='center'
        )
        titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
        
        # Auswahl-Zeile mit Text und Button
        auswahl_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),  # Erhöht für bessere Lesbarkeit
            spacing=dp(10)
        )
        
        # Auswahl-Text
        text_color = "Primary" if auswahl_text not in [DEFAULT_TALENT_TEXT, DEFAULT_ATTRIBUT_TEXT, DEFAULT_FERTIGKEIT_TEXT] else "Secondary"
        auswahl_label = MDLabel(
            text=auswahl_text,
            font_style="Body",
            theme_text_color=text_color,
            size_hint_x=0.8,
            size_hint_y=None,
            height=dp(40),  # Feste Höhe für bessere Lesbarkeit
            halign='left',
            valign='center'
        )
        auswahl_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
        
        # Dropdown-Button
        dropdown_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: callback(),
            disabled=not is_active
        )
        
        auswahl_row.add_widget(auswahl_label)
        auswahl_row.add_widget(dropdown_button)
        
        auswahl_box.add_widget(titel_label)
        auswahl_box.add_widget(auswahl_row)
        
        return auswahl_box

    def _create_detail_section(self, volk):
        """Erstellt den Detail-Bereich für Völker-Informationen."""
        
        # Kategorien definieren
        kategorien = [
            ('Handicaps', getattr(volk, 'handicaps', [])),
            ('Talente', getattr(volk, 'talente', [])),
            ('Besonderheiten', getattr(volk, 'besonderheiten', []))
        ]
        
        # Höhe basierend auf Textlänge berechnen
        detail_height = 0
        for kategorie, items in kategorien:
            if items:
                detail_height += dp(35)  # Kategorie-Header
                for item in items:
                    # Geschätzte Höhe basierend auf Textlänge
                    text_length = len(item)
                    if text_length > 100:  # Sehr langer Text
                        detail_height += dp(70)  # Doppelte Höhe
                    elif text_length > 50:  # Mittellanger Text
                        detail_height += dp(50)  # 1.5x Höhe
                    else:  # Kurzer Text
                        detail_height += dp(35)  # Normale Höhe
        
        if detail_height == 0:
            return None
        
        # Container für alle Detail-Kategorien mit berechneter Höhe
        detail_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=detail_height,  # Dynamische Höhe basierend auf Textlänge
            spacing=dp(5)
        )
        
        for kategorie, items in kategorien:
            if items:
                # Kategorie-Überschrift
                kategorie_label = MDLabel(
                    text=f"{kategorie}:",
                    font_style="Body",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(35),  # Einheitliche Höhe für Kategorie-Header
                    halign='left',
                    valign='top'  # Top-Alignment für bessere Lesbarkeit
                )
                kategorie_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
                detail_container.add_widget(kategorie_label)
                
                # Items der Kategorie
                for item in items:
                    # Höhe basierend auf Textlänge
                    text_length = len(item)
                    if text_length > 100:  # Sehr langer Text
                        item_height = dp(70)
                    elif text_length > 50:  # Mittellanger Text
                        item_height = dp(50)
                    else:  # Kurzer Text
                        item_height = dp(35)
                    
                    item_label = MDLabel(
                        text=f"  • {item}",
                        font_style="Body",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=item_height,  # Dynamische Höhe
                        halign='left',
                        valign='top'  # Top-Alignment für bessere Lesbarkeit
                    )
                    # Wichtig: Text-Wrapping für lange Beschreibungen
                    item_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
                    detail_container.add_widget(item_label)
        
        return detail_container

    def _on_checkbox_active(self, checkbox, value, volk_name):
        """Event-Handler für Checkbox-Änderungen."""
        try:
            charakter = self.controller.charakter
            charakter.voelker_selected[volk_name] = value
            
            if not value:
                self._remove_volk_auswahl(volk_name)
            
            # UI aktualisieren
            Clock.schedule_once(self.aktualisiere_ui, 0.1)
            charakter.dispatch('on_charakter_change')

        except Exception as e:
            Logger.error(f"Fehler in _on_checkbox_active: {e}")

    def _hat_freies_talent(self, volk_name, volk):
        return (volk_name == "Mensch" or 
                (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freies_talent')))

    def _hat_freies_attribut(self, volk_name, volk):
        return ((volk_name == "Mensch" and self._ist_savage_pathfinder_aktiv()) or
                volk_name == "Halbelf" or
                (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freies_attribut')))

    def _hat_freie_fertigkeit(self, volk_name, volk):
        return (volk_name == "Gnom" or
                (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freie_verstandsfertigkeit')))

    def _ist_savage_pathfinder_aktiv(self):
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return False
        charakter = self.controller.charakter
        if hasattr(charakter, 'setting_regeln') and charakter.setting_regeln:
            return charakter.setting_regeln.savage_pathfinder
        return False

    def _remove_volk_auswahl(self, volk_name):
        """Entfernt alle Auswahlen für ein bestimmtes Volk."""
        if volk_name not in self.voelker_auswahlen:
            return
            
        charakter = self.controller.charakter
        auswahl = self.voelker_auswahlen[volk_name]
        
        # Alle Auswahlen zurücksetzen
        for auswahl_typ in ['talent', 'attribut', 'fertigkeit']:
            if auswahl_typ in auswahl:
                if auswahl_typ == 'talent':
                    talent_name = auswahl[auswahl_typ]
                    if hasattr(charakter, 'selected_talente') and talent_name in charakter.selected_talente:
                        charakter.selected_talente.remove(talent_name)
                    if hasattr(charakter, 'talente') and talent_name in charakter.talente:
                        charakter.talente[talent_name].ausgewaehlt = False
                elif auswahl_typ == 'attribut':
                    attribut_name = auswahl[auswahl_typ]
                    if hasattr(charakter, 'attribute') and attribut_name in charakter.attribute:
                        charakter.attribute[attribut_name].wert -= 1
                elif auswahl_typ == 'fertigkeit':
                    fertigkeit_name = auswahl[auswahl_typ]
                    if hasattr(charakter, 'fertigkeiten') and fertigkeit_name in charakter.fertigkeiten:
                        charakter.fertigkeiten[fertigkeit_name].wert -= 1
        
        # Auswahl zurücksetzen
        del self.voelker_auswahlen[volk_name]

    # Erweiterte Dialog-Methoden mit verbesserter UX  
    def show_talent_search_dialog(self, button, volk_name):
        """Zeigt erweiterten Dialog für Talent-Auswahl."""
        try:
            freie_talente = self._get_freie_talente()
            if not freie_talente or freie_talente == [NO_TALENT_AVAILABLE_TEXT]:
                return
            
            self._show_improved_dropdown(
                title="Freies Talent auswählen:",
                items=freie_talente,
                callback=lambda talent: self._select_talent(volk_name, talent),
                caller=button if button else self
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Talent-Dialog: {e}")

    def show_attribut_search_dialog(self, button, volk_name):
        """Zeigt erweiterten Dialog für Attribut-Auswahl."""
        try:
            verfuegbare_attribute = self._get_verfuegbare_attribute()
            if not verfuegbare_attribute:
                return
            
            self._show_improved_dropdown(
                title="Freies Attribut auswählen:",
                items=verfuegbare_attribute,
                callback=lambda attribut: self._select_attribut(volk_name, attribut),
                caller=button if button else self
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Attribut-Dialog: {e}")

    def show_fertigkeit_search_dialog(self, button, volk_name):
        """Zeigt erweiterten Dialog für Fertigkeiten-Auswahl."""
        try:
            verfuegbare_fertigkeiten = self._get_verfuegbare_fertigkeiten()
            if not verfuegbare_fertigkeiten:
                return
            
            self._show_improved_dropdown(
                title="Freie Fertigkeit auswählen:",
                items=verfuegbare_fertigkeiten,
                callback=lambda fertigkeit: self._select_fertigkeit(volk_name, fertigkeit),
                caller=button if button else self
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Fertigkeiten-Dialog: {e}")

    def _show_improved_dropdown(self, title, items, callback, caller):
        """Zeigt ein verbessertes Dropdown-Menü mit Titel."""
        try:
            # Titel und Items kombinieren
            menu_items = []
            
            # Titel als erstes Element (leer on_release = nicht klickbar)
            menu_items.append({
                "text": f"🔍 {title}",
                "on_release": lambda: None,  # Leer = nicht klickbar
            })
            
            # Trennlinie
            menu_items.append({
                "text": "─" * 25,
                "on_release": lambda: None,  # Leer = nicht klickbar
            })
            
            # Eigentliche Items hinzufügen
            for item in items:
                menu_items.append({
                    "text": f"  {item}",
                    "on_release": lambda x=item: self._handle_dropdown_selection(callback, x),
                })
            
            # Dropdown-Menü erstellen und anzeigen
            self.dropdown_menu = MDDropdownMenu(
                caller=caller,
                items=menu_items,
                width=dp(350),  # Breiter für bessere Lesbarkeit
                max_height=dp(400)  # Maximale Höhe für Scrolling
            )
            self.dropdown_menu.open()
            
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Dropdown-Menüs: {e}")
            # Fallback: Einfaches Dropdown ohne Titel
            self._show_simple_dropdown(items, callback, caller)

    def _show_simple_dropdown(self, items, callback, caller):
        """Fallback: Einfaches Dropdown ohne spezielle Features."""
        try:
            menu_items = [
                {
                    "text": item,
                    "on_release": lambda x=item: self._handle_dropdown_selection(callback, x),
                } for item in items
            ]
            
            self.dropdown_menu = MDDropdownMenu(
                caller=caller,
                items=menu_items,
                width=dp(300)
            )
            self.dropdown_menu.open()
            
        except Exception as e:
            Logger.error(f"Fehler beim Fallback-Dropdown: {e}")

    def _handle_dropdown_selection(self, callback, item):
        """Behandelt die Auswahl aus dem Dropdown-Menü."""
        try:
            if self.dropdown_menu:
                self.dropdown_menu.dismiss()
            callback(item)
        except Exception as e:
            Logger.error(f"Fehler bei Dropdown-Auswahl: {e}")

    def _get_freie_talente(self):
        """Gibt freie Talente zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return [NO_TALENT_AVAILABLE_TEXT]
        try:
            charakter = self.controller.charakter
            frei_talente = []
            if hasattr(charakter, 'talente') and charakter.talente:
                for name, talent in charakter.talente.items():
                    if hasattr(talent, 'aktiv') and hasattr(talent, 'ausgewaehlt'):
                        if talent.aktiv and not talent.ausgewaehlt:
                            frei_talente.append(name)
            frei_talente.sort()
            return frei_talente if frei_talente else [NO_TALENT_AVAILABLE_TEXT]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen freier Talente: {e}")
            return [NO_TALENT_AVAILABLE_TEXT]

    def _get_verfuegbare_attribute(self):
        """Gibt verfügbare Attribute zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return []
        try:
            charakter = self.controller.charakter
            if hasattr(charakter, 'attribute') and charakter.attribute:
                return list(charakter.attribute.keys())
            return []
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Attribute: {e}")
            return []

    def _get_verfuegbare_fertigkeiten(self):
        """Gibt verfügbare verstandsbasierte Fertigkeiten zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return []
        try:
            charakter = self.controller.charakter
            verstandsfertigkeiten = []
            if hasattr(charakter, 'fertigkeiten') and charakter.fertigkeiten:
                for name, fertigkeit in charakter.fertigkeiten.items():
                    if hasattr(fertigkeit, 'attribut') and fertigkeit.attribut == 'Verstand':
                        verstandsfertigkeiten.append(name)
            verstandsfertigkeiten.sort()
            return verstandsfertigkeiten
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Fertigkeiten: {e}")
            return []

    def _select_talent(self, volk_name, talent_name):
        """Wählt ein Talent aus."""
        try:
            if hasattr(self, 'dropdown_menu') and self.dropdown_menu:
                self.dropdown_menu.dismiss()
            if talent_name == NO_TALENT_AVAILABLE_TEXT:
                return
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['talent'] = talent_name
            
            charakter = self.controller.charakter
            if hasattr(charakter, 'talente') and talent_name in charakter.talente:
                charakter.talente[talent_name].ausgewaehlt = True
                if hasattr(charakter, 'selected_talente'):
                    if talent_name not in charakter.selected_talente:
                        charakter.selected_talente.append(talent_name)
            
            Logger.info(f"Talent '{talent_name}' für '{volk_name}' ausgewählt")
            self.aktualisiere_ui()
        except Exception as e:
            Logger.error(f"Fehler bei Talent-Auswahl: {e}")

    def _select_attribut(self, volk_name, attribut_name):
        """Wählt ein Attribut aus."""
        try:
            if hasattr(self, 'dropdown_menu') and self.dropdown_menu:
                self.dropdown_menu.dismiss()
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['attribut'] = attribut_name
            
            charakter = self.controller.charakter
            if hasattr(charakter, 'attribute') and attribut_name in charakter.attribute:
                charakter.attribute[attribut_name].wert += 1
            
            Logger.info(f"Attribut '{attribut_name}' für '{volk_name}' ausgewählt")
            self.aktualisiere_ui()
        except Exception as e:
            Logger.error(f"Fehler bei Attribut-Auswahl: {e}")

    def _select_fertigkeit(self, volk_name, fertigkeit_name):
        """Wählt eine Fertigkeit aus."""
        try:
            if hasattr(self, 'dropdown_menu') and self.dropdown_menu:
                self.dropdown_menu.dismiss()
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['fertigkeit'] = fertigkeit_name
            
            charakter = self.controller.charakter
            if hasattr(charakter, 'fertigkeiten') and fertigkeit_name in charakter.fertigkeiten:
                charakter.fertigkeiten[fertigkeit_name].wert += 1
            
            Logger.info(f"Fertigkeit '{fertigkeit_name}' für '{volk_name}' ausgewählt")
            self.aktualisiere_ui()
        except Exception as e:
            Logger.error(f"Fehler bei Fertigkeiten-Auswahl: {e}")