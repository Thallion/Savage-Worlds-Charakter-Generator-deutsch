# backup/template_management_backup.py
"""
BACKUP: Template-Management-Code aus CharakterVerwaltungWidget
Ausgelagert am 2026-03-21, da noch nicht ausgereift.
Kann später wieder eingebaut werden.
"""

# ==================== IMPORTS (benötigt für Template-Management) ====================
# from controllers.template_handler import TemplateHandler

# ==================== HANDLER-INITIALISIERUNG ====================
# In _initialize_handlers():
#     self.template_handler = TemplateHandler(self)

# ==================== TEMPLATE-MANAGEMENT METHODEN ====================

"""
def open_template_selection_dialog(self):
    '''Öffnet Template-Auswahl Dialog'''
    return self.template_handler.open_template_selection_dialog()

def show_template_selection_dialog(self):
    '''Zeigt Template-Auswahl Dialog'''
    return self.template_handler.show_template_selection_dialog()

def generate_character_from_selected_template(self):
    '''Generiert Charakter aus ausgewähltem Template'''
    return self.template_handler.generate_character_from_selected_template()

@property
def selected_template(self):
    '''Property für ausgewähltes Template (für KV-Zugriff)'''
    if hasattr(self, 'template_handler') and self.template_handler:
        return getattr(self.template_handler, 'selected_template', None)
    return None

def create_template_wizard(self):
    '''Startet den Template-Wizard für benutzerfreundliche Template-Erstellung'''
    try:
        from views.template_wizard import show_template_wizard

        def on_template_created(template_path, template_data):
            '''Callback nach erfolgreicher Template-Erstellung'''
            Logger.info(f"Template erstellt: {template_path}")

            # Template-Handler aktualisieren falls verfügbar
            if hasattr(self, 'template_handler') and self.template_handler:
                # Templates neu laden
                self.template_handler._load_templates()

                # Neues Template automatisch auswählen
                template_name = template_data.get('name', 'Neues Template')
                self.template_handler.selected_template = {
                    'name': template_name,
                    'path': str(template_path),
                    'data': template_data
                }
                Logger.info(f"Template '{template_name}' automatisch ausgewählt")

            # Erfolgs-Dialog anzeigen
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(
                    f"Template '{template_data.get('name', 'Unbenannt')}' wurde erfolgreich erstellt und ist jetzt verfügbar!",
                    "Template-Wizard erfolgreich"
                )

        # Wizard starten
        show_template_wizard(callback=on_template_created)
        Logger.info("Template-Wizard gestartet")

    except Exception as e:
        Logger.error(f"Fehler beim Starten des Template-Wizards: {e}")

        # Fehler-Dialog anzeigen
        from services.service_container import service_container
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_error_dialog(
                f"Template-Wizard konnte nicht gestartet werden: {str(e)}"
            )
"""

# ==================== KV-LAYOUT (Desktop) ====================
"""
# Template Management Bereich
MDCard:
    style: "elevated"
    md_bg_color: app.theme_cls.surfaceContainerColor
    padding: "16dp"
    size_hint_y: None
    adaptive_height: True

    MDBoxLayout:
        orientation: "vertical"
        spacing: "12dp"
        adaptive_height: True

        MDLabel:
            text: "Template-Management"
            theme_text_color: "Primary"
            font_style: "Title"
            size_hint_y: None
            height: "40dp"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "8dp"
            size_hint_y: None
            height: "50dp"

            MDButton:
                style: "elevated"
                on_release: root.open_template_selection_dialog()

                MDButtonIcon:
                    icon: "file-document-multiple"

                MDButtonText:
                    text: "Template auswählen"

            MDButton:
                style: "elevated"
                on_release: root.generate_character_from_selected_template()
                disabled: not root.selected_template

                MDButtonIcon:
                    icon: "auto-fix"

                MDButtonText:
                    text: "Charakter generieren"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: "8dp"
            size_hint_y: None
            height: "50dp"

            MDButton:
                style: "filled"
                on_release: root.create_template_wizard()

                MDButtonIcon:
                    icon: "file-document-plus"

                MDButtonText:
                    text: "Neues Template erstellen"

        # Template Info
        MDCard:
            style: "outlined"
            size_hint_y: None
            height: "60dp" if root.selected_template else "40dp"
            padding: "8dp"

            MDLabel:
                text: f"Ausgewählt: {root.selected_template['name'] if root.selected_template else 'Kein Template'}"
                theme_text_color: "Secondary"
                font_style: "Body"
                halign: "center"
"""

# ==================== KV-LAYOUT (Mobile) ====================
"""
# ===== Template-Management =====
MDBoxLayout:
    orientation: 'vertical'
    spacing: dp(8)
    size_hint_y: None
    height: self.minimum_height
    padding: [dp(4), dp(8)]

    MDLabel:
        text: "Templates"
        bold: True
        size_hint_y: None
        height: dp(32)

    MDGridLayout:
        cols: 2
        spacing: dp(6)
        size_hint_y: None
        height: dp(48)

        MDButton:
            style: "elevated"
            size_hint_x: 1
            on_release: root.open_template_selection_dialog()
            MDButtonIcon:
                icon: "file-document-multiple"
            MDButtonText:
                text: "Auswählen"

        MDButton:
            style: "elevated"
            size_hint_x: 1
            on_release: root.generate_character_from_selected_template()
            disabled: not root.selected_template
            MDButtonIcon:
                icon: "auto-fix"
            MDButtonText:
                text: "Generieren"

    MDButton:
        style: "filled"
        size_hint_x: 1
        on_release: root.create_template_wizard()
        MDButtonIcon:
            icon: "file-document-plus"
        MDButtonText:
            text: "Neues Template erstellen"

    # Template Info
    MDLabel:
        text: f"Ausgewählt: {root.selected_template['name'] if root.selected_template else 'Kein Template'}"
        theme_text_color: "Secondary"
        font_style: "Body"
        size_hint_y: None
        height: dp(32)
        halign: "center"
"""
