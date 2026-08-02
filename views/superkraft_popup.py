# views/superkraft_popup.py
"""
Popup-System für Superkräfte-Auswahl und -Konfiguration.
Superkräfte werden aus dem Setting gewählt (nicht manuell erstellt).
Zwei Dialog-Stufen:
1. Auswahl-Dialog: Liste verfügbarer Superkräfte mit Suche
2. Konfigurations-Dialog: Kosten festlegen und Modifikatoren wählen
"""
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingCheckbox,
)
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView

import functions.superkraft_funktionen as superkraft_funktionen

import os
import sys
import time

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    kv_path = os.path.join(base_path, 'views', 'superkraft_popup.kv')
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"superkraft_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()


class SuperkraftAuswahlContent(MDBoxLayout):
    """Content-Widget für den Superkraft-Auswahl-Dialog.
    Zeigt eine durchsuchbare Liste verfügbarer Superkräfte."""

    def __init__(self, krafte_list=None, on_kraft_selected=None, **kwargs):
        super().__init__(**kwargs)
        self.alle_krafte = krafte_list or []
        self.on_kraft_selected_callback = on_kraft_selected
        self.kraft_items = {}
        Clock.schedule_once(self._build_list, 0.1)

    def _build_list(self, dt):
        """Erstellt die Kräfte-Liste."""
        self._update_list(self.alle_krafte)

    def on_search_text(self, text):
        """Filtert die Liste bei Texteingabe."""
        if not text.strip():
            self._update_list(self.alle_krafte)
        else:
            gefiltert = [k for k in self.alle_krafte
                        if text.lower() in k['name'].lower()]
            self._update_list(gefiltert)

    def _update_list(self, krafte):
        """Aktualisiert die angezeigte Liste."""
        # Entferne die alte Liste falls vorhanden
        old_scroll = None
        for child in self.children:
            if isinstance(child, MDScrollView):
                old_scroll = child
                break
        if old_scroll:
            self.remove_widget(old_scroll)

        scroll = MDScrollView(size_hint_y=1)
        list_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(2),
            size_hint_y=None,
            padding=(0, 0, 0, 0),
        )
        list_box.bind(minimum_height=list_box.setter('height'))

        for kraft_data in krafte:
            name = kraft_data['name']
            kosten = kraft_data.get('kosten', '')
            beschreibung = kraft_data.get('beschreibung', '')

            kosten_text = f"SKP: {kosten}"
            if kraft_data.get('ausgewaehlt', False):
                kosten_text += " [bereits gewählt]"

            item = MDListItem(
                MDListItemHeadlineText(text=name),
                MDListItemSupportingText(text=kosten_text),
                on_release=lambda x, n=name: self._on_item_click(n),
            )

            # Bereits gewählte Kräfte visuell markieren
            if kraft_data.get('ausgewaehlt', False):
                item.disabled = True

            list_box.add_widget(item)

        scroll.add_widget(list_box)
        self.add_widget(scroll)

        # Höhe anpassen
        list_height = min(len(krafte) * dp(72), dp(400))
        self.height = dp(60) + list_height

    def _on_item_click(self, kraft_name):
        """Callback wenn eine Kraft aus der Liste gewählt wird."""
        if self.on_kraft_selected_callback:
            self.on_kraft_selected_callback(kraft_name)


