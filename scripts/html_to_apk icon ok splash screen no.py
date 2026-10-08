#!/usr/bin/env python3
"""
HTML to APK Conversion GUI using Capacitor
Enhanced version with Icon & Splash Screen Generation
Maintains all original functionality with enhanced GUI interface and settings persistence
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime
import threading
import time
import queue
import configparser
from typing import Optional, Tuple, List

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

# Try to import PIL for image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class HTMLToAPKConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HTML to APK Converter")
        self.root.geometry("850x750")
        self.root.resizable(True, True)
        
        # Configuration file path - save in same directory as script
        script_dir = Path(__file__).parent if __file__ else Path.cwd()
        self.config_file = script_dir / "html_to_apk_config.ini"
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
        # Variables
        self.html_dir_var = tk.StringVar()
        self.app_name_var = tk.StringVar(value="MyApp")
        self.app_id_var = tk.StringVar(value="com.example.myapp")
        self.output_dir_var = tk.StringVar()
        
        # Asset variables
        self.icon_file_var = tk.StringVar()
        self.splash_file_var = tk.StringVar()
        self.use_custom_assets = tk.BooleanVar(value=False)
        self.auto_generate_assets = tk.BooleanVar(value=True)
        
        # Build state
        self.is_building = False
        self.build_thread = None
        self.start_time = None
        self.current_step = 0
        self.total_steps = 10  # Increased for asset generation steps
        
        # Log window reference
        self.log_window = None
        
        # Asset preview references
        self.icon_preview_label = None
        self.splash_preview_label = None
        
        # Check PIL availability
        if not PIL_AVAILABLE:
            messagebox.showwarning(
                "Missing Dependencies", 
                "PIL (Python Imaging Library) is not installed.\n\n"
                "Icon and splash screen generation will be disabled.\n\n"
                "To enable these features, install Pillow:\n"
                "pip install Pillow"
            )
        
        # Load saved configuration before setting up UI
        self.load_configuration()
        
        self.setup_ui()
        self.setup_queue_monitoring()
        
        # Save configuration when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # Android icon sizes (in pixels)
    ANDROID_ICON_SIZES = {
        'mdpi': 48,
        'hdpi': 72,
        'xhdpi': 96,
        'xxhdpi': 144,
        'xxxhdpi': 192
    }
    
    # Splash screen sizes for different densities
    SPLASH_SCREEN_SIZES = {
        'mdpi': (320, 480),
        'hdpi': (480, 800),
        'xhdpi': (720, 1280),
        'xxhdpi': (1080, 1920),
        'xxxhdpi': (1440, 2560)
    }
        
    def load_configuration(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            return
            
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if 'Settings' in config:
                settings = config['Settings']
                
                # Load each setting if it exists
                if 'html_directory' in settings:
                    html_dir = settings['html_directory']
                    # Only set if the directory still exists
                    if Path(html_dir).exists():
                        self.html_dir_var.set(html_dir)
                
                if 'output_directory' in settings:
                    self.output_dir_var.set(settings['output_directory'])
                
                if 'app_name' in settings:
                    self.app_name_var.set(settings['app_name'])
                
                if 'app_id' in settings:
                    self.app_id_var.set(settings['app_id'])
                
                # Load asset settings
                if 'icon_file' in settings and Path(settings['icon_file']).exists():
                    self.icon_file_var.set(settings['icon_file'])
                
                if 'splash_file' in settings and Path(settings['splash_file']).exists():
                    self.splash_file_var.set(settings['splash_file'])
                
                if 'use_custom_assets' in settings:
                    self.use_custom_assets.set(settings.getboolean('use_custom_assets'))
                
                if 'auto_generate_assets' in settings:
                    self.auto_generate_assets.set(settings.getboolean('auto_generate_assets'))
                    
            print(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config = configparser.ConfigParser()
            config['Settings'] = {
                'html_directory': self.html_dir_var.get(),
                'output_directory': self.output_dir_var.get(),
                'app_name': self.app_name_var.get(),
                'app_id': self.app_id_var.get(),
                'icon_file': self.icon_file_var.get(),
                'splash_file': self.splash_file_var.get(),
                'use_custom_assets': str(self.use_custom_assets.get()),
                'auto_generate_assets': str(self.auto_generate_assets.get())
            }
            
            with open(self.config_file, 'w') as configfile:
                config.write(configfile)
                
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            
    def on_closing(self):
        """Handle window closing event"""
        # Save configuration before closing
        self.save_configuration()
        
        # Stop any running build process
        if self.is_building and self.build_thread:
            self.is_building = False
            
        # Close log window if open
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.destroy()
            
        # Close main window
        self.root.destroy()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main settings tab
        main_frame = ttk.Frame(notebook, padding="10")
        notebook.add(main_frame, text="Project Settings")
        
        # Assets tab
        assets_frame = ttk.Frame(notebook, padding="10")
        notebook.add(assets_frame, text="Assets (Icons & Splash)")
        
        # Setup main tab
        self.setup_main_tab(main_frame)
        
        # Setup assets tab
        self.setup_assets_tab(assets_frame)
        
    def setup_main_tab(self, parent):
        """Setup the main project settings tab"""
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        
        # Title
        title_font = Font(size=16, weight="bold")
        title_label = ttk.Label(parent, text="HTML to APK Converter", font=title_font)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(parent, 
                              text="Convert your HTML project to an Android APK using Capacitor",
                              foreground="gray")
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # HTML Directory Selection
        ttk.Label(parent, text="HTML Project Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.html_dir_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_html_dir).grid(row=2, column=2, padx=(5, 0), pady=5)
        
        # App Name
        ttk.Label(parent, text="App Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.app_name_var, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # App ID
        ttk.Label(parent, text="App ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.app_id_var, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # Output Directory
        ttk.Label(parent, text="Output Directory:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.output_dir_var, width=50).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_output_dir).grid(row=5, column=2, padx=(5, 0), pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Overall progress
        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.overall_progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Progress labels
        self.progress_label = ttk.Label(progress_frame, text="Ready to start")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.time_label = ttk.Label(progress_frame, text="", foreground="gray")
        self.time_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Current step progress
        self.step_progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.step_progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(20, 0))
        
        # Start/Stop button
        self.start_button = ttk.Button(button_frame, text="Start Conversion", 
                                      command=self.toggle_conversion, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Show logs button
        self.logs_button = ttk.Button(button_frame, text="Show Build Logs", 
                                     command=self.show_log_window)
        self.logs_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save Settings button
        self.save_button = ttk.Button(button_frame, text="Save Settings", 
                                     command=self.save_configuration)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT)
        
        # Status bar
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="gray")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Debug mode checkbox
        self.debug_mode = tk.BooleanVar()
        debug_check = ttk.Checkbutton(status_frame, text="Debug mode", variable=self.debug_mode)
        debug_check.grid(row=0, column=1, sticky=tk.E)
        
        # Show config file location
        config_info = ttk.Label(status_frame, text=f"Config: {self.config_file.name}", 
                               foreground="lightgray", font=("TkDefaultFont", 8))
        config_info.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # Auto-fill output directory when app name changes
        self.app_name_var.trace_add('write', self.update_output_dir)
        
        # Auto-save configuration when any field changes
        for var in [self.html_dir_var, self.app_name_var, self.app_id_var, self.output_dir_var]:
            var.trace_add('write', self.auto_save_config)
    
    def setup_assets_tab(self, parent):
        """Setup the assets (icons & splash screens) tab"""
        parent.columnconfigure(1, weight=1)
        
        # Title
        title_font = Font(size=14, weight="bold")
        title_label = ttk.Label(parent, text="Icon & Splash Screen Generation", font=title_font)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        if not PIL_AVAILABLE:
            # Warning label if PIL is not available
            warning_frame = ttk.Frame(parent, style="Warning.TFrame")
            warning_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
            warning_frame.columnconfigure(0, weight=1)
            
            warning_label = ttk.Label(warning_frame, 
                                    text="⚠️ Asset generation disabled - PIL not installed",
                                    foreground="red", font=("TkDefaultFont", 10, "bold"))
            warning_label.grid(row=0, column=0, pady=5)
            
            install_label = ttk.Label(warning_frame, 
                                    text="Run 'pip install Pillow' to enable icon and splash screen generation",
                                    foreground="gray")
            install_label.grid(row=1, column=0, pady=2)
            
            # Disable asset functionality
            state = 'disabled'
        else:
            state = 'normal'
        
        # Asset generation options
        options_frame = ttk.LabelFrame(parent, text="Asset Generation Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Checkbutton(options_frame, text="Use custom icons and splash screens", 
                       variable=self.use_custom_assets,
                       command=self.toggle_custom_assets,
                       state=state).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Auto-generate all Android asset sizes", 
                       variable=self.auto_generate_assets,
                       state=state).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Icon section
        icon_frame = ttk.LabelFrame(parent, text="App Icon", padding="10")
        icon_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        icon_frame.columnconfigure(1, weight=1)
        
        ttk.Label(icon_frame, text="Icon File (1024x1024 PNG recommended):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_file_var, width=50, state=state)
        self.icon_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        self.icon_browse_btn = ttk.Button(icon_frame, text="Browse", command=self.browse_icon_file, state=state)
        self.icon_browse_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Icon preview
        self.icon_preview_frame = ttk.Frame(icon_frame)
        self.icon_preview_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.icon_preview_label = ttk.Label(self.icon_preview_frame, text="No icon selected")
        self.icon_preview_label.pack()
        
        # Icon requirements
        icon_req_label = ttk.Label(icon_frame, 
                                  text="• Use square images (1:1 aspect ratio)\n• Minimum 1024x1024 pixels\n• PNG format recommended\n• Avoid transparency for better compatibility",
                                  foreground="gray", font=("TkDefaultFont", 9))
        icon_req_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Splash screen section
        splash_frame = ttk.LabelFrame(parent, text="Splash Screen", padding="10")
        splash_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        splash_frame.columnconfigure(1, weight=1)
        
        ttk.Label(splash_frame, text="Splash Image (2732x2732 PNG recommended):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.splash_entry = ttk.Entry(splash_frame, textvariable=self.splash_file_var, width=50, state=state)
        self.splash_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        self.splash_browse_btn = ttk.Button(splash_frame, text="Browse", command=self.browse_splash_file, state=state)
        self.splash_browse_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Splash preview
        self.splash_preview_frame = ttk.Frame(splash_frame)
        self.splash_preview_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.splash_preview_label = ttk.Label(self.splash_preview_frame, text="No splash screen selected")
        self.splash_preview_label.pack()
        
        # Splash requirements
        splash_req_label = ttk.Label(splash_frame, 
                                    text="• Use square images (1:1 aspect ratio) for best results\n• Minimum 2732x2732 pixels\n• PNG format recommended\n• Center important content (will be cropped for different screen ratios)",
                                    foreground="gray", font=("TkDefaultFont", 9))
        splash_req_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Preview generation button
        if PIL_AVAILABLE:
            self.preview_button = ttk.Button(parent, text="Generate Asset Previews", 
                                           command=self.generate_asset_previews)
            self.preview_button.grid(row=5, column=0, columnspan=3, pady=15)
        
        # Set up traces for asset variables
        self.icon_file_var.trace_add('write', self.on_icon_changed)
        self.splash_file_var.trace_add('write', self.on_splash_changed)
        self.icon_file_var.trace_add('write', self.auto_save_config)
        self.splash_file_var.trace_add('write', self.auto_save_config)
        self.use_custom_assets.trace_add('write', self.auto_save_config)
        self.auto_generate_assets.trace_add('write', self.auto_save_config)
        
        # Initial state update
        self.toggle_custom_assets()
        
    def toggle_custom_assets(self):
        """Toggle the enabled state of custom asset controls"""
        if not PIL_AVAILABLE:
            return
            
        state = 'normal' if self.use_custom_assets.get() else 'disabled'
        
        # Toggle icon controls
        self.icon_entry.config(state=state)
        self.icon_browse_btn.config(state=state)
        
        # Toggle splash controls  
        self.splash_entry.config(state=state)
        self.splash_browse_btn.config(state=state)
        
    def browse_icon_file(self):
        """Browse for app icon file"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select App Icon",
            filetypes=filetypes
        )
        
        if filename:
            self.icon_file_var.set(filename)
            
    def browse_splash_file(self):
        """Browse for splash screen file"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Splash Screen",
            filetypes=filetypes
        )
        
        if filename:
            self.splash_file_var.set(filename)
            
    def on_icon_changed(self, *args):
        """Called when icon file changes"""
        if PIL_AVAILABLE:
            self.update_icon_preview()
            
    def on_splash_changed(self, *args):
        """Called when splash file changes"""  
        if PIL_AVAILABLE:
            self.update_splash_preview()
            
    def update_icon_preview(self):
        """Update the icon preview"""
        icon_path = self.icon_file_var.get().strip()
        
        if not icon_path or not Path(icon_path).exists():
            self.icon_preview_label.config(text="No icon selected", image="")
            return
            
        try:
            # Load and resize image for preview
            img = Image.open(icon_path)
            
            # Show image info
            info_text = f"Size: {img.width}x{img.height}\nFormat: {img.format}\nMode: {img.mode}"
            
            # Check if image meets requirements
            if img.width < 512 or img.height < 512:
                info_text += "\n⚠️ Too small (min 1024x1024)"
            elif img.width != img.height:
                info_text += "\n⚠️ Not square"
            elif img.width >= 1024 and img.height >= 1024:
                info_text += "\n✅ Good size"
            
            # Create preview thumbnail
            preview_size = (64, 64)
            img_preview = img.copy()
            img_preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            import tkinter as tk
            photo = tk.PhotoImage(data=self.pil_to_base64(img_preview))
            
            self.icon_preview_label.config(text=info_text, image=photo, compound=tk.TOP)
            self.icon_preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.icon_preview_label.config(text=f"Error loading image: {e}", image="")
            
    def update_splash_preview(self):
        """Update the splash screen preview"""
        splash_path = self.splash_file_var.get().strip()
        
        if not splash_path or not Path(splash_path).exists():
            self.splash_preview_label.config(text="No splash screen selected", image="")
            return
            
        try:
            # Load and resize image for preview
            img = Image.open(splash_path)
            
            # Show image info
            info_text = f"Size: {img.width}x{img.height}\nFormat: {img.format}\nMode: {img.mode}"
            
            # Check if image meets requirements
            if img.width < 1024 or img.height < 1024:
                info_text += "\n⚠️ Too small (min 2732x2732)"
            elif img.width < 2732 or img.height < 2732:
                info_text += "\n⚠️ Small for splash (rec 2732x2732)"
            else:
                info_text += "\n✅ Good size"
            
            # Create preview thumbnail
            preview_size = (64, 64)
            img_preview = img.copy()
            img_preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            import tkinter as tk
            photo = tk.PhotoImage(data=self.pil_to_base64(img_preview))
            
            self.splash_preview_label.config(text=info_text, image=photo, compound=tk.TOP)
            self.splash_preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.splash_preview_label.config(text=f"Error loading image: {e}", image="")
            
    def pil_to_base64(self, pil_image):
        """Convert PIL image to base64 for tkinter PhotoImage"""
        import io
        import base64
        
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
        
    def generate_asset_previews(self):
        """Generate and show previews of all asset sizes that will be created"""
        if not PIL_AVAILABLE:
            messagebox.showerror("Error", "PIL is required for asset preview generation")
            return
            
        if not self.use_custom_assets.get():
            messagebox.showinfo("Info", "Custom assets are not enabled. Enable them to generate previews.")
            return
            
        icon_path = self.icon_file_var.get().strip()
        splash_path = self.splash_file_var.get().strip()
        
        if not icon_path and not splash_path:
            messagebox.showinfo("Info", "Please select at least one asset file to preview")
            return
            
        self.show_asset_preview_window(icon_path, splash_path)
        
    def show_asset_preview_window(self, icon_path, splash_path):
        """Show a window with previews of generated assets"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Asset Preview")
        preview_window.geometry("600x500")
        
        # Create scrollable frame
        canvas = tk.Canvas(preview_window)
        scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Show icon previews
        if icon_path and Path(icon_path).exists():
            try:
                icon_frame = ttk.LabelFrame(scrollable_frame, text="App Icons", padding="10")
                icon_frame.pack(fill=tk.X, pady=5)
                
                icon_img = Image.open(icon_path)
                row = 0
                
                for density, size in self.ANDROID_ICON_SIZES.items():
                    # Generate icon at this size
                    resized_icon = icon_img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Create preview (max 48x48 for display)
                    display_size = min(48, size)
                    preview_icon = resized_icon.resize((display_size, display_size), Image.Resampling.LANCZOS)
                    
                    # Convert to tkinter format
                    photo = tk.PhotoImage(data=self.pil_to_base64(preview_icon))
                    
                    # Create label with preview
                    label = ttk.Label(icon_frame, text=f"{density}: {size}x{size}px", image=photo, compound=tk.LEFT)
                    label.image = photo
                    label.pack(anchor=tk.W, pady=2)
                    
            except Exception as e:
                ttk.Label(scrollable_frame, text=f"Error previewing icons: {e}").pack(pady=5)
        
        # Show splash previews
        if splash_path and Path(splash_path).exists():
            try:
                splash_frame = ttk.LabelFrame(scrollable_frame, text="Splash Screens", padding="10")
                splash_frame.pack(fill=tk.X, pady=5)
                
                splash_img = Image.open(splash_path)
                
                for density, size in self.SPLASH_SCREEN_SIZES.items():
                    width, height = size
                    
                    # Generate splash at this size (crop from center)
                    splash_resized = self.resize_splash_for_screen(splash_img, width, height)
                    
                    # Create preview (scale down for display)
                    aspect_ratio = width / height
                    if aspect_ratio > 1:
                        preview_w, preview_h = 64, int(64 / aspect_ratio)
                    else:
                        preview_w, preview_h = int(64 * aspect_ratio), 64
                    
                    preview_splash = splash_resized.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
                    
                    # Convert to tkinter format
                    photo = tk.PhotoImage(data=self.pil_to_base64(preview_splash))
                    
                    # Create label with preview
                    label = ttk.Label(splash_frame, text=f"{density}: {width}x{height}px", image=photo, compound=tk.LEFT)
                    label.image = photo
                    label.pack(anchor=tk.W, pady=2)
                    
            except Exception as e:
                ttk.Label(scrollable_frame, text=f"Error previewing splash screens: {e}").pack(pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add close button
        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
        
    def resize_splash_for_screen(self, img, target_width, target_height):
        """Resize splash screen image for specific screen size (crop from center)"""
        # Calculate scaling to fill the target size
        scale_w = target_width / img.width
        scale_h = target_height / img.height
        scale = max(scale_w, scale_h)  # Scale to fill, not fit
        
        # Scale the image
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from center
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        cropped_img = scaled_img.crop((left, top, right, bottom))
        return cropped_img
        
    def generate_android_icons(self, source_path, output_dir):
        """Generate all Android icon sizes from source image"""
        if not PIL_AVAILABLE:
            self.log("❌ PIL not available - cannot generate icons")
            return False
            
        self.log("🎨 Generating Android app icons...")
        
        try:
            # Load source image
            source_img = Image.open(source_path)
            self.log(f"📐 Source icon size: {source_img.width}x{source_img.height}")
            
            # Create mipmap directories
            android_res_dir = Path(output_dir) / "android" / "app" / "src" / "main" / "res"
            
            for density, size in self.ANDROID_ICON_SIZES.items():
                mipmap_dir = android_res_dir / f"mipmap-{density}"
                mipmap_dir.mkdir(parents=True, exist_ok=True)
                
                # Resize icon
                resized_icon = source_img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Save as PNG
                icon_path = mipmap_dir / "ic_launcher.png"
                resized_icon.save(icon_path, "PNG")
                
                self.log(f"✅ Generated {density} icon: {size}x{size}px -> {icon_path.name}")
            
            # Also create adaptive icon background and foreground
            self.generate_adaptive_icons(source_img, android_res_dir)
            
            self.log("✅ All app icons generated successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to generate icons: {e}")
            return False
            
    def generate_adaptive_icons(self, source_img, res_dir):
        """Generate adaptive icon components (API 26+)"""
        try:
            self.log("🎨 Generating adaptive icons...")
            
            # Create a simple background (solid color or gradient)
            for density, size in self.ANDROID_ICON_SIZES.items():
                mipmap_dir = res_dir / f"mipmap-{density}"
                
                # Background - solid color
                bg_img = Image.new('RGB', (size, size), color='#FFFFFF')
                bg_path = mipmap_dir / "ic_launcher_background.png" 
                bg_img.save(bg_path, "PNG")
                
                # Foreground - scaled down source icon with padding
                fg_size = int(size * 0.6)  # 60% of full size for safe area
                padding = (size - fg_size) // 2
                
                fg_img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
                resized_source = source_img.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
                fg_img.paste(resized_source, (padding, padding))
                
                fg_path = mipmap_dir / "ic_launcher_foreground.png"
                fg_img.save(fg_path, "PNG")
                
            self.log("✅ Adaptive icons generated")
            
        except Exception as e:
            self.log(f"⚠️ Failed to generate adaptive icons: {e}")
            
    def generate_splash_screens(self, source_path, output_dir):
        """Generate splash screens for different screen densities"""
        if not PIL_AVAILABLE:
            self.log("❌ PIL not available - cannot generate splash screens")
            return False
            
        self.log("🖼️ Generating splash screens...")
        
        try:
            # Load source image
            source_img = Image.open(source_path)
            self.log(f"📐 Source splash size: {source_img.width}x{source_img.height}")
            
            # Create drawable directories
            android_res_dir = Path(output_dir) / "android" / "app" / "src" / "main" / "res"
            
            for density, size in self.SPLASH_SCREEN_SIZES.items():
                width, height = size
                drawable_dir = android_res_dir / f"drawable-{density}"
                drawable_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate splash for this size
                splash_img = self.resize_splash_for_screen(source_img, width, height)
                
                # Save splash screen
                splash_path = drawable_dir / "splash.png"
                splash_img.save(splash_path, "PNG")
                
                self.log(f"✅ Generated {density} splash: {width}x{height}px -> {splash_path.name}")
                
                # Also generate landscape version
                landscape_img = self.resize_splash_for_screen(source_img, height, width)
                landscape_path = drawable_dir / "splash_landscape.png"
                landscape_img.save(landscape_path, "PNG")
                
                self.log(f"✅ Generated {density} landscape splash: {height}x{width}px -> {landscape_path.name}")
            
            # Generate splash drawable XML
            self.generate_splash_drawable_xml(android_res_dir)
            
            self.log("✅ All splash screens generated successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to generate splash screens: {e}")
            return False
            
    def generate_splash_drawable_xml(self, res_dir):
        """Generate XML drawable for splash screen"""
        try:
            drawable_dir = res_dir / "drawable"
            drawable_dir.mkdir(parents=True, exist_ok=True)
            
            # Create splash drawable XML
            splash_xml = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap
            android:gravity="center"
            android:src="@drawable/splash" />
    </item>
</layer-list>'''
            
            xml_path = drawable_dir / "splash_drawable.xml"
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(splash_xml)
                
            self.log("✅ Splash drawable XML created")
            
        except Exception as e:
            self.log(f"⚠️ Failed to create splash drawable XML: {e}")
            
    def update_android_manifest_for_splash(self, project_dir):
        """Update AndroidManifest.xml to use custom splash screen"""
        try:
            manifest_path = project_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
            
            if not manifest_path.exists():
                self.log("⚠️ AndroidManifest.xml not found - splash screen configuration skipped")
                return
                
            # Read current manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Add splash screen theme if not already present
            if 'android:theme="@style/AppTheme.Splash"' not in manifest_content:
                # This would require more complex XML manipulation
                # For now, just log that manual configuration may be needed
                self.log("ℹ️ Splash screen assets generated - manual AndroidManifest.xml configuration may be needed")
            
        except Exception as e:
            self.log(f"⚠️ Could not update AndroidManifest.xml: {e}")
    
    def auto_save_config(self, *args):
        """Automatically save configuration when fields change"""
        # Use after_idle to avoid saving too frequently during rapid changes
        if not hasattr(self, '_save_pending'):
            self._save_pending = True
            self.root.after_idle(self._do_auto_save)
            
    def _do_auto_save(self):
        """Perform the actual auto-save"""
        self.save_configuration()
        self._save_pending = False
        
    def setup_queue_monitoring(self):
        """Setup monitoring of queues for thread communication"""
        self.root.after(100, self.check_queues)
        
    def check_queues(self):
        """Check queues for messages from worker thread"""
        # Check log queue
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.append_to_log_window(message)
        except queue.Empty:
            pass
        
        # Check progress queue
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                self.update_progress_ui(progress_data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queues)
        
    def browse_html_dir(self):
        """Browse for HTML project directory"""
        directory = filedialog.askdirectory(title="Select HTML Project Directory")
        if directory:
            self.html_dir_var.set(directory)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def update_output_dir(self, *args):
        """Auto-update output directory based on app name"""
        if not self.output_dir_var.get() or not self.output_dir_var.get().strip():
            app_name = self.app_name_var.get().strip()
            if app_name:
                self.output_dir_var.set(f"{app_name}_capacitor")
                
    def clear_form(self):
        """Clear all form fields"""
        # Show confirmation dialog
        result = messagebox.askyesnocancel(
            "Clear Settings", 
            "What would you like to clear?\n\n"
            "Yes = Clear all settings\n"
            "No = Clear only project settings\n"
            "Cancel = Keep everything"
        )
        
        if result is None:  # Cancel
            return
        elif result:  # Yes - clear all
            self.html_dir_var.set("")
            self.app_name_var.set("MyApp")
            self.app_id_var.set("com.example.myapp")
            self.output_dir_var.set("")
            self.icon_file_var.set("")
            self.splash_file_var.set("")
            self.use_custom_assets.set(False)
            self.auto_generate_assets.set(True)
        else:  # No - clear only project settings
            self.html_dir_var.set("")
            self.app_name_var.set("MyApp")
            self.app_id_var.set("com.example.myapp")
            self.output_dir_var.set("")
        
        # Save the cleared configuration
        self.save_configuration()
        
    def validate_input(self):
        """Validate user input"""
        if not self.html_dir_var.get().strip():
            messagebox.showerror("Error", "Please select an HTML project directory")
            return False
            
        if not Path(self.html_dir_var.get()).exists():
            messagebox.showerror("Error", "HTML project directory does not exist")
            return False
            
        if not self.app_name_var.get().strip():
            messagebox.showerror("Error", "Please enter an app name")
            return False
            
        if not self.app_id_var.get().strip():
            messagebox.showerror("Error", "Please enter an app ID")
            return False
            
        if not self.output_dir_var.get().strip():
            messagebox.showerror("Error", "Please specify an output directory")
            return False
        
        # Validate assets if custom assets are enabled
        if self.use_custom_assets.get() and PIL_AVAILABLE:
            icon_path = self.icon_file_var.get().strip()
            splash_path = self.splash_file_var.get().strip()
            
            if icon_path and not Path(icon_path).exists():
                messagebox.showerror("Error", f"Icon file does not exist: {icon_path}")
                return False
                
            if splash_path and not Path(splash_path).exists():
                messagebox.showerror("Error", f"Splash screen file does not exist: {splash_path}")
                return False
            
            # Validate image dimensions
            if icon_path:
                try:
                    img = Image.open(icon_path)
                    if img.width < 512 or img.height < 512:
                        result = messagebox.askyesno("Image Warning", 
                            f"Icon image is {img.width}x{img.height}px.\n"
                            "Recommended minimum is 1024x1024px.\n\n"
                            "Continue anyway?")
                        if not result:
                            return False
                except Exception as e:
                    messagebox.showerror("Error", f"Could not validate icon image: {e}")
                    return False
            
        return True
        
    def toggle_conversion(self):
        """Start or stop the conversion process"""
        if not self.is_building:
            self.start_conversion()
        else:
            self.stop_conversion()
            
    def start_conversion(self):
        """Start the conversion process"""
        if not self.validate_input():
            return
            
        # Save current settings before starting build
        self.save_configuration()
            
        self.is_building = True
        self.start_time = time.time()
        self.current_step = 0
        
        # Update UI
        self.start_button.config(text="Cancel", style="")
        self.overall_progress['value'] = 0
        self.step_progress.start(10)
        
        # Start worker thread
        self.build_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.build_thread.start()
        
    def stop_conversion(self):
        """Stop the conversion process"""
        self.is_building = False
        self.start_button.config(text="Start Conversion", style="Accent.TButton")
        self.step_progress.stop()
        self.progress_label.config(text="Cancelled by user")
        self.log("⚠️ Conversion cancelled by user")
        
    def conversion_worker(self):
        """Worker thread for the conversion process"""
        original_cwd = os.getcwd()
        try:
            self.log("🚀 Starting HTML to APK conversion...")
            self.log("=" * 50)
            
            # Get input values
            html_dir = Path(self.html_dir_var.get())
            app_name = self.app_name_var.get().strip()
            app_id = self.app_id_var.get().strip()
            output_dir = self.output_dir_var.get().strip()
            
            self.log(f"📋 Configuration:")
            self.log(f"  HTML Directory: {html_dir.absolute()}")
            self.log(f"  App Name: {app_name}")
            self.log(f"  App ID: {app_id}")
            self.log(f"  Output Directory: {output_dir}")
            
            if self.use_custom_assets.get() and PIL_AVAILABLE:
                self.log(f"  Custom Assets: Enabled")
                if self.icon_file_var.get().strip():
                    self.log(f"  Icon: {self.icon_file_var.get()}")
                if self.splash_file_var.get().strip():
                    self.log(f"  Splash: {self.splash_file_var.get()}")
            
            self.log("-" * 50)
            
            # Step 1: Check prerequisites
            self.update_step(1, "Checking prerequisites...")
            if not self.is_building:
                return
            if not self.check_prerequisites():
                self.log("❌ Prerequisites check failed")
                return
                
            # Step 2: Create project
            self.update_step(2, "Creating Capacitor project...")
            if not self.is_building:
                return
            if not self.create_capacitor_project(output_dir, app_name, app_id):
                self.log("❌ Failed to create Capacitor project")
                return
                
            project_path = Path(output_dir).absolute()
            self.log(f"✅ Project path: {project_path}")
            
            # Step 3: Copy HTML files
            self.update_step(3, "Copying HTML files...")
            if not self.is_building:
                return
            if not self.copy_html_files(html_dir, project_path):
                self.log("❌ Failed to copy HTML files")
                return
                
            # Step 4: Setup Android platform
            self.update_step(4, "Setting up Android platform...")
            if not self.is_building:
                return
            if not self.setup_android_platform(project_path, app_name, app_id):
                self.log("❌ Failed to setup Android platform")
                return
            
            # Step 5: Generate custom assets
            if self.use_custom_assets.get() and PIL_AVAILABLE:
                self.update_step(5, "Generating custom assets...")
                if not self.is_building:
                    return
                    
                icon_path = self.icon_file_var.get().strip()
                splash_path = self.splash_file_var.get().strip()
                
                if icon_path and Path(icon_path).exists():
                    self.generate_android_icons(icon_path, project_path)
                    
                if splash_path and Path(splash_path).exists():
                    self.generate_splash_screens(splash_path, project_path)
                    self.update_android_manifest_for_splash(project_path)
            else:
                self.update_step(5, "Skipping asset generation...")
                self.log("ℹ️ Custom assets disabled or PIL not available")
            
            # Step 6: Find Android SDK
            self.update_step(6, "Locating Android SDK...")
            if not self.is_building:
                return
            self.find_android_sdk()
            
            # Step 7: Sync Capacitor files
            self.update_step(7, "Syncing Capacitor files...")
            if not self.is_building:
                return
            self.sync_capacitor_files(project_path)
            
            # Step 8: Build APK
            self.update_step(8, "Building APK (this may take several minutes)...")
            if not self.is_building:
                return
            apk_path = self.build_apk(project_path, app_name)
            
            if not apk_path:
                self.log("❌ APK build failed")
                return
            
            # Step 9: Finalize
            self.update_step(9, "Finalizing...")
            if not self.is_building:
                return
            time.sleep(1)  # Brief pause for visual feedback
            
            # Step 10: Complete
            self.update_step(10, "Conversion complete!")
            
            self.log("=" * 50)
            self.log("🎉 HTML to APK conversion completed successfully!")
            self.log(f"📱 APK: {apk_path.name if apk_path else 'See build logs'}")
            self.log(f"📁 Project: {project_path}")
            if self.use_custom_assets.get() and PIL_AVAILABLE:
                self.log("🎨 Custom assets generated and integrated")
            self.log("=" * 50)
            
            # Success notification
            if self.is_building:  # Only show if not cancelled
                self.show_success_notification(apk_path, project_path)
            
        except Exception as e:
            self.log(f"❌ Unexpected error during conversion: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log(f"💥 Error details: {error_details}")
            
            if self.is_building:  # Only show error if not cancelled
                self.root.after(0, lambda: messagebox.showerror(
                    "Conversion Error", 
                    f"An unexpected error occurred during conversion:\n\n{e}\n\nCheck the build logs for more details."
                ))
        finally:
            # Clean up
            self.is_building = False
            try:
                os.chdir(original_cwd)
            except:
                pass
            self.root.after(0, self.reset_ui)
    
    def sync_capacitor_files(self, project_path):
        """Sync Capacitor files to native projects"""
        original_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            self.log("🔄 Syncing files to Android project...")
            if not self.run_command_with_timeout("npx cap sync android", 
                                                timeout=180,
                                                progress_message="Syncing files to Android project"):
                self.log("⚠️ Sync failed, but continuing with build...")
            else:
                self.log("✅ Files synced successfully")
        except Exception as e:
            self.log(f"⚠️ Error during sync: {e}")
        finally:
            try:
                os.chdir(original_cwd)
            except:
                pass
            
    def reset_ui(self):
        """Reset UI after conversion completes"""
        self.start_button.config(text="Start Conversion", style="Accent.TButton")
        self.step_progress.stop()
        
    def update_step(self, step_number, message):
        """Update the current step and progress"""
        if not self.is_building:
            return
            
        self.current_step = step_number
        progress_data = {
            'step': step_number,
            'total_steps': self.total_steps,
            'message': message,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }
        self.progress_queue.put(progress_data)
        self.log(f"📋 Step {step_number}/{self.total_steps}: {message}")
        
    def update_progress_ui(self, progress_data):
        """Update progress UI elements"""
        step = progress_data['step']
        total_steps = progress_data['total_steps']
        message = progress_data['message']
        elapsed_time = progress_data['elapsed_time']
        
        # Update progress bar
        progress_percent = (step / total_steps) * 100
        self.overall_progress['value'] = progress_percent
        
        # Update labels
        self.progress_label.config(text=f"Step {step}/{total_steps}: {message}")
        
        # Update time estimation
        if step > 0 and elapsed_time > 0:
            estimated_total = elapsed_time * (total_steps / step)
            remaining_time = estimated_total - elapsed_time
            
            elapsed_str = self.format_time(elapsed_time)
            remaining_str = self.format_time(remaining_time) if remaining_time > 0 else "Almost done"
            
            self.time_label.config(text=f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
        
    def format_time(self, seconds):
        """Format seconds into human readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
            
    def log(self, message):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
        
        # Also update status bar if it's an important message
        if "✅" in message or "Step" in message:
            # Extract clean message for status
            clean_msg = message.replace("✅", "").replace("📋", "").strip()
            if clean_msg:
                self.update_status(clean_msg)
        
    def update_status(self, message):
        """Update the status label"""
        try:
            self.root.after(0, lambda: self.status_label.config(text=message))
        except:
            pass
        
    def show_log_window(self):
        """Show or create the log window"""
        if self.log_window is None or not self.log_window.winfo_exists():
            self.create_log_window()
        else:
            self.log_window.lift()
            self.log_window.focus()
            
    def create_log_window(self):
        """Create the log window"""
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Build Logs")
        self.log_window.geometry("800x600")
        
        # Text area for logs
        text_frame = ttk.Frame(self.log_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        
        # Buttons
        button_frame = ttk.Frame(self.log_window, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save Logs", 
                  command=self.save_logs).pack(side=tk.LEFT)
        
    def append_to_log_window(self, message):
        """Append message to log window if it exists"""
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_text.insert(tk.END, message + '\n')
            
            # Apply color based on content
            line_start = f"{float(self.log_text.index(tk.END)) - 1.0:.1f}"
            if "✅" in message or "SUCCESS" in message:
                self.log_text.tag_add("success", line_start, tk.END)
            elif "❌" in message or "ERROR" in message:
                self.log_text.tag_add("error", line_start, tk.END)
            elif "⚠️" in message or "WARNING" in message:
                self.log_text.tag_add("warning", line_start, tk.END)
            elif "📋" in message or "INFO" in message:
                self.log_text.tag_add("info", line_start, tk.END)
            
            # Auto-scroll to bottom
            self.log_text.see(tk.END)
            
    def clear_logs(self):
        """Clear the log window"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            
    def save_logs(self):
        """Save logs to file"""
        if hasattr(self, 'log_text'):
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Build Logs"
            )
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.log_text.get(1.0, tk.END))
                    messagebox.showinfo("Success", f"Logs saved to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save logs: {e}")
                    
    def show_success_notification(self, apk_path, project_path):
        """Show success notification"""
        self.root.after(0, lambda: self._show_success_dialog(apk_path, project_path))
        
    def _show_success_dialog(self, apk_path, project_path):
        """Show success dialog in main thread"""
        asset_info = ""
        if self.use_custom_assets.get() and PIL_AVAILABLE:
            asset_info = "\n\nCustom icons and splash screens have been integrated into your APK!"
            
        result = messagebox.showinfo(
            "Conversion Complete!",
            f"Your HTML project has been successfully converted to an APK!{asset_info}\n\n"
            f"APK Location: {apk_path.name if apk_path else 'Check build logs'}\n"
            f"Project Directory: {project_path}\n\n"
            f"You can now test the APK on an Android device."
        )
        
    # Original conversion methods adapted for GUI with asset generation
    def run_command(self, command, cwd=None, shell=True, progress_message="Running command"):
        """Run a command and return success status"""
        if not self.is_building:
            return False
            
        try:
            if self.debug_mode.get():
                self.log(f"🛠 DEBUG: Working directory: {cwd or os.getcwd()}")
                self.log(f"🛠 DEBUG: Shell mode: {shell}")
                
            self.log(f"🔧 Running: {command}")
            
            # Use shell=True on Windows for better compatibility
            if os.name == 'nt':  # Windows
                shell = True
            
            if isinstance(command, list):
                result = subprocess.run(command, cwd=cwd, shell=False, capture_output=True, 
                                      text=True, timeout=300)
            else:
                result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, 
                                      text=True, timeout=300)
            
            if self.debug_mode.get():
                self.log(f"🛠 DEBUG: Return code: {result.returncode}")
                if result.stderr and result.stderr.strip():
                    self.log(f"🛠 DEBUG: Full stderr: {result.stderr.strip()}")
            
            if result.returncode != 0:
                self.log(f"❌ Command failed: {command}")
                if result.stderr and result.stderr.strip():
                    self.log(f"❌ Error: {result.stderr.strip()}")
                if result.stdout and result.stdout.strip():
                    self.log(f"📄 Output: {result.stdout.strip()}")
                return False
            else:
                if result.stdout and result.stdout.strip():
                    # Split output into lines and log each one
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.log(f"📄 {line.strip()}")
                self.log(f"✅ {progress_message} completed successfully")
                return True
        except subprocess.TimeoutExpired:
            self.log(f"❌ Command timed out: {command}")
            return False
        except Exception as e:
            self.log(f"❌ Exception running command: {e}")
            if self.debug_mode.get():
                import traceback
                self.log(f"🛠 DEBUG: Exception details: {traceback.format_exc()}")
            return False
            
    def run_command_with_timeout(self, command, cwd=None, shell=True, timeout=300, progress_message="Running command"):
        """Run a command with extended timeout and better error handling"""
        if not self.is_building:
            return False
            
        try:
            self.log(f"🔧 Running: {command}")
            
            # Create process with non-blocking I/O for real-time output
            if isinstance(command, list):
                process = subprocess.Popen(command, cwd=cwd, shell=False, 
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         text=True, bufsize=1, universal_newlines=True)
            else:
                process = subprocess.Popen(command, cwd=cwd, shell=shell, 
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         text=True, bufsize=1, universal_newlines=True)
            
            # Read output in real-time
            output_lines = []
            start_time = time.time()
            
            while True:
                if not self.is_building:  # Check for cancellation
                    process.terminate()
                    return False
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    self.log(f"❌ Command timed out after {timeout} seconds")
                    process.terminate()
                    return False
                
                # Try to read output
                try:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output and output.strip():
                        line = output.strip()
                        self.log(f"📄 {line}")
                        output_lines.append(line)
                except:
                    pass
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
            return_code = process.poll()
            
            if return_code == 0:
                self.log(f"✅ {progress_message} completed successfully")
                return True
            else:
                self.log(f"❌ Command failed with return code: {return_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception running command: {e}")
            return False
            
    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.log("🔍 Checking prerequisites...")
        
        # Check Node.js
        self.log("📦 Checking Node.js...")
        if not self.run_command("node --version", progress_message="Checking Node.js"):
            self.log("❌ Node.js is not installed or not in PATH")
            self.log("💡 Please install Node.js from https://nodejs.org")
            
            response = messagebox.askyesno(
                "Node.js Required",
                "Node.js is required but not found.\n\n"
                "Do you want to continue anyway? (Build will likely fail)"
            )
            if not response:
                return False
        
        # Check npm
        self.log("📦 Checking npm...")
        if not self.run_command("npm --version", progress_message="Checking npm"):
            self.log("❌ npm is not installed or not in PATH")
            self.log("💡 npm should come with Node.js installation")
            
            response = messagebox.askyesno(
                "npm Required",
                "npm is required but not found.\n\n"
                "Do you want to continue anyway? (Build will likely fail)"
            )
            if not response:
                return False
        
        # Check/install Capacitor CLI
        self.log("🔌 Checking Capacitor CLI...")
        try:
            result = subprocess.run(["npm", "list", "-g", "@capacitor/cli"], 
                                  capture_output=True, text=True, shell=True, timeout=30)
            if result.returncode != 0:
                self.log("⚠️ Capacitor CLI not found globally. Installing...")
                if not self.run_command_with_timeout("npm install -g @capacitor/cli", 
                                                   timeout=180,
                                                   progress_message="Installing Capacitor CLI"):
                    self.log("❌ Failed to install Capacitor CLI")
                    
                    response = messagebox.askyesno(
                        "Capacitor CLI Installation Failed",
                        "Failed to install Capacitor CLI globally.\n\n"
                        "Do you want to continue? (We'll try to use npx instead)"
                    )
                    if not response:
                        return False
            else:
                self.log("✅ Capacitor CLI is available globally")
        except subprocess.TimeoutExpired:
            self.log("⚠️ npm command timed out while checking Capacitor CLI")
        except Exception as e:
            self.log(f"⚠️ Error checking Capacitor CLI: {e}")
        
        # Test basic npm functionality
        self.log("🧪 Testing npm functionality...")
        if not self.run_command_with_timeout("npm --version", 
                                            timeout=30, 
                                            progress_message="Testing npm"):
            self.log("⚠️ npm is not responding properly")
            
            response = messagebox.askyesno(
                "npm Issues Detected",
                "npm appears to have issues.\n\n"
                "Do you want to continue anyway?"
            )
            if not response:
                return False
        
        self.log("✅ Prerequisites check completed")
        return True
        
    def create_capacitor_project(self, output_dir, app_name, app_id):
        """Create a new Capacitor project"""
        self.log("🗃️ Creating Capacitor project...")
        
        # Check if directory exists
        output_path = Path(output_dir)
        if output_path.exists():
            self.log(f"⚠️ Directory '{output_dir}' already exists!")
            
            # Show what's in the directory
            try:
                contents = list(output_path.iterdir())
                if contents:
                    self.log("📋 Current contents:")
                    for item in contents[:10]:  # Show first 10 items
                        self.log(f"  - {item.name}")
                    if len(contents) > 10:
                        self.log(f"  ... and {len(contents) - 10} more items")
                else:
                    self.log("📁 Directory is empty")
            except:
                self.log("📁 Could not list directory contents")
            
            # Ask user what to do
            response = messagebox.askyesnocancel(
                "Directory Exists",
                f"Directory '{output_dir}' already exists.\n\n"
                f"Do you want to delete it and continue?\n"
                f"(No = Choose different directory, Cancel = Stop)"
            )
            
            if response is None:  # Cancel
                self.log("❌ Operation cancelled by user")
                return False
            elif response:  # Yes, delete
                self.log("🗑️ Removing existing directory...")
                try:
                    shutil.rmtree(output_dir)
                    self.log("✅ Directory removed successfully")
                except Exception as e:
                    self.log(f"❌ Failed to remove directory: {e}")
                    return False
            else:  # No, choose different
                new_output = filedialog.askdirectory(title="Choose New Output Directory")
                if not new_output:
                    self.log("❌ No directory selected")
                    return False
                # Update the output directory variable and try again
                self.output_dir_var.set(new_output)
                return self.create_capacitor_project(new_output, app_name, app_id)
        
        # First, install @capacitor/create-app globally to avoid prompts
        self.log("📦 Installing @capacitor/create-app globally to avoid prompts...")
        if not self.run_command("npm install -g @capacitor/create-app", 
                          progress_message="Installing create-app tool"):
            self.log("⚠️ Failed to install create-app globally, continuing anyway...")
        
        # Try multiple methods to create the project
        methods = [
            # Method 1: Use -y flag to auto-accept
            f'npx -y @capacitor/create-app "{output_dir}" "{app_name}" "{app_id}" --template blank',
            
            # Method 2: Use --yes flag
            f'npx --yes @capacitor/create-app "{output_dir}" "{app_name}" "{app_id}" --template blank',
            
            # Method 3: Without quotes
            f'npx -y @capacitor/create-app {output_dir} {app_name} {app_id} --template blank',
            
            # Method 4: Use global installation directly
            f'create-app "{output_dir}" "{app_name}" "{app_id}" --template blank',
        ]
        
        for i, command in enumerate(methods, 1):
            if not self.is_building:  # Check if cancelled
                return False
                
            self.log(f"🔧 Trying method {i}/{len(methods)}: {command}")
            
            if self.run_command_with_timeout(command, timeout=120, progress_message=f"Creating project (method {i})"):
                self.log("✅ Project created successfully!")
                break
            else:
                self.log(f"⚠️ Method {i} failed, trying next method...")
                time.sleep(1)  # Brief pause between attempts
        else:
            self.log("❌ All automated methods failed. Attempting manual project creation...")
            
            # Manual fallback - create basic structure
            try:
                self.log("🛠️ Creating project structure manually...")
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Create basic package.json
                package_json = {
                    "name": app_name.lower().replace(" ", "-"),
                    "version": "1.0.0",
                    "description": f"{app_name} mobile app",
                    "main": "index.js",
                    "scripts": {
                        "build": "echo 'No build script'",
                        "start": "echo 'No start script'"
                    },
                    "dependencies": {
                        "@capacitor/core": "latest",
                        "@capacitor/android": "latest"
                    },
                    "devDependencies": {
                        "@capacitor/cli": "latest"
                    }
                }
                
                with open(output_path / "package.json", "w") as f:
                    json.dump(package_json, f, indent=2)
                self.log("📄 Created package.json")
                
                # Create basic capacitor.config.ts
                config_content = f'''import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: '{app_id}',
  appName: '{app_name}',
  webDir: 'www',
  server: {{
    androidScheme: 'https'
  }}
}};

