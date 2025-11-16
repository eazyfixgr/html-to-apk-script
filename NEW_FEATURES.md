# New Features Guide - HTML to APK Converter Pro

This document describes all the new features added to the HTML to APK Converter.

## 🎨 1. Dark Mode UI

**Status**: ✅ Implemented
**Dependencies**: None

### What it does:
- Toggle between light and dark themes
- Reduces eye strain during extended use
- Modern, professional appearance

### How to use:
1. Look for "Dark Mode" checkbox in settings
2. Click to toggle between themes
3. Theme persists between sessions

### Technical Details:
- Method: `toggle_dark_mode()` (`html_to_apk_converter.py:2399`)
- Theme colors defined in `self.themes` dict
- Applies to all ttk widgets automatically

---

## 📂 2. Recent Projects

**Status**: ✅ Implemented
**Dependencies**: None

### What it does:
- Automatically tracks your last 10 projects
- Quick access dropdown to reload projects
- Saves time re-entering project details

### How to use:
1. Build any project - it's automatically saved to recent
2. Click "Recent Projects" dropdown
3. Select a project to reload all its settings

### Stored Information:
- HTML directory path
- App name and ID
- Output directory
- Last build timestamp

### Technical Details:
- Saved to: `recent_projects.json`
- Methods:
  - `load_recent_projects()` (`html_to_apk_converter.py:2420`)
  - `save_recent_projects()` (`html_to_apk_converter.py:2431`)
  - `add_to_recent_projects()` (`html_to_apk_converter.py:2440`)
  - `load_recent_project()` (`html_to_apk_converter.py:2479`)
- Max projects: 10 (configurable via `self.max_recent_projects`)

---

## 🎯 3. Drag & Drop Support

**Status**: ✅ Implemented
**Dependencies**: `tkinterdnd2` (optional)

### What it does:
- Drag HTML folder directly onto the app
- No need to click "Browse" button
- Faster workflow

### How to use:
1. Open the HTML to APK Converter
2. Drag your HTML project folder
3. Drop it on the HTML directory field
4. Path is automatically filled

### Installation:
```bash
pip install tkinterdnd2
```

**Note**: If `tkinterdnd2` is not installed, browse button still works normally.

### Technical Details:
- Method: `setup_drag_drop()` (`html_to_apk_converter.py:2491`)
- Validates dropped item is a directory
- Shows warning if file (not folder) is dropped
- Graceful fallback if library not available

---

## 🔔 4. Desktop Notifications

**Status**: ✅ Implemented
**Dependencies**: `plyer`

### What it does:
- Desktop notification when build completes
- Notification when APK is ready
- Works in background

### How to use:
1. Enable "Build Notifications" in settings
2. Start a build
3. Minimize the app or work on other tasks
4. Get notified when done

### Installation:
```bash
pip install plyer
```

### Technical Details:
- Method: `send_notification()` (`html_to_apk_converter.py:2511`)
- 10-second notification timeout
- Graceful fallback if library not available

### Example notifications:
- "Build Complete! - Your APK is ready"
- "Build Failed - Check build logs for details"
- "APK Installed - App installed on device successfully"

---

## 🔍 5. APK Analyzer

**Status**: ✅ Implemented
**Dependencies**: None (enhanced with `aapt` if Android SDK available)

### What it does:
- Detailed APK analysis after build
- File size breakdown by type
- Permissions list
- Package information
- SDK versions

### How to use:
1. After building an APK, click "Analyze APK" button
2. Or: Right-click APK → Analyze
3. View comprehensive report

### Analysis Report Includes:
- **File Information**:
  - Total size in MB
  - Number of files

- **Package Information** (requires Android SDK):
  - Package name
  - Version name and code
  - Min SDK version
  - Target SDK version

- **Size Breakdown**:
  - Size by file type (.dex, .png, .js, etc.)
  - Percentage of total size
  - Top 15 file types

- **Permissions**:
  - List of all permissions
  - Total permission count

- **Components**:
  - AndroidManifest.xml presence
  - DEX files detection

### Technical Details:
- Methods:
  - `analyze_apk()` (`html_to_apk_converter.py:2530`)
  - `get_aapt_info()` (`html_to_apk_converter.py:2572`)
  - `show_apk_analysis_window()` (`html_to_apk_converter.py:2630`)
- Uses Python's `zipfile` module for basic analysis
- Uses Android `aapt` tool for detailed info (if available)
- Results shown in scrollable window

---

## 📊 6. Version Management

**Status**: ✅ Implemented
**Dependencies**: None

### What it does:
- Automatic version incrementing
- Build history tracking
- Version comparison
- Changelog support

### How to use:
1. Set initial version (e.g., 1.0.0)
2. Check "Auto-increment version" in settings
3. Each build automatically increments version
4. View version history

