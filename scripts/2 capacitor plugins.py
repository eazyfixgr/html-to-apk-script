#!/usr/bin/env python3
"""
Capacitor Project Configurator
Adds plugins and splash screen to an existing Capacitor project
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import time
import threading
import queue

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class CapacitorConfigurator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Capacitor Project Configurator")
        self.root.geometry("1000x700")
        
        # Variables
        self.project_dir_var = tk.StringVar()
        self.splash_image_var = tk.StringVar()
        
        # State
        self.is_processing = False
        self.log_queue = queue.Queue()
        
        # Plugin categories with Capacitor plugins
        self.plugin_categories = {
            "Camera & Media": {
                "@capacitor/camera": {
                    "name": "Camera",
                    "description": "Take photos and access photo library",
                    "permissions": {
                        "android": ["android.permission.CAMERA", "android.permission.READ_EXTERNAL_STORAGE", 
                                   "android.permission.WRITE_EXTERNAL_STORAGE"],
                        "ios": ["NSCameraUsageDescription", "NSPhotoLibraryUsageDescription"]
                    }
                }
            },
            "Location": {
                "@capacitor/geolocation": {
                    "name": "Geolocation",
                    "description": "Get device GPS coordinates",
                    "permissions": {
                        "android": ["android.permission.ACCESS_FINE_LOCATION", 
                                   "android.permission.ACCESS_COARSE_LOCATION"],
                        "ios": ["NSLocationWhenInUseUsageDescription"]
                    }
                }
            },
            "Storage & Data": {
                "@capacitor/preferences": {
                    "name": "Preferences",
                    "description": "Simple key-value storage",
                    "permissions": {"android": [], "ios": []}
                },
                "@capacitor/filesystem": {
                    "name": "Filesystem",
                    "description": "Read and write files",
                    "permissions": {
                        "android": ["android.permission.READ_EXTERNAL_STORAGE", 
                                   "android.permission.WRITE_EXTERNAL_STORAGE"],
                        "ios": []
                    }
                }
            },
            "Network": {
                "@capacitor/network": {
                    "name": "Network",
                    "description": "Monitor network connectivity",
                    "permissions": {"android": ["android.permission.ACCESS_NETWORK_STATE"], "ios": []}
                }
            },
            "Device Info": {
                "@capacitor/device": {
                    "name": "Device",
                    "description": "Get device information",
                    "permissions": {"android": [], "ios": []}
                }
            },
            "Notifications": {
                "@capacitor/local-notifications": {
                    "name": "Local Notifications",
                    "description": "Schedule local notifications",
                    "permissions": {
                        "android": ["android.permission.POST_NOTIFICATIONS"],
                        "ios": []
                    }
                },
                "@capacitor/push-notifications": {
                    "name": "Push Notifications",
                    "description": "Receive push notifications",
                    "permissions": {
                        "android": ["android.permission.POST_NOTIFICATIONS"],
                        "ios": []
                    }
                }
            },
            "UI & UX": {
                "@capacitor/status-bar": {
                    "name": "Status Bar",
                    "description": "Control status bar appearance",
                    "permissions": {"android": [], "ios": []}
                },
                "@capacitor/splash-screen": {
                    "name": "Splash Screen",
                    "description": "Control splash screen (auto-selected)",
                    "permissions": {"android": [], "ios": []},
                    "auto_select": True
                },
                "@capacitor/haptics": {
                    "name": "Haptics",
                    "description": "Vibration feedback",
                    "permissions": {
                        "android": ["android.permission.VIBRATE"],
                        "ios": []
                    }
                },
                "@capacitor/keyboard": {
                    "name": "Keyboard",
                    "description": "Keyboard display control",
                    "permissions": {"android": [], "ios": []}
                }
            },
            "Sharing & Browser": {
                "@capacitor/share": {
                    "name": "Share",
                    "description": "Share content with other apps",
                    "permissions": {"android": [], "ios": []}
                },
                "@capacitor/browser": {
                    "name": "Browser",
                    "description": "Open URLs in system browser",
                    "permissions": {"android": [], "ios": []}
                }
            },
            "App Control": {
                "@capacitor/app": {
                    "name": "App",
                    "description": "Handle app state and URL opening",
                    "permissions": {"android": [], "ios": []}
                }
            }
        }
        
        # Plugin selection storage
        self.selected_plugins = {}
        for category in self.plugin_categories.values():
            for package in category.keys():
                auto_select = category[package].get("auto_select", False)
                self.selected_plugins[package] = tk.BooleanVar(value=auto_select)
        
        # Splash screen sizes
        self.SPLASH_SIZES = {
            'mdpi': (320, 480),
            'hdpi': (480, 800),
            'xhdpi': (720, 1280),
            'xxhdpi': (1080, 1920),
            'xxxhdpi': (1440, 2560)
        }
        
        self.setup_ui()
        self.setup_queue_monitoring()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_container, text="Capacitor Project Configurator", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=(0, 5))
        
        desc_label = ttk.Label(main_container, 
                              text="Add plugins and splash screen to your Capacitor project",
                              foreground="gray")
        desc_label.pack(pady=(0, 20))
        
        # Project selection
        project_frame = ttk.LabelFrame(main_container, text="Project", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(project_frame, text="Capacitor Project Directory:").pack(side=tk.LEFT)
        ttk.Entry(project_frame, textvariable=self.project_dir_var, width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(project_frame, text="Browse", command=self.browse_project).pack(side=tk.LEFT)
        ttk.Button(project_frame, text="Validate", command=self.validate_project).pack(side=tk.LEFT, padx=(5, 0))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Plugins tab
        plugins_tab = ttk.Frame(notebook, padding="10")
        notebook.add(plugins_tab, text="Plugins")
        self.setup_plugins_tab(plugins_tab)
        
        # Splash screen tab
        splash_tab = ttk.Frame(notebook, padding="10")
        notebook.add(splash_tab, text="Splash Screen")
        self.setup_splash_tab(splash_tab)
        
        # Log tab
        log_tab = ttk.Frame(notebook, padding="10")
        notebook.add(log_tab, text="Log")
        self.setup_log_tab(log_tab)
        
        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.apply_button = ttk.Button(button_frame, text="Apply Configuration", 
                                       command=self.apply_configuration, style="Accent.TButton")
        self.apply_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Selection", command=self.clear_selection).pack(side=tk.LEFT)
        
        # Status bar
        self.status_label = ttk.Label(main_container, text="Ready", foreground="gray")
        self.status_label.pack(side=tk.BOTTOM, anchor=tk.W, pady=(5, 0))
        
    def setup_plugins_tab(self, parent):
        """Setup the plugins selection tab"""
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Select All", command=self.select_all_plugins).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Deselect All", command=self.deselect_all_plugins).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Select Recommended", command=self.select_recommended).pack(side=tk.LEFT)
        
        # Plugin count
        self.plugin_count_label = ttk.Label(btn_frame, text="0 plugins selected", foreground="blue")
        self.plugin_count_label.pack(side=tk.RIGHT)
        
        # Scrollable plugin list
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create categorized plugin checkboxes
        for category_name, plugins in self.plugin_categories.items():
            category_frame = ttk.LabelFrame(scrollable_frame, text=category_name, padding="10")
            category_frame.pack(fill=tk.X, pady=5, padx=5)
            
            for package, info in plugins.items():
                plugin_frame = ttk.Frame(category_frame)
                plugin_frame.pack(fill=tk.X, pady=3)
                
                cb = ttk.Checkbutton(plugin_frame, variable=self.selected_plugins[package],
                                   command=self.update_plugin_count)
                cb.pack(side=tk.LEFT, padx=(0, 10))
                
                info_frame = ttk.Frame(plugin_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                name_label = ttk.Label(info_frame, text=info["name"], font=("TkDefaultFont", 10, "bold"))
                name_label.pack(anchor=tk.W)
                
                desc_label = ttk.Label(info_frame, text=info["description"], foreground="gray", 
                                      font=("TkDefaultFont", 9))
                desc_label.pack(anchor=tk.W)
                
                pkg_label = ttk.Label(info_frame, text=package, foreground="blue", 
                                     font=("TkDefaultFont", 8))
                pkg_label.pack(anchor=tk.W)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update initial count
        self.update_plugin_count()
        
    def setup_splash_tab(self, parent):
        """Setup the splash screen tab"""
        if not PIL_AVAILABLE:
            warning = ttk.Label(parent, text="⚠ PIL not installed. Install with: pip install Pillow", 
                              foreground="red", font=("TkDefaultFont", 10, "bold"))
            warning.pack(pady=20)
            return
        
        # Instructions
        inst_frame = ttk.Frame(parent)
        inst_frame.pack(fill=tk.X, pady=(0, 20))
        
        inst_text = """How to add a splash screen:
