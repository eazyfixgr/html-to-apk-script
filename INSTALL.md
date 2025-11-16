# Installation Guide - HTML to APK Converter Pro

Complete installation guide for all features of the HTML to APK Converter.

## 📋 Table of Contents

1. [Quick Start (Minimum Setup)](#quick-start)
2. [Full Installation (All Features)](#full-installation)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Dependency Details](#dependency-details)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start (Minimum Setup)

**Minimum requirements to run the converter:**

```bash
# Install only required dependency
pip install Pillow
```

This gives you:
- ✅ Core HTML to APK conversion
- ✅ Icon and splash screen generation
- ✅ Plugin selection
- ✅ Basic build functionality

Missing features:
- ❌ Build optimization
- ❌ Desktop notifications
- ❌ Drag and drop
- ❌ APK signing
- ❌ ADB installation

---

## 🎯 Full Installation (All Features)

### Step 1: Install Python Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt
```

Or install individually:

```bash
# Core (required)
pip install Pillow

# Optimization (recommended)
pip install htmlmin csscompressor jsmin

# Notifications (optional)
pip install plyer

# Drag and Drop (optional)
pip install tkinterdnd2
```

### Step 2: Install System Tools

#### Java JDK (for APK Signing)

Required for keystore generation and release builds.

**Windows**:
1. Download Java JDK from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://adoptium.net/)
2. Run installer
3. Add to PATH:
   - Control Panel → System → Advanced → Environment Variables
   - Add `C:\Program Files\Java\jdk-XX\bin` to PATH

**macOS**:
```bash
brew install openjdk@17
```

**Linux**:
```bash
sudo apt-get update
sudo apt-get install openjdk-17-jdk
```

Verify installation:
```bash
java -version
keytool -help
```

#### Android SDK (for ADB and AAPT)

Required for device installation and APK analysis.

**Option A: Android Studio (Recommended)**
1. Download [Android Studio](https://developer.android.com/studio)
2. Install with default settings
3. Open Android Studio → SDK Manager
4. Install:
   - Android SDK Platform Tools
   - Android SDK Build Tools

5. Set environment variables:

**Windows**:
```batch
setx ANDROID_HOME "C:\Users\YourUsername\AppData\Local\Android\Sdk"
setx PATH "%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\build-tools"
```

**macOS/Linux**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
export ANDROID_HOME=$HOME/Android/Sdk          # Linux
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0
```

**Option B: Command Line Tools Only (Lightweight)**

**macOS**:
```bash
brew install android-platform-tools
```

**Linux**:
```bash
sudo apt-get install android-tools-adb android-tools-fastboot
```

**Windows**:
Download [Platform Tools](https://developer.android.com/studio/releases/platform-tools) and extract to `C:\platform-tools`, then add to PATH.

Verify installation:
```bash
adb version
```

---

## 💻 Platform-Specific Instructions

### Windows

**1. Install Prerequisites**:
```batch
# Python (if not installed)
# Download from https://www.python.org/downloads/

# Verify Python
python --version

# Install dependencies
pip install -r requirements.txt
```

**2. Install Java JDK**:
- Download from https://adoptium.net/
- Install to default location
- Add to PATH (see above)

**3. Install Android Studio** (or Platform Tools):
- Download from https://developer.android.com/studio
- Install with default options
- Set ANDROID_HOME environment variable

**4. Optional - Visual C++ Build Tools**:
Some Python packages may require:
- Download [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- Select "Desktop development with C++"

---

### macOS

**1. Install Homebrew** (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**2. Install Python** (if not installed):
```bash
brew install python python-tk
```

**3. Install Dependencies**:
```bash
# Python packages
pip3 install -r requirements.txt

# Java
brew install openjdk@17

# Android tools
brew install android-platform-tools
```

**4. Install Android Studio** (optional, for full SDK):
- Download from https://developer.android.com/studio
- Drag to Applications folder
- Run and complete setup

---

### Linux (Ubuntu/Debian)

**1. Install System Dependencies**:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    openjdk-17-jdk \
    android-tools-adb \
    android-tools-fastboot
```

**2. Install Python Packages**:
```bash
pip3 install -r requirements.txt
```

**3. Set Android Environment** (if using Android Studio):
```bash
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

---

## 📦 Dependency Details

### Core Dependencies (Required)

#### Pillow
**What**: Python Imaging Library
**Used for**: Icon and splash screen generation
**Install**:
```bash
pip install Pillow
```
**Verify**:
```python
python -c "from PIL import Image; print('Pillow OK')"
```

### Optimization Dependencies (Optional but Recommended)

#### htmlmin
**What**: HTML minification
**Used for**: Reducing HTML file sizes
**Savings**: 20-30% size reduction
**Install**:
```bash
pip install htmlmin
```

#### csscompressor
**What**: CSS compression
**Used for**: Reducing CSS file sizes
**Savings**: 30-40% size reduction
**Install**:
```bash
pip install csscompressor
```

#### jsmin
**What**: JavaScript minification
**Used for**: Reducing JS file sizes
**Savings**: 20-35% size reduction
**Install**:
```bash
pip install jsmin
```

### UI Enhancement Dependencies (Optional)

#### plyer
**What**: Cross-platform notifications
**Used for**: Desktop notifications when build completes
**Install**:
```bash
pip install plyer
```
**Note**: May require additional system packages on Linux

#### tkinterdnd2
**What**: Drag and drop for Tkinter
**Used for**: Dragging HTML folders onto the app
**Install**:
```bash
pip install tkinterdnd2
```
**Note**:
- May not work on all systems
- Windows: Usually works fine
- macOS: May require additional setup
- Linux: May require tcl-dnd package

---

## ✅ Verification

### Check All Installations

Run this verification script:

```python
#!/usr/bin/env python3
"""Verify all dependencies for HTML to APK Converter"""

import sys

def check_module(name, package=None):
    package = package or name
    try:
        __import__(package)
        print(f"✅ {name}")
        return True
    except ImportError:
        print(f"❌ {name} (install with: pip install {package})")
        return False

def check_command(cmd, install_hint):
    import subprocess
    try:
        result = subprocess.run([cmd, '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print(f"✅ {cmd}")
            return True
        else:
            print(f"❌ {cmd} ({install_hint})")
            return False
    except FileNotFoundError:
        print(f"❌ {cmd} ({install_hint})")
        return False
    except Exception as e:
        print(f"⚠️  {cmd} (error: {e})")
        return False

print("=" * 60)
print("HTML to APK Converter - Dependency Check")
print("=" * 60)

print("\n📦 Required Python Packages:")
required_ok = check_module("Pillow", "PIL")

print("\n⚡ Optional Python Packages (Optimization):")
opt_count = 0
opt_count += check_module("htmlmin")
opt_count += check_module("csscompressor")
opt_count += check_module("jsmin")

print("\n🎨 Optional Python Packages (UI Features):")
ui_count = 0
ui_count += check_module("plyer")
ui_count += check_module("tkinterdnd2")

print("\n🔧 System Tools:")
sys_count = 0
sys_count += check_command("java", "Install Java JDK")
sys_count += check_command("keytool", "Included with Java JDK")
sys_count += check_command("adb", "Install Android SDK Platform Tools")
sys_count += check_command("node", "Download from nodejs.org")
sys_count += check_command("npm", "Included with Node.js")

print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print(f"Required: {'✅ OK' if required_ok else '❌ Missing'}")
print(f"Optimization: {opt_count}/3 packages available")
print(f"UI Features: {ui_count}/2 packages available")
print(f"System Tools: {sys_count}/5 tools available")

if required_ok:
    print("\n✅ Minimum requirements met - app will run!")
else:
    print("\n❌ Missing required packages - app will not work")
    sys.exit(1)

if opt_count < 3:
    print("ℹ️  Install optimization packages for smaller APK sizes")

if ui_count < 2:
    print("ℹ️  Install UI packages for enhanced features")

if sys_count < 5:
    print("ℹ️  Install system tools for advanced features")
```

Save as `check_dependencies.py` and run:
```bash
python check_dependencies.py
```

---

## 🐛 Troubleshooting

### Python Package Installation Fails

**Issue**: `pip install` fails with permission error

**Solution**:
```bash
# Linux/macOS
pip install --user <package>

# Or use sudo (not recommended)
sudo pip install <package>

# Windows (run as Administrator)
pip install <package>
```

**Issue**: SSL certificate error

**Solution**:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

### tkinterdnd2 Installation Issues

**Windows**:
- Usually works fine with `pip install tkinterdnd2`

**macOS**:
- May need: `brew install tcl-tk`
- Or use alternative: Manual file drag detection

**Linux**:
- Install: `sudo apt-get install python3-tk tk-dev`
- May need tcl-dnd: Not always available

**Alternative**: App works fine without drag-drop, use Browse button

### Java/Keytool Not Found

**Issue**: `keytool: command not found`

**Solution**:
1. Verify Java installed: `java -version`
2. Find Java location:
   - Windows: `where java`
   - macOS/Linux: `which java`
3. Add to PATH (see platform instructions above)

### ADB Not Found

**Issue**: `adb: command not found`

**Solution**:
1. Install Android SDK Platform Tools
2. Find adb location:
   - Windows: `C:\Users\<user>\AppData\Local\Android\Sdk\platform-tools`
   - macOS: `~/Library/Android/sdk/platform-tools`
   - Linux: `~/Android/Sdk/platform-tools`
3. Add to PATH

### Permission Denied (Linux/macOS)

**Issue**: Can't execute script

**Solution**:
```bash
chmod +x html_to_apk_converter.py
```

### Module Import Errors

**Issue**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
# Make sure you're using the correct Python version
python --version
python3 --version

# Install for specific Python version
python3 -m pip install <package>
```

---

## 🎯 Recommended Setup for Different Use Cases

### Casual User (Just Want APKs):
```bash
pip install Pillow
```
- ✅ Basic functionality
- ✅ Icon/splash generation
- ❌ No optimization

### Developer (Quality Builds):
```bash
pip install Pillow htmlmin csscompressor jsmin
```
- ✅ Full functionality
- ✅ Optimized builds
- ✅ Smaller APK sizes

### Professional (Production Apps):
```bash
# All Python packages
pip install -r requirements.txt

# Java JDK (for signing)
# Android SDK (for testing)
```
- ✅ All features
- ✅ Release builds
- ✅ Device testing
- ✅ APK signing

---

## 📞 Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [NEW_FEATURES.md](NEW_FEATURES.md) for feature-specific help
3. Check console output for specific error messages
4. Verify all dependencies with check script

---

## 🔄 Updating

To update to latest version:

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update system tools
# Java: Download latest JDK
# Android SDK: Update via Android Studio SDK Manager
```

---

**Version**: 2.0.0
**Last Updated**: 2024