### Features:
- **Version Code**: Integer that increments (1, 2, 3...)
- **Version Name**: Semantic versioning (1.0.0, 1.0.1, 1.1.0)
- **Auto Increment**: Optional patch version increment
- **History**: Last 50 builds saved

### Version History Includes:
- Timestamp of build
- Version code and name
- APK file path
- APK file size
- App name and ID

### Technical Details:
- Methods:
  - `increment_version()` (`html_to_apk_converter.py:2699`)
  - `save_version_history()` (`html_to_apk_converter.py:2726`)
- History saved to: `version_history.json`
- Keeps last 50 builds
- Semantic versioning: MAJOR.MINOR.PATCH

---

## ⚡ 7. Build Optimization

**Status**: ✅ Implemented
**Dependencies**: `htmlmin`, `csscompressor`, `jsmin` (optional)

### What it does:
- Minifies HTML files
- Compresses CSS files
- Minifies JavaScript files
- Optimizes images (PNG/JPG)
- Significantly reduces APK size

### How to use:
1. Enable "Optimize Build" in settings
2. Build your project
3. Optimization happens automatically
4. View optimization report in build logs

### Optimization Process:
1. **HTML Minification**:
   - Removes comments
   - Removes whitespace
   - Typical savings: 20-30%

2. **CSS Compression**:
   - Removes comments and whitespace
   - Shortens color codes
   - Typical savings: 30-40%

3. **JavaScript Minification**:
   - Removes comments and whitespace
   - Typical savings: 20-35%

4. **Image Optimization**:
   - PNG/JPG compression
   - Quality: 85 (good balance)
   - Typical savings: 30-70%

### Installation:
```bash
pip install htmlmin csscompressor jsmin
```

### Example Output:
```
🎯 Optimizing web assets...
  📄 index.html: saved 1,234 bytes
  🎨 style.css: saved 2,456 bytes
  📜 main.js: saved 3,678 bytes
  🖼️  logo.png: saved 45,678 bytes
✅ Optimized 15 files, saved 156.34 KB
```

### Technical Details:
- Method: `optimize_web_assets()` (`html_to_apk_converter.py:2759`)
- Runs after HTML files are copied to www directory
- Individual file errors don't stop build
- Reports total bytes saved

### Performance Impact:
- Average APK size reduction: **25-50%**
- Faster app downloads for users
- Better performance on low-end devices

---

## 🔐 8. APK Signing & Release Build

**Status**: ✅ Implemented
**Dependencies**: Java JDK (`keytool`)

### What it does:
- Generate Android keystores
- Sign APKs for Google Play Store
- Build release APKs (not debug)
- Store signing configuration

### Why it matters:
- **Debug APKs**: Cannot be published to Play Store
- **Release APKs**: Production-ready, signed, optimized

### How to use:

#### Option A: Generate New Keystore
1. Click "Generate Keystore" button
2. Fill in keystore details:
   - Alias (key name)
   - Password (minimum 6 characters)
   - Validity period (years)
   - Your name
   - Organization name
3. Choose where to save `.jks` file
4. **IMPORTANT**: Keep keystore and password safe!

#### Option B: Use Existing Keystore
1. Click "Browse" next to Keystore Path
2. Select your existing `.jks` file
3. Enter alias and password
4. Click "Save Configuration"

#### Building Release APK
1. Configure keystore (see above)
2. Check "Build Release APK" option
3. Click "Build APK"
4. Wait for signed release APK

### Keystore Best Practices:
- ⚠️ **NEVER lose your keystore!**
- Keep multiple backups
- Use strong password (12+ characters)
- Store in secure location
- Same keystore for all app updates

### Technical Details:
- Methods:
  - `generate_keystore()` (`html_to_apk_converter.py:2881`)
  - `save_keystore_config()` (`html_to_apk_converter.py:3000`)
  - `load_keystore_config()` (`html_to_apk_converter.py:3015`)
  - `build_signed_apk()` (`html_to_apk_converter.py:3029`)
- Uses Java `keytool` command
- Configuration saved to: `keystore_config.json`
- **Security Note**: Password stored in plain text (encrypt in production!)

### Gradle Configuration:
Automatically adds to `gradle.properties`:
```properties
RELEASE_STORE_FILE=/path/to/keystore.jks
RELEASE_STORE_PASSWORD=yourpassword
RELEASE_KEY_ALIAS=your-alias
RELEASE_KEY_PASSWORD=yourpassword
```

---

## 📱 9. ADB Integration (Direct Device Installation)

**Status**: ✅ Implemented
**Dependencies**: Android SDK Platform Tools (adb)

### What it does:
- Detect connected Android devices
- Install APK directly to device
- Launch app after installation
- One-click testing workflow

### How to use:

#### Setup:
1. Install Android SDK Platform Tools
2. Enable USB Debugging on your Android device
3. Connect device via USB
4. Accept USB debugging prompt on device