class SuperkraftKonfigContent(MDBoxLayout):
    """Content-Widget für den Superkraft-Konfigurations-Dialog.
    Hier werden Kosten festgelegt und Modifikatoren gewählt."""

    def __init__(self, kraft_data=None, kraftobergrenze=15,
                 verbleibende_skp=45, **kwargs):
        super().__init__(**kwargs)
        self.kraft_data = kraft_data or {}
        self.kraftobergrenze = kraftobergrenze
        self.verbleibende_skp = verbleibende_skp
        self.gewaehlte_mods = {}
        Clock.schedule_once(self._setup, 0.1)

    def _setup(self, dt):
        """Initialisiert die Felder mit Kraft-Daten."""
        name = self.kraft_data.get('name', '')
        beschreibung = self.kraft_data.get('beschreibung', '')
        kosten = self.kraft_data.get('kosten', '')
        modifikatoren = self.kraft_data.get('modifikatoren', {})

        if hasattr(self.ids, 'kraft_name_label'):
            self.ids.kraft_name_label.text = name

        if hasattr(self.ids, 'kraft_beschreibung_label'):
            self.ids.kraft_beschreibung_label.text = beschreibung

        # Kosten-Info
        kosten_str = str(kosten)
        hat_variable = self._hat_variable_kosten(kosten_str)

        if hasattr(self.ids, 'kosten_input'):
            if not hat_variable:
                # Feste Kosten: Feld vorausfüllen und readonly machen
                try:
                    self.ids.kosten_input.text = str(int(kosten))
                except (ValueError, TypeError):
                    self.ids.kosten_input.text = kosten_str
                self.ids.kosten_input.disabled = True
            else:
                self.ids.kosten_input.text = ""

        if hasattr(self.ids, 'kosten_info_label'):
            if hat_variable:
                self.ids.kosten_info_label.text = f"({kosten_str})"
            else:
                self.ids.kosten_info_label.text = ""

        # Modifikatoren-Liste aufbauen
        self._build_modifikatoren(modifikatoren)

        # Gesamtkosten aktualisieren
        self._update_gesamt_kosten()

    def _hat_variable_kosten(self, kosten_str):
        """Prüft ob variable Kosten vorliegen."""
        kosten_str = kosten_str.strip()
        if not kosten_str:
            return True
        if '-' in kosten_str and kosten_str[0] != '-':
            return True
        if '/' in kosten_str:
            return True
        if kosten_str.lower() == 'speziell':
            return True
        return False

    def _build_modifikatoren(self, modifikatoren):
        """Erstellt die Modifikator-Checkboxen."""
        if not hasattr(self.ids, 'mod_list'):
            return

        self.ids.mod_list.clear_widgets()
        self.gewaehlte_mods = {}

        if not modifikatoren:
            self.ids.modifikatoren_header.text = "Keine Modifikatoren verfügbar"
            return

        self.ids.modifikatoren_header.text = f"Verfügbare Modifikatoren ({len(modifikatoren)}):"

        for mod_name, mod_data in modifikatoren.items():
            mod_kosten = mod_data.get('kosten', 0)
            mod_beschreibung = mod_data.get('beschreibung', '')

            kosten_text = f"{mod_kosten:+d} SKP" if isinstance(mod_kosten, int) else f"{mod_kosten} SKP"

            row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8),
                padding=(dp(8), 0, dp(8), 0),
            )

            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos_hint={"center_y": 0.5},
            )
            checkbox.bind(active=lambda cb, active, mn=mod_name: self._on_mod_toggle(mn, active))

            text_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(2),
            )
            text_box.add_widget(MDLabel(
                text=f"{mod_name} ({kosten_text})",
                theme_text_color="Primary",
                font_style="Body",
                role="medium",
            ))
            if mod_beschreibung:
                text_box.add_widget(MDLabel(
                    text=mod_beschreibung,
                    theme_text_color="Secondary",
                    font_style="Body",
                    role="small",
                ))

            row.add_widget(checkbox)
            row.add_widget(text_box)
            self.ids.mod_list.add_widget(row)

    def _on_mod_toggle(self, mod_name, active):
        """Callback wenn ein Modifikator an/abgewählt wird."""
        # Android Touch-Bounce Debounce PRO Modifikator (Solution 4, siehe
        # docs/ANDROID_WORKAROUNDS.md). Ein gemeinsamer Timer für alle
        # Checkboxen würde beim schnellen Auswählen mehrerer Modifikatoren
        # den zweiten Klick verwerfen — die Checkbox zeigt dann "aktiv",
        # gewaehlte_mods enthält den Modifikator aber nicht.
        now = time.monotonic()
        if not hasattr(self, '_last_mod_toggle_times'):
            self._last_mod_toggle_times = {}
        letzter = self._last_mod_toggle_times.get(mod_name)
        if letzter is not None and (now - letzter) < 0.5:
            return
        self._last_mod_toggle_times[mod_name] = now
        if active:
            mod_data = self.kraft_data.get('modifikatoren', {}).get(mod_name, {})
            self.gewaehlte_mods[mod_name] = mod_data
        else:
            self.gewaehlte_mods.pop(mod_name, None)
        self._update_gesamt_kosten()

    def _update_gesamt_kosten(self):
        """Aktualisiert die Gesamtkosten-Anzeige."""
        basis = self.get_basis_kosten()
        mod_kosten = 0
        for mod_data in self.gewaehlte_mods.values():
            kosten = mod_data.get('kosten', 0)
            if isinstance(kosten, (int, float)):
                mod_kosten += int(kosten)
            elif isinstance(kosten, str):
                try:
                    erster = kosten.split('/')[0].strip()
                    ziffern = ''
                    negativ = erster.startswith('-')
                    for ch in erster.lstrip('-'):
                        if ch.isdigit():
                            ziffern += ch
                        elif ziffern:
                            break
                    if ziffern:
                        wert = int(ziffern)
                        mod_kosten += -wert if negativ else wert
                except (ValueError, IndexError):
                    pass

        gesamt = max(0, basis + mod_kosten)

        if hasattr(self.ids, 'gesamt_kosten_label'):
            text = f"{gesamt} SKP"
            if gesamt > self.kraftobergrenze:
                text += f"  (Obergrenze: {self.kraftobergrenze}!)"
            elif gesamt > self.verbleibende_skp:
                text += f"  (nur {self.verbleibende_skp} verfügbar!)"
            self.ids.gesamt_kosten_label.text = text

    def get_basis_kosten(self):
        """Gibt die eingegebenen Basiskosten zurück."""
        if hasattr(self.ids, 'kosten_input'):
            text = self.ids.kosten_input.text.strip()
            if text.isdigit():
                return int(text)
            # Bei negativen Werten
            if text.startswith('-') and text[1:].isdigit():
                return int(text)
        return 0

    def get_gewaehlte_modifikatoren(self):
        """Gibt die gewählten Modifikatoren zurück."""
        return dict(self.gewaehlte_mods)


