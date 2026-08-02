# ============================================================================
# R8-/ProGuard-Regeln für den python-for-android-Build
#
# Wird von build_fixes.py -> fix_gradle_r8_optimization() in die Dist kopiert
# und in build.gradle als proguardFiles eingetragen.
#
# ACHTUNG: In dieser App ist praktisch KEINE Java-Klasse statisch erreichbar.
# Der Einstiegspunkt ist natives C (SDL2 + CPython), die gesamte App-Logik ist
# Python. Java wird nur auf zwei Wegen angefasst:
#   1. JNI aus nativem Code   (SDL2 -> org.libsdl.app, start.c -> PythonActivity)
#   2. Reflection aus Python  (pyjnius autoclass()/PythonJavaClass)
# R8 sieht beide Wege NICHT. Ohne die folgenden Keep-Regeln entfernt oder
# umbenennt es die Klassen, und die App stürzt beim Start ab — aber nur im
# Release-Build, nicht im Debug-Build.
#
# Regel: Wer hier etwas entfernt, muss einen Release-Build auf einem echten
# Gerät starten und Splash, Intent-Empfang (Teilen) sowie PDF-/HTML-Export
# durchtesten. Ein erfolgreicher Build beweist gar nichts.
# ============================================================================

# --- SDL2 -------------------------------------------------------------------
# SDL ruft seine Java-Seite komplett aus nativem Code über JNI auf
# (SDLActivity, SDLSurface, SDLAudioManager, SDLControllerManager,
# HIDDeviceManager). Kein einziger dieser Aufrufe ist für R8 sichtbar.
-keep class org.libsdl.app.** { *; }

# --- python-for-android Bootstrap -------------------------------------------
# PythonActivity ist die Manifest-Activity (würde als Klasse überleben), aber
# ihre Methoden und statischen Felder werden aus nativem Code und aus Python
# angesprochen: PythonActivity.mActivity (pyjnius, überall in der App),
# registerNewIntentListener() (android.activity.bind() für on_new_intent),
# PythonUtil.unpackAsset()/loadLibraries(), ResourceManager.getIdentifier()
# (Presplash-Lookup zur Laufzeit).
-keep class org.kivy.android.** { *; }
-keep class org.renpy.android.** { *; }

# --- pyjnius ----------------------------------------------------------------
# org.jnius.NativeInvocationHandler ist die Brücke für PythonJavaClass: Python
# implementiert damit Java-Interfaces (u.a. der NewIntentListener aus
# android.activity.bind()). Die Klasse wird ausschließlich reflektiv
# instanziiert und ist für R8 komplett unsichtbar.
-keep class org.jnius.** { *; }

# --- jtar -------------------------------------------------------------------
# Entpackt das Python-Bundle beim ersten Start (PythonUtil.unpackAsset).
-keep class org.kamranzafar.jtar.** { *; }

# --- Über pyjnius autoclass() angesprochene Bibliotheksklassen --------------
# Framework-Klassen (android.*, java.*) liegen in android.jar, sind nicht Teil
# des APK und werden von R8 nicht angefasst — die brauchen keine Regel.
# Gebündelte AndroidX-Klassen dagegen schon:
#   manager/html_manager.py, utils/share_utils.py -> FileProvider.getUriForFile
-keep class androidx.core.content.FileProvider { *; }

# --- Allgemein: alles, was über JNI erreichbar ist --------------------------
# Native Methoden und ihre Klassen dürfen nicht umbenannt werden, sonst findet
# der JNI-Linker sie nicht mehr.
-keepclasseswithmembernames class * {
    native <methods>;
}

# --- Attribute --------------------------------------------------------------
# Signature/Exceptions/InnerClasses: pyjnius reflektiert über Methodensignaturen.
# SourceFile/LineNumberTable: lesbare Stacktraces in der Play Console
# (die mapping.txt wird beim AAB-Upload automatisch mit hochgeladen).
-keepattributes Signature,Exceptions,InnerClasses,EnclosingMethod,*Annotation*
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
