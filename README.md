# HTML to APK Converter

A Python GUI application that converts HTML projects to Android APK files using Capacitor, with support for plugin selection, custom assets, and comprehensive build management.

## Features

- **Interactive GUI**: User-friendly interface built with Tkinter
- **Capacitor Integration**: Seamless conversion of HTML projects to native Android apps
- **Plugin System**: Select from 15+ Capacitor plugins (Camera, Geolocation, Storage, etc.)
- **Custom Assets**: Generate app icons and splash screens for all Android densities
- **Build Management**: Separate project creation and APK building workflows
- **Configuration Persistence**: Auto-save settings between sessions
- **Real-time Logging**: Detailed build logs with progress tracking
- **Debug Mode**: Enhanced debugging information for troubleshooting

## Requirements

- Python 3.7+
- Node.js and npm
- Android SDK (for APK building)
- Pillow (PIL) - optional, for icon/splash screen generation

### Python Dependencies

```bash
pip install Pillow
```

### System Dependencies

- Node.js: https://nodejs.org
- Android Studio: https://developer.android.com/studio (for Android SDK)

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install Pillow
   ```
3. Ensure Node.js and npm are installed
4. Set up Android SDK (set `ANDROID_HOME` environment variable)

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

## Recent Improvements

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

## License

This project is provided as-is for educational and development purposes.

## Credits

Built with:
- [Capacitor](https://capacitorjs.com/) - Native app runtime
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [Pillow (PIL)](https://python-pillow.org/) - Image processing
