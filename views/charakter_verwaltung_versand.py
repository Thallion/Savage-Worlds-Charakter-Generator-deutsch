# views/charakter_verwaltung_versand.py
"""
Versand-Subsystem der Charakterverwaltung: Charaktere/Settings als Dateien
sammeln und per Share-Intent/Mail versenden.
Mixin von CharakterVerwaltungWidget (views/charakter_verwaltung_widget.py).
"""

from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from pathlib import Path
from services.service_container import service_container, get_event_service
from utils.path_utils import get_application_root, safe_filename_stem
import os

from utils.platform_utils import is_mobile_layout
_mobile = is_mobile_layout()


class CharakterVersandMixin:

    # ==================== TEILEN / VERSENDEN ====================

    def versende_charakter(self):
        """Zeigt Dialog zum Versenden von Charakter-Dateien (JSON, PDF, HTML)"""
        try:
            controller = self.app.controller
            if not controller or not controller.charakter:
                self._show_share_warning("Kein Charakter geladen.")
                return

            char_name = getattr(controller.charakter, 'char_name', 'Charakter')
            char_file_path = getattr(controller, 'current_character_file_path', None)

            # Verfügbare Dateien sammeln
            dateien = self._sammle_charakter_dateien(char_file_path, char_name)

            if not dateien:
                self._show_share_warning(
                    "Keine Charakter-Dateien zum Versenden gefunden.\n"
                    "Speichere den Charakter zuerst."
                )
                return

            self._zeige_versende_dialog(dateien, f"Charakter versenden: {char_name}")
        except Exception as e:
            Logger.error(f"Fehler beim Versenden des Charakters: {e}")

    def _sammle_charakter_dateien(self, char_file_path, char_name):
        """Sammelt alle vorhandenen Dateien eines Charakters (JSON, PDF, HTML)."""
        dateien = []

        if char_file_path and os.path.exists(char_file_path):
            dateien.append({
                'pfad': char_file_path,
                'name': os.path.basename(char_file_path),
                'typ': 'Charakter (JSON)',
                'icon': 'code-json',
            })

            # Zugehörige PDF/HTML im gleichen Verzeichnis suchen
            ordner = os.path.dirname(char_file_path)
            basis = Path(char_file_path).stem

            pdf_pfad = os.path.join(ordner, f"{basis}.pdf")
            if os.path.exists(pdf_pfad):
                dateien.append({
                    'pfad': pdf_pfad,
                    'name': os.path.basename(pdf_pfad),
                    'typ': 'Charakterbogen (PDF)',
                    'icon': 'file-pdf-box',
                })

            html_pfad = os.path.join(ordner, f"{basis}.html")
            if os.path.exists(html_pfad):
                dateien.append({
                    'pfad': html_pfad,
                    'name': os.path.basename(html_pfad),
                    'typ': 'Charakterbogen (HTML)',
                    'icon': 'language-html5',
                })
        else:
            # Kein gespeicherter Charakter - in chars/ und Archetypen/ nach passenden Dateien suchen
            from utils.path_utils import get_chars_path, get_resource_path
            import glob as glob_mod

            chars_dir = get_chars_path()
            for ext in ('*.json', '*.pdf', '*.html'):
                for f in glob_mod.glob(os.path.join(chars_dir, ext)):
                    if char_name.lower() in os.path.basename(f).lower():
                        icon = 'code-json' if f.endswith('.json') else (
                            'file-pdf-box' if f.endswith('.pdf') else 'language-html5'
                        )
                        typ = 'JSON' if f.endswith('.json') else (
                            'PDF' if f.endswith('.pdf') else 'HTML'
                        )
                        dateien.append({
                            'pfad': f,
                            'name': os.path.basename(f),
                            'typ': typ,
                            'icon': icon,
                        })

            # Auch in Archetypen/ suchen (gebündelt + persistentes Verzeichnis auf Android)
            archetypen_dirs = set()
            
            # Suche an mehreren möglichen Stellen (wie in main.py)
            app_root = Path(get_application_root())
            
            # Gebündelte Archetypen aus verschiedenen Quellen
            possible_archetypen = [
                app_root / 'Archetypen',
                app_root / 'chars' / 'Archetypen',
                Path(get_resource_path('Archetypen')),
                Path(get_resource_path('chars/Archetypen')),
            ]
            
            for arch_path in possible_archetypen:
                if arch_path.exists() and arch_path.is_dir():
                    archetypen_dirs.add(str(arch_path))
                    Logger.debug(f"Archetypen: Gefunden in {arch_path}")
            
            # Auf Android: auch im persistenten User-Chars-Verzeichnis
            user_archetypen = os.path.join(get_chars_path(), 'Archetypen')
            archetypen_dirs.add(user_archetypen)

            for archetyps_dir in archetypen_dirs:
                if os.path.isdir(archetyps_dir):
                    for ext in ('*.json', '*.pdf', '*.html'):
                        for f in glob_mod.glob(os.path.join(archetyps_dir, ext)):
                            if char_name.lower() in os.path.basename(f).lower():
                                # Prüfen ob bereits in dateien
                                if not any(d['pfad'] == f for d in dateien):
                                    icon = 'code-json' if f.endswith('.json') else (
                                        'file-pdf-box' if f.endswith('.pdf') else 'language-html5'
                                    )
                                    typ = 'Archetyp (JSON)' if f.endswith('.json') else (
                                        'Archetyp (PDF)' if f.endswith('.pdf') else 'Archetyp (HTML)'
                                    )
                                    dateien.append({
                                        'pfad': f,
                                        'name': os.path.basename(f),
                                        'typ': typ,
                                        'icon': icon,
                                    })

        return dateien

    def _zeige_versende_dialog(self, dateien, titel):
        """Zeigt einen Dialog mit Checkboxen für die zu versendenden Dateien."""
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTrailingCheckbox
        from kivymd.uix.label import MDIcon
        from kivymd.uix.scrollview import MDScrollView

        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(16),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        dialog_content.add_widget(MDLabel(
            text="Dateien zum Versenden auswählen:",
            size_hint_y=None,
            height=dp(30),
        ))

        checkboxes = []

        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=min(dp(300), dp(48) * len(dateien) + dp(20)),
            bar_width=dp(20) if _mobile else dp(15),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            scroll_view.scroll_type = ['bars', 'content']
        scroll_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(48) * len(dateien),
            padding=[0, 0, dp(32), 0] if _mobile else [0, 0, 0, 0],
        )
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        for datei in dateien:
            item = MDListItem(
                size_hint_y=None,
                height=dp(48),
            )
            item.add_widget(MDIcon(
                icon=datei['icon'],
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                pos_hint={"center_y": .5},
            ))
            item.add_widget(MDListItemHeadlineText(
                text=f"{datei['name']} ({datei['typ']})",
            ))

            trailing = MDListItemTrailingCheckbox(
                active=True,
            )
            item.add_widget(trailing)
            checkboxes.append((trailing, datei, item))

            scroll_layout.add_widget(item)

        scroll_view.add_widget(scroll_layout)
        dialog_content.add_widget(scroll_view)

        def _on_versenden(x):
            self._versende_dialog.dismiss()
            ausgewaehlte = [d['pfad'] for cb, d, item in checkboxes if cb.active]
            if ausgewaehlte:
                self._versende_dateien(ausgewaehlte, titel)

        self._versende_dialog = MDDialog(
            MDDialogHeadlineText(text=titel),
            MDDialogContentContainer(dialog_content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._versende_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Versenden"),
                    style="text",
                    on_release=_on_versenden,
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._versende_dialog.open()

    def _versende_dateien(self, dateipfade, titel="Dateien versenden"):
        """Versendet die ausgewählten Dateien über die Plattform-Teilen-Funktion."""
        from utils.share_utils import share_file, share_multiple_files, get_mime_type

        try:
            if len(dateipfade) == 1:
                mime = get_mime_type(dateipfade[0])
                success = share_file(dateipfade[0], mime, titel)
            else:
                success = share_multiple_files(dateipfade, '*/*', titel)

            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog(
                        "Versenden fehlgeschlagen."
                    )
        except Exception as e:
            Logger.error(f"Fehler beim Versenden: {e}")

    def versende_setting(self):
        """Versendet das aktuell aktive Setting als JSON-Datei."""
        try:
            controller = self.app.controller
            if not controller or not controller.charakter:
                self._show_share_warning("Kein Charakter geladen.")
                return

            setting_name = getattr(controller.charakter, 'active_setting_name', None)
            if not setting_name:
                self._show_share_warning("Kein aktives Setting vorhanden.")
                return

            # Setting-Datei finden (zuerst im Benutzer-Verzeichnis, dann nativ)
            from utils.path_utils import get_settings_path, get_user_settings_path

            setting_file = None
            user_file = os.path.join(get_user_settings_path(), f"{setting_name}.json")
            native_file = os.path.join(get_settings_path(), f"{setting_name}.json")

            if os.path.exists(user_file):
                setting_file = user_file
            elif os.path.exists(native_file):
                setting_file = native_file

            if not setting_file:
                self._show_share_warning(f"Setting-Datei für '{setting_name}' nicht gefunden.")
                return

            from utils.share_utils import share_file
            success = share_file(setting_file, 'application/json', f"Setting versenden: {setting_name}")

            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog(
                        "Versenden fehlgeschlagen."
                    )
        except Exception as e:
            Logger.error(f"Fehler beim Versenden des Settings: {e}")

    def _show_share_warning(self, message):
        """Zeigt eine Warnung beim Versenden."""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_warning_dialog(message)