1. Select your Capacitor project directory
2. Choose a splash screen image (PNG recommended, 2732x2732px ideal)
3. Click 'Apply Configuration' to generate all required sizes and configure the project"""
        
        ttk.Label(inst_frame, text=inst_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Image selection
        img_frame = ttk.LabelFrame(parent, text="Splash Screen Image", padding="10")
        img_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(img_frame, text="Image File:").pack(side=tk.LEFT)
        ttk.Entry(img_frame, textvariable=self.splash_image_var, width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(img_frame, text="Browse", command=self.browse_splash_image).pack(side=tk.LEFT)
        
        # Preview
        self.preview_frame = ttk.LabelFrame(parent, text="Preview", padding="10")
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(self.preview_frame, text="No image selected")
        self.preview_label.pack(expand=True)
        
        self.splash_image_var.trace_add('write', self.update_splash_preview)
        
    def setup_log_tab(self, parent):
        """Setup the log tab"""
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        
    def browse_project(self):
        """Browse for project directory"""
        directory = filedialog.askdirectory(title="Select Capacitor Project Directory")
        if directory:
            self.project_dir_var.set(directory)
            self.validate_project()
            
    def validate_project(self):
        """Validate that the directory is a valid Capacitor project"""
        project_dir = self.project_dir_var.get().strip()
        if not project_dir:
            return
        
        path = Path(project_dir)
        
        # Check for key files
        has_package_json = (path / "package.json").exists()
        has_capacitor_config = (path / "capacitor.config.ts").exists() or (path / "capacitor.config.json").exists()
        has_android = (path / "android").exists()
        
        if has_package_json and has_capacitor_config:
            if has_android:
                messagebox.showinfo("Valid Project", 
                                  "✓ Valid Capacitor project with Android platform detected")
            else:
                messagebox.showwarning("Android Missing", 
                                     "⚠ Valid Capacitor project, but Android platform not found.\n"
                                     "Make sure to run 'npx cap add android' first.")
        else:
            missing = []
            if not has_package_json:
                missing.append("package.json")
            if not has_capacitor_config:
                missing.append("capacitor.config.*")
            
            messagebox.showerror("Invalid Project", 
                               f"✗ Not a valid Capacitor project.\nMissing: {', '.join(missing)}")
            
    def browse_splash_image(self):
        """Browse for splash screen image"""
        filetypes = [("PNG files", "*.png"), ("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select Splash Screen Image", filetypes=filetypes)
        if filename:
            self.splash_image_var.set(filename)
            
    def update_splash_preview(self, *args):
        """Update splash screen preview"""
        if not PIL_AVAILABLE:
            return
            
        img_path = self.splash_image_var.get().strip()
        if not img_path or not Path(img_path).exists():
            self.preview_label.config(text="No image selected", image="")
            return
        
        try:
            img = Image.open(img_path)
            info = f"Size: {img.width}x{img.height}\nFormat: {img.format}"
            
            if img.width < 1024 or img.height < 1024:
                info += "\n⚠ Too small (min 1024x1024)"
            elif img.width >= 2732 and img.height >= 2732:
                info += "\n✓ Good size"
            
            # Create thumbnail
            thumb = img.copy()
            thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            import io
            import base64
            buffer = io.BytesIO()
            thumb.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            photo = tk.PhotoImage(data=img_data)
            self.preview_label.config(text=info, image=photo, compound=tk.TOP)
            self.preview_label.image = photo
            
        except Exception as e:
            self.preview_label.config(text=f"Error: {e}", image="")
            
    def update_plugin_count(self):
        """Update plugin count label"""
        count = sum(1 for var in self.selected_plugins.values() if var.get())
        self.plugin_count_label.config(text=f"{count} plugin{'s' if count != 1 else ''} selected")
        
    def select_all_plugins(self):
        """Select all plugins"""
        for var in self.selected_plugins.values():
            var.set(True)
        self.update_plugin_count()
        
    def deselect_all_plugins(self):
        """Deselect all plugins"""
        # Keep splash screen plugin selected
        for package, var in self.selected_plugins.items():
            if package == "@capacitor/splash-screen":
                continue
            var.set(False)
        self.update_plugin_count()
        
    def select_recommended(self):
        """Select recommended plugins"""
        recommended = ["@capacitor/splash-screen", "@capacitor/status-bar", 
                      "@capacitor/device", "@capacitor/app"]
        self.deselect_all_plugins()
        for package in recommended:
            if package in self.selected_plugins:
                self.selected_plugins[package].set(True)
        self.update_plugin_count()
        
    def clear_selection(self):
        """Clear all selections"""
        self.deselect_all_plugins()
        self.splash_image_var.set("")
        
    def setup_queue_monitoring(self):
        """Setup queue monitoring for log messages"""
        self.root.after(100, self.check_log_queue)
        
    def check_log_queue(self):
        """Check log queue for new messages"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.append_log(message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_log_queue)
        
    def log(self, message, level="info"):
        """Add message to log queue"""
        self.log_queue.put((message, level))
        
    def append_log(self, data):
        """Append message to log text widget"""
        message, level = data
        self.log_text.insert(tk.END, f"{message}\n")
        
        line_start = f"{float(self.log_text.index(tk.END)) - 1.0:.1f}"
        if level == "success":
            self.log_text.tag_add("success", line_start, tk.END)
        elif level == "error":
            self.log_text.tag_add("error", line_start, tk.END)
        elif level == "warning":
            self.log_text.tag_add("warning", line_start, tk.END)
            
        self.log_text.see(tk.END)
        self.status_label.config(text=message[:100])
        
    def apply_configuration(self):
        """Apply the selected configuration"""
        if self.is_processing:
            messagebox.showwarning("Busy", "Configuration is already being applied")
            return
        
        # Validate
        project_dir = self.project_dir_var.get().strip()
        if not project_dir:
            messagebox.showerror("Error", "Please select a project directory")
            return
        
        if not Path(project_dir).exists():
            messagebox.showerror("Error", "Project directory does not exist")
            return
        
        selected_packages = [pkg for pkg, var in self.selected_plugins.items() if var.get()]
        splash_image = self.splash_image_var.get().strip()
        
        if not selected_packages and not splash_image:
            messagebox.showwarning("Nothing Selected", 
                                 "Please select at least one plugin or add a splash screen")
            return
        
        # Confirm
        msg = f"This will:\n"
        if selected_packages:
            msg += f"• Install {len(selected_packages)} plugin(s)\n"
        if splash_image:
            msg += f"• Configure splash screen\n"
        msg += f"\nContinue?"
        
        if not messagebox.askyesno("Confirm", msg):
            return
        
        # Start processing in thread
        self.is_processing = True
        self.apply_button.config(state='disabled', text="Processing...")
        
        thread = threading.Thread(target=self.process_configuration, daemon=True)
        thread.start()
        
    def process_configuration(self):
        """Process the configuration in background thread"""
        try:
            project_dir = Path(self.project_dir_var.get().strip())
            self.log("=" * 60, "info")
            self.log("Starting Configuration", "info")
            self.log("=" * 60, "info")
            
            # Install plugins
            selected_packages = [pkg for pkg, var in self.selected_plugins.items() if var.get()]
            if selected_packages:
                self.install_plugins(project_dir, selected_packages)
            
            # Setup splash screen
            splash_image = self.splash_image_var.get().strip()
            if splash_image and Path(splash_image).exists() and PIL_AVAILABLE:
                self.setup_splash_screen(project_dir, splash_image)
            
            # Update AndroidManifest with permissions
            self.update_android_manifest(project_dir, selected_packages)
            
            # Sync Capacitor
            self.sync_capacitor(project_dir)
            
            self.log("=" * 60, "success")
            self.log("✓ Configuration completed successfully!", "success")
            self.log("=" * 60, "success")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                "Configuration applied successfully!\n\n"
                "Your project is now ready to build."))
            
        except Exception as e:
            self.log(f"✗ Error: {e}", "error")
            import traceback
            self.log(traceback.format_exc(), "error")
            self.root.after(0, lambda: messagebox.showerror("Error", 
                f"Configuration failed:\n{e}\n\nCheck the log for details."))
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.apply_button.config(state='normal', text="Apply Configuration"))
            
    def run_command(self, command, cwd=None):
        """Run a shell command"""
        try:
            self.log(f"Running: {command}", "info")
            result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, 
                                  text=True, timeout=300)
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.log(f"  {line.strip()}", "info")
            
            if result.returncode != 0:
                if result.stderr:
                    self.log(f"Error: {result.stderr.strip()}", "error")
                return False
            
            return True
        except Exception as e:
            self.log(f"Command failed: {e}", "error")
            return False
            
    def install_plugins(self, project_dir, packages):
        """Install selected plugins"""
        self.log(f"\n📦 Installing {len(packages)} plugin(s)...", "info")
        
        original_dir = os.getcwd()
        try:
            os.chdir(project_dir)
            
            for i, package in enumerate(packages, 1):
                # Get plugin info
                plugin_info = None
                for category in self.plugin_categories.values():
                    if package in category:
                        plugin_info = category[package]
                        break
                
                name = plugin_info["name"] if plugin_info else package
                self.log(f"\n[{i}/{len(packages)}] Installing {name}...", "info")
                
                if self.run_command(f"npm install {package}"):
                    self.log(f"✓ {name} installed successfully", "success")
                else:
                    self.log(f"✗ Failed to install {name}", "error")
            
            self.log("\n✓ Plugin installation completed", "success")
            
        finally:
            os.chdir(original_dir)
            
    def update_android_manifest(self, project_dir, packages):
        """Update AndroidManifest.xml with required permissions"""
        self.log("\n🔒 Updating Android permissions...", "info")
        
        manifest_path = project_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
        
        if not manifest_path.exists():
            self.log("⚠ AndroidManifest.xml not found", "warning")
            return
        
        # Collect all permissions
        all_permissions = set()
        for package in packages:
            for category in self.plugin_categories.values():
                if package in category:
                    perms = category[package]["permissions"]["android"]
                    all_permissions.update(perms)
                    break
        
        if not all_permissions:
            self.log("No additional permissions required", "info")
            return
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add permissions
            added = 0
            for perm in all_permissions:
                perm_tag = f'<uses-permission android:name="{perm}" />'
                if perm not in content:
                    content = content.replace('</manifest>', f'    {perm_tag}\n</manifest>')
                    self.log(f"  + {perm}", "info")
                    added += 1
            
            # Add GPS features if geolocation is used
            if "@capacitor/geolocation" in packages:
                if 'android.hardware.location.gps' not in content:
                    features = '''
    <uses-feature android:name="android.hardware.location" android:required="true" />
    <uses-feature android:name="android.hardware.location.gps" android:required="false" />'''
                    content = content.replace('</manifest>', f'{features}\n</manifest>')
                    self.log("  + GPS features", "info")
                    added += 1
            
            if added > 0:
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"✓ Added {added} permission(s)/feature(s)", "success")
            else:
                self.log("All permissions already present", "info")
                
        except Exception as e:
            self.log(f"✗ Failed to update manifest: {e}", "error")
            
    def setup_splash_screen(self, project_dir, splash_image_path):
        """Setup splash screen in the Android project"""
        self.log("\n🎨 Setting up splash screen...", "info")
        
        try:
            source_img = Image.open(splash_image_path)
            self.log(f"Source image: {source_img.width}x{source_img.height}", "info")
            
            android_res = project_dir / "android" / "app" / "src" / "main" / "res"
            
            # Clean up any existing splash files first to avoid duplicates
            self.log("  Cleaning existing splash files...", "info")
            for density in ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi', '']:
                if density:
                    drawable_dir = android_res / f"drawable-{density}"
                else:
                    drawable_dir = android_res / "drawable"
                
                if drawable_dir.exists():
                    for splash_file in drawable_dir.glob("splash*"):
                        splash_file.unlink()
                        self.log(f"    Removed {splash_file.name}", "info")
            
            # Generate splash screens for each density (portrait only)
            for density, size in self.SPLASH_SIZES.items():
                drawable_dir = android_res / f"drawable-{density}"
                drawable_dir.mkdir(parents=True, exist_ok=True)
                
                # Portrait splash
                splash_img = self.resize_splash(source_img, size[0], size[1])
                splash_img.save(drawable_dir / "splash.png", "PNG")
                
                self.log(f"  ✓ Generated {density} splash ({size[0]}x{size[1]})", "info")
            
            # Update MainActivity theme
            self.update_main_activity(project_dir)
            
            self.log("✓ Splash screen configured successfully", "success")
            
        except Exception as e:
            self.log(f"✗ Failed to setup splash screen: {e}", "error")
            
    def resize_splash(self, img, target_w, target_h):
        """Resize splash screen image to target size (crop from center)"""
        # Calculate scale to fill target
        scale = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        
        scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop from center
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return scaled.crop((left, top, left + target_w, top + target_h))
        
    def update_main_activity(self, project_dir):
        """Update MainActivity to use splash screen theme"""
        manifest_path = project_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
        
        if not manifest_path.exists():
            self.log("  ⚠ AndroidManifest.xml not found", "warning")
            return
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update MainActivity theme to show splash
            if 'android:theme="@style/' in content:
                # MainActivity already has a theme, update it
                if 'AppTheme.NoActionBarLaunch' not in content:
                    content = content.replace(
                        'android:theme="@style/AppTheme"',
                        'android:theme="@style/AppTheme.NoActionBarLaunch"'
                    )
                    self.log("  ✓ Updated MainActivity theme", "info")
            
            # Ensure colors.xml exists
            values_dir = project_dir / "android" / "app" / "src" / "main" / "res" / "values"
            values_dir.mkdir(parents=True, exist_ok=True)
            
            colors_path = values_dir / "colors.xml"
            if not colors_path.exists():
                colors_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#3F51B5</color>
    <color name="colorPrimaryDark">#303F9F</color>
    <color name="colorAccent">#FF4081</color>