class SuperkraftDialogHandler:
    """Verwaltet die Superkraft-Dialoge (Auswahl, Konfiguration, Entfernung)."""

    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.konfig_overlay = None
        self.dialog_content = None
        self.selected_kraft = None

    def _get_charakter(self):
        """Gibt das aktuelle Charakter-Objekt zurück."""
        if self.controller and hasattr(self.controller, 'charakter'):
            return self.controller.charakter
        return None

    def _get_overlay(self):
        """Gibt eine gecachte ElementOverlay-Instanz zurück"""
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def _get_konfig_overlay(self):
        """Gibt eine separate Overlay-Instanz für die Konfiguration zurück"""
        from views.element_overlay import ElementOverlay
        if not self.konfig_overlay:
            self.konfig_overlay = ElementOverlay()
        return self.konfig_overlay

    # ==================== AUSWAHL-DIALOG ====================

    def show_auswahl_dialog(self):
        """Zeigt das Overlay zur Auswahl einer Superkraft."""
        charakter = self._get_charakter()
        if not charakter:
            self.show_error("Kein Charakter verfügbar.")
            return

        krafte_list = self._get_verfuegbare_krafte_list(charakter)
        if not krafte_list:
            self.show_error("Keine Superkräfte im aktuellen Setting verfügbar.")
            return

        self.dialog_content = SuperkraftAuswahlContent(
            krafte_list=krafte_list,
            on_kraft_selected=self._on_kraft_ausgewaehlt,
        )

        overlay = self._get_overlay()
        overlay.open(
            title=f"Superkraft auswählen  —  SKP: {superkraft_funktionen.get_verbleibende_skp(charakter)}/{charakter.superkraft_punkte_gesamt}  |  Obergrenze: {charakter.kraftobergrenze}",
            content_widget=self.dialog_content,
            action_text="Schließen",
            on_action=self.dismiss_dialog,
        )

    def _get_verfuegbare_krafte_list(self, charakter):
        """Erstellt eine Liste aller Superkräfte mit Status-Info."""
        krafte_list = []
        for name, kraft in sorted(charakter.superkraefte.items()):
            krafte_list.append({
                'name': name,
                'kosten': kraft.basis_kosten,
                'beschreibung': kraft.beschreibung,
                'modifikatoren': kraft.verfuegbare_modifikatoren,
                'ausgewaehlt': kraft.ausgewaehlt,
            })
        return krafte_list

    def _on_kraft_ausgewaehlt(self, kraft_name):
        """Callback wenn eine Kraft in der Auswahlliste angeklickt wird."""
        charakter = self._get_charakter()
        if not charakter or kraft_name not in charakter.superkraefte:
            return

        kraft = charakter.superkraefte[kraft_name]
        if kraft.ausgewaehlt:
            return

        # Schließe den Auswahl-Dialog
        self.dismiss_dialog()

        # Öffne den Konfigurations-Dialog
        self.show_konfig_dialog(kraft_name)

    # ==================== KONFIGURATIONS-DIALOG ====================

    def show_konfig_dialog(self, kraft_name):
        """Zeigt das Overlay zur Konfiguration einer Superkraft (Kosten + Modifikatoren)."""
        charakter = self._get_charakter()
        if not charakter or kraft_name not in charakter.superkraefte:
            return

        kraft = charakter.superkraefte[kraft_name]
        self.selected_kraft = kraft_name

        kraft_data = {
            'name': kraft.name,
            'kosten': kraft.basis_kosten,
            'beschreibung': kraft.beschreibung,
            'modifikatoren': kraft.verfuegbare_modifikatoren,
        }

        verbleibend = superkraft_funktionen.get_verbleibende_skp(charakter)

        self.dialog_content = SuperkraftKonfigContent(
            kraft_data=kraft_data,
            kraftobergrenze=charakter.kraftobergrenze,
            verbleibende_skp=verbleibend,
        )

        konfig_overlay = self._get_konfig_overlay()
        konfig_overlay.open(
            title=f"'{kraft_name}' konfigurieren",
            content_widget=self.dialog_content,
            action_text="Hinzufügen",
            on_action=self._on_konfig_bestaetigt,
        )

    def _on_konfig_bestaetigt(self, *args):
        """Callback wenn die Konfiguration bestätigt wird."""
        charakter = self._get_charakter()
        if not charakter or not self.selected_kraft or not self.dialog_content:
            return

        kraft_name = self.selected_kraft
        basis_kosten = self.dialog_content.get_basis_kosten()
        gewaehlte_mods = self.dialog_content.get_gewaehlte_modifikatoren()

        if basis_kosten <= 0:
            self.show_error("Bitte gültige Kosten eingeben (mindestens 1 SKP).")
            return

        # Superkraft auswählen
        result = superkraft_funktionen.waehle_superkraft(charakter, kraft_name, kosten=basis_kosten)

        if result == "ueber_obergrenze":
            self.show_error(
                f"Kosten ({basis_kosten} SKP) überschreiten die Kraftobergrenze "
                f"({charakter.kraftobergrenze} SKP)."
            )
            return
        elif result == "nicht_genug_skp":
            verbleibend = superkraft_funktionen.get_verbleibende_skp(charakter)
            self.show_error(
                f"Nicht genug SKP: {basis_kosten} benötigt, {verbleibend} verfügbar."
            )
            return
        elif result is False:
            self.show_error(f"Superkraft '{kraft_name}' konnte nicht hinzugefügt werden.")
            return

        # Modifikatoren hinzufügen
        for mod_name in gewaehlte_mods:
            mod_result = superkraft_funktionen.waehle_modifikator(charakter, kraft_name, mod_name)
            if mod_result == "ueber_obergrenze":
                Logger.warning(f"Modifikator '{mod_name}' übersteigt Kraftobergrenze - übersprungen")
            elif mod_result == "nicht_genug_skp":
                Logger.warning(f"Nicht genug SKP für Modifikator '{mod_name}' - übersprungen")

        Logger.info(f"Superkraft '{kraft_name}' konfiguriert: "
                   f"{charakter.superkraefte[kraft_name].gesamt_kosten} SKP")

        self._dismiss_konfig_dialog()
        self._refresh_ui()

    # ==================== ENTFERNUNG-DIALOG ====================

    def show_entfernen_dialog(self, kraft_name):
        """Zeigt ein Overlay zum Entfernen einer Superkraft."""
        charakter = self._get_charakter()
        if not charakter or kraft_name not in charakter.superkraefte:
            return

        kraft = charakter.superkraefte[kraft_name]
        if not kraft.ausgewaehlt:
            return

        self.selected_kraft = kraft_name

        # Bestätigungs-Content
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            padding=(dp(16), dp(16), dp(16), dp(16)),
        )
        content.add_widget(MDLabel(
            text=f"'{kraft_name}' entfernen?",
            theme_text_color="Primary",
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(32),
        ))
        content.add_widget(MDLabel(
            text=f"Kosten: {kraft.gesamt_kosten} SKP werden freigegeben.",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(48),
        ))

        overlay = self._get_overlay()
        overlay.open(
            title="Superkraft entfernen",
            content_widget=content,
            action_text="Entfernen",
            on_action=self._on_entfernen_bestaetigt,
        )

    def _on_entfernen_bestaetigt(self, *args):
        """Callback wenn die Entfernung bestätigt wird."""
        charakter = self._get_charakter()
        if not charakter or not self.selected_kraft:
            return

        success = superkraft_funktionen.entferne_superkraft(charakter, self.selected_kraft)
        if success:
            Logger.info(f"Superkraft '{self.selected_kraft}' entfernt")
        else:
            self.show_error(f"Fehler beim Entfernen von '{self.selected_kraft}'")

        self.dismiss_dialog()
        self._refresh_ui()

    # ==================== MACHTSTUFE-DIALOG ====================

    def show_machtstufe_dialog(self):
        """Zeigt ein Overlay zur Auswahl der Machtstufe."""
        charakter = self._get_charakter()
        if not charakter:
            return

        from kivymd.uix.list import MDList, MDListItemLeadingIcon

        aktuelle_stufe = charakter.machtstufe

        stufen_info = {
            "I": "Stufe I - Pulp-Helden (15 SKP)",
            "II": "Stufe II - Straßenkämpfer (30 SKP)",
            "III": "Stufe III - Four-Color-Helden (45 SKP)",
            "IV": "Stufe IV - Schwere Kaliber (60 SKP)",
            "V": "Stufe V - Kosmische Beschützer (75 SKP)",
        }

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            padding=(dp(4), dp(8), dp(4), dp(8)),
        )
        content.bind(minimum_height=content.setter('height'))

        # Hinweis
        content.add_widget(MDLabel(
            text=f"Aktuelle Stufe: {aktuelle_stufe}\nÄnderung der Machtstufe ändert das SKP-Budget!",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(48),
        ))

        list_widget = MDList(
            size_hint_y=None,
        )
        list_widget.bind(minimum_height=list_widget.setter('height'))

        for stufe, text in stufen_info.items():
            ist_aktiv = (stufe == aktuelle_stufe)
            item = MDListItem(
                on_release=lambda x, s=stufe: self._on_machtstufe_gewaehlt(s),
                size_hint_y=None,
                height=dp(56),
            )
            item.add_widget(MDListItemHeadlineText(text=text))
            if ist_aktiv:
                item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                item.md_bg_color = self.overlay.theme_cls.primaryContainerColor if self.overlay else [0.2, 0.5, 0.2, 0.3]
            else:
                item.add_widget(MDListItemLeadingIcon(icon="circle-outline"))
            list_widget.add_widget(item)

        content.add_widget(list_widget)

        overlay = self._get_overlay()
        overlay.open(
            title="Machtstufe wählen",
            content_widget=content,
            action_text="Schließen",
            on_action=self.dismiss_dialog,
        )

    def _on_machtstufe_gewaehlt(self, stufe):
        """Callback wenn eine Machtstufe gewählt wird."""
        charakter = self._get_charakter()
        if not charakter:
            return

        superkraft_funktionen.setze_machtstufe(charakter, stufe)
        self.dismiss_dialog()
        self._refresh_ui()

    # ==================== HILFSMETHODEN ====================

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog."""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_kraft = None

    def _dismiss_konfig_dialog(self, *args):
        """Schließt den Konfigurations-Dialog."""
        if self.konfig_overlay and self.konfig_overlay._is_open:
            self.konfig_overlay.close()
        self.dialog_content = None
        self.selected_kraft = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Superkraft-Fehler: {message}")

    def _refresh_ui(self):
        """Aktualisiert die UI nach Änderungen."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                # SuperkraefteWidget refreshen
                sk_widget = app.get_widget_by_tab_text('Superkräfte', 'superkraefte_widget')
                if sk_widget and hasattr(sk_widget, 'refresh_widget'):
                    Clock.schedule_once(lambda dt: sk_widget.refresh_widget(), 0)
                    Logger.debug("SuperkraftDialogHandler: SuperkraefteWidget refresh ausgelöst")
                else:
                    Logger.warning("SuperkraftDialogHandler: SuperkraefteWidget nicht gefunden")

            # Event-System benachrichtigen
            from services.service_container import service_container
            event_service = service_container.get_event_service()
            if event_service:
                from services.event_service import EventTypes
                event_service.publish(EventTypes.CHARACTER_UPDATED, {})

        except Exception as e:
            Logger.warning(f"Fehler beim UI-Refresh: {e}")
