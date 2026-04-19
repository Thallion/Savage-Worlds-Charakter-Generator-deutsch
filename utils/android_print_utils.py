# utils/android_print_utils.py
"""
Android Druck- und PDF-Export-Funktionalität.
Nutzt den Android PrintManager mit einem unsichtbaren WebView, um HTML
in ein PDF zu konvertieren und im Download-Ordner zu speichern.

WICHTIG – Drei Android-Einschränkungen, die das Design bestimmen:

1. WebView, PrintManager und createPrintDocumentAdapter dürfen NUR auf dem
   Android-UI-Thread aufgerufen werden (der einen vorbereiteten Looper hat).
   Ein normaler Python-threading.Thread hat keinen Looper → JVM-Crash:
       "Attempt to read from field 'android.os.MessageQueue
        android.os.Looper.mQueue' on a null object reference"
   → Lösung: Activity.runOnUiThread() + Handler.postDelayed()

2. android.webkit.WebViewClient ist eine abstrakte KLASSE, kein Interface.
   pyjnius' PythonJavaClass/__javainterfaces__ nutzt Java-Proxy, der nur
   Interfaces unterstützt → IllegalArgumentException.
   → Lösung: Kein WebViewClient. Stattdessen fester Delay via
   Handler.postDelayed(), damit der WebView die Seite laden kann.

3. file://-URLs können auf Android 10+ (Scoped Storage) Probleme machen.
   → Lösung: HTML-Inhalt per loadDataWithBaseURL() direkt laden.
"""

import os
from kivy.logger import Logger
from kivy.utils import platform as kivy_platform

# Modul-globale Referenzen verhindern, dass Python die PythonJavaClass-
# Instanzen und zugehörige Java-Objekte per GC entsorgt, während
# asynchrone Android-Callbacks noch ausstehen.
_active_print_refs = []


def is_android():
    """Prüft ob die App auf Android läuft."""
    return kivy_platform == 'android'


def print_html_to_pdf(html_path, pdf_name=None):
    """
    Konvertiert HTML auf Android via PrintManager in PDF.

    Erzeugt einen unsichtbaren WebView, lädt den HTML-Inhalt, und öffnet
    nach einer kurzen Verzögerung den System-Druckdialog (PrintManager).
    Der Benutzer kann dort "Als PDF speichern" wählen.

    Args:
        html_path: Pfad zur HTML-Datei
        pdf_name: Optionaler Name für die PDF-Datei (ohne .pdf Endung)

    Returns:
        str: pdf_name bei Erfolg, None bei Fehler
    """
    if not is_android():
        Logger.warning("Android Print: Nur auf Android verfügbar")
        return None

    if not os.path.exists(html_path):
        Logger.error(f"Android Print: HTML-Datei nicht gefunden: {html_path}")
        return None

    try:
        from jnius import autoclass

        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        context = PythonActivity.mActivity
        if context is None:
            Logger.error("Android Print: Keine Activity verfügbar")
            return None

        print_manager = context.getSystemService(Context.PRINT_SERVICE)
        if print_manager is None:
            Logger.error("Android Print: PrintManager nicht verfügbar")
            return None

        if pdf_name is None:
            base_name = os.path.splitext(os.path.basename(html_path))[0]
            pdf_name = base_name
        if not pdf_name.lower().endswith('.pdf'):
            pdf_name += '.pdf'

        Logger.info(f"Android Print: Konvertiere {html_path} nach PDF")

        return _print_html_to_pdf_async(context, print_manager, html_path, pdf_name)

    except ImportError as e:
        Logger.error(f"Android Print: pyjnius nicht verfügbar: {e}")
        return None
    except Exception as e:
        Logger.error(f"Android Print: Fehler beim Starten: {e}")
        return None