</resources>'''
                with open(colors_path, 'w', encoding='utf-8') as f:
                    f.write(colors_xml)
                self.log("  ✓ Created colors.xml", "info")
            
            # Create proper styles.xml
            styles_path = values_dir / "styles.xml"
            styles_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
    </style>
    
    <style name="AppTheme.NoActionBarLaunch" parent="AppTheme">
        <item name="android:windowBackground">@drawable/splash</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:windowActionBar">false</item>
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowContentOverlay">@null</item>
    </style>
</resources>'''
            with open(styles_path, 'w', encoding='utf-8') as f:
                f.write(styles_xml)
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("  ✓ Configured splash screen theme", "info")
            
        except Exception as e:
            self.log(f"  ✗ Failed to update MainActivity: {e}", "error")
        
    def sync_capacitor(self, project_dir):
        """Sync Capacitor to native projects"""
        self.log("\n🔄 Syncing Capacitor...", "info")
        
        original_dir = os.getcwd()
        try:
            os.chdir(project_dir)
            
            if self.run_command("npx cap sync android"):
                self.log("✓ Capacitor synced successfully", "success")
            else:
                self.log("⚠ Sync completed with warnings", "warning")
                
        finally:
            os.chdir(original_dir)
            
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    if not PIL_AVAILABLE:
        print("WARNING: PIL (Pillow) not installed")
        print("Splash screen generation will be disabled")
        print("Install with: pip install Pillow")
        print()
    
    app = CapacitorConfigurator()
    app.run()

if __name__ == "__main__":
    main()