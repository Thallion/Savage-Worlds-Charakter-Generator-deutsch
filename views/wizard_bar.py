# views/wizard_bar.py
"""
Wizard-Bar Widget für die Anzeige des Wizard-Fortschritts.
"""

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.logger import Logger

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp


class WizardBar(MDBoxLayout):
    """
    Widget zur Anzeige des Wizard-Fortschritts.
    
    Zeigt eine Fortschrittsleiste, den aktuellen Schritt und Navigation.
    """
    
    wizard_service = ObjectProperty(None, allownone=True)
    show_navigation = BooleanProperty(True)
    height = NumericProperty("56dp")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = "8dp"
        self.padding = ["8dp", "4dp", "8dp", "4dp"]
        self.size_hint_y = None
        self.height = "56dp"
        
        self._wizard_callbacks_bound = False
        self._current_popup_dialog = None
    
    def on_wizard_service(self, instance, value):
        """Wird aufgerufen wenn der Wizard-Service gesetzt wird."""
        if value:
            self._bind_wizard_events()
            self._update_display()
        else:
            self._unbind_wizard_events()
    
    def _bind_wizard_events(self):
        """Bindet die Wizard-Events."""
        if not self.wizard_service or self._wizard_callbacks_bound:
            return
        
        self.wizard_service.bind_event('on_wizard_started', self._on_wizard_started)
        self.wizard_service.bind_event('on_wizard_finished', self._on_wizard_finished)
        self.wizard_service.bind_event('on_wizard_cancelled', self._on_wizard_cancelled)
        self.wizard_service.bind_event('on_step_changed', self._on_step_changed)
        self._wizard_callbacks_bound = True
    
    def _unbind_wizard_events(self):
        """Entfernt die Wizard-Events."""
        if not self.wizard_service or not self._wizard_callbacks_bound:
            return
        
        self.wizard_service.unbind_event('on_wizard_started', self._on_wizard_started)
        self.wizard_service.unbind_event('on_wizard_finished', self._on_wizard_finished)
        self.wizard_service.unbind_event('on_wizard_cancelled', self._on_wizard_cancelled)
        self.wizard_service.unbind_event('on_step_changed', self._on_step_changed)
        self._wizard_callbacks_bound = False
    
    def _on_wizard_started(self, schritt):
        """Wird aufgerufen wenn der Wizard startet."""
        Logger.info("WizardBar: Wizard gestartet")
        self._update_display()
    
    def _on_wizard_finished(self):
        """Wird aufgerufen wenn der Wizard beendet wird."""
        Logger.info("WizardBar: Wizard beendet")
        self._update_display()
    
    def _on_wizard_cancelled(self):
        """Wird aufgerufen wenn der Wizard abgebrochen wird."""
        Logger.info("WizardBar: Wizard abgebrochen")
        self._update_display()
    
    def _on_step_changed(self, schritt):
        """Wird aufgerufen wenn sich der Schritt ändert."""
        self._update_display()
        # Erklärungs-Popup automatisch öffnen
        if schritt and schritt.popup_title:
            self.on_help_pressed()
    
    def _update_display(self):
        """Aktualisiert die Anzeige."""
        if not self.wizard_service:
            return
        
        if not self.wizard_service.aktiv:
            return
        
        schritt = self.wizard_service.get_aktueller_schritt()
        if schritt:
            self._update_step_label(schritt)
            self._update_progress()
    
    def _update_step_label(self, schritt):
        """Aktualisiert das Schritt-Label."""
        step_label = self.ids.get('step_label')
        if step_label:
            step_label.text = f"Schritt {self.wizard_service.aktueller_schritt_index + 1}/{len(self.wizard_service.schritte)}: {schritt.title}"
    
    def _update_progress(self):
        """Aktualisiert die Fortschrittsleiste."""
        progress = self.ids.get('progress')
        if progress:
            progress.value = self.wizard_service.get_fortschritt_prozent()
    
    def on_prev_pressed(self):
        """Wird aufgerufen wenn der Zurück-Button gedrückt wird."""
        if self.wizard_service:
            self.wizard_service.vorheriger_schritt()
    
    def on_next_pressed(self):
        """Wird aufgerufen wenn der Weiter-Button gedrückt wird."""
        if self.wizard_service:
            self.wizard_service.naechster_schritt()
    
    def on_cancel_pressed(self):
        """Wird aufgerufen wenn der Abbrechen-Button gedrückt wird."""
        if self.wizard_service:
            self.wizard_service.abbrechen()
    
    def on_skip_pressed(self):
        """Wird aufgerufen wenn der Überspringen-Button gedrückt wird."""
        if self.wizard_service:
            self.wizard_service.schritt_ueberspringen()
    
    def on_help_pressed(self):
        """Zeigt ein Erklärungs-Popup für den aktuellen Schritt."""
        if not self.wizard_service:
            return
        
        schritt = self.wizard_service.get_aktueller_schritt()
        if not schritt or not schritt.popup_title:
            return
        
        if self._current_popup_dialog:
            self._current_popup_dialog.dismiss()
        
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, adaptive_height=True)
        
        scroll = MDScrollView(size_hint_y=None, height="300dp")
        text_label = MDLabel(
            text=schritt.popup_text,
            theme_text_color="Primary",
            size_hint_y=None,
            adaptive_height=True,
        )
        scroll.add_widget(text_label)
        content.add_widget(scroll)
        
        self._current_popup_dialog = MDDialog(
            MDDialogHeadlineText(text=schritt.popup_title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Verstanden"),
                    style="filled",
                    on_release=lambda x: self._current_popup_dialog.dismiss() if self._current_popup_dialog else None
                ),
            ),
            size_hint=(0.85, None),
        )
        self._current_popup_dialog.open()