#### Testing Workflow:
1. Build your APK
2. Click "Install to Device" button
3. Select target device (if multiple)
4. APK installs automatically
5. App launches automatically

### Device Detection:
- Automatically scans for connected devices
- Shows device ID in dropdown
- Supports multiple devices
- Real-time device status

### Installation Options:
- **Replace existing**: Automatic update
- **Launch after install**: Opens app immediately
- **Install and test**: One-click workflow

### Technical Details:
- Methods:
  - `detect_adb_devices()` (`html_to_apk_converter.py:3106`)
  - `install_apk_to_device()` (`html_to_apk_converter.py:3137`)
  - `launch_app_on_device()` (`html_to_apk_converter.py:3172`)
- Requires `adb` in system PATH
- Timeout: 120 seconds for installation
- Uses `adb install -r` (replace existing)

### ADB Installation:

**Windows**:
```bash
# Download Android SDK Platform Tools
# Add to PATH environment variable
```

**macOS**:
```bash
brew install android-platform-tools
```

**Linux**:
```bash
sudo apt-get install android-tools-adb
```

### Troubleshooting:
- **Device not detected**: Check USB cable, enable USB debugging
- **Unauthorized**: Accept prompt on device
- **Installation failed**: Check storage space, uninstall old version manually
- **ADB not found**: Install Platform Tools, add to PATH

---

## 📦 Feature Availability Matrix

| Feature | Status | Required Dependencies | Optional Dependencies |
|---------|--------|----------------------|----------------------|
| Dark Mode | ✅ Ready | None | - |
| Recent Projects | ✅ Ready | None | - |
| Drag & Drop | ✅ Ready | None | tkinterdnd2 |
| Notifications | ✅ Ready | None | plyer |
| APK Analyzer | ✅ Ready | None | Android SDK (aapt) |
| Version Management | ✅ Ready | None | - |
| Build Optimization | ✅ Ready | None | htmlmin, csscompressor, jsmin |
| APK Signing | ✅ Ready | Java JDK (keytool) | - |
| ADB Integration | ✅ Ready | Android SDK Platform Tools | - |

---

## 🚀 Quick Start Guide

### Minimal Setup (Core Features Only):
```bash
pip install Pillow
```

### Recommended Setup (All Features):
```bash
# Install Python dependencies
pip install Pillow htmlmin csscompressor jsmin plyer

# Install system tools
# - Java JDK (for keystore generation)
# - Android SDK (for adb and aapt)
```

### Full Setup (Maximum Features):
```bash
# Python packages
pip install -r requirements.txt

# System tools (varies by OS)
# Windows: Install Java JDK, Android Studio
# macOS: brew install openjdk android-platform-tools
# Linux: sudo apt-get install openjdk-17-jdk android-tools-adb
```

---

## 💡 Tips & Best Practices

### Build Optimization:
- Always enable for production builds
- Test optimized build on device (some minification may break code)
- Keep unoptimized source files backed up

### Version Management:
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

### APK Signing:
- Generate keystore once, use forever
- **NEVER lose keystore** - you can't update app without it
- Use different keystores for different apps
- Backup keystore to cloud storage (encrypted)

### ADB Testing:
- Keep device plugged in during development
- Use "Install and Launch" for quick iteration
- Check logcat for runtime errors
- Test on multiple devices/Android versions

### Recent Projects:
- Clean up old projects periodically
- Use descriptive app names
- Organize output directories

---

## 🐛 Troubleshooting

### "Feature not available" warnings:
- Check if optional dependencies are installed
- See requirements.txt for package list
- Features work gracefully without optional deps

### Dark mode doesn't apply fully:
- Some widgets may not support theming
- Restart app after theme change
- Check if custom styles override theme

### Build optimization breaks app:
- Disable optimization for that specific file type
- Check console for optimization errors
- Some JavaScript may not minify correctly

### Keystore generation fails:
- Install Java JDK (not just JRE)
- Add `keytool` to system PATH
- Check Java version: `java -version`

### ADB device not detected:
- Enable USB debugging on device
- Try different USB cable/port
- Run `adb devices` in terminal to verify
- Restart adb server: `adb kill-server && adb start-server`

---

## 📚 Additional Resources

- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Android Developer Guide](https://developer.android.com/guide)
- [Android Keystore System](https://developer.android.com/training/articles/keystore)
- [ADB Documentation](https://developer.android.com/studio/command-line/adb)

---

## 🔄 Update Notes

All features are backward compatible. Existing projects will continue to work.

New features are **opt-in** - enable in settings to use them.

Configuration files are created automatically when features are first used.

---

## ✅ Feature Status Legend

- ✅ **Ready**: Fully implemented and tested
- 🚧 **In Progress**: Partially implemented
- 📋 **Planned**: Scheduled for future release
- ❌ **Not Available**: Not implemented

---

**Version**: 2.0.0
**Last Updated**: 2024
**Author**: HTML to APK Converter Team
