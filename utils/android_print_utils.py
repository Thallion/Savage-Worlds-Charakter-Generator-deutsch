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
    """
    try:
        from jnius import autoclass, cast, PythonJavaClass, java_method

        WebView = autoclass('android.webkit.WebView')
        WebSettings = autoclass('android.webkit.WebSettings')
        PrintAttributes = autoclass('android.print.PrintAttributes$Builder')
        PrintManager = autoclass('android.print.PrintManager')
        Environment = autoclass('android.os.Environment')
        File = autoclass('java.io.File')
        FileOutputStream = autoclass('java.io.FileOutputStream')

        result_container = {'pdf_path': None, 'error': None}

        class AsyncPrintHelper(PythonJavaClass):
            __javainterfaces__ = ['android/webkit/WebViewClient']

            def __init__(self, context, print_manager, html_path, pdf_name, callback):
                super().__init__()
                self.context = context
                self.print_manager = print_manager
                self.html_path = html_path
                self.pdf_name = pdf_name
                self.callback = callback

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;Landroid/graphics/Bitmap;)V')
            def onPageStarted(self, view, url, favicon):
                pass

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onPageFinished(self, view, url):
                threading.Thread(target=self._delayed_print, daemon=True).start()

            def _delayed_print(self):
                time.sleep(1.0)
                try:
                    self.web_view.post(lambda: self._do_print())
                except Exception as e:
                    Logger.error(f"Android Print: Print-Fehler: {e}")
                    self.callback(None, str(e))

            def _do_print(self):
                try:
                    job_name = f"Charakterbogen - {self.pdf_name}"
                    print_adapter = self.web_view.createPrintDocumentAdapter(job_name)

                    print_attrs = (PrintAttributes.Builder()
                                   .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                                   .setResolution(PrintAttributes.Resolution("pdf", "pdf", 300, 300))
                                   .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
                                   .build())

                    self.print_manager.print(job_name, print_adapter, print_attrs)
                    Logger.info(f"Android Print: Druckauftrag gestartet: {job_name}")

                except Exception as e:
                    Logger.error(f"Android Print: Druckauftrag Fehler: {e}")

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onReceivedError(self, view, error):
                Logger.error(f"Android Print: WebView Fehler: {error}")
                self.callback(None, str(error))

        def run_in_thread():
            try:
                web_view = WebView(context)
                settings = web_view.getSettings()
                settings.setJavaScriptEnabled(True)
                settings.setAllowFileAccess(True)
                settings.setDomStorageEnabled(True)

                web_view.getSettings().setPluginState(
                    autoclass('android.webkit.WebSettings$PluginState').ON)

                abs_path = os.path.abspath(html_path)
                file_url = f"file://{abs_path}"

                helper = AsyncPrintHelper(context, print_manager, html_path, pdf_name,
                                         lambda path, err: None)
                helper.web_view = web_view
                web_view.setWebViewClient(helper)

                web_view.loadUrl(file_url)

            except Exception as e:
                Logger.error(f"Android Print: Thread Fehler: {e}")

        threading.Thread(target=run_in_thread, daemon=True).start()
        Logger.info("Android Print: WebView gestartet, Druckdialog sollte erscheinen")

        return pdf_name

    except Exception as e:
        Logger.error(f"Android Print: Async Fehler: {e}")
        return None


def save_html_to_pdf_direct(html_path, pdf_name=None):
    """
    Speichert HTML direkt als PDF-Datei im Download-Ordner.
    Verwendet dieAndroid PDF-Renderer API für direkte Konvertierung.

    Args:
        html_path: Pfad zur HTML-Datei
        pdf_name: Optionaler Name für die PDF-Datei

    Returns:
        str: Pfad zur erstellten PDF oder None bei Fehler
    """
    if not is_android():
        Logger.warning("Android PDF: Nur auf Android verfügbar")
        return None

    if not os.path.exists(html_path):
        Logger.error(f"Android PDF: HTML-Datei nicht gefunden: {html_path}")
        return None

    try:
        from jnius import autoclass

        Context = autoclass('android.content.Context')
        Environment = autoclass('android.os.Environment')
        File = autoclass('java.io.File')
        FileOutputStream = autoclass('java.io.FileOutputStream')
        BufferedInputStream = autoclass('java.io.BufferedInputStream')
        FileInputStream = autoclass('java.io.FileInputStream')
        PdfRenderer = autoclass('android.graphics.pdf.PdfRenderer')
        ParcelFileDescriptor = autoclass('android.os.ParcelFileDescriptor')
        Bitmap = autoclass('android.graphics.Bitmap')
        Canvas = autoclass('android.graphics.Canvas')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        context = PythonActivity.mActivity

        if pdf_name is None:
            base_name = os.path.splitext(os.path.basename(html_path))[0]
            pdf_name = base_name + ".pdf"
        elif not pdf_name.lower().endswith('.pdf'):
            pdf_name += '.pdf'

        pdf_name = pdf_name.replace(" ", "_")

        downloads_dir = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS)

        if not downloads_dir.exists():
            downloads_dir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
        if not downloads_dir:
            downloads_dir = context.getFilesDir()

        output_pdf = File(downloads_dir, pdf_name)

        Logger.info(f"Android PDF: Erstelle PDF: {output_pdf.getAbsolutePath()}")

        return _convert_html_to_pdf_with_webview(context, html_path, output_pdf)

    except ImportError as e:
        Logger.error(f"Android PDF: pyjnius nicht verfügbar: {e}")
        return None
    except Exception as e:
        Logger.error(f"Android PDF: Fehler: {e}")
        return None


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