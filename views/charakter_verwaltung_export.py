# views/charakter_verwaltung_export.py
"""
Charakterbogen-Export der Charakterverwaltung: PDF/HTML erzeugen und
gespeicherte Bögen auflisten/öffnen.
Mixin von CharakterVerwaltungWidget (views/charakter_verwaltung_widget.py).
"""

from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from services.service_container import service_container, get_event_service
from utils.platform_utils import is_mobile_layout, landscape_height
import os

from utils.platform_utils import is_mobile_layout
_mobile = is_mobile_layout()


class CharakterbogenExportMixin:

    def erzeuge_charakterbogen_pdf(self):
        """Erstellt Charakterbogen als PDF"""
        from kivy.utils import platform as kivy_platform

        # Auf Android: Nutze HTML->PDF über PrintManager
        if kivy_platform == 'android':
            if hasattr(self, 'html_manager') and self.html_manager:
                return self.html_manager.create_character_pdf_android()
            else:
                Logger.error("HTMLManager nicht verfügbar für Android-PDF")
                return

        # Auf Desktop: Nutze klassischen PDF-Manager
        return self.character_handler.erzeuge_charakterbogen_pdf()

    def erzeuge_charakterbogen_html(self):
        """Erstellt Charakterbogen als HTML"""
        if hasattr(self, 'html_manager') and self.html_manager:
            return self.html_manager.create_character_html()
        else:
            Logger.error("HTMLManager nicht verfügbar")

    def lade_charakterbogen(self):
        """Öffnet einen gespeicherten Charakterbogen (HTML oder PDF)"""
        try:
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                return

            chars_dir = file_service.get_default_directory('chars')
            self._show_charakterbogen_file_list(chars_dir)
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakterbogens: {e}")

    def _show_charakterbogen_file_list(self, chars_dir):
        """Zeigt eine Liste aller HTML/PDF Charakterbögen zum Öffnen"""
        import glob as glob_mod

        # HTML und PDF Dateien suchen
        files = []
        for ext in ('*.html', '*.pdf'):
            files.extend(glob_mod.glob(os.path.join(str(chars_dir), ext)))

        if not files:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_info_dialog(
                    "Keine Charakterbögen (HTML/PDF) gefunden.\n"
                    "Erstelle zuerst einen Charakterbogen über 'HTML erstellen' oder 'PDF erstellen'.",
                    "Keine Dateien"
                )
            return

        # Nach Änderungsdatum sortieren (neueste zuerst)
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

        self._bogen_selected_file = files[0] if files else None

        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        # Suchfeld
        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            size_hint_x=1
        )
        search_field.add_widget(MDTextFieldHintText(text="Datei suchen..."))
        dialog_content.add_widget(search_field)

        # Scrollbare Liste
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=landscape_height(280, 0.45),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(20) if _mobile else dp(15),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            scroll_view.scroll_type = ['bars', 'content']
        scroll_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None))
        items_list = MDList(size_hint_y=None, size_hint_x=1)
        items_list.bind(minimum_height=items_list.setter('height'))
        scroll_layout.add_widget(items_list)
        scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
        scroll_view.add_widget(scroll_layout)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        dialog_content.add_widget(scroll_view)

        def populate_list(*args):
            items_list.clear_widgets()
            search_text = search_field.text.lower() if search_field.text else ""
            pending = self._bogen_selected_file

            for fpath in files:
                fname = os.path.basename(fpath)
                if search_text and search_text not in fname.lower():
                    continue
                is_sel = (pending == fpath)
                is_pdf = fname.lower().endswith('.pdf')
                icon = "file-pdf-box" if is_pdf else "language-html5"

                item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, p=fpath: _select_file(p),
                    md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                )
                if is_sel:
                    item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                else:
                    item.add_widget(MDListItemLeadingIcon(icon=icon))
                headline = MDListItemHeadlineText(text=fname)
                if is_sel:
                    headline.bold = True
                item.add_widget(headline)
                items_list.add_widget(item)

        def _select_file(fpath):
            self._bogen_selected_file = fpath
            populate_list()

        search_field.bind(text=populate_list)
        populate_list()

        # Button-Zeile
        button_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_cancel = MDButton(
            MDButtonText(text="Abbrechen"),
            style="text",
            on_release=lambda x: self._bogen_dialog.dismiss(),
        )
        btn_open = MDButton(
            MDButtonText(text="Öffnen"),
            style="text",
            on_release=lambda x: self._open_selected_bogen(),
        )
        button_row.add_widget(btn_cancel)
        button_row.add_widget(btn_open)
        dialog_content.add_widget(button_row)

        self._bogen_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakterbogen öffnen"),
            MDDialogContentContainer(
                dialog_content, orientation="vertical", padding=dp(0)
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._bogen_dialog.open()

    def _open_selected_bogen(self):
        """Öffnet den ausgewählten Charakterbogen"""
        self._bogen_dialog.dismiss()
        fpath = getattr(self, '_bogen_selected_file', None)
        if not fpath:
            return

        try:
            from kivy.utils import platform as kivy_platform
            is_pdf = fpath.lower().endswith('.pdf')
            mime = 'application/pdf' if is_pdf else 'text/html'

            if kivy_platform == 'android':
                from manager.html_manager import HTMLManager
                HTMLManager._open_file_on_android(fpath, mime)
            else:
                import webbrowser
                file_url = 'file://' + os.path.abspath(fpath)
                webbrowser.open(file_url)
                Logger.info(f"Charakterbogen geöffnet: {file_url}")
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Charakterbogens: {e}")
            if self.dialog_service:
                self.dialog_service.show_error_dialog(
                    f"Fehler beim Öffnen: {e}"
                )