def _print_html_to_pdf_async(context, print_manager, html_path, pdf_name):
    """
    Plant die HTML→PDF-Konvertierung auf dem Android-UI-Thread ein.

    Ablauf:
    1. runOnUiThread: WebView erstellen, HTML laden (loadDataWithBaseURL)
    2. Handler.postDelayed (3s): createPrintDocumentAdapter + PrintManager.print
    """
    try:
        from jnius import autoclass

        WebView = autoclass('android.webkit.WebView')
        PrintAttrsBuilder = autoclass('android.print.PrintAttributes$Builder')
        MediaSize = autoclass('android.print.PrintAttributes$MediaSize')
        Resolution = autoclass('android.print.PrintAttributes$Resolution')
        Margins = autoclass('android.print.PrintAttributes$Margins')
        Handler = autoclass('android.os.Handler')
        Looper = autoclass('android.os.Looper')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        activity = PythonActivity.mActivity

        html_content = None
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            Logger.error(f"Android Print: HTML lesen fehlgeschlagen: {e}")
            return None

        state = {
            'web_view': None,
            'printed': False,
            'runnables': [],
        }

        def _do_print():
            """Erzeugt den PrintDocumentAdapter und startet den Druckdialog."""
            if state['printed']:
                return
            state['printed'] = True
            try:
                web_view = state['web_view']
                if web_view is None:
                    Logger.error("Android Print: WebView ist None bei Druckstart")
                    return

                job_name = f"Charakterbogen - {pdf_name}"
                print_adapter = web_view.createPrintDocumentAdapter(job_name)

                print_attrs = (PrintAttrsBuilder()
                               .setMediaSize(MediaSize.ISO_A4)
                               .setResolution(Resolution("pdf", "pdf", 300, 300))
                               .setMinMargins(Margins.NO_MARGINS)
                               .build())

                print_manager.print(job_name, print_adapter, print_attrs)
                Logger.info(f"Android Print: Druckdialog geöffnet: {job_name}")

            except Exception as e:
                Logger.error(f"Android Print: Druckauftrag Fehler: {e}")

        def _setup_on_ui_thread():
            """WebView erstellen, HTML laden, Druck-Delay einplanen."""
            try:
                Logger.info("Android Print: Setup läuft auf UI-Thread")

                web_view = WebView(context)
                state['web_view'] = web_view

                settings = web_view.getSettings()
                settings.setJavaScriptEnabled(True)
                settings.setAllowFileAccess(True)
                settings.setDomStorageEnabled(True)
                try:
                    settings.setAllowFileAccessFromFileURLs(True)
                    settings.setAllowUniversalAccessFromFileURLs(True)
                except Exception:
                    pass

                base_dir = os.path.dirname(os.path.abspath(html_path))
                base_url = f"file://{base_dir}/"
                web_view.loadDataWithBaseURL(
                    base_url, html_content, "text/html", "UTF-8", None
                )
                Logger.info("Android Print: HTML via loadDataWithBaseURL geladen")

                # 3 Sekunden warten, damit WebView rendern kann, dann drucken.
                print_runnable = _make_runnable(_do_print)
                state['runnables'].append(print_runnable)
                handler = Handler(Looper.getMainLooper())
                handler.postDelayed(print_runnable, 3000)
                state['handler'] = handler
                Logger.info("Android Print: Druck in 3s eingeplant")

            except Exception as e:
                Logger.error(f"Android Print: UI-Thread Setup-Fehler: {e}")

        setup_runnable = _make_runnable(_setup_on_ui_thread)
        state['runnables'].append(setup_runnable)
        _active_print_refs.append(state)

        activity.runOnUiThread(setup_runnable)
        Logger.info("Android Print: Setup an UI-Thread übergeben")

        return pdf_name

    except Exception as e:
        Logger.error(f"Android Print: Async Fehler: {e}")
        return None


def _make_runnable(py_callable):
    """
    Erzeugt ein java.lang.Runnable, das ein Python-Callable ausführt.
    Runnable ist ein echtes Java-Interface und funktioniert mit pyjnius.
    """
    from jnius import PythonJavaClass, java_method

    class _PyRunnable(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']

        def __init__(self, func):
            super().__init__()
            self._func = func

        @java_method('()V')
        def run(self):
            try:
                self._func()
            except Exception as exc:
                Logger.error(f"Android Print: Runnable-Fehler: {exc}")

    return _PyRunnable(py_callable)


def get_downloads_path():
    """
    Gibt den Pfad zum Download-Ordner auf Android zurück.

    Returns:
        str: Pfad zum Download-Ordner oder None
    """
    if not is_android():
        return None

    try:
        from jnius import autoclass

        Environment = autoclass('android.os.Environment')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity

        downloads_dir = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS)

        if downloads_dir and downloads_dir.exists():
            return downloads_dir.getAbsolutePath()

        alt_dir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
        if alt_dir and alt_dir.exists():
            return alt_dir.getAbsolutePath()

        return context.getFilesDir().getAbsolutePath()

    except Exception as e:
        Logger.error(f"Android: Download-Pfad Fehler: {e}")
        return None
