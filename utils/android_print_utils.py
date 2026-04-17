# utils/android_print_utils.py
"""
Android Druck- und PDF-Export-Funktionalität.
Nutzt den Android PrintManager mit einem unsichtbaren WebView, um HTML
in ein PDF zu konvertieren und im Download-Ordner zu speichern.
"""

import os
import threading
import time
from kivy.logger import Logger
from kivy.utils import platform as kivy_platform

# Modul-globale Referenzen, damit Python die PythonJavaClass-Instanzen und
# WebViews während des asynchronen Android-Druckvorgangs nicht per GC entsorgt.
# Ohne diese Referenzen können Java-Callbacks auf freigegebene Python-Objekte
# zugreifen und abstürzen.
_active_print_refs = []


def is_android():
    """Prüft ob die App auf Android läuft."""
    return kivy_platform == 'android'


def print_html_to_pdf(html_path, pdf_name=None):
    """
    Konvertiert HTML auf Android via PrintManager in PDF und speichert es.

    Args:
        html_path: Pfad zur HTML-Datei
        pdf_name: Optionaler Name für die PDF-Datei (ohne .pdf Endung)

    Returns:
        str: Pfad zur erstellten PDF-Datei oder None bei Fehler
    """
    if not is_android():
        Logger.warning("Android Print: Nur auf Android verfügbar")
        return None

    if not os.path.exists(html_path):
        Logger.error(f"Android Print: HTML-Datei nicht gefunden: {html_path}")
        return None

    try:
        from jnius import autoclass, cast

        Context = autoclass('android.content.Context')
        Intent = autoclass('android.content.Intent')
        PrintAttributes = autoclass('android.print.PrintAttributes$Builder')
        PrintDocumentAdapter = autoclass('android.print.PrintDocumentAdapter')
        PrintManager = autoclass('android.print.PrintManager')
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Environment = autoclass('android.os.Environment')
        File = autoclass('java.io.File')

        context = PythonActivity.mActivity
        print_manager = context.getSystemService(Context.PRINT_SERVICE)
        
        Logger.info(f"Android Print: Context und PrintManager erhalten")

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
    Führt die HTML-zu-PDF Konvertierung asynchron durch.
    Nutzt einen einfachen WebView mit PrintDocumentAdapter.

    WICHTIG: WebView, PrintManager und createPrintDocumentAdapter dürfen NUR
    auf dem Android-UI-Thread (der einen vorbereiteten Looper hat) erzeugt und
    aufgerufen werden. Aufrufe von einem normalen Python-`threading.Thread`
    führen zu einer JVM-Exception:
        "Attempt to read from field 'android.os.MessageQueue
         android.os.Looper.mQueue' on a null object reference ..."
    Deshalb planen wir alle Android-Aufrufe via ``Activity.runOnUiThread`` ein.
    """
    Logger.info(f"Android Print: Starte async PDF-Erstellung für {html_path}")
    try:
        from jnius import autoclass, PythonJavaClass, java_method

        WebView = autoclass('android.webkit.WebView')
        PrintAttributes = autoclass('android.print.PrintAttributes$Builder')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        activity = PythonActivity.mActivity

        class AsyncPrintHelper(PythonJavaClass):
            __javainterfaces__ = ['android/webkit/WebViewClient']

            def __init__(self, context, print_manager, html_path, pdf_name):
                super().__init__()
                self.context = context
                self.print_manager = print_manager
                self.html_path = html_path
                self.pdf_name = pdf_name
                self.web_view = None
                self._print_started = False

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;Landroid/graphics/Bitmap;)V')
            def onPageStarted(self, view, url, favicon):
                pass

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onPageFinished(self, view, url):
                # onPageFinished wird vom WebView bereits auf dem UI-Thread
                # aufgerufen. Wir starten den Druck aber leicht verzögert,
                # damit Rendering und Layout vollständig sind.
                Logger.info(f"Android Print: onPageFinished aufgerufen für {url}")
                if self._print_started:
                    Logger.info("Android Print: Druck bereits gestartet, ignoriere")
                    return
                self._print_started = True
                try:
                    DoPrintRunnable = _make_runnable(self._do_print)
                    # 400 ms Verzögerung auf dem UI-Thread über postDelayed.
                    Logger.info("Android Print: Planze Druck-Runnable mit 400ms Verzögerung")
                    view.postDelayed(DoPrintRunnable, 400)
                    # Referenz behalten, damit das Runnable nicht vor Ausführung GC'd wird.
                    self._pending_runnable = DoPrintRunnable
                except Exception as e:
                    Logger.error(f"Android Print: Print-Scheduling-Fehler: {e}")

            def _do_print(self):
                Logger.info("Android Print: _do_print wird ausgeführt")
                try:
                    job_name = f"Charakterbogen - {self.pdf_name}"
                    Logger.info(f"Android Print: Erstelle PrintDocumentAdapter für {job_name}")
                    print_adapter = self.web_view.createPrintDocumentAdapter(job_name)

                    print_attrs = (PrintAttributes.Builder()
                                   .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                                   .setResolution(PrintAttributes.Resolution("pdf", "pdf", 300, 300))
                                   .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
                                   .build())
                    Logger.info("Android Print: Rufe print_manager.print auf")
                    self.print_manager.print(job_name, print_adapter, print_attrs)
                    Logger.info(f"Android Print: Druckauftrag gestartet: {job_name}")

                except Exception as e:
                    Logger.error(f"Android Print: Druckauftrag Fehler: {e}")

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onReceivedError(self, view, error):
                Logger.error(f"Android Print: WebView Fehler: {error}")

        helper = AsyncPrintHelper(context, print_manager, html_path, pdf_name)
        # Modul-globale Referenz, damit Java-Callbacks nicht in freigegebenen
        # Python-Speicher laufen.
        _active_print_refs.append(helper)

        def _setup_on_ui_thread():
            Logger.info("Android Print: _setup_on_ui_thread wird ausgeführt")
            try:
                web_view = WebView(context)
                settings = web_view.getSettings()
                settings.setJavaScriptEnabled(True)
                settings.setAllowFileAccess(True)
                settings.setDomStorageEnabled(True)

                helper.web_view = web_view
                web_view.setWebViewClient(helper)

                abs_path = os.path.abspath(html_path)
                file_url = f"file://{abs_path}"
                web_view.loadUrl(file_url)

                Logger.info(
                    "Android Print: WebView auf UI-Thread erstellt, lade HTML"
                )
            except Exception as e:
                Logger.error(f"Android Print: UI-Thread Setup-Fehler: {e}")
                try:
                    _active_print_refs.remove(helper)
                except ValueError:
                    pass

        setup_runnable = _make_runnable(_setup_on_ui_thread)
        # Referenz behalten, bis runOnUiThread es ausgeführt hat.
        helper._setup_runnable = setup_runnable
        activity.runOnUiThread(setup_runnable)

        Logger.info("Android Print: Setup auf UI-Thread eingeplant")
        Logger.info(f"Android Print: Rückgabe von pdf_name: {pdf_name}")

        return pdf_name

    except Exception as e:
        Logger.error(f"Android Print: Async Fehler: {e}")
        return None


def _make_runnable(py_callable):
    """
    Erzeugt ein java.lang.Runnable, das ein Python-Callable ausführt.
    Fängt Fehler ab, damit sie nicht in die JVM propagieren.
    """
    from jnius import PythonJavaClass, java_method

    class _PyRunnable(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']

        def __init__(self, func):
            super().__init__()
            self._func = func

        @java_method('()V')
        def run(self):
            Logger.info("Android Print: Runnable.run wird ausgeführt")
            try:
                self._func()
                Logger.info("Android Print: Runnable abgeschlossen")
            except Exception as exc:
                Logger.error(f"Android Print: Runnable-Fehler: {exc}")

    return _PyRunnable(py_callable)


def save_html_to_pdf_direct(html_path, pdf_name=None):
    """
    Speichert HTML direkt als PDF-Datei im Download-Ordner.
    Verwendet dieAndroid PDF-Renderer API für direkte Konvertierung.
    HINWEIS: Direkte PDF-Erstellung ohne Dialog ist derzeit nicht implementiert.
    Stattdessen wird der normale Druckdialog geöffnet.

    Args:
        html_path: Pfad zur HTML-Datei
        pdf_name: Optionaler Name für die PDF-Datei

    Returns:
        str: Pfad zur erstellten PDF oder None bei Fehler
    """
    Logger.warning("Android PDF: save_html_to_pdf_direct wird aufgerufen - direkte PDF-Erstellung nicht verfügbar, öffne Druckdialog")
    # Verwende die vorhandene PrintManager-Lösung mit Dialog
    return print_html_to_pdf(html_path, pdf_name)


def _convert_html_to_pdf_with_webview(context, html_path, output_pdf):
    """
    Konvertiert HTML zu PDF mittels WebView und PrintDocumentAdapter.
    """
    try:
        from jnius import autoclass, PythonJavaClass, java_method

        WebView = autoclass('android.webkit.WebView')
        WebSettings = autoclass('android.webkit.WebSettings')
        PrintAttributes = autoclass('android.print.PrintAttributes$Builder')
        PrintManager = autoclass('android.print.PrintManager')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Looper = autoclass('android.os.Looper')
        Context = autoclass('android.content.Context')

        print_manager = context.getSystemService(Context.PRINT_SERVICE)

        result = {'success': False, 'path': None}
        result_lock = threading.Lock()

        class CustomWebViewClient(PythonJavaClass):
            __javainterfaces__ = ['android/webkit/WebViewClient']

            def __init__(self, ctx, pm, hp, opdf, res):
                super().__init__()
                self._context = ctx
                self._print_manager = pm
                self._html_path = hp
                self._output_pdf = opdf
                self._result = res

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onPageFinished(self, web_view, url):
                threading.Thread(target=lambda: _perform_print_and_save(
                    self._context, self._print_manager, web_view,
                    self._html_path, self._output_pdf, self._result),
                    daemon=True).start()

        def _perform_print_and_save(ctx, pm, web_view, hp, opdf, res):
            try:
                Looper.prepare()

                time.sleep(0.5)

                job_name = "Charakterbogen PDF Export"
                print_adapter = web_view.createPrintDocumentAdapter(job_name)

                print_attrs = (PrintAttributes.Builder()
                               .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                               .setResolution(PrintAttributes.Resolution("default", "default", 300, 300))
                               .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
                               .build())

                pm.print(job_name, print_adapter, print_attrs)

                Logger.info("Android PDF: Druckdialog geöffnet - bitte als PDF speichern")

                with result_lock:
                    res['success'] = True
                    res['path'] = opdf.getAbsolutePath()

                Looper.loop()

            except Exception as e:
                Logger.error(f"Android PDF: Druckfehler: {e}")
                with result_lock:
                    res['success'] = False
                    res['error'] = str(e)

        web_view = WebView(context)
        settings = web_view.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setAllowFileAccess(True)
        settings.setDomStorageEnabled(True)
        settings.setLoadWithOverviewMode(True)
        settings.setUseWideViewPort(True)

        client = CustomWebViewClient(context, print_manager, html_path, output_pdf, result)
        web_view.setWebViewClient(client)

        abs_path = os.path.abspath(html_path)
        file_url = f"file://{abs_path}"
        web_view.loadUrl(file_url)

        Logger.info("Android PDF: WebView gestartet, warte auf Druckvorgang...")

        return output_pdf.getAbsolutePath()

    except Exception as e:
        Logger.error(f"Android PDF: Konvertierungsfehler: {e}")
        return None


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