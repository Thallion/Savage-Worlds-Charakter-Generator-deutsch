# views/charakter_verwaltung_config.py
"""
Konfigurations-Popups der Charakterverwaltung: Charakter-Einstellungen,
Punkte- und Vermögens-Popup.
Mixin von CharakterVerwaltungWidget (views/charakter_verwaltung_widget.py).
"""

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from utils.platform_utils import is_mobile_layout, landscape_height


class CharakterConfigMixin:

    def _show_character_config_popup(self):
        """Schritt 2: Startpunkte und Vermögen konfigurieren.
        Verwendet ModalView statt MDDialog für Android-Kompatibilität."""
        from kivy.uix.modalview import ModalView
        from kivy.animation import Animation

        # Bottom-Padding für Android-Navigationsleiste
        from kivy.utils import platform as kivy_platform
        bottom_pad = dp(48) if kivy_platform == 'android' else 0

        # Sheet-Container
        sheet = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=landscape_height(380, 0.75) + bottom_pad,
            pos_hint={'center_x': 0.5},
            md_bg_color=self.app.theme_cls.surfaceContainerColor,
            radius=[dp(16), dp(16), 0, 0],
            padding=[0, dp(8), 0, bottom_pad],
        )

        # Drag-Handle
        handle_container = MDBoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(20),
            padding=[0, dp(8), 0, dp(4)],
        )
        handle_container.add_widget(MDBoxLayout(
            size_hint=(None, None), size=(dp(32), dp(4)),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.5, 0.5, 0.5, 1), radius=[dp(2)],
        ))
        sheet.add_widget(handle_container)

        # Header: Zurück + Titel + Weiter
        header = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48),
            padding=[dp(8), 0, dp(8), 0], spacing=dp(8),
        )
        from kivymd.uix.button import MDIconButton
        header.add_widget(MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self._config_sheet_back(modal),
            pos_hint={'center_y': 0.5},
        ))
        header.add_widget(MDLabel(
            text="Charakter-Einstellungen",
            font_style="Title", role="medium", bold=True,
            size_hint_x=1, pos_hint={'center_y': 0.5},
        ))
        header.add_widget(MDIconButton(
            icon="check",
            on_release=lambda x: self._config_sheet_confirm(modal),
            pos_hint={'center_y': 0.5},
        ))
        sheet.add_widget(header)

        # Formular-Inhalt
        form = MDBoxLayout(
            orientation='vertical', spacing=dp(16),
            padding=[dp(20), dp(8), dp(20), dp(16)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))

        # Info-Label
        form.add_widget(MDLabel(
            text=f"Setting: {self._wizard_selected_setting}",
            theme_text_color="Secondary", font_style="Body",
            size_hint_y=None, height=dp(24),
        ))

        # Attribut-Punkte
        attr_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        attr_row.add_widget(MDLabel(
            text="Attributs-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_attr_field = MDTextField(
            text="5", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        attr_row.add_widget(self._wizard_attr_field)
        form.add_widget(attr_row)

        # Fertigkeits-Punkte
        fert_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        fert_row.add_widget(MDLabel(
            text="Fertigkeits-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_fert_field = MDTextField(
            text="12", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        fert_row.add_widget(self._wizard_fert_field)
        form.add_widget(fert_row)

        # Vermögen und Währung
        money_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        money_row.add_widget(MDLabel(
            text="Vermögen:", size_hint_x=0.3,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_money_field = MDTextField(
            text="500", mode="outlined",
            size_hint_x=0.35, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        money_row.add_widget(self._wizard_money_field)
        self._wizard_currency_field = MDTextField(
            text="Gold", mode="outlined",
            size_hint_x=0.35, size_hint_y=None, height=dp(56),
        )
        money_row.add_widget(self._wizard_currency_field)
        form.add_widget(money_row)

        sheet.add_widget(form)

        # ModalView erstellen
        modal = ModalView(
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0),
            background='',
            auto_dismiss=False,
        )
        modal.add_widget(sheet)
        self._wizard_config_sheet = sheet
        self._wizard_config_modal = modal

        # Öffnen mit Animation
        modal.open()
        sheet.y = -sheet.height
        Animation(y=0, duration=0.25, t='out_cubic').start(sheet)

    def _config_sheet_back(self, modal):
        """Zurück zur Setting-Auswahl"""
        from kivy.animation import Animation
        sheet = self._wizard_config_sheet
        anim = Animation(y=-sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: modal.dismiss())
        anim.start(sheet)
        Clock.schedule_once(lambda dt: self._show_setting_selection_popup(), 0.3)

    def _config_sheet_confirm(self, modal):
        """Wizard abschließen: Charakter erstellen und zum Profil wechseln"""
        # Werte aus den Feldern lesen
        try:
            attr_punkte = int(self._wizard_attr_field.text)
        except (ValueError, AttributeError):
            attr_punkte = 5
        try:
            fert_punkte = int(self._wizard_fert_field.text)
        except (ValueError, AttributeError):
            fert_punkte = 12
        try:
            vermoegen = int(self._wizard_money_field.text)
        except (ValueError, AttributeError):
            vermoegen = 500
        waehrung = getattr(self._wizard_currency_field, 'text', 'Gold') or 'Gold'

        # Sheet schließen
        from kivy.animation import Animation
        sheet = self._wizard_config_sheet
        anim = Animation(y=-sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: modal.dismiss())
        anim.start(sheet)

        setting_name = self._wizard_selected_setting

        # Charakter erstellen über Controller
        if self.app.controller:
            self.app.controller.neuer_charakter(setting_name=setting_name)

            char = self.app.controller.charakter
            if char:
                char.char_gen_completed = False
                char.maximale_attributsteigerungen = attr_punkte
                char.verbleibende_attributsteigerungen = attr_punkte
                char.maximale_fertigkeitssteigerungen = fert_punkte
                char.verbleibende_fertigkeitssteigerungen = fert_punkte
                char.vermoegen = vermoegen
                char.waehrungseinheit = waehrung

            # UI aktualisieren
            self.character_handler._update_ui_fields()
            self.character_handler._refresh_profil_widget()

        # Zum Profil-Tab wechseln (Index 3)
        Clock.schedule_once(lambda dt: self._switch_to_profil(), 0.3)

        Logger.info(f"Neuer Charakter mit Setting '{setting_name}' erstellt "
                    f"(Attr: {attr_punkte}, Fert: {fert_punkte}, "
                    f"Vermögen: {vermoegen} {waehrung})")

    # ==================== MOBILE POPUPS ====================

    def open_punkte_popup(self):
        """Öffnet Popup für Attribut-/Fertigkeitspunkte (Mobile)"""
        try:
            char = self.app.controller.charakter if self.app.controller else None
            attr_val = str(getattr(char, 'maximale_attributsteigerungen', 5)) if char else '5'
            fert_val = str(getattr(char, 'maximale_fertigkeitssteigerungen', 12)) if char else '12'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Attribut-Punkte
            attr_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            attr_row.add_widget(MDLabel(
                text="Attributs-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_attr_field = MDTextField(
                text=attr_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            attr_row.add_widget(self._popup_attr_field)
            content.add_widget(attr_row)

            # Fertigkeits-Punkte
            fert_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            fert_row.add_widget(MDLabel(
                text="Fertigkeits-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_fert_field = MDTextField(
                text=fert_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            fert_row.add_widget(self._popup_fert_field)
            content.add_widget(fert_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._punkte_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_punkte_popup),
            ))
            content.add_widget(button_row)

            self._punkte_dialog = MDDialog(
                MDDialogHeadlineText(text="Start-Punkte"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._punkte_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Punkte-Popups: {e}")

    def _apply_punkte_popup(self):
        """Wendet die Werte aus dem Punkte-Popup an"""
        try:
            self._punkte_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                attr_val = int(self._popup_attr_field.text)
                old_attr = char.maximale_attributsteigerungen
                differenz = attr_val - old_attr
                char.maximale_attributsteigerungen = attr_val
                char.verbleibende_attributsteigerungen = max(0, char.verbleibende_attributsteigerungen + differenz)
                if 'attributsteigerungen_field' in self.ids:
                    self.ids.attributsteigerungen_field.text = str(attr_val)
            except ValueError:
                pass

            try:
                fert_val = int(self._popup_fert_field.text)
                old_fert = char.maximale_fertigkeitssteigerungen
                differenz = fert_val - old_fert
                char.maximale_fertigkeitssteigerungen = fert_val
                char.verbleibende_fertigkeitssteigerungen = max(0, char.verbleibende_fertigkeitssteigerungen + differenz)
                if 'fertigkeitssteigerungen_field' in self.ids:
                    self.ids.fertigkeitssteigerungen_field.text = str(fert_val)
            except ValueError:
                pass

            # Button-Text aktualisieren
            if 'punkte_button_text' in self.ids:
                self.ids.punkte_button_text.text = (
                    f"Attr: {char.maximale_attributsteigerungen} / "
                    f"Fert: {char.maximale_fertigkeitssteigerungen}"
                )

            Logger.info(f"Punkte aktualisiert: Attr={char.maximale_attributsteigerungen}, "
                        f"Fert={char.maximale_fertigkeitssteigerungen}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Punkte: {e}")

    def open_vermoegen_popup(self):
        """Öffnet Popup für Vermögen/Währung (Mobile)"""
        try:
            char = self.app.controller.charakter if self.app.controller else None
            money_val = str(getattr(char, 'vermoegen', 500)) if char else '500'
            currency_val = str(getattr(char, 'waehrungseinheit', 'Gold')) if char else 'Gold'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Vermögen
            money_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            money_row.add_widget(MDLabel(
                text="Vermögen:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_money_field = MDTextField(
                text=money_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            money_row.add_widget(self._popup_money_field)
            content.add_widget(money_row)

            # Währung
            currency_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            currency_row.add_widget(MDLabel(
                text="Währung:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_currency_field = MDTextField(
                text=currency_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
            )
            currency_row.add_widget(self._popup_currency_field)
            content.add_widget(currency_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._vermoegen_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_vermoegen_popup),
            ))
            content.add_widget(button_row)

            self._vermoegen_dialog = MDDialog(
                MDDialogHeadlineText(text="Vermögen & Währung"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._vermoegen_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Vermögen-Popups: {e}")

    def _apply_vermoegen_popup(self):
        """Wendet die Werte aus dem Vermögen-Popup an"""
        try:
            self._vermoegen_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                money_val = int(self._popup_money_field.text)
                char.vermoegen = money_val
                if 'vermoegen_field' in self.ids:
                    self.ids.vermoegen_field.text = str(money_val)
            except ValueError:
                pass

            currency_val = self._popup_currency_field.text or 'Gold'
            char.waehrungseinheit = currency_val
            if 'waehrung_field' in self.ids:
                self.ids.waehrung_field.text = currency_val

            # Button-Text aktualisieren
            if 'vermoegen_button_text' in self.ids:
                self.ids.vermoegen_button_text.text = f"{char.vermoegen} {char.waehrungseinheit}"

            Logger.info(f"Vermögen aktualisiert: {char.vermoegen} {char.waehrungseinheit}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden des Vermögens: {e}")
