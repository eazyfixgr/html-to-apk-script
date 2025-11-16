# HTML to APK Converter Pro

A Python GUI application that converts HTML projects to Android APK files using Capacitor, with professional features for production-ready apps.

## 🎉 Version 2.0 - NEW FEATURES!

### ✨ Major Enhancements

🎨 **Dark Mode** - Easy on the eyes, professional appearance
📂 **Recent Projects** - Quick access to your last 10 projects
🎯 **Drag & Drop** - Drop HTML folders directly onto the app
🔔 **Desktop Notifications** - Get alerted when builds complete
🔍 **APK Analyzer** - Detailed analysis of APK size, permissions, and content
📊 **Version Management** - Automatic version incrementing and build history
⚡ **Build Optimization** - Minify HTML/CSS/JS, compress images (25-50% size reduction!)
🔐 **APK Signing** - Generate keystores and build release APKs for Google Play
📱 **ADB Integration** - Install APKs directly to connected devices with one click

## Core Features

- **Interactive GUI**: User-friendly interface with dark mode support
- **Capacitor Integration**: Seamless conversion of HTML projects to native Android apps
- **Plugin System**: Select from 15+ Capacitor plugins (Camera, Geolocation, Storage, etc.)
- **Custom Assets**: Generate app icons and splash screens for all Android densities
- **Build Management**: Separate project creation and APK building workflows
- **Configuration Persistence**: Auto-save settings between sessions
- **Real-time Logging**: Detailed build logs with progress tracking
- **Debug Mode**: Enhanced debugging information for troubleshooting
- **Professional Tools**: Everything you need for production-ready apps

## Requirements

### Minimum (Core Features)
- Python 3.7+
- Node.js and npm
- Pillow (PIL)

### Recommended (All Features)
- Python 3.7+
- Node.js and npm
- Pillow, htmlmin, csscompressor, jsmin, plyer
- Java JDK (for APK signing)
- Android SDK (for device installation and APK analysis)

## Installation

### Quick Start (Basic Features)

```bash
# Install minimum dependencies
pip install Pillow

# Run the application
python html_to_apk_converter.py
```

### Full Installation (All Features)

```bash
# Install all Python dependencies
pip install -r requirements.txt

# Install system tools (see INSTALL.md for details)
# - Java JDK for keystore generation
# - Android SDK for ADB and AAPT
```

📖 **See [INSTALL.md](INSTALL.md) for complete installation instructions**

## Usage

### Running the Application

```bash
python html_to_apk_converter.py
```

### Basic Workflow

1. **Configure Project**:
   - Select your HTML project directory (must contain `index.html`)
   - Enter app name (will be sanitized if contains invalid characters)
   - Enter app ID in reverse domain format (e.g., `com.example.myapp`)
   - Specify output directory

2. **Select Plugins** (Optional):
   - Navigate to "Capacitor Plugins" tab
   - Select desired plugins from the list
   - Use preset buttons for common plugin combinations

3. **Configure Assets** (Optional):
   - Navigate to "Assets (Icons & Splash)" tab
   - Enable custom assets
   - Select icon file (recommended: 1024x1024 PNG)
   - Select splash screen (recommended: 2732x2732 PNG)
   - Enable auto-generation for all Android sizes

4. **Create Project**:
   - Click "Create Project with Plugins"
   - Wait for project creation to complete
   - View detailed logs in build log window

5. **Build APK**:
   - Click "Build APK"
   - Wait for build process (may take several minutes)
   - Find generated APK in project directory

### Updating Assets for Existing Projects

**New in v2.1**: You can now change icons and splash screens without recreating the entire project!

1. **Navigate to Assets Tab**:
   - Go to "Assets (Icons & Splash)" tab

2. **Select New Assets**:
   - Choose new icon file and/or new splash screen file
   - Preview will update automatically

3. **Regenerate Assets**:
   - Click "🔄 Regenerate Assets for Existing Project" button
   - Confirm the regeneration
   - Wait for process to complete

4. **Build APK**:
   - Return to main tab
   - Click "Build APK"
   - New assets will be included in the APK

**Benefits**:
- No need to recreate the entire project structure
- Update only the assets you want to change
- Quick iterative design workflow
- Assets are automatically synced to Android project

## Recent Improvements

### Version 2.1 Improvements

#### New Feature: Asset Regeneration
- **Regenerate icons and splash screens for existing projects**: No need to create a new project when you want to change assets
- **Flexible updates**: Change icon only, splash only, or both
- **Automatic synchronization**: Capacitor sync runs automatically after regeneration
- **Time-saving workflow**: Update assets in seconds, not minutes

### Version 2.0 Improvements

#### Security Enhancements
- **Fixed command injection vulnerabilities**: Commands are now executed safely using list format instead of shell strings
- **Input validation**: App ID must follow reverse domain notation (e.g., `com.example.app`)
- **App name sanitization**: Special characters are automatically removed or user is prompted
- **HTML directory validation**: Pre-flight check ensures `index.html` exists before starting

#### Bug Fixes
- **Fixed PIL image preview**: Now uses `ImageTk.PhotoImage` instead of broken base64 method
- **Improved ImageTk integration**: Proper import and usage of PIL's ImageTk module
- **Memory leak fixes**: Image references are properly managed to prevent memory leaks
- **Process cleanup**: Subprocess resources are properly cleaned up in finally blocks

