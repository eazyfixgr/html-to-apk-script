# HTML to APK Converter

A desktop tool that turns an HTML/CSS/JS project into an Android APK using **Capacitor** — with plugin selection, icon/splash generation and build automation.

> **Download:** grab the latest `HtmlToApk.exe` from the [Releases](https://github.com/eazyfixgr/html-to-apk-script/releases) page. No installation required (needs Node.js + Android SDK for building).

## Features

- Convert an HTML/CSS/JS (or React) project to an Android APK
- Capacitor plugin selection (Firebase, splash screen, icons…)
- Automatic icon & splash screen generation
- Separate project creation and build steps
- Asset optimisation (HTML / CSS / JS minification)
- Desktop notifications when the build finishes

## Requirements

- **Node.js** and **Capacitor**
- **Android SDK / Android Studio** (for the actual APK build)

## Run from source

```bash
python -m pip install pillow plyer tkinterdnd2 csscompressor jsmin
python "html_to_apk_converter(v3).py"
```

## Build a standalone EXE

```bash
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --collect-all tkinterdnd2 --name HtmlToApk "html_to_apk_converter(v3).py"
```

## License

Released under the [MIT License](LICENSE).

---

# HTML to APK Converter (Ελληνικά)

Εργαλείο που μετατρέπει ένα project HTML/CSS/JS σε **APK για Android** μέσω **Capacitor**, με επιλογή plugins, δημιουργία εικονιδίων/splash και αυτοματοποίηση του build.

> **Λήψη:** κατεβάστε το `HtmlToApk.exe` από τη σελίδα [Releases](https://github.com/eazyfixgr/html-to-apk-script/releases). Απαιτούνται Node.js + Android SDK για το build.

## Δυνατότητες

- Μετατροπή HTML/CSS/JS (ή React) σε APK
- Επιλογή Capacitor plugins
- Αυτόματη δημιουργία icon & splash screen
- Βελτιστοποίηση αρχείων (minify HTML/CSS/JS)
- Ειδοποιήσεις όταν ολοκληρωθεί το build
