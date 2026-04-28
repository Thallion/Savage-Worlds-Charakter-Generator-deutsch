# views/voelker_view.py - UI-Komponente mit MDDropdownMenu
"""
View-Komponente für Völker nach dem MVC-Pattern.
ÜBERARBEITET: UI-Darstellung getrennt von Geschäftslogik (volk_funktionen.py)
KORRIGIERT: KivyMD 2.0.1 Kompatibilität (adaptive_height entfernt)
NEU: MDDropdownMenu für platzsparende Völker-Auswahl
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty, DictProperty
from kivy.metrics import dp
import logging

# Import der ausgelagerten Geschäftslogik
from functions.volk_funktionen import (
    waehle_volk, abwaehlen_volk, get_selected_volk,
    hat_volk_wahlmoeglichkeit, get_volk_zusatzelemente, get_volk_attribut_optionen,
    get_freie_talente, get_verfuegbare_attribute, get_verfuegbare_fertigkeiten,
    waehle_freies_talent, waehle_freies_attribut, waehle_freie_fertigkeit,
    reset_volk_auswahlen, initialisiere_voelker_system, get_voelker_status_info,
    waehle_halbelf_talent, waehle_halbelf_attribut,  # NEUE: Halbelf-spezifische Funktionen
    waehle_mensch_talent, waehle_mensch_fertigkeitspunkte,  # NEUE: Menschen-Vielseitig-Funktionen
    DEFAULT_TALENT_TEXT, DEFAULT_ATTRIBUT_TEXT, DEFAULT_FERTIGKEIT_TEXT,
    NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT
)

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# KV-Datei laden mit PyInstaller-kompatiblem Pfad und Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'voelker_view_mobile.kv' if _mobile else 'voelker_view.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'voelker_view.kv')
Builder.load_file(_kv_path)
Logger.info(f"voelker_view: KV-Datei geladen: {os.path.basename(_kv_path)}")


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    ÜBERARBEITET: Reine UI-Komponente, Geschäftslogik in volk_funktionen.py
    NEU: Verwendet MDDropdownMenu für platzsparende Völker-Auswahl
    """
    controller = ObjectProperty(None)
    voelker_auswahlen = DictProperty({})
    selected_volk_name = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voelker_auswahlen = {}
        self.selected_volk_name = None
        self.volk_dropdown_menu = None  # Für das Dropdown-Menü
        self.search_dialog = None  # Für Such-Dialoge
        
        # Controller aus der App initialisieren
        Clock.schedule_once(self._initialize_controller, 0)
        Clock.schedule_once(self.aktualisiere_ui, 0.1)

    def set_controller(self, controller):
        """Setzt den Controller für das Widget."""
        self.controller = controller
        if controller and hasattr(controller, 'charakter'):
            controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
            self.aktualisiere_ui()

    def _defocus_and_call(self, callback):
        """Defokussiert alle TextFields und ruft callback verzögert auf.
        Behebt Android-Problem: TextField-Fokus schluckt Button-Touch-Events."""
        Window.release_all_keyboards()
        Clock.schedule_once(lambda dt: callback(), 0.1)

    def _initialize_controller(self, dt=None):
        """Initialisiert die Verbindung zum Controller aus der App."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller'):
                self.set_controller(app.controller)
            else:
                Logger.warning("VoelkerWidget: App-Controller noch nicht verfügbar")
                Clock.schedule_once(self._initialize_controller, 1.0)
        except Exception as e:
            Logger.error(f"Fehler bei Controller-Initialisierung: {e}")

    def open_volk_dropdown(self):
        """Öffnet das Völker-Auswahl-Overlay (Slide-In von rechts)."""
        try:
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("Controller nicht verfügbar")
                return

            charakter = self.controller.charakter

            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                Logger.warning("Keine Völker verfügbar")
                return

            from views.voelker_auswahl_overlay import VoelkerAuswahlOverlay

            if not hasattr(self, '_voelker_overlay'):
                self._voelker_overlay = VoelkerAuswahlOverlay()

            self._voelker_overlay.open(
                current_volk=self.selected_volk_name or "",
                available_voelker=sorted(charakter.voelker.keys()),
                charakter=charakter,
                on_volk_chosen=self._on_overlay_volk_chosen,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Völker-Overlays: {e}", exc_info=True)

    def _on_overlay_volk_chosen(self, volk_name, zusatzelemente):
        """Callback vom VoelkerAuswahlOverlay - Volk + Zusatzelemente gewählt"""
        try:
            Logger.info(f"[DEBUG] _on_overlay_volk_chosen aufgerufen: volk_name={volk_name}, zusatzelemente={zusatzelemente}")
            # Volk auswählen/abwählen
            self._select_volk_from_dropdown(volk_name)

            # Zusatzelemente anwenden
            if volk_name and zusatzelemente:
                charakter = self.controller.charakter

                # Initialize volk_auswahlen entry if needed
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}

                def _as_list(v):
                    """Akzeptiert sowohl Listen (Multi-Slot) als auch Skalare (Legacy)."""
                    if v is None:
                        return []
                    if isinstance(v, list):
                        return [x for x in v if x]
                    return [v]

                # Freies Talent (all types) - kann mehrere Slots haben
                talente = _as_list(zusatzelemente.get('freies_talent'))
                if talente:
                    talent_liste = []
                    for talent in talente:
                        Logger.info(f"[DEBUG] Rufe waehle_freies_talent auf für '{volk_name}' mit Talent '{talent}'")
                        result = waehle_freies_talent(charakter, volk_name, talent)
                        Logger.info(f"[DEBUG] waehle_freies_talent result: {result}")
                        if result == "needs_voraussetzungen_confirmation":
                            # Bisher gewählte Talente sichern, dann Dialog zeigen
                            if talent_liste:
                                self.voelker_auswahlen[volk_name]['talent'] = talent_liste
                            self._show_voraussetzungen_confirmation_dialog(volk_name, 'freies_talent', talent)
                            return
                        elif result:
                            talent_liste.append(talent)
                        else:
                            Logger.error(f"Fehler bei Auswahl von freiem Talent '{talent}' für Volk '{volk_name}'")
                    if talent_liste:
                        self.voelker_auswahlen[volk_name]['talent'] = talent_liste

                # Halbelf Talent
                if zusatzelemente.get('halbelf_talent'):
                    talent = zusatzelemente['halbelf_talent']
                    result = waehle_halbelf_talent(charakter, volk_name, talent)
                    if result == "needs_voraussetzungen_confirmation":
                        self._show_voraussetzungen_confirmation_dialog(volk_name, 'halbelf_talent', talent)
                        return  # Abbrechen, Dialog wird angezeigt
                    elif result:
                        self.voelker_auswahlen[volk_name]['halbelf_wahl'] = f'Talent: {talent}'
                    else:
                        Logger.error(f"Fehler bei Auswahl von Halbelf-Talent '{talent}' für Volk '{volk_name}'")

                # Halbelf Attribut
                if zusatzelemente.get('halbelf_attribut'):
                    waehle_halbelf_attribut(charakter, volk_name)
                    self.voelker_auswahlen[volk_name]['halbelf_wahl'] = 'Geschicklichkeit W6'

                # Mensch Talent
                if zusatzelemente.get('mensch_talent'):
                    talent = zusatzelemente['mensch_talent']
                    result = waehle_mensch_talent(charakter, volk_name, talent)
                    if result == "needs_voraussetzungen_confirmation":
                        self._show_voraussetzungen_confirmation_dialog(volk_name, 'mensch_talent', talent)
                        return  # Abbrechen, Dialog wird angezeigt
                    elif result:
                        self.voelker_auswahlen[volk_name]['vielseitig_wahl'] = f"Talent: {talent}"
                    else:
                        Logger.error(f"Fehler bei Auswahl von Mensch-Talent '{talent}' für Volk '{volk_name}'")

                # Mensch Fertigkeitspunkte
                if zusatzelemente.get('mensch_fertigkeitspunkte'):
                    waehle_mensch_fertigkeitspunkte(charakter, volk_name)
                    self.voelker_auswahlen[volk_name]['vielseitig_wahl'] = '+2 Fertigkeitspunkte'

                # Freies Attribut - kann mehrere Slots haben
                attribute = _as_list(zusatzelemente.get('freies_attribut'))
                if attribute:
                    attr_liste = []
                    for attr in attribute:
                        Logger.info(f"[DEBUG] Rufe waehle_freies_attribut auf für '{volk_name}' mit Attribut '{attr}'")
                        if waehle_freies_attribut(charakter, volk_name, attr):
                            attr_liste.append(attr)
                    if attr_liste:
                        self.voelker_auswahlen[volk_name]['attribut'] = attr_liste

                # Freies Attribut (Malus) - kann mehrere Slots haben
                malus_werte = _as_list(zusatzelemente.get('freies_attribut_malus'))
                if malus_werte:
                    from functions.volk_funktionen import waehle_freies_attribut_malus
                    malus_liste = []
                    for attr in malus_werte:
                        Logger.info(f"[DEBUG] Rufe waehle_freies_attribut_malus auf für '{volk_name}' mit Attribut '{attr}'")
                        if waehle_freies_attribut_malus(charakter, volk_name, attr):
                            malus_liste.append(attr)
                    if malus_liste:
                        self.voelker_auswahlen[volk_name]['attribut_malus'] = malus_liste

                # Freie Fertigkeit - kann mehrere Slots haben
                fertigkeiten = _as_list(zusatzelemente.get('freie_fertigkeit'))
                if fertigkeiten:
                    fert_liste = []
                    for fert in fertigkeiten:
                        if waehle_freie_fertigkeit(charakter, volk_name, fert):
                            fert_liste.append(fert)
                    if fert_liste:
                        self.voelker_auswahlen[volk_name]['fertigkeit'] = fert_liste

                # UI aktualisieren nach Zusatzelemente-Anwendung
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

        except Exception as e:
            Logger.error(f"Fehler bei Overlay-Volk-Auswahl: {e}", exc_info=True)

    def _show_voraussetzungen_confirmation_dialog(self, volk_name, talent_typ, talent_name):
        """Zeigt einen Dialog für nicht erfüllte Voraussetzungen (wie in talente_view.py)."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivy.metrics import dp
        
        charakter = self.controller.charakter
        fehlermeldungen = getattr(charakter, 'temp_voraussetzungs_fehler', [])
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=dp(90) + (len(fehlermeldungen) * dp(40))
        )
        
        main_label = MDLabel(
            text="Die Voraussetzungen für dieses Talent sind nicht erfüllt:",
            size_hint_y=None,
            height=dp(32),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(main_label)
        
        spacer = MDLabel(size_hint_y=None, height=dp(8))
        content.add_widget(spacer)
        
        for fehler in fehlermeldungen:
            fehler_label = MDLabel(
                text=f"• {fehler}",
                size_hint_y=None,
                height=dp(36),
                theme_text_color="Error",
                halign="left",
                valign="middle",
            )
            content.add_widget(fehler_label)
        
        frage_label = MDLabel(
            text="\nTrotzdem auswählen?",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(frage_label)
        
        # Speichere Kontext für Bestätigung
        self._pending_voraussetzungen = {
            'volk_name': volk_name,
            'talent_typ': talent_typ,
            'talent_name': talent_name
        }
        
        self.voraussetzungen_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Voraussetzungen nicht erfüllt",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.voraussetzungen_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_talent_without_voraussetzungen(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.voraussetzungen_dialog.open()

    def _confirm_talent_without_voraussetzungen(self):
        """Wählt das Talent mit ignore_voraussetzungen=True nach Bestätigung."""
        if not hasattr(self, '_pending_voraussetzungen'):
            return
        context = self._pending_voraussetzungen
        volk_name = context['volk_name']
        talent_typ = context['talent_typ']
        talent_name = context['talent_name']
        
        charakter = self.controller.charakter
        from functions.volk_funktionen import waehle_freies_talent, waehle_mensch_talent, waehle_halbelf_talent
        
        success = False
        if talent_typ == 'freies_talent':
            success = waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=True)
        elif talent_typ == 'mensch_talent':
            success = waehle_mensch_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=True)
        elif talent_typ == 'halbelf_talent':
            success = waehle_halbelf_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=True)
        
        if success:
            # UI aktualisieren
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            if talent_typ == 'freies_talent':
                # An die Talent-Liste anhängen (Multi-Slot)
                aktuell = self.voelker_auswahlen[volk_name].get('talent')
                if isinstance(aktuell, list):
                    if talent_name not in aktuell:
                        aktuell.append(talent_name)
                else:
                    self.voelker_auswahlen[volk_name]['talent'] = (
                        [aktuell, talent_name] if aktuell else [talent_name]
                    )
            elif talent_typ == 'halbelf_talent':
                self.voelker_auswahlen[volk_name]['halbelf_wahl'] = f'Talent: {talent_name}'
            elif talent_typ == 'mensch_talent':
                self.voelker_auswahlen[volk_name]['vielseitig_wahl'] = f"Talent: {talent_name}"
            
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
        
        if hasattr(self, 'voraussetzungen_dialog'):
            self.voraussetzungen_dialog.dismiss()
        delattr(self, '_pending_voraussetzungen')

    def _show_volk_search_popup(self):
        """Zeigt einen Auswahl-Dialog für Völker mit Suchfeld und scrollbarer Liste.
        Gleicher Stil wie der Setting-Wechsel-Dialog in der Charakter-Verwaltung."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon

        try:
            charakter = self.controller.charakter
            voelker_namen = sorted(charakter.voelker.keys())
            current_volk = self.selected_volk_name

            self._volk_pending_selection = current_volk

            # Hauptcontainer
            dialog_content = MDBoxLayout(
                orientation="vertical", spacing=dp(15), padding=dp(20),
                size_hint_y=None,
            )
            dialog_content.bind(minimum_height=dialog_content.setter('height'))

            # Info
            dialog_content.add_widget(MDLabel(
                text=f"Aktuelles Volk: {current_volk or 'Keins'}",
                theme_text_color="Secondary", font_style="Body",
                size_hint_y=None, height=dp(30),
            ))

            # Suchfeld
            from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
            search_field = MDTextField(
                mode="outlined", size_hint_y=None, height=dp(56), size_hint_x=1
            )
            search_field.add_widget(MDTextFieldHintText(text="Volk suchen..."))
            dialog_content.add_widget(search_field)

            # Scrollbare Liste
            scroll_view = MDScrollView(size_hint=(1, None), height=dp(250))
            scroll_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None))
            items_list = MDList(size_hint_y=None, size_hint_x=1)
            items_list.bind(minimum_height=items_list.setter('height'))
            scroll_layout.add_widget(items_list)
            scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
            scroll_view.add_widget(scroll_layout)
            scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
            dialog_content.add_widget(scroll_view)

            app = App.get_running_app()

            def populate_list(*args):
                items_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                pending = self._volk_pending_selection

                # "Kein Volk" Option
                if not search_text or search_text in "kein volk":
                    is_sel = pending is None
                    item = MDListItem(
                        size_hint_y=None, height=dp(48),
                        on_release=lambda x: _select(None),
                        md_bg_color=app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                    )
                    if is_sel:
                        item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                    headline = MDListItemHeadlineText(text="Kein Volk")
                    if is_sel:
                        headline.bold = True
                    item.add_widget(headline)
                    items_list.add_widget(item)

                for name in voelker_namen:
                    if search_text and search_text not in name.lower():
                        continue
                    is_sel = (pending == name)
                    item = MDListItem(
                        size_hint_y=None, height=dp(48),
                        on_release=lambda x, n=name: _select(n),
                        md_bg_color=app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                    )
                    if is_sel:
                        item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                    headline = MDListItemHeadlineText(text=name)
                    if is_sel:
                        headline.bold = True
                    item.add_widget(headline)
                    items_list.add_widget(item)

            def _select(volk_name):
                self._volk_pending_selection = volk_name
                populate_list()

            search_field.bind(text=populate_list)
            populate_list()

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._volk_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Auswählen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_volk_selection),
            ))
            dialog_content.add_widget(button_row)

            self._volk_dialog = MDDialog(
                MDDialogHeadlineText(text="Volk auswählen"),
                MDDialogContentContainer(dialog_content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._volk_dialog.open()
            Logger.debug(f"Völker-Dialog geöffnet mit {len(voelker_namen)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler bei Völker-Dialog: {e}", exc_info=True)

    def _apply_volk_selection(self):
        """Wendet die Volk-Auswahl aus dem Dialog an."""
        try:
            self._volk_dialog.dismiss()
            chosen = getattr(self, '_volk_pending_selection', None)
            if chosen != self.selected_volk_name:
                self._select_volk_from_dropdown(chosen)
        except Exception as e:
            Logger.error(f"Fehler bei Volk-Auswahl: {e}", exc_info=True)

    def _on_volk_popup_selected(self, volk_name):
        """Behandelt die Auswahl eines Volkes im Popup-Dialog."""
        try:
            if hasattr(self, 'volk_search_dialog') and self.volk_search_dialog:
                self.volk_search_dialog.dismiss()
                self.volk_search_dialog = None
            self._select_volk_from_dropdown(volk_name)
        except Exception as e:
            Logger.error(f"Fehler bei Völker-Popup-Auswahl: {e}", exc_info=True)

    def _select_volk_from_dropdown(self, volk_name):
        """Behandelt die Völker-Auswahl aus dem Popup/Dropdown."""
        try:
            
            charakter = self.controller.charakter
            
            # Aktuell ausgewähltes Volk ermitteln
            current_volk = None
            for name, selected in charakter.voelker_selected.items():
                if selected:
                    current_volk = name
                    break
            
            # Wenn "Kein Volk" ausgewählt
            if volk_name is None:
                if current_volk:
                    # Aktuelles Volk abwählen
                    success = abwaehlen_volk(charakter, current_volk)
                    if success:
                        self.selected_volk_name = None
                        reset_volk_auswahlen(charakter, current_volk, self.voelker_auswahlen)
                        self._update_dropdown_text("Kein Volk ausgewählt")
                        Logger.info("Kein Volk ausgewählt")
                        
                        # UI aktualisieren
                        Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                        Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
                return
            
            # Neues Volk auswählen
            if current_volk == volk_name:
                Logger.info(f"Volk '{volk_name}' ist bereits ausgewählt")
                return
            
            # Altes Volk abwählen (falls vorhanden)
            if current_volk:
                abwaehlen_volk(charakter, current_volk)
                reset_volk_auswahlen(charakter, current_volk, self.voelker_auswahlen)
            
            # Neues Volk auswählen
            Logger.debug(f"VOELKER_VIEW: Using charakter {id(charakter)} to select volk {volk_name}")
            success = waehle_volk(charakter, volk_name)
            if success:
                self.selected_volk_name = volk_name
                self._update_dropdown_text(volk_name)
                Logger.info(f"Volk '{volk_name}' ausgewählt")
                
                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
            else:
                Logger.error(f"Fehler beim Auswählen von Volk '{volk_name}'")
                
        except Exception as e:
            Logger.error(f"Fehler bei Völker-Auswahl aus Dropdown: {e}", exc_info=True)

    def _update_dropdown_text(self, text):
        """Aktualisiert den Text des Auswahl-Buttons."""
        try:
            if 'selected_volk_text' in self.ids:
                self.ids.selected_volk_text.text = text
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Dropdown-Texts: {e}")

    def open_add_volk_dialog(self):
        """Öffnet den Dialog zum Erstellen eines neuen Volkes."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service and hasattr(dialog_service, 'volk_dialog_handler'):
                dialog_service.volk_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Volk-erstellen-Dialogs: {e}")

    def open_edit_volk_dialog(self):
        """Öffnet den Dialog zum Bearbeiten des ausgewählten Volkes."""
        try:
            if not self.selected_volk_name:
                from services.service_container import service_container
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog("Bitte wähle zuerst ein Volk aus.")
                return
            
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service and hasattr(dialog_service, 'volk_dialog_handler'):
                dialog_service.volk_dialog_handler.show_edit_dialog(self.selected_volk_name)
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Volk-bearbeiten-Dialogs: {e}")

    def open_delete_volk_dialog(self):
        """Öffnet den Dialog zum Löschen von Völkern."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service and hasattr(dialog_service, 'volk_dialog_handler'):
                dialog_service.volk_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Volk-löschen-Dialogs: {e}")

    # === MOBILE INLINE-LISTE METHODEN ===

    def _populate_voelker_liste(self):
        """Befüllt die Inline-Völker-Liste (nur Mobile)."""
        if not _mobile:
            return
        try:
            if 'voelker_liste_container' not in self.ids:
                return

            container = self.ids.voelker_liste_container
            container.clear_widgets()

            if not self.controller or not hasattr(self.controller, 'charakter'):
                return

            charakter = self.controller.charakter
            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                return

            # Suchtext ermitteln
            search_text = ""
            if 'search_input' in self.ids and self.ids.search_input.text:
                search_text = self.ids.search_input.text.lower()

            # "Kein Volk" Option
            if not search_text or "kein" in search_text:
                is_selected = self.selected_volk_name is None
                item = self._create_volk_list_item("Kein Volk", is_selected, volk_name=None)
                container.add_widget(item)

            # Alle Völker alphabetisch sortiert
            for volk_name in sorted(charakter.voelker.keys()):
                if search_text and search_text not in volk_name.lower():
                    continue
                is_selected = (self.selected_volk_name == volk_name)
                item = self._create_volk_list_item(volk_name, is_selected, volk_name=volk_name)
                container.add_widget(item)

        except Exception as e:
            Logger.error(f"Fehler beim Befüllen der Völker-Liste: {e}", exc_info=True)

    def filter_voelker(self):
        """Filtert die Völker-Liste basierend auf dem Suchfeld (Mobile)."""
        self._populate_voelker_liste()

    def _create_volk_list_item(self, display_name, is_selected, volk_name=None):
        """Erstellt ein einzelnes Listenelement für die Völker-Inline-Liste.
        Nutzt MDListItem statt MDCard für zuverlässiges Scrolling auf Android."""
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon

        list_item = MDListItem(
            size_hint_y=None,
            height=dp(44),
            on_release=lambda x, vn=volk_name: self._select_volk_from_dropdown(vn),
            md_bg_color=self.theme_cls.primaryContainerColor if is_selected else self.theme_cls.surfaceContainerLowColor,
        )

        if is_selected:
            list_item.add_widget(MDListItemLeadingIcon(
                icon="check-circle",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.primaryColor,
            ))

        headline = MDListItemHeadlineText(
            text=display_name,
        )
        if is_selected:
            headline.bold = True
        list_item.add_widget(headline)

        return list_item

    def aktualisiere_ui(self, dt=None):
        """Aktualisiert die gesamte UI basierend auf den aktuellen Charakter-Daten."""
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        try:
            # Controller-Verfügbarkeit prüfen
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("VoelkerWidget: Controller nicht verfügbar - Retry in 1s")
                Clock.schedule_once(self.aktualisiere_ui, 1.0)
                return
                
            # UI-Container prüfen
            if not hasattr(self, 'ids'):
                Logger.debug("VoelkerWidget: UI-Container noch nicht verfügbar")
                Clock.schedule_once(self.aktualisiere_ui, 0.5)
                return

            charakter = self.controller.charakter

            # Persistierte Pro-Volk-Auswahlen aus dem Charakter übernehmen,
            # damit nach dem Laden die Edit-Buttons & Slot-Anzeige korrekt sind.
            geladen = getattr(charakter, 'voelker_auswahlen', None)
            if isinstance(geladen, dict) and geladen:
                # Nur überschreiben, wenn das Widget selbst noch keine
                # neueren Auswahlen hält (Reload-Szenario).
                if not self.voelker_auswahlen:
                    self.voelker_auswahlen = dict(geladen)

            # Völker-Daten prüfen
            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                self._show_no_data_message()
                return
            
            # Völker-System initialisieren und bereinigen
            initialisiere_voelker_system(charakter)
            
            # Debug-Informationen ausgeben
            status = get_voelker_status_info(charakter)
            Logger.debug(f"Völker-Status: {status}")

            # Aktuell ausgewähltes Volk ermitteln
            selected_volk = get_selected_volk(charakter)
            self.selected_volk_name = selected_volk.name if selected_volk else None

            # Auswahl-Button-Text aktualisieren
            if self.selected_volk_name:
                self._update_dropdown_text(self.selected_volk_name)
            else:
                self._update_dropdown_text("Kein Volk ausgewählt")

            # UI-Komponenten aktualisieren
            self._update_zusatzelemente()
            self._update_selected_volk_details()
                
            Logger.debug(f"VoelkerWidget: UI erfolgreich aktualisiert mit {len(charakter.voelker)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _show_no_data_message(self):
        """Zeigt eine Nachricht an, wenn keine Völker-Daten verfügbar sind."""
        if _mobile:
            # Inline-Liste leeren
            if 'voelker_liste_container' in self.ids:
                self.ids.voelker_liste_container.clear_widgets()
        else:
            # Dropdown-Text aktualisieren
            self._update_dropdown_text("Keine Völker verfügbar")

        # Container leeren
        for container_id in ['zusatzelemente_container', 'selected_volk_container']:
            if container_id in self.ids:
                self.ids[container_id].clear_widgets()
        
        if 'selected_volk_container' in self.ids:
            placeholder = MDLabel(
                text="Keine Völker-Daten verfügbar",
                halign='center',
                theme_text_color="Secondary",
                font_style="Body",
                size_hint_y=None,
                height=dp(100)
            )
            self.ids.selected_volk_container.add_widget(placeholder)

    def _update_zusatzelemente(self):
        """Zeigt die ausgewählten Zusatzelemente an (aus voelker_auswahlen)."""
        container = self.ids.get('zusatzelemente_container')
        if not container:
            return
        
        container.clear_widgets()
        
        if not self.selected_volk_name:
            return
        
        wahl = self.voelker_auswahlen.get(self.selected_volk_name, {})

        # Collect all selections for this volk.
        # Multi-Slot-Keys liefern eine Zeile pro Listeneintrag mit slot_index;
        # Unique-Keys (halbelf_wahl, vielseitig_wahl, magieaffin) liefern eine
        # Zeile mit slot_index=None.
        selections = []  # Tupel: (label, value, slot_index)

        def _expand(label, value):
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if v:
                        selections.append((label, v, i))
            elif value:
                # Legacy-Skalar in Slot 0 abbilden, damit Edit-Logik einheitlich greift
                selections.append((label, value, 0))

        # Talent (Multi-Slot)
        _expand('Freies Talent', wahl.get('talent'))

        # Halbelf Wahl (Unique)
        if wahl.get('halbelf_wahl'):
            selections.append(('Halbelf Wahl', wahl['halbelf_wahl'], None))

        # Vielseitig Wahl (Mensch, Unique)
        if wahl.get('vielseitig_wahl'):
            selections.append(('Vielseitig Wahl', wahl['vielseitig_wahl'], None))

        # Attribut (Multi-Slot)
        _expand('Freies Attribut', wahl.get('attribut'))

        # Attributs Schwäche (Multi-Slot)
        _expand('Attributs Schwäche', wahl.get('attribut_malus'))

        # Fertigkeit (Multi-Slot)
        _expand('Freie Fertigkeit', wahl.get('fertigkeit'))

        # Magieaffin (zeigt das gewählte AH-Talent + die zugeordnete Arkane Fertigkeit)
        from functions.volk_funktionen import (
            get_aktuelle_magieaffin_fertigkeit,
            get_aktuelles_magieaffin_ah,
            hat_volk_magieaffin,
        )
        if hat_volk_magieaffin(self.controller.charakter, self.selected_volk_name):
            magieaffin_ah = get_aktuelles_magieaffin_ah(self.controller.charakter, self.selected_volk_name)
            magieaffin_fertigkeit = get_aktuelle_magieaffin_fertigkeit(self.controller.charakter, self.selected_volk_name)
            if magieaffin_ah:
                anzeige = f"{magieaffin_ah} ({magieaffin_fertigkeit})" if magieaffin_fertigkeit else magieaffin_ah
                selections.append(('Magieaffin', anzeige, None))
            elif magieaffin_fertigkeit:
                # Backward-Compat: Alte Auswahl ohne AH-Talent
                selections.append(('Magieaffin', magieaffin_fertigkeit, None))
            else:
                selections.append(('Magieaffin', 'Auswählen...', None))
        
        if not selections:
            return
        
        # Create display for selections
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.button import MDIconButton
        
        # Wenn ein Label mehrfach erscheint (z.B. zwei "Freies Talent"), Index in der Anzeige nummerieren
        from collections import Counter
        label_counts = Counter(l for l, _, _ in selections)

        for label, value, slot_index in selections:
            row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(8))
            display_label = label
            if label_counts[label] > 1 and slot_index is not None:
                display_label = f"{label} {slot_index + 1}"
            label_widget = MDLabel(
                text=f"{display_label}:",
                size_hint_x=None,
                width=dp(120),
                theme_text_color="Secondary",
                halign='left',
            )
            row.add_widget(label_widget)

            # Hintergrundfarbe sicherstellen (nie None)
            if hasattr(self, 'theme_cls') and self.theme_cls:
                bg_color = self.theme_cls.primaryContainerColor
            else:
                bg_color = [0.7, 0.8, 1.0, 1.0]  # hellblau als Fallback

            chip = MDChip(
                MDChipText(text=value),
                type="filter",
                active=True,
                md_bg_color=bg_color,
            )
            row.add_widget(chip)

            # Edit-Button für Talent-Auswahl (nur bei Talenten) und Attribut
            if label in ['Freies Talent', 'Halbelf Wahl', 'Vielseitig Wahl', 'Freies Attribut', 'Attributs Schwäche', 'Freie Fertigkeit', 'Magieaffin']:
                # Elementnamen extrahieren
                element_name = value
                if label == 'Halbelf Wahl' and value.startswith('Talent: '):
                    element_name = value.replace('Talent: ', '')
                elif label == 'Vielseitig Wahl' and value.startswith('Talent: '):
                    element_name = value.replace('Talent: ', '')
                # Edit-Button hinzufügen
                edit_btn = MDIconButton(
                    icon="pencil",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    pos_hint={"center_y": 0.5}
                )
                btn = edit_btn
                idx = slot_index  # für Lambda-Capture
                if label == 'Freies Attribut':
                    edit_btn.bind(on_release=lambda x, btn=btn, attr=element_name, i=idx: self._on_edit_attribut(attr, slot_index=i))
                elif label == 'Attributs Schwäche':
                    edit_btn.bind(on_release=lambda x, btn=btn, attr=element_name, i=idx: self._on_edit_attribut_malus(attr, slot_index=i))
                elif label == 'Freie Fertigkeit':
                    edit_btn.bind(on_release=lambda x, btn=btn, fert=element_name, i=idx: self._on_edit_fertigkeit(fert, slot_index=i))
                elif label == 'Magieaffin':
                    edit_btn.bind(on_release=lambda x, btn=btn: self._on_edit_magieaffin())
                else:
                    edit_btn.bind(on_release=lambda x, btn=btn, l=label, tn=element_name, i=idx: self._on_edit_zusatzelement(l, tn, slot_index=i))
                row.add_widget(edit_btn)
            
            container.add_widget(row)

    def _on_edit_zusatzelement(self, label, talent_name, slot_index=None):
        """Öffnet das Talent-Auswahl-Overlay zum Bearbeiten eines bereits gewählten Talents.
        slot_index gibt bei Multi-Slot-Talenten an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        if not hasattr(self, '_voelker_overlay'):
            Logger.error("VoelkerOverlay nicht initialisiert")
            return
        
        # Talenttyp bestimmen
        talent_typ = None
        if label == 'Freies Talent':
            talent_typ = 'freies_talent'
        elif label == 'Halbelf Wahl':
            talent_typ = 'halbelf_talent'
        elif label == 'Vielseitig Wahl':
            talent_typ = 'mensch_talent'
        else:
            Logger.warning(f"Unbekannter Label für Edit: {label}")
            return
        
        # Overlay für aktuelles Volk vorbereiten
        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return
        
        self._voelker_overlay._charakter = self.controller.charakter
        self._voelker_overlay._selected_volk = volk_name
        # Overlay-Zustand für Edit-Modus vorbereiten: _selected_extras zurücksetzen und
        # _zusatzelemente_info auf nur das bearbeitete Element begrenzen, damit
        # _all_extras_selected() nach einer Auswahl True zurückgibt.
        self._voelker_overlay._selected_extras = {}
        if talent_typ == 'freies_talent':
            self._voelker_overlay._zusatzelemente_info = {'freie_talente': True}
        elif talent_typ == 'halbelf_talent':
            self._voelker_overlay._zusatzelemente_info = {'halbelf_entweder_oder': True}
        elif talent_typ == 'mensch_talent':
            self._voelker_overlay._zusatzelemente_info = {'menschen_vielseitig': True}
        self._voelker_overlay.on_volk_chosen = self._on_overlay_volk_chosen
        # Talentauswahl direkt öffnen
        self._voelker_overlay._show_talent_selection(talent_typ)

    def _on_edit_attribut(self, attribut_name, slot_index=None):
        """Öffnet einen Dialog zum Bearbeiten des ausgewählten freien Attributs.
        slot_index gibt bei Multi-Slot-Attributen an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp
        
        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return
        
        charakter = self.controller.charakter
        
        # Verfügbare Attribut-Optionen abrufen
        from functions.volk_funktionen import get_volk_attribut_optionen, NO_ATTRIBUT_AVAILABLE_TEXT
        attribut_optionen = get_volk_attribut_optionen(charakter, volk_name)
        
        if not attribut_optionen or attribut_optionen == [NO_ATTRIBUT_AVAILABLE_TEXT]:
            Logger.warning(f"Keine Attribut-Optionen verfügbar für Volk '{volk_name}'")
            return
        
        # Dialog-Content mit Chips
        # Höhe explizit berechnen (MDDialog Fixed Height: size_hint_y=None braucht feste Höhe)
        scroll_height = min(dp(350), len(attribut_optionen) * dp(52))
        content_height = dp(86) + scroll_height  # padding(40) + label(34) + spacing(12) + scroll
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        # Info-Label
        info_label = MDLabel(
            text="Wähle ein neues Attribut:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        # Chips-Box
        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))
        
        # Bereits in anderen Slots gewählte Attribute ausblenden, damit der User
        # in diesem Slot kein Duplikat wählt. Den Wert des aktuellen Slots erlauben.
        bereits_gewaehlt = set()
        eintrag_attr = self.voelker_auswahlen.get(volk_name, {}).get('attribut')
        if isinstance(eintrag_attr, list):
            cur_idx = getattr(self, '_current_edit_slot_index', None) or 0
            for i, v in enumerate(eintrag_attr):
                if v and i != cur_idx:
                    bereits_gewaehlt.add(v)

        for attr in sorted(attribut_optionen):
            if attr == NO_ATTRIBUT_AVAILABLE_TEXT:
                continue
            if attr in bereits_gewaehlt:
                continue

            # Chip mit Hervorhebung des aktuell ausgewählten Attributs
            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, a=attr: self._on_attribut_chosen(a),
            }
            # Hintergrundfarbe setzen (nie None)
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor
            else:
                # Fallback: hellgrau für nicht-ausgewählt, blau für ausgewählt
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = [0.7, 0.8, 1.0, 1.0]  # hellblau
                else:
                    chip_kwargs['md_bg_color'] = [0.95, 0.95, 0.95, 1.0]  # hellgrau
            
            chip = MDChip(
                MDChipText(text=attr),
                **chip_kwargs
            )
            chips_box.add_widget(chip)
        
        # ScrollView für viele Optionen
        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView(
            size_hint_y=None,
            height=scroll_height,
            do_scroll_x=False,
        )
        scroll.add_widget(chips_box)
        content.add_widget(scroll)
        
        # Dialog-Buttons
        button_container = MDDialogButtonContainer(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
            spacing="8dp",
        )
        
        # Dialog erstellen
        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Attribut für {volk_name} ändern"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )
        
        self._attribut_dialog = dialog
        dialog.open()
    
    def _on_attribut_chosen(self, attribut_name):
        """Wird aufgerufen wenn ein neues Attribut im Bearbeitungs-Dialog ausgewählt wird.
        Berücksichtigt _current_edit_slot_index für Multi-Slot."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_freies_attribut

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        slot_index = getattr(self, '_current_edit_slot_index', None) or 0

        Logger.info(f"[DEBUG] Ändere freies Attribut für '{volk_name}' Slot {slot_index} zu '{attribut_name}'")

        # Alten Wert dieses Slots ermitteln und ggf. zurückrollen.
        eintrag = self.voelker_auswahlen.get(volk_name, {})
        alt = eintrag.get('attribut')
        if isinstance(alt, list):
            alt_wert = alt[slot_index] if 0 <= slot_index < len(alt) else None
        else:
            alt_wert = alt
        if alt_wert and alt_wert != attribut_name:
            # Für Nicht-Mensch-Völker manuell die alte Erhöhung zurücknehmen
            # (waehle_freies_attribut macht das nur für Menschen).
            if volk_name.lower() not in ["mensch", "menschen", "human"]:
                if hasattr(charakter, 'attribute') and alt_wert in charakter.attribute:
                    charakter.attribute[alt_wert].wert = max(4, charakter.attribute[alt_wert].wert - 1)

        success = waehle_freies_attribut(charakter, volk_name, attribut_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            aktuell = self.voelker_auswahlen[volk_name].get('attribut')
            if isinstance(aktuell, list):
                # Listen-Update an gewünschtem Slot
                if 0 <= slot_index < len(aktuell):
                    aktuell[slot_index] = attribut_name
                else:
                    aktuell.append(attribut_name)
            else:
                self.voelker_auswahlen[volk_name]['attribut'] = [attribut_name]

            if hasattr(self, '_attribut_dialog') and self._attribut_dialog:
                self._attribut_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Freies Attribut für '{volk_name}' Slot {slot_index} erfolgreich geändert zu '{attribut_name}'")
        else:
            Logger.error(f"Fehler beim Ändern des Attributs für '{volk_name}'")

    def _on_edit_attribut_malus(self, attribut_name, slot_index=None):
        """Öffnet einen Dialog zum Bearbeiten der Attributs-Schwäche (Malus).
        slot_index gibt bei Multi-Slot-Schwächen an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return

        charakter = self.controller.charakter

        # Verfügbare Malus-Attribut-Optionen abrufen (gleicher Pool wie Bonus)
        from functions.volk_funktionen import get_volk_attribut_optionen, NO_ATTRIBUT_AVAILABLE_TEXT
        attribut_optionen = get_volk_attribut_optionen(charakter, volk_name)

        if not attribut_optionen or attribut_optionen == [NO_ATTRIBUT_AVAILABLE_TEXT]:
            Logger.warning(f"Keine Attribut-Optionen für Schwäche verfügbar für Volk '{volk_name}'")
            return

        # Höhe explizit berechnen
        scroll_height = min(dp(350), len(attribut_optionen) * dp(52))
        content_height = dp(86) + scroll_height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        info_label = MDLabel(
            text="Wähle ein neues zu schwächendes Attribut:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))

        # Bereits in anderen Schwäche-Slots gewählte Attribute ausblenden
        bereits_gewaehlt = set()
        eintrag_malus = self.voelker_auswahlen.get(volk_name, {}).get('attribut_malus')
        if isinstance(eintrag_malus, list):
            cur_idx = getattr(self, '_current_edit_slot_index', None) or 0
            for i, v in enumerate(eintrag_malus):
                if v and i != cur_idx:
                    bereits_gewaehlt.add(v)

        for attr in sorted(attribut_optionen):
            if attr == NO_ATTRIBUT_AVAILABLE_TEXT:
                continue
            if attr in bereits_gewaehlt:
                continue

            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, a=attr: self._on_attribut_malus_chosen(a),
            }
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor
            else:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = [0.7, 0.8, 1.0, 1.0]
                else:
                    chip_kwargs['md_bg_color'] = [0.95, 0.95, 0.95, 1.0]

            chip = MDChip(
                MDChipText(text=attr),
                **chip_kwargs
            )
            chips_box.add_widget(chip)

        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView(
            size_hint_y=None,
            height=scroll_height,
            do_scroll_x=False,
        )
        scroll.add_widget(chips_box)
        content.add_widget(scroll)

        button_container = MDDialogButtonContainer(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
            spacing="8dp",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Attributs Schwäche für {volk_name} ändern"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )

        self._attribut_malus_dialog = dialog
        dialog.open()

    def _on_attribut_malus_chosen(self, attribut_name):
        """Wird aufgerufen, wenn ein neues Schwäche-Attribut ausgewählt wird.
        Berücksichtigt _current_edit_slot_index für Multi-Slot."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_freies_attribut_malus

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        slot_index = getattr(self, '_current_edit_slot_index', None) or 0

        # Alten Wert dieses Slots ermitteln und Schwäche zurückrollen
        eintrag = self.voelker_auswahlen.get(volk_name, {})
        alt = eintrag.get('attribut_malus')
        if isinstance(alt, list):
            alte_schwaeche = alt[slot_index] if 0 <= slot_index < len(alt) else None
        else:
            alte_schwaeche = alt

        if alte_schwaeche and alte_schwaeche != attribut_name:
            try:
                if hasattr(charakter, 'attribute') and alte_schwaeche in charakter.attribute:
                    altes_attribut = charakter.attribute[alte_schwaeche]
                    alter_wert = altes_attribut.wert
                    if alter_wert >= 10:
                        altes_attribut.wert += 2
                    else:
                        altes_attribut.wert += 1
                    if hasattr(charakter, 'berechne_abgeleitete_werte'):
                        charakter.berechne_abgeleitete_werte()
            except Exception as e:
                Logger.warning(f"Konnte alte Attributs-Schwäche '{alte_schwaeche}' nicht zurücksetzen: {e}")

        Logger.info(f"[DEBUG] Ändere Attributs-Schwäche für '{volk_name}' Slot {slot_index} zu '{attribut_name}'")
        success = waehle_freies_attribut_malus(charakter, volk_name, attribut_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            aktuell = self.voelker_auswahlen[volk_name].get('attribut_malus')
            if isinstance(aktuell, list):
                if 0 <= slot_index < len(aktuell):
                    aktuell[slot_index] = attribut_name
                else:
                    aktuell.append(attribut_name)
            else:
                self.voelker_auswahlen[volk_name]['attribut_malus'] = [attribut_name]

            if hasattr(self, '_attribut_malus_dialog') and self._attribut_malus_dialog:
                self._attribut_malus_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Attributs-Schwäche für '{volk_name}' Slot {slot_index} erfolgreich geändert zu '{attribut_name}'")
        else:
            Logger.error(f"Fehler beim Ändern der Attributs-Schwäche für '{volk_name}'")

    def _on_edit_fertigkeit(self, fertigkeit_name, slot_index=None):
        """Platzhalter für Fertigkeits-Bearbeitung (noch nicht implementiert)."""
        self._current_edit_slot_index = slot_index
        Logger.warning("Bearbeiten von freien Fertigkeiten ist noch nicht implementiert")
        # TODO: Implementieren ähnlich wie _on_edit_attribut

    def _on_edit_magieaffin(self):
        """Öffnet einen Dialog zum Auswählen eines Arkanen Hintergrunds (AH) für Magieaffin.
        Das gewählte AH-Talent legt automatisch die zugehörige Arkane Fertigkeit fest."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        from functions.volk_funktionen import get_magieaffin_optionen, get_aktuelles_magieaffin_ah

        ah_optionen = get_magieaffin_optionen(charakter, volk_name)
        aktuelles_ah = get_aktuelles_magieaffin_ah(charakter, volk_name)

        if not ah_optionen:
            from services.service_container import service_container
            ds = service_container.get_dialog_service()
            if ds:
                ds.show_warning_dialog(
                    "Im aktiven Setting ist kein Arkaner Hintergrund (AH) verfügbar. "
                    "Magieaffin kann daher nicht ausgewählt werden."
                )
            else:
                Logger.warning("Magieaffin: Keine AH-Talente im aktiven Setting verfügbar")
            return

        scroll_height = min(dp(350), len(ah_optionen) * dp(52))
        content_height = dp(86) + scroll_height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        info_label = MDLabel(
            text="Wähle einen Arkanen Hintergrund:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))

        for ah_name, fertigkeit_name in ah_optionen:
            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, ah=ah_name: self._on_magieaffin_chosen(ah),
            }
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if ah_name == aktuelles_ah:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor

            chip = MDChip(
                MDChipText(text=f"{ah_name}  →  {fertigkeit_name}"),
                **chip_kwargs,
            )
            chips_box.add_widget(chip)

        scroll = MDScrollView(size_hint_y=None, height=scroll_height, do_scroll_x=False)
        scroll.add_widget(chips_box)
        content.add_widget(scroll)

        button_container = MDDialogButtonContainer(MDBoxLayout(orientation="horizontal", spacing=dp(8)))
        cancel_btn = MDButton(style="text", on_release=lambda x: self._magieaffin_dialog.dismiss() if hasattr(self, '_magieaffin_dialog') else None)
        cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        button_container.add_widget(cancel_btn)

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Magieaffin für {volk_name}"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )

        self._magieaffin_dialog = dialog
        dialog.open()

    def _on_magieaffin_chosen(self, ah_talent_name):
        """Wird aufgerufen wenn ein AH-Talent im Magieaffin-Dialog ausgewählt wird."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_magieaffin_fertigkeit

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        Logger.info(f"[DEBUG] Wähle Magieaffin-AH '{ah_talent_name}' für '{volk_name}'")

        success = waehle_magieaffin_fertigkeit(charakter, volk_name, ah_talent_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['magieaffin'] = ah_talent_name

            if hasattr(self, '_magieaffin_dialog') and self._magieaffin_dialog:
                self._magieaffin_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Magieaffin-AH für '{volk_name}' erfolgreich auf '{ah_talent_name}' gesetzt")
        else:
            Logger.error(f"Fehler beim Setzen des Magieaffin-AH für '{volk_name}'")

    def _create_zusatzelement_section(self, titel, volk_name, auswahl_typ, get_options_func, select_func, placeholder_text, get_alle_items_func=None):
        """Erstellt eine Sektion für Zusatzelemente mit Inline-Chip-Auswahl.
        Ersetzt den bisherigen Dialog-basierten Ansatz für bessere Android-Kompatibilität."""
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        # Kompaktere Werte für Mobile
        _pad = dp(10) if _mobile else dp(14)
        _spacing = dp(6) if _mobile else dp(10)

        # Hauptcontainer für die Sektion
        section_card = MDCard(
            size_hint_x=1,
            size_hint_y=None,
            padding=_pad,
            spacing=_spacing,
            elevation=3,
            radius=[12],
            md_bg_color=self.theme_cls.surfaceContainerHighColor,
            style="elevated",
        )

        section_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=_spacing
        )
        section_content.bind(minimum_height=section_content.setter('height'))
        section_card.bind(minimum_height=section_card.setter('height'))

        # Titel der Sektion
        titel_label = MDLabel(
            text=f"{titel}:",
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24) if _mobile else dp(30),
            halign='left',
            valign='center',
            bold=True
        )
        section_content.add_widget(titel_label)

        # Aktuell ausgewählten Text ermitteln
        current_selection = self.voelker_auswahlen.get(volk_name, {}).get(auswahl_typ, None)

        # Ausgewähltes Element anzeigen (wenn vorhanden)
        if current_selection and current_selection != placeholder_text:
            auswahl_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(44),
                spacing=dp(10)
            )
            # Hintergrundfarbe sicherstellen (nie None)
            if hasattr(self, 'theme_cls') and self.theme_cls:
                bg_color = self.theme_cls.primaryContainerColor
            else:
                bg_color = [0.7, 0.8, 1.0, 1.0]  # hellblau als Fallback
            
            selected_chip = MDChip(
                MDChipText(text=current_selection),
                type="filter",
                active=True,
                md_bg_color=bg_color,
            )
            auswahl_row.add_widget(selected_chip)

            # Ändern-Button
            aendern_button = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(dp(44), dp(44)),
            )
            auswahl_row.add_widget(aendern_button)
            section_content.add_widget(auswahl_row)

        # Suchfeld
        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            size_hint_x=1
        )
        search_field.add_widget(MDTextFieldHintText(text="Suchen..."))

        # Filter-Toggle State
        filter_state = {'nur_verfuegbare': True}

        # Suchzeile mit optionalem Filter-Button
        search_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10)
        )
        search_row.add_widget(search_field)

        if get_alle_items_func:
            filter_button = MDIconButton(
                icon="filter",
                style="tonal",
                size_hint=(None, None),
                size=(dp(56), dp(56))
            )
            search_row.add_widget(filter_button)

        # Scrollbare Chip-Liste
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200),
        )

        chips_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(4)]
        )
        chips_container.bind(minimum_height=chips_container.setter('height'))

        def populate_chips(item_list):
            """Befüllt den Container mit Chips."""
            chips_container.clear_widgets()
            search_text = search_field.text.lower() if search_field.text else ""
            for item in sorted(item_list):
                if not item or not str(item).strip():
                    continue
                if item in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
                    continue
                if search_text and search_text not in str(item).lower():
                    continue
                is_selected = (str(item) == current_selection)
                # Hintergrundfarbe sicherstellen (nie None)
                if hasattr(self, 'theme_cls') and self.theme_cls:
                    bg_color = self.theme_cls.primaryContainerColor if is_selected else self.theme_cls.surfaceColor
                else:
                    # Fallback-Farben
                    bg_color = [0.7, 0.8, 1.0, 1.0] if is_selected else [0.95, 0.95, 0.95, 1.0]
                
                chip = MDChip(
                    MDChipText(text=str(item)),
                    type="filter",
                    active=is_selected,
                    md_bg_color=bg_color,
                    size_hint_y=None,
                    height=dp(40),
                    on_release=lambda x, selected_item=item: self._on_chip_selected(select_func, selected_item)
                )
                chips_container.add_widget(chip)

            if not chips_container.children:
                chips_container.add_widget(MDLabel(
                    text="Keine Einträge gefunden",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(40),
                    halign='center'
                ))

        # Initiale Chips anzeigen
        options = get_options_func()
        populate_chips(options)

        scroll_view.add_widget(chips_container)

        # Such-Funktionalität
        def filter_items(instance, text):
            if filter_state['nur_verfuegbare']:
                current_items = get_options_func()
            else:
                current_items = get_alle_items_func() if get_alle_items_func else get_options_func()
            populate_chips(current_items)

        search_field.bind(text=filter_items)

        # Filter-Toggle
        if get_alle_items_func:
            def toggle_filter(instance):
                filter_state['nur_verfuegbare'] = not filter_state['nur_verfuegbare']
                if filter_state['nur_verfuegbare']:
                    filter_button.icon = "filter"
                    filter_button.style = "tonal"
                    current_items = get_options_func()
                else:
                    filter_button.icon = "filter-off"
                    filter_button.style = "outlined"
                    current_items = get_alle_items_func()
                populate_chips(current_items)

            filter_button.bind(on_release=toggle_filter)

        # Aufklapp-Logik: Suchfeld + Chips zunächst versteckt wenn bereits ausgewählt
        expandable_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8)
        )
        expandable_box.bind(minimum_height=expandable_box.setter('height'))
        expandable_box.add_widget(search_row)
        expandable_box.add_widget(scroll_view)

        if current_selection and current_selection != placeholder_text:
            # Versteckt starten - nur Ändern-Button sichtbar
            expandable_box.opacity = 0
            expandable_box.disabled = True
            expandable_box.size_hint_y = None
            expandable_box.height = 0

            def toggle_expand(instance):
                if expandable_box.height == 0:
                    expandable_box.opacity = 1
                    expandable_box.disabled = False
                    expandable_box.size_hint_y = None
                    expandable_box.bind(minimum_height=expandable_box.setter('height'))
                    # Höhe neu berechnen
                    expandable_box.height = search_row.height + scroll_view.height + dp(8)
                else:
                    expandable_box.opacity = 0
                    expandable_box.disabled = True
                    expandable_box.height = 0

            aendern_button.bind(on_release=toggle_expand)

        section_content.add_widget(expandable_box)
        section_card.add_widget(section_content)

        return section_card

    def _on_chip_selected(self, select_func, item):
        """Behandelt die Auswahl eines Chips in der Inline-Auswahl."""
        try:
            Logger.debug(f"Chip ausgewählt: {item}")
            Window.release_all_keyboards()
            if select_func:
                select_func(item)
        except Exception as e:
            Logger.error(f"Fehler bei Chip-Auswahl: {e}", exc_info=True)

    def _show_dropdown_menu(self, items, callback, caller, get_options_func=None, get_alle_items_func=None):
        """Zeigt ein verbessertes Dialog-Menü mit Suchfeld."""
        # Items validieren
        Logger.debug(f"Dialog-Items: {items}")

        if not items:
            Logger.warning("Keine Items für Dialog verfügbar")
            return

        if len(items) == 1 and items[0] in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
            Logger.warning(f"Nur Fehlermeldung verfügbar: {items[0]}")
            return

        try:
            # Erstelle Search-Dialog statt Dropdown
            self._show_search_dialog(items, callback, caller, get_options_func=get_options_func, get_alle_items_func=get_alle_items_func)

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Dialog-Menüs: {e}", exc_info=True)

    def _show_search_dialog(self, items, callback, caller, get_options_func=None, get_alle_items_func=None):
        """Zeigt einen erweiterten Dialog mit Suchfeld für Talent/Attribut/Fertigkeiten-Auswahl.
        Aufbau wie Setting-Wechsel-Dialog für Android-Kompatibilität."""
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText,
            MDDialogContentContainer
        )
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
        from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
        from kivymd.uix.scrollview import MDScrollView

        try:
            # State für Filter-Toggle
            filter_state = {'nur_verfuegbare': True}

            # Hauptcontainer für den Dialog
            dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            dialog_content.bind(minimum_height=dialog_content.setter('height'))

            # Suchzeile mit optionalem Filter-Button
            search_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(56),
                spacing=dp(10)
            )

            # Suchfeld
            search_field = MDTextField(
                mode="outlined",
                size_hint_y=None,
                height=dp(56),
                size_hint_x=1
            )
            search_hint = MDTextFieldHintText(text="Suchen...")
            search_field.add_widget(search_hint)
            search_row.add_widget(search_field)

            # Filter-Button nur anzeigen wenn alle-Items-Funktion vorhanden
            if get_alle_items_func and get_options_func:
                filter_button = MDIconButton(
                    icon="filter",
                    style="tonal",
                    size_hint=(None, None),
                    size=(dp(56), dp(56))
                )
                search_row.add_widget(filter_button)

            # Scrollbare Liste
            scroll_view = MDScrollView(
                size_hint=(1, None),
                height=dp(250),
            )

            # Container für Liste
            list_container = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None)
            )
            list_container.bind(minimum_height=list_container.setter('height'))

            items_list = MDList(
                size_hint_y=None,
                size_hint_x=1
            )
            items_list.bind(minimum_height=items_list.setter('height'))

            def populate_list(item_list):
                """Befüllt die Liste mit Items."""
                items_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                for item in sorted(item_list):
                    if item and str(item).strip():
                        if search_text and search_text not in str(item).lower():
                            continue
                        list_item = MDListItem(
                            size_hint_y=None,
                            height=dp(48),
                            on_release=lambda x, selected_item=item: self._defocus_and_call(lambda: self._on_search_dialog_item_selected(callback, selected_item))
                        )
                        list_item.add_widget(MDListItemHeadlineText(text=str(item)))
                        items_list.add_widget(list_item)

            # Initiale Items anzeigen
            populate_list(items)

            # Container zusammenbauen
            list_container.add_widget(items_list)
            list_container.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
            scroll_view.add_widget(list_container)
            list_container.bind(minimum_height=list_container.setter('height'))

            # Such-Funktionalität
            def filter_items(instance, text):
                if filter_state['nur_verfuegbare']:
                    current_items = get_options_func() if get_options_func else items
                else:
                    current_items = get_alle_items_func() if get_alle_items_func else items
                populate_list(current_items)

            search_field.bind(text=filter_items)

            # Filter-Toggle Funktionalität
            if get_alle_items_func and get_options_func:
                def toggle_filter(instance):
                    filter_state['nur_verfuegbare'] = not filter_state['nur_verfuegbare']
                    if filter_state['nur_verfuegbare']:
                        filter_button.icon = "filter"
                        filter_button.style = "tonal"
                        current_items = get_options_func()
                    else:
                        filter_button.icon = "filter-off"
                        filter_button.style = "outlined"
                        current_items = get_alle_items_func()
                    populate_list(current_items)
                    Logger.debug(f"Filter-Toggle: nur_verfuegbare={filter_state['nur_verfuegbare']}")

                filter_button.bind(on_release=toggle_filter)

            # Container zusammenbauen
            dialog_content.add_widget(search_row)
            dialog_content.add_widget(scroll_view)

            # Buttons innerhalb des Content-Containers (wie Setting-Wechsel-Dialog)
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self.search_dialog.dismiss),
            ))
            dialog_content.add_widget(button_row)

            # Dialog erstellen - auto_dismiss=False für Android-Kompatibilität
            self.search_dialog = MDDialog(
                MDDialogHeadlineText(text="Auswahl treffen"),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                    padding=dp(0),
                ),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )

            self.search_dialog.open()
            Logger.debug(f"Search-Dialog erfolgreich geöffnet mit {len(items)} Items")

        except Exception as e:
            Logger.error(f"Fehler beim Search-Dialog: {e}", exc_info=True)

    def _on_search_dialog_item_selected(self, callback, item):
        """Behandelt die Auswahl eines Items im Search-Dialog."""
        try:
            Logger.debug(f"Search-Dialog-Item ausgewählt: {item}")
            
            if hasattr(self, 'search_dialog'):
                self.search_dialog.dismiss()
                
            # Überprüfen ob es sich um eine Fehlermeldung handelt
            if item in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
                Logger.warning(f"Fehlermeldung ausgewählt: {item}")
                return
                
            # Callback ausführen
            if callback:
                callback(item)
                Logger.debug(f"Callback für Item '{item}' ausgeführt")
            else:
                Logger.warning("Kein Callback für Dialog-Auswahl definiert")
                
        except Exception as e:
            Logger.error(f"Fehler bei Search-Dialog-Auswahl: {e}", exc_info=True)

    # === AUSWAHL-FUNKTIONEN (rufen jetzt volk_funktionen.py auf) ===
    
    def _select_talent(self, volk_name, talent_name):
        """Wählt ein Talent aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter
            
            # Geschäftslogik aufrufen
            success = waehle_freies_talent(charakter, volk_name, talent_name)
            
            if success:
                # UI-lokale Auswahl speichern für Anzeige (an Liste anhängen)
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('talent', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['talent'] = liste
                liste.append(talent_name)

                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)

        except Exception as e:
            Logger.error(f"Fehler bei Talent-Auswahl (UI): {e}", exc_info=True)

    def _select_attribut(self, volk_name, attribut_name):
        """Wählt ein Attribut aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter

            # Geschäftslogik aufrufen
            success = waehle_freies_attribut(charakter, volk_name, attribut_name)

            if success:
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('attribut', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['attribut'] = liste
                liste.append(attribut_name)

                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)

        except Exception as e:
            Logger.error(f"Fehler bei Attribut-Auswahl (UI): {e}", exc_info=True)

    def _select_fertigkeit(self, volk_name, fertigkeit_name):
        """Wählt eine Fertigkeit aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter

            # Geschäftslogik aufrufen
            success = waehle_freie_fertigkeit(charakter, volk_name, fertigkeit_name)

            if success:
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('fertigkeit', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['fertigkeit'] = liste
                liste.append(fertigkeit_name)
                
                # UI aktualisieren  
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                
        except Exception as e:
            Logger.error(f"Fehler bei Fertigkeiten-Auswahl (UI): {e}", exc_info=True)

    def _update_selected_volk_details(self):
        """Aktualisiert die Details des ausgewählten Volks."""
        selected_volk_container = self.ids.selected_volk_container
        selected_volk_container.clear_widgets()
        
        if not self.selected_volk_name:
            return
        
        charakter = self.controller.charakter
        
        if self.selected_volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{self.selected_volk_name}' nicht in voelker gefunden")
            return
        
        volk_obj = charakter.voelker[self.selected_volk_name]  # Das ist ein Volk-Objekt
        
        # Titel mit reduzierter Schriftgröße
        title_label = MDLabel(
            text=self.selected_volk_name,
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(35),
            halign='left',
            valign='center',
            bold=True
        )
        selected_volk_container.add_widget(title_label)
        
        # Effekte-Sektion (Attribute, Fertigkeiten, Robustheit, Bewegungsweite etc.)
        effects = getattr(volk_obj, 'effects', {})
        effekt_zeilen = self._build_effekt_zeilen(effects)
        if effekt_zeilen:
            effekt_label = MDLabel(
                text="Effekte:",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(28),
                halign='left',
                valign='center',
                bold=True
            )
            selected_volk_container.add_widget(effekt_label)

            effekt_text = "\n\n".join([f"• {z}" for z in effekt_zeilen])
            effekt_content = MDLabel(
                text=effekt_text,
                font_style="Body",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='top',
                markup=True
            )

            def _update_effekt_height(label, *args):
                if label.width > 0:
                    label.text_size = (label.width - dp(10), None)
                    label.texture_update()
                    label.height = max(dp(30), label.texture_size[1] + dp(10))

            effekt_content.bind(
                width=lambda inst, w: Clock.schedule_once(lambda dt: _update_effekt_height(inst), 0)
            )
            selected_volk_container.add_widget(effekt_content)

        # Details strukturiert anzeigen - KORRIGIERT: Direkter Zugriff auf Objekt-Attribute
        detail_sections = [
            ('Handicaps', getattr(volk_obj, 'handicaps', [])),
            ('Besonderheiten', getattr(volk_obj, 'besonderheiten', [])),
            ('Talente', getattr(volk_obj, 'talente', [])),
        ]

        # Beschreibung nur hinzufügen, wenn sie existiert
        if hasattr(volk_obj, 'beschreibung'):
            detail_sections.append(('Beschreibung', getattr(volk_obj, 'beschreibung', '')))

        for section_title, content in detail_sections:
            if self._has_valid_content(content):
                # Sektion-Titel mit reduzierter Schriftgröße
                section_label = MDLabel(
                    text=f"{section_title}:",
                    font_style="Body",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(28),
                    halign='left',
                    valign='center',
                    bold=True
                )
                selected_volk_container.add_widget(section_label)

                # Sektion-Inhalt mit dynamischer Höhe
                formatted_text = self._format_content(content)
                content_label = MDLabel(
                    text=formatted_text,
                    font_style="Body",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top',
                    markup=True
                )

                def _update_label_height(label, *args):
                    """Setzt text_size und berechnet Höhe nach Layout-Pass"""
                    if label.width > 0:
                        label.text_size = (label.width - dp(10), None)
                        label.texture_update()
                        label.height = max(dp(30), label.texture_size[1] + dp(10))

                # Erst nach dem nächsten Frame, wenn width bekannt ist
                content_label.bind(
                    width=lambda inst, w: Clock.schedule_once(lambda dt: _update_label_height(inst), 0)
                )

                selected_volk_container.add_widget(content_label)

    def _has_valid_content(self, content):
        """Prüft, ob Content valid und nicht leer ist."""
        if content is None:
            return False
        if isinstance(content, list):
            return len(content) > 0 and any(item and str(item).strip() for item in content)
        if isinstance(content, str):
            return content.strip() != ""
        return bool(content)

    def _format_content(self, content):
        """Formatiert den Inhalt für bessere Darstellung."""
        try:
            if isinstance(content, list):
                valid_items = [str(item).strip() for item in content if item and str(item).strip()]
                if not valid_items:
                    return "Keine Details verfügbar"
                # VERBESSERT: Mehr Abstand zwischen Bulletpoints
                return "\n\n".join([f"• {item}" for item in valid_items])  # Doppelte Leerzeile für besseren Abstand
            else:
                text = str(content).strip()
                if not text:
                    return "Keine Details verfügbar"
                
                # Lange kommaseparierte Listen formatieren
                if ", " in text and len(text) > 80:
                    parts = [part.strip() for part in text.split(", ") if part.strip()]
                    # VERBESSERT: Mehr Abstand zwischen Bulletpoints
                    return "\n\n".join([f"• {part}" for part in parts])  # Doppelte Leerzeile
                
                # Lange Texte bei Satzzeichen umbrechen
                if len(text) > 100:
                    sentences = []
                    current = ""
                    for char in text:
                        current += char
                        if char in '.!?' and len(current) > 40:
                            sentences.append(current.strip())
                            current = ""
                    if current.strip():
                        sentences.append(current.strip())
                    # VERBESSERT: Bessere Formatierung für Sätze
                    return "\n\n".join(sentences) if len(sentences) > 1 else text
                
                return text
        except Exception as e:
            Logger.error(f"Fehler beim Formatieren des Inhalts: {e}")
            return "Fehler beim Anzeigen der Details"

    def _build_effekt_zeilen(self, effects):
        """Baut eine Liste lesbarer Zeilen aus dem Volk-Effects-Dictionary."""
        zeilen = []
        if not effects:
            return zeilen

        # Attribut-Boni / -Mali
        for attr_name, bonus in effects.get('attribute_bonuses', {}).items():
            if bonus > 0:
                zeilen.append(f"{attr_name} W{4 + bonus}")
            elif bonus < 0:
                zeilen.append(f"{attr_name} W{4 + bonus}")

        # Fertigkeits-Startboni
        for fert_name, bonus in effects.get('fertigkeits_startboni', {}).items():
            if bonus > 0:
                zeilen.append(f"{fert_name} W{4 + bonus}")
            elif bonus == 0:
                zeilen.append(f"{fert_name} W4")

        # Robustheit
        rob = effects.get('robustheit_bonus', 0)
        if rob != 0:
            zeilen.append(f"Robustheit {rob:+d}")

        # Bewegungsweite
        bew = effects.get('bewegungsweite_bonus', 0)
        if bew != 0:
            zeilen.append(f"Bewegungsweite {bew:+d}")

        # Auto-Talente
        for talent in effects.get('auto_talente', []):
            zeilen.append(f"Talent: {talent}")

        # Auto-Handicaps
        for handicap in effects.get('auto_handicaps', []):
            zeilen.append(f"Handicap: {handicap}")

        # Spezielle Effekte
        spezial = effects.get('spezielle_effekte', {})
        if isinstance(spezial, dict):
            for key, val in spezial.items():
                if val:
                    zeilen.append(key.replace('_', ' ').capitalize())
        elif isinstance(spezial, list):
            for item in spezial:
                if isinstance(item, dict):
                    zeilen.append(item.get('typ', '').replace('_', ' ').capitalize())
                else:
                    zeilen.append(str(item))

        # Wahlmöglichkeiten
        wahl = effects.get('wahlmoeglichkeiten', {})
        if wahl.get('freies_talent'):
            zeilen.append("Freies Anfängertalent")
        if wahl.get('freies_attribut'):
            zeilen.append("Freie Attributserhöhung")

        return zeilen

    # === NEUE METHODEN FÜR ERWEITERTE VÖLKER-WAHLMÖGLICHKEITEN ===

    def _create_halbelf_entweder_oder_section(self):
        """
        NEUE: Erstellt spezielle Halbelf ENTWEDER/ODER Sektion.
        Halbelf kann ENTWEDER freies Talent ODER Geschicklichkeit +2 wählen.
        """
        try:
            # Aktuelle Auswahl prüfen
            current_wahl = self.voelker_auswahlen.get(self.selected_volk_name, {}).get('halbelf_wahl', None)
            hat_talent = current_wahl and current_wahl.startswith('Talent: ')
            hat_attribut = current_wahl == 'Geschicklichkeit W6'

            # Kompaktere Werte für Mobile
            _pad = dp(10) if _mobile else dp(14)
            _spacing = dp(6) if _mobile else dp(10)
            _btn_spacing = dp(10) if _mobile else dp(20)
            _btn_height = dp(40) if _mobile else dp(48)
            _row_height = dp(44) if _mobile else dp(55)
            _title_height = dp(30) if _mobile else dp(40)

            # Hauptcontainer für die Sektion
            section_card = MDCard(
                size_hint_x=1,
                size_hint_y=None,
                padding=_pad,
                elevation=3,
                radius=[12],
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                style="elevated",
            )
            section_card.bind(minimum_height=section_card.setter('height'))

            section_content = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=_spacing
            )
            section_content.bind(minimum_height=section_content.setter('height'))

            # Titel der Sektion mit reduzierter Schriftgröße
            titel_label = MDLabel(
                text="Erbe (ENTWEDER freies Talent ODER Geschicklichkeit W4 -> W6):",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=_title_height,
                halign='left',
                valign='top',
                bold=True
            )
            titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
            titel_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(_title_height, instance.texture_size[1] + dp(6))))

            # Zwei Buttons für die Auswahl
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=_row_height,
                spacing=_btn_spacing
            )

            # Button 1: Freies Talent - filled wenn ausgewählt
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._halbelf_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: Geschicklichkeit +2 - filled wenn ausgewählt
            attribut_button = MDButton(
                style="filled" if hat_attribut else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._halbelf_waehle_attribut()
            )
            attribut_button.add_widget(MDButtonText(text="Geschicklichkeit W6"))

            buttons_row.add_widget(talent_button)
            buttons_row.add_widget(attribut_button)

            section_content.add_widget(titel_label)
            section_content.add_widget(buttons_row)

            # Aktuelle Auswahl anzeigen
            if current_wahl:
                auswahl_label = MDLabel(
                    text=f"Gewählt: {current_wahl}",
                    font_style="Body",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(24) if _mobile else dp(30),
                    halign='left',
                    valign='center',
                    bold=True
                )
                section_content.add_widget(auswahl_label)

            section_card.add_widget(section_content)

            Logger.debug(f"Halbelf ENTWEDER/ODER Sektion erstellt (Auswahl: {current_wahl})")
            return section_card

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Halbelf ENTWEDER/ODER Sektion: {e}")
            # Fallback: Leere Card zurückgeben
            return MDCard(size_hint_x=1, size_hint_y=None, height=dp(50))

    def _create_menschen_vielseitig_section(self):
        """
        Erstellt spezielle Menschen-Vielseitig ENTWEDER/ODER Sektion.
        Mensch kann ENTWEDER freies Talent ODER +2 Fertigkeitspunkte wählen.
        """
        try:
            from functions.volk_funktionen import (
                _get_menschen_freies_talent, _get_mensch_fertigkeitspunkte_gewaehlt
            )

            charakter = self.controller.charakter

            # Aktuelle Auswahl prüfen
            current_wahl = self.voelker_auswahlen.get(self.selected_volk_name, {}).get('vielseitig_wahl', None)
            hat_talent = current_wahl and current_wahl.startswith('Talent: ')
            hat_fertigkeitspunkte = current_wahl == '+2 Fertigkeitspunkte'

            # Kompaktere Werte für Mobile
            _pad = dp(10) if _mobile else dp(14)
            _spacing = dp(6) if _mobile else dp(10)
            _btn_spacing = dp(10) if _mobile else dp(20)
            _btn_height = dp(40) if _mobile else dp(48)
            _row_height = dp(44) if _mobile else dp(55)
            _title_height = dp(30) if _mobile else dp(40)

            # Hauptcontainer
            section_card = MDCard(
                size_hint_x=1,
                size_hint_y=None,
                padding=_pad,
                elevation=3,
                radius=[12],
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                style="elevated",
            )
            section_card.bind(minimum_height=section_card.setter('height'))

            section_content = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=_spacing
            )
            section_content.bind(minimum_height=section_content.setter('height'))

            # Titel
            titel_label = MDLabel(
                text="Vielseitig (ENTWEDER freies Talent ODER +2 Fertigkeitspunkte):",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=_title_height,
                halign='left',
                valign='top',
                bold=True
            )
            titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
            titel_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(_title_height, instance.texture_size[1] + dp(6))))

            # Zwei Buttons
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=_row_height,
                spacing=_btn_spacing
            )

            # Button 1: Freies Talent
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._mensch_vielseitig_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: +2 Fertigkeitspunkte
            fp_button = MDButton(
                style="filled" if hat_fertigkeitspunkte else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._mensch_vielseitig_waehle_fertigkeitspunkte()
            )
            fp_button.add_widget(MDButtonText(text="+2 Fertigkeitspunkte"))

            buttons_row.add_widget(talent_button)
            buttons_row.add_widget(fp_button)

            section_content.add_widget(titel_label)
            section_content.add_widget(buttons_row)

            # Aktuelle Auswahl anzeigen
            if current_wahl:
                auswahl_label = MDLabel(
                    text=f"Gewählt: {current_wahl}",
                    font_style="Body",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(24) if _mobile else dp(30),
                    halign='left',
                    valign='center',
                    bold=True
                )
                section_content.add_widget(auswahl_label)

            section_card.add_widget(section_content)

            Logger.debug(f"Menschen Vielseitig Sektion erstellt (Auswahl: {current_wahl})")
            return section_card

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Menschen-Vielseitig Sektion: {e}")
            return MDCard(size_hint_x=1, size_hint_y=None, height=dp(50))

    def _mensch_vielseitig_waehle_talent(self):
        """Menschen-Vielseitig: Wählt freies Talent (ENTWEDER-Option)."""
        try:
            Logger.debug("Mensch Vielseitig: Freies Talent-Option ausgewählt")

            charakter = self.controller.charakter
            freie_talente = get_freie_talente(charakter)

            if not freie_talente or freie_talente == [NO_TALENT_AVAILABLE_TEXT]:
                Logger.warning("Keine freien Talente verfügbar")
                return

            # Dropdown-Menü für Talent-Auswahl erstellen
            menu_items = []
            for talent in freie_talente:
                menu_items.append({
                    "text": talent,
                    "on_release": lambda t=talent: self._mensch_vielseitig_talent_gewaehlt(t)
                })

            self._talent_menu = MDDropdownMenu(
                caller=self.ids.zusatzelemente_container,
                items=menu_items,
                width_mult=4,
                max_height=dp(300)
            )
            self._talent_menu.open()

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Auswahl: {e}")

    def _mensch_vielseitig_talent_gewaehlt(self, talent_name):
        """Callback wenn Talent aus Dropdown gewählt wird."""
        try:
            if hasattr(self, '_talent_menu'):
                self._talent_menu.dismiss()

            charakter = self.controller.charakter
            success = waehle_mensch_talent(charakter, self.selected_volk_name, talent_name)

            if success:
                # Auswahl im Dictionary speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['vielseitig_wahl'] = f"Talent: {talent_name}"

                # UI aktualisieren
                self._update_zusatzelemente()

                # Controller informieren
                if hasattr(self.controller, 'dispatch'):
                    self.controller.dispatch('on_charakter_updated')

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Callback: {e}")

    def _mensch_vielseitig_waehle_fertigkeitspunkte(self):
        """Menschen-Vielseitig: Wählt +2 Fertigkeitspunkte (ODER-Option)."""
        try:
            Logger.debug("Mensch Vielseitig: +2 Fertigkeitspunkte-Option ausgewählt")

            charakter = self.controller.charakter
            success = waehle_mensch_fertigkeitspunkte(charakter, self.selected_volk_name)

            if success:
                # Auswahl im Dictionary speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['vielseitig_wahl'] = '+2 Fertigkeitspunkte'

                # UI aktualisieren
                self._update_zusatzelemente()

                # Controller informieren
                if hasattr(self.controller, 'dispatch'):
                    self.controller.dispatch('on_charakter_updated')

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Fertigkeitspunkte-Callback: {e}")

    def _halbelf_waehle_talent(self):
        """NEUE: Halbelf wählt freies Talent (ENTWEDER-Option)."""
        try:
            Logger.debug("Halbelf: Freies Talent-Option ausgewählt")

            charakter = self.controller.charakter
            freie_talente = get_freie_talente(charakter)

            if not freie_talente or freie_talente == [NO_TALENT_AVAILABLE_TEXT]:
                Logger.warning("Keine freien Talente für Halbelf verfügbar")
                return

            # Zeige Talent-Auswahl Dialog mit Filter-Button
            self._show_search_dialog(
                freie_talente,
                lambda talent: self._halbelf_talent_selected(talent),
                None,
                get_options_func=lambda: get_freie_talente(charakter),
                get_alle_items_func=lambda: get_freie_talente(charakter, nur_verfuegbare=False)
            )
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Talent-Wahl: {e}", exc_info=True)

    def _halbelf_waehle_attribut(self):
        """NEUE: Halbelf wählt Geschicklichkeit +2 (ODER-Option)."""
        try:
            Logger.debug("Halbelf: Geschicklichkeit +2 Option ausgewählt")
            
            charakter = self.controller.charakter
            success = waehle_halbelf_attribut(charakter, self.selected_volk_name)
            
            if success:
                # UI-lokale Auswahl speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['halbelf_wahl'] = 'Geschicklichkeit W6'
                
                Logger.info(f"Halbelf '{self.selected_volk_name}' hat Geschicklichkeit +2 gewählt")
                
                # UI aktualisieren - zeige Bestätigung statt erneutem Dropdown
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            else:
                Logger.error("Fehler beim Anwenden des Geschicklichkeits-Bonus für Halbelf")
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Attribut-Wahl: {e}", exc_info=True)

    def _halbelf_talent_selected(self, talent_name):
        """NEUE: Callback für Halbelf Talent-Auswahl."""
        try:
            Logger.debug(f"Halbelf Talent ausgewählt: {talent_name}")
            
            charakter = self.controller.charakter
            success = waehle_halbelf_talent(charakter, self.selected_volk_name, talent_name)
            
            if success:
                # UI-lokale Auswahl speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['halbelf_wahl'] = f'Talent: {talent_name}'
                
                Logger.info(f"Halbelf '{self.selected_volk_name}' hat Talent '{talent_name}' gewählt")
                
                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            else:
                Logger.error(f"Fehler beim Auswählen des Talents '{talent_name}' für Halbelf")
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Talent-Auswahl: {e}", exc_info=True)