#### Error Handling
- **Robust configuration loading**: Individual setting errors don't break entire config load
- **Configuration backup**: Corrupted config files are automatically backed up
- **Atomic config save**: Uses temporary file + rename to prevent corruption
- **Better error messages**: More descriptive error messages with context
- **File operation resilience**: Permission errors and I/O errors are handled gracefully

#### Code Quality
- **Removed duplicate code**: Eliminated redundant `import tkinter` statements in methods
- **Consistent path handling**: All paths use `pathlib.Path` for cross-platform compatibility
- **Improved resource management**: Proper cleanup in finally blocks
- **Better cancellation handling**: Operations can be cancelled cleanly without resource leaks
- **Enhanced debug mode**: More detailed debugging information available

#### User Experience
- **File renamed**: Removed spaces from filename (`html_to_apk_converter.py`)
- **Better validation messages**: Clear, actionable error messages
- **Progress tracking**: More granular progress updates during build
- **File count reporting**: Shows number of files/directories copied

## App ID Format

The app ID must follow reverse domain notation:
- Format: `com.example.appname`
- Must have at least 2 segments separated by dots
- Each segment must start with a lowercase letter
- Can contain lowercase letters, numbers, and underscores
- Examples:
  - ✅ `com.mycompany.myapp`
  - ✅ `org.example.app123`
  - ❌ `myapp` (only one segment)
  - ❌ `com.My-App` (uppercase and hyphens not allowed)

## Available Capacitor Plugins

1. **Camera** - Access device camera and photo library
2. **Geolocation** - Get device location coordinates
3. **Storage** (Preferences) - Store key-value data persistently
4. **Network** - Monitor network connectivity status
5. **Device Info** - Get device information
6. **Filesystem** - Read and write files to device storage
7. **Local Notifications** - Schedule and display local notifications
8. **Push Notifications** - Handle push notifications
9. **Status Bar** - Control the status bar appearance
10. **Splash Screen** - Control the splash screen
11. **Haptics** - Trigger haptic feedback
12. **Share** - Share content with other apps
13. **Browser** - Open URLs in system browser
14. **App** - Handle app state and URL opening
15. **Keyboard** - Keyboard display and behavior control

## Configuration File

Settings are automatically saved to `html_to_apk_config.ini` in the same directory as the script. This includes:
- Project paths
- App name and ID
- Asset settings
- Plugin selections

The configuration is loaded automatically on startup and saved on exit or when clicking "Save Settings".

## Troubleshooting

### "PIL not available" warning
Install Pillow: `pip install Pillow`

### "Node.js is not installed"
Download and install from https://nodejs.org

### "Android SDK not found"
1. Install Android Studio
2. Set `ANDROID_HOME` environment variable to SDK location
3. Common locations:
   - Windows: `C:\Users\<username>\AppData\Local\Android\Sdk`
   - macOS: `~/Library/Android/sdk`
   - Linux: `~/Android/Sdk`

### Build fails with Gradle errors
1. Ensure ANDROID_HOME is set correctly
2. Check build logs for specific errors
3. Try running Gradle clean: Delete `android/build` folder
4. Enable debug mode for more detailed logs

### "index.html not found"
Ensure your HTML project directory contains an `index.html` file at the root level.

## Debug Mode

Enable "Debug mode" checkbox in the main tab for:
- Detailed command execution logs
- Working directory information
- Full stderr output
- Exception stack traces

## 🆕 New in Version 2.0

### Complete Feature Guides

📖 **[NEW_FEATURES.md](NEW_FEATURES.md)** - Comprehensive guide to all 9 new features
- Dark Mode
- Recent Projects
- Drag & Drop
- Desktop Notifications
- APK Analyzer
- Version Management
- Build Optimization
- APK Signing & Release Builds
- ADB Integration

📦 **[INSTALL.md](INSTALL.md)** - Detailed installation guide for all platforms
- Windows, macOS, Linux specific instructions
- Dependency installation guides
- Verification scripts
- Troubleshooting

📝 **[CHANGELOG.md](CHANGELOG.md)** - Complete version history and changes

### Quick Feature Overview

#### 🔐 Production-Ready Builds
- Generate Android keystores
- Sign APKs for Google Play Store
- Build release APKs (not just debug)

#### ⚡ Optimization
- Minify HTML, CSS, JavaScript
- Compress images automatically
- **25-50% smaller APK sizes!**

#### 📱 Testing Workflow
- Detect connected Android devices
- Install APK with one click
- Launch app automatically
- Real-time device testing

#### 📊 Professional Tools
- Version history tracking
- APK analysis and reporting
- Build notifications
- Dark mode UI

### Optional Dependencies

For full features, install:
```bash
pip install htmlmin csscompressor jsmin plyer
```

See [INSTALL.md](INSTALL.md) for complete setup instructions.

## License

This project is provided as-is for educational and development purposes.

## Credits

Built with:
- [Capacitor](https://capacitorjs.com/) - Native app runtime
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [Pillow (PIL)](https://python-pillow.org/) - Image processing