export default config;
'''
                with open(output_path / "capacitor.config.ts", "w") as f:
                    f.write(config_content)
                self.log("⚙️ Created capacitor.config.ts")
                
                # Create www directory
                (output_path / "www").mkdir(exist_ok=True)
                self.log("📁 Created www directory")
                
                self.log("✅ Manual project structure created successfully")
                
            except Exception as e:
                self.log(f"❌ Manual creation also failed: {e}")
                return False
        
        # Verify the project was created
        if output_path.exists():
            self.log(f"✅ Project directory created: {output_path}")
            try:
                contents = list(output_path.iterdir())
                self.log(f"📋 Created {len(contents)} files/folders:")
                for item in contents[:5]:
                    self.log(f"  - {item.name}")
                if len(contents) > 5:
                    self.log(f"  ... and {len(contents) - 5} more")
            except:
                self.log("📁 Project directory exists but contents couldn't be listed")
            return True
        else:
            self.log("❌ Project directory was not created")
            return False
            
    def copy_html_files(self, html_dir, project_dir):
        """Copy HTML files to the www directory"""
        self.log("📂 Copying HTML files...")
        
        www_dir = project_dir / "www"
        
        # Clear existing files
        if www_dir.exists():
            shutil.rmtree(www_dir)
        www_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy all files from HTML directory
            html_path = Path(html_dir)
            for item in html_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, www_dir)
                    self.log(f"📄 Copied: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, www_dir / item.name)
                    self.log(f"📁 Copied directory: {item.name}")
            
            # Check for index.html
            if not (www_dir / "index.html").exists():
                self.log("❌ index.html not found in the HTML directory")
                return False
            
            self.log("✅ HTML files copied successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to copy HTML files: {e}")
            return False
            
    def setup_android_platform(self, project_dir, app_name, app_id):
        """Add and configure Android platform"""
        self.log("🤖 Setting up Android platform...")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            self.log(f"📁 Changed to project directory: {project_dir}")
            
            # Check if package.json exists
            if not (project_dir / "package.json").exists():
                self.log("❌ package.json not found in project directory")
                return False
            
            # Install dependencies first
            self.log("📦 Installing project dependencies...")
            if not self.run_command_with_timeout("npm install", 
                                                timeout=300,
                                                progress_message="Installing dependencies"):
                self.log("⚠️ npm install failed, but continuing...")
            
            # Install Android platform
            self.log("📱 Installing Android platform...")
            if not self.run_command_with_timeout("npm install @capacitor/android", 
                                                timeout=180,
                                                progress_message="Installing Android platform"):
                self.log("❌ Failed to install Android platform")
                return False
            
            # Add Android platform
            self.log("➕ Adding Android platform...")
            if not self.run_command_with_timeout("npx cap add android", 
                                                timeout=120,
                                                progress_message="Adding Android platform"):
                self.log("❌ Failed to add Android platform")
                return False
            
            # Create/update capacitor.config.ts
            self.log("⚙️ Updating Capacitor configuration...")
            config_content = f'''import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: '{app_id}',
  appName: '{app_name}',
  webDir: 'www',
  server: {{
    androidScheme: 'https'
  }}
}};

export default config;
'''
            
            try:
                with open("capacitor.config.ts", "w", encoding='utf-8') as f:
                    f.write(config_content)
                self.log("✅ Configuration updated")
            except Exception as e:
                self.log(f"❌ Failed to update configuration: {e}")
                return False
            
            # Verify Android directory was created
            android_dir = project_dir / "android"
            if not android_dir.exists():
                self.log("❌ Android directory was not created")
                return False
            
            self.log("✅ Android directory created successfully")
            
            # Sync files
            self.log("📄 Syncing files to Android project...")
            if not self.run_command_with_timeout("npx cap sync android", 
                                                timeout=180,
                                                progress_message="Syncing files to Android project"):
                self.log("⚠️ Failed to sync files, but Android project should still work")
            
            self.log("✅ Android platform setup completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Exception during Android platform setup: {e}")
            return False
        finally:
            # Always restore original working directory
            try:
                os.chdir(original_cwd)
            except:
                pass
        
    def find_android_sdk(self):
        """Try to find Android SDK installation"""
        self.log("🔍 Checking for Android SDK...")
        
        # Check ANDROID_HOME environment variable
        android_home = os.environ.get('ANDROID_HOME')
        if android_home and Path(android_home).exists():
            self.log(f"✅ Found Android SDK at: {android_home}")
            return android_home
        
        # Common Android SDK locations
        possible_paths = [
            Path.home() / "Android" / "Sdk",
            Path.home() / "Library" / "Android" / "sdk",
            Path("/usr/local/android-sdk"),
            Path("/opt/android-sdk"),
            Path("C:/Android/Sdk"),
            Path("C:/Users") / os.environ.get('USERNAME', '') / "AppData" / "Local" / "Android" / "Sdk"
        ]
        
        for path in possible_paths:
            if path.exists():
                android_home = str(path)
                os.environ['ANDROID_HOME'] = android_home
                self.log(f"✅ Found Android SDK at: {android_home}")
                return android_home
        
        self.log("⚠️ Android SDK not found. Please install Android Studio or set ANDROID_HOME.")
        return None
        
    def build_apk(self, project_dir, app_name):
        """Build the APK"""
        self.log("🔨 Building APK...")
        
        android_dir = project_dir / "android"
        if not android_dir.exists():
            self.log("❌ Android directory not found. Make sure Android platform was added successfully.")
            return None
            
        os.chdir(android_dir)
        
        # Make gradlew executable (on Unix-like systems)
        gradlew_path = android_dir / "gradlew"
        if gradlew_path.exists():
            try:
                os.chmod(gradlew_path, 0o755)
                self.log("✅ Made gradlew executable")
            except Exception as e:
                self.log(f"⚠️ Could not make gradlew executable: {e}")
        
        # Determine the correct gradle command
        if os.name == 'nt':  # Windows
            gradle_cmd = "gradlew.bat"
            if not (android_dir / gradle_cmd).exists():
                gradle_cmd = "gradlew"
        else:
            gradle_cmd = "./gradlew"
            if not (android_dir / "gradlew").exists():
                gradle_cmd = "gradle"
        
        self.log(f"🔧 Using Gradle command: {gradle_cmd}")
        
        # Clean build (optional, but helps avoid issues)
        self.log("🧹 Cleaning previous build...")
        if not self.run_command_with_timeout(f"{gradle_cmd} clean", 
                                           timeout=180, 
                                           progress_message="Cleaning previous build"):
            self.log("⚠️ Gradle clean failed, but continuing with build...")
        
        # Build debug APK with extended timeout
        self.log("🗃️ Building APK (this may take several minutes)...")
        if not self.run_command_with_timeout(f"{gradle_cmd} assembleDebug", 
                                           timeout=600,  # 10 minutes timeout
                                           progress_message="Building APK"):
            self.log("❌ Gradle assembleDebug failed")
            
            # Try alternative build command
            self.log("🔄 Trying alternative build command...")
            if not self.run_command_with_timeout(f"{gradle_cmd} build", 
                                               timeout=600, 
                                               progress_message="Building with alternative command"):
                self.log("❌ All build attempts failed")
                return None
        
        # Find the generated APK
        self.log("🔍 Locating generated APK...")
        apk_search_paths = [
            android_dir / "app" / "build" / "outputs" / "apk" / "debug",
            android_dir / "app" / "build" / "outputs" / "apk",
            android_dir / "build" / "outputs" / "apk" / "debug",
            android_dir / "build" / "outputs" / "apk"
        ]
        
        apk_files = []
        for search_path in apk_search_paths:
            if search_path.exists():
                apk_files.extend(list(search_path.rglob("*.apk")))
                
        # Also search recursively in the entire android directory as fallback
        if not apk_files:
            self.log("🔍 Searching entire android directory for APK files...")
            apk_files = list(android_dir.rglob("*.apk"))
        
        if not apk_files:
            self.log("❌ No APK files found after build")
            self.log("📋 Searched in:")
            for path in apk_search_paths:
                self.log(f"  - {path}")
            return None
        
        # Filter for debug APKs first, then any APK
        debug_apks = [apk for apk in apk_files if "debug" in apk.name.lower()]
        if debug_apks:
            apk_path = debug_apks[0]
            self.log(f"✅ Found debug APK: {apk_path}")
        else:
            apk_path = apk_files[0]
            self.log(f"✅ Found APK: {apk_path}")
        
        # Log all found APKs for reference
        if len(apk_files) > 1:
            self.log("📋 All available APK files:")
            for apk in apk_files:
                self.log(f"  - {apk}")
        
        # Copy APK to project root with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        final_apk_name = f"{app_name}-{timestamp}.apk"
        final_apk_path = project_dir / final_apk_name
        
        try:
            self.log("📱 Copying APK to project directory...")
            shutil.copy2(apk_path, final_apk_path)
            
            # Get APK size
            apk_size = final_apk_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            self.log("✅ APK build completed successfully!")
            self.log(f"📱 APK location: {final_apk_path}")
            self.log(f"📏 APK size: {apk_size:.2f} MB")
            return final_apk_path
        except Exception as e:
            self.log(f"❌ Failed to copy APK: {e}")
            # Return the original path if copy failed
            self.log(f"📱 APK available at: {apk_path}")
            return apk_path
            
    def run(self):
        """Run the GUI application"""
        try:
            # Configure ttk styles
            style = ttk.Style()
            style.theme_use('clam')
            
            # Run the main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main function"""
    app = HTMLToAPKConverter()
    app.run()

if __name__ == "__main__":
    main()