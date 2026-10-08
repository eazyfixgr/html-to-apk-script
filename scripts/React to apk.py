#!/usr/bin/env python3
"""
React + Firebase to APK Converter with Capacitor 7
Automatic conversion of React+Vite+Firebase projects to Android APK
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
import re

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

class ReactToAPKConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("React + Firebase to APK Converter")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Configuration
        script_dir = Path(__file__).parent if __file__ else Path.cwd()
        self.config_file = script_dir / "react_to_apk_config.ini"
        
        # Queues for threading
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
        # Variables
        self.react_dir_var = tk.StringVar()
        self.app_name_var = tk.StringVar(value="MyReactApp")
        self.app_id_var = tk.StringVar(value="com.example.reactapp")
        self.output_dir_var = tk.StringVar()
        
        # Firebase config variables
        self.firebase_api_key_var = tk.StringVar()
        self.firebase_auth_domain_var = tk.StringVar()
        self.firebase_project_id_var = tk.StringVar()
        self.firebase_storage_bucket_var = tk.StringVar()
        self.firebase_messaging_sender_id_var = tk.StringVar()
        self.firebase_app_id_var = tk.StringVar()
        
        # Build options
        self.install_capacitor_plugins = tk.BooleanVar(value=True)
        self.use_firebase = tk.BooleanVar(value=True)
        self.debug_mode = tk.BooleanVar(value=False)
        
        # Build state
        self.is_building = False
        self.build_thread = None
        self.start_time = None
        self.current_step = 0
        self.total_steps = 15
        
        # Log window
        self.log_window = None
        
        # Essential Capacitor plugins for React apps
        self.essential_plugins = [
            "@capacitor/preferences",  # Για αντικατάσταση localStorage
            "@capacitor/network",      # Network detection
            "@capacitor/app",          # App lifecycle & deep linking
            "@capacitor/splash-screen", # Splash screen
            "@capacitor/status-bar"    # Status bar control
        ]
        
        self.load_configuration()
        self.setup_ui()
        self.setup_queue_monitoring()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_configuration(self):
        """Load saved configuration"""
        if not self.config_file.exists():
            return
            
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if 'Settings' in config:
                s = config['Settings']
                if 'react_directory' in s and Path(s['react_directory']).exists():
                    self.react_dir_var.set(s['react_directory'])
                if 'output_directory' in s:
                    self.output_dir_var.set(s['output_directory'])
                if 'app_name' in s:
                    self.app_name_var.set(s['app_name'])
                if 'app_id' in s:
                    self.app_id_var.set(s['app_id'])
                    
            if 'Firebase' in config:
                f = config['Firebase']
                if 'api_key' in f:
                    self.firebase_api_key_var.set(f['api_key'])
                if 'auth_domain' in f:
                    self.firebase_auth_domain_var.set(f['auth_domain'])
                if 'project_id' in f:
                    self.firebase_project_id_var.set(f['project_id'])
                if 'storage_bucket' in f:
                    self.firebase_storage_bucket_var.set(f['storage_bucket'])
                if 'messaging_sender_id' in f:
                    self.firebase_messaging_sender_id_var.set(f['messaging_sender_id'])
                if 'app_id' in f:
                    self.firebase_app_id_var.set(f['app_id'])
                    
            print(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            
    def save_configuration(self):
        """Save current configuration"""
        try:
            config = configparser.ConfigParser()
            config['Settings'] = {
                'react_directory': self.react_dir_var.get(),
                'output_directory': self.output_dir_var.get(),
                'app_name': self.app_name_var.get(),
                'app_id': self.app_id_var.get()
            }
            config['Firebase'] = {
                'api_key': self.firebase_api_key_var.get(),
                'auth_domain': self.firebase_auth_domain_var.get(),
                'project_id': self.firebase_project_id_var.get(),
                'storage_bucket': self.firebase_storage_bucket_var.get(),
                'messaging_sender_id': self.firebase_messaging_sender_id_var.get(),
                'app_id': self.firebase_app_id_var.get()
            }
            
            with open(self.config_file, 'w') as configfile:
                config.write(configfile)
                
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            
    def on_closing(self):
        """Handle window closing"""
        self.save_configuration()
        if self.is_building:
            self.is_building = False
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.destroy()
        self.root.destroy()
        
    def setup_ui(self):
        """Setup the main UI"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook, padding="10")
        notebook.add(main_frame, text="Project Settings")
        
        # Firebase tab
        firebase_frame = ttk.Frame(notebook, padding="10")
        notebook.add(firebase_frame, text="Firebase Configuration")
        
        # Build options tab
        options_frame = ttk.Frame(notebook, padding="10")
        notebook.add(options_frame, text="Build Options")
        
        self.setup_main_tab(main_frame)
        self.setup_firebase_tab(firebase_frame)
        self.setup_options_tab(options_frame)
        
    def setup_main_tab(self, parent):
        """Setup main project settings tab"""
        parent.columnconfigure(1, weight=1)
        
        # Title
        title_font = Font(size=16, weight="bold")
        title_label = ttk.Label(parent, text="React + Firebase → Android APK", font=title_font)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        desc_label = ttk.Label(parent, 
            text="Αυτόματη μετατροπή React+Vite+Firebase project σε Android APK με Capacitor 7",
            foreground="gray")
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # React Project Directory
        ttk.Label(parent, text="React Project Folder:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.react_dir_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_react_dir).grid(row=2, column=2, padx=(5, 0), pady=5)
        
        hint_label = ttk.Label(parent, text="Ο φάκελος με το React project (που έχει package.json, src/, public/)", 
                              foreground="gray", font=("TkDefaultFont", 9))
        hint_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # App Name
        ttk.Label(parent, text="App Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.app_name_var, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # App ID
        ttk.Label(parent, text="App ID (Package):").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.app_id_var, width=50).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        hint2_label = ttk.Label(parent, text="π.χ. com.yourcompany.appname (ΔΕΝ αλλάζει μετά!)", 
                               foreground="gray", font=("TkDefaultFont", 9))
        hint2_label.grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Output Directory
        ttk.Label(parent, text="Output Directory:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.output_dir_var, width=50).grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_output_dir).grid(row=7, column=2, padx=(5, 0), pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="Build Progress", padding="10")
        progress_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate', length=500)
        self.overall_progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.time_label = ttk.Label(progress_frame, text="", foreground="gray")
        self.time_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.step_progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=500)
        self.step_progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=9, column=0, columnspan=3, pady=(20, 0))
        
        self.convert_button = ttk.Button(button_frame, text="🚀 Convert to APK", 
                                        command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.logs_button = ttk.Button(button_frame, text="📋 Show Logs", 
                                     command=self.show_log_window)
        self.logs_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="💾 Save Settings", 
                                     command=self.save_configuration)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_form).pack(side=tk.LEFT)
        
        # Status bar
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="gray")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Auto-update output directory
        self.app_name_var.trace_add('write', self.update_output_dir)
        
    def setup_firebase_tab(self, parent):
        """Setup Firebase configuration tab"""
        parent.columnconfigure(1, weight=1)
        
        title_font = Font(size=14, weight="bold")
        title_label = ttk.Label(parent, text="Firebase Configuration", font=title_font)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        desc_label = ttk.Label(parent, 
            text="Πάρε τα στοιχεία από Firebase Console → Project Settings → Your App",
            foreground="gray")
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Enable Firebase checkbox
        ttk.Checkbutton(parent, text="Χρησιμοποίησε Firebase", 
                       variable=self.use_firebase).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        # Firebase fields
        fields = [
            ("API Key:", self.firebase_api_key_var, "AIzaSy..."),
            ("Auth Domain:", self.firebase_auth_domain_var, "yourapp.firebaseapp.com"),
            ("Project ID:", self.firebase_project_id_var, "yourapp-12345"),
            ("Storage Bucket:", self.firebase_storage_bucket_var, "yourapp.appspot.com"),
            ("Messaging Sender ID:", self.firebase_messaging_sender_id_var, "123456789"),
            ("App ID:", self.firebase_app_id_var, "1:123456789:android:abc123...")
        ]
        
        for i, (label_text, var, placeholder) in enumerate(fields, start=3):
            ttk.Label(parent, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(parent, textvariable=var, width=60)
            entry.grid(row=i, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            entry.insert(0, '')
            
            # Placeholder
            hint = ttk.Label(parent, text=placeholder, foreground="lightgray", font=("TkDefaultFont", 8))
            hint.grid(row=i+1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Load from .env button
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=20, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(button_frame, text="📂 Load from .env File", 
                  command=self.load_firebase_from_env).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔗 Open Firebase Console", 
                  command=self.open_firebase_console).pack(side=tk.LEFT)
        
    def setup_options_tab(self, parent):
        """Setup build options tab"""
        title_font = Font(size=14, weight="bold")
        title_label = ttk.Label(parent, text="Build Options", font=title_font)
        title_label.pack(pady=(0, 20))
        
        # Options
        options_frame = ttk.LabelFrame(parent, text="Επιλογές Build", padding="20")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Checkbutton(options_frame, 
                       text="Εγκατάσταση Essential Capacitor Plugins",
                       variable=self.install_capacitor_plugins).pack(anchor=tk.W, pady=5)
        
        plugins_info = ttk.Label(options_frame, 
            text="(Preferences, Network, App, Splash Screen, Status Bar)",
            foreground="gray", font=("TkDefaultFont", 9))
        plugins_info.pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Separator(options_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        ttk.Checkbutton(options_frame, 
                       text="Debug Mode (περισσότερα logs)",
                       variable=self.debug_mode).pack(anchor=tk.W, pady=5)
        
        # Info section
        info_frame = ttk.LabelFrame(parent, text="Τι θα κάνει το script", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        steps = [
            "✅ Έλεγχος Node.js, npm, Android SDK",
            "✅ Εγκατάσταση Capacitor 7",
            "✅ Εγκατάσταση Firebase dependencies",
            "✅ Setup Firebase configuration αυτόματα",
            "✅ Προσθήκη Android platform",
            "✅ Εγκατάσταση essential plugins",
            "✅ Build του React project",
            "✅ Sync σε Capacitor",
            "✅ Build APK με Gradle",
            "✅ Αντιγραφή APK στον output folder"
        ]
        
        for step in steps:
            ttk.Label(info_frame, text=step).pack(anchor=tk.W, pady=2)
            
    def browse_react_dir(self):
        """Browse for React project directory"""
        directory = filedialog.askdirectory(title="Διάλεξε React Project Folder")
        if directory:
            self.react_dir_var.set(directory)
            # Auto-detect package.json and set app name
            self.auto_detect_project_info(directory)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Διάλεξε Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def update_output_dir(self, *args):
        """Auto-update output directory"""
        if not self.output_dir_var.get():
            app_name = self.app_name_var.get().strip()
            if app_name:
                self.output_dir_var.set(f"{app_name}_android")
                
    def auto_detect_project_info(self, project_dir):
        """Auto-detect project information from package.json"""
        try:
            package_json = Path(project_dir) / "package.json"
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'name' in data:
                        name = data['name'].replace('-', ' ').replace('_', ' ').title()
                        self.app_name_var.set(name)
                        self.log(f"Auto-detected app name: {name}")
        except Exception as e:
            self.log(f"Could not auto-detect project info: {e}")
            
    def load_firebase_from_env(self):
        """Load Firebase config from .env file"""
        env_file = filedialog.askopenfilename(
            title="Select .env File",
            filetypes=[("Environment files", "*.env"), ("All files", "*.*")]
        )
        
        if not env_file:
            return
            
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
            # Parse .env file
            patterns = {
                'api_key': r'VITE_FIREBASE_API_KEY=(.+)',
                'auth_domain': r'VITE_FIREBASE_AUTH_DOMAIN=(.+)',
                'project_id': r'VITE_FIREBASE_PROJECT_ID=(.+)',
                'storage_bucket': r'VITE_FIREBASE_STORAGE_BUCKET=(.+)',
                'messaging_sender_id': r'VITE_FIREBASE_MESSAGING_SENDER_ID=(.+)',
                'app_id': r'VITE_FIREBASE_APP_ID=(.+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    value = match.group(1).strip().strip('"\'')
                    getattr(self, f'firebase_{key}_var').set(value)
                    
            messagebox.showinfo("Success", "Firebase configuration loaded from .env file!")
            self.log("Firebase config loaded from .env")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load .env file:\n{e}")
            
    def open_firebase_console(self):
        """Open Firebase Console in browser"""
        import webbrowser
        webbrowser.open("https://console.firebase.google.com/")
        
    def clear_form(self):
        """Clear all form fields"""
        if messagebox.askyesno("Clear", "Σίγουρα θέλεις να καθαρίσεις όλα τα πεδία;"):
            self.react_dir_var.set("")
            self.app_name_var.set("MyReactApp")
            self.app_id_var.set("com.example.reactapp")
            self.output_dir_var.set("")
            # Clear Firebase fields
            for var in [self.firebase_api_key_var, self.firebase_auth_domain_var,
                       self.firebase_project_id_var, self.firebase_storage_bucket_var,
                       self.firebase_messaging_sender_id_var, self.firebase_app_id_var]:
                var.set("")
                
    def setup_queue_monitoring(self):
        """Setup queue monitoring for thread communication"""
        self.root.after(100, self.check_queues)
        
    def check_queues(self):
        """Check queues for messages"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.append_to_log_window(message)
        except queue.Empty:
            pass
            
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                self.update_progress_ui(progress_data)
        except queue.Empty:
            pass
            
        self.root.after(100, self.check_queues)
        
    def show_log_window(self):
        """Show or create log window"""
        if self.log_window is None or not self.log_window.winfo_exists():
            self.create_log_window()
        else:
            self.log_window.lift()
            
    def create_log_window(self):
        """Create log window"""
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Build Logs")
        self.log_window.geometry("900x700")
        
        text_frame = ttk.Frame(self.log_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=40)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        
        button_frame = ttk.Frame(self.log_window, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
    def append_to_log_window(self, message):
        """Append message to log window"""
        if self.log_window and self.log_window.winfo_exists():
            self.log_text.insert(tk.END, message + '\n')
            
            if "✅" in message or "Success" in message:
                line_start = f"{float(self.log_text.index(tk.END)) - 1.0:.1f}"
                self.log_text.tag_add("success", line_start, tk.END)
            elif "❌" in message or "ERROR" in message or "Failed" in message:
                line_start = f"{float(self.log_text.index(tk.END)) - 1.0:.1f}"
                self.log_text.tag_add("error", line_start, tk.END)
            elif "⚠️" in message or "Warning" in message:
                line_start = f"{float(self.log_text.index(tk.END)) - 1.0:.1f}"
                self.log_text.tag_add("warning", line_start, tk.END)
                
            self.log_text.see(tk.END)
            
    def clear_logs(self):
        """Clear log window"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            
    def save_logs(self):
        """Save logs to file"""
        if hasattr(self, 'log_text'):
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                title="Save Build Logs"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {filename}")
                
    def log(self, message):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
        
    def update_step(self, step, message):
        """Update current step"""
        if not self.is_building:
            return
            
        self.current_step = step
        progress_data = {
            'step': step,
            'total_steps': self.total_steps,
            'message': message,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }
        self.progress_queue.put(progress_data)
        self.log(f"📍 Step {step}/{self.total_steps}: {message}")
        
    def update_progress_ui(self, data):
        """Update progress UI"""
        step = data['step']
        total = data['total_steps']
        message = data['message']
        elapsed = data['elapsed_time']
        
        progress_percent = (step / total) * 100
        self.overall_progress['value'] = progress_percent
        self.progress_label.config(text=f"Step {step}/{total}: {message}")
        
        if elapsed > 0:
            elapsed_str = self.format_time(elapsed)
            estimated_total = elapsed * (total / step) if step > 0 else 0
            remaining = estimated_total - elapsed
            remaining_str = self.format_time(remaining) if remaining > 0 else "Σχεδόν έτοιμο"
            self.time_label.config(text=f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
            
    def format_time(self, seconds):
        """Format seconds to readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
            
    def validate_input(self):
        """Validate user input"""
        if not self.react_dir_var.get():
            messagebox.showerror("Error", "Παρακαλώ διάλεξε React project folder")
            return False
            
        react_dir = Path(self.react_dir_var.get())
        if not react_dir.exists():
            messagebox.showerror("Error", "Το React project folder δεν υπάρχει")
            return False
            
        # Check for package.json
        if not (react_dir / "package.json").exists():
            messagebox.showerror("Error", "Δεν βρέθηκε package.json στον φάκελο.\nΣίγουρα είναι React project;")
            return False
            
        if not self.app_name_var.get():
            messagebox.showerror("Error", "Παρακαλώ γράψε App Name")
            return False
            
        if not self.app_id_var.get():
            messagebox.showerror("Error", "Παρακαλώ γράψε App ID")
            return False
            
        if not self.output_dir_var.get():
            messagebox.showerror("Error", "Παρακαλώ γράψε Output Directory")
            return False
            
        # Validate Firebase config if enabled
        if self.use_firebase.get():
            if not all([
                self.firebase_api_key_var.get(),
                self.firebase_auth_domain_var.get(),
                self.firebase_project_id_var.get()
            ]):
                result = messagebox.askyesno("Incomplete Firebase Config",
                    "Τα Firebase στοιχεία είναι incomplete.\n\n"
                    "Θέλεις να συνεχίσεις χωρίς Firebase;")
                if result:
                    self.use_firebase.set(False)
                else:
                    return False
                    
        return True
        
    def start_conversion(self):
        """Start the conversion process"""
        if not self.validate_input():
            return
            
        if self.is_building:
            self.stop_operation()
            return
            
        self.save_configuration()
        self.is_building = True
        self.start_time = time.time()
        self.current_step = 0
        
        self.convert_button.config(text="⛔ Cancel")
        self.overall_progress['value'] = 0
        self.step_progress.start(10)
        
        self.build_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.build_thread.start()
        
    def stop_operation(self):
        """Stop the operation"""
        self.is_building = False
        self.reset_ui()
        self.log("❌ Operation cancelled by user")
        
    def reset_ui(self):
        """Reset UI after operation"""
        self.convert_button.config(text="🚀 Convert to APK")
        self.step_progress.stop()
        
    def conversion_worker(self):
        """Main conversion worker thread"""
        try:
            self.log("="*60)
            self.log("🚀 STARTING REACT → ANDROID APK CONVERSION")
            self.log("="*60)
            
            react_dir = Path(self.react_dir_var.get())
            output_dir = Path(self.output_dir_var.get())
            app_name = self.app_name_var.get()
            app_id = self.app_id_var.get()
            
            # Step 1: Check prerequisites
            self.update_step(1, "Checking prerequisites...")
            if not self.check_prerequisites():
                return
                
            # Step 2: Copy React project
            self.update_step(2, "Copying React project...")
            if not self.copy_react_project(react_dir, output_dir):
                return
                
            # Step 3: Install dependencies
            self.update_step(3, "Installing npm dependencies...")
            if not self.install_dependencies(output_dir):
                return
                
            # Step 4: Install Capacitor
            self.update_step(4, "Installing Capacitor 7...")
            if not self.install_capacitor(output_dir, app_name, app_id):
                return
                
            # Step 5: Setup Firebase
            if self.use_firebase.get():
                self.update_step(5, "Setting up Firebase...")
                if not self.setup_firebase(output_dir):
                    return
            else:
                self.update_step(5, "Skipping Firebase setup...")
                
            # Step 6: Install Tailwind (if needed)
            self.update_step(6, "Checking for Tailwind CSS...")
            self.check_and_fix_tailwind(output_dir)
            
            # Step 7: Install essential plugins
            if self.install_capacitor_plugins.get():
                self.update_step(7, "Installing Capacitor plugins...")
                if not self.install_plugins(output_dir):
                    return
            else:
                self.update_step(7, "Skipping plugins...")
                
            # Step 8: Add Android platform
            self.update_step(8, "Adding Android platform...")
            if not self.add_android_platform(output_dir):
                return
                
            # Step 9: Configure Capacitor
            self.update_step(9, "Configuring Capacitor...")
            if not self.configure_capacitor(output_dir, app_name, app_id):
                return
                
            # Step 10: Update AndroidManifest
            self.update_step(10, "Updating AndroidManifest.xml...")
            self.update_android_manifest(output_dir)
            
            # Step 11: Build React app
            self.update_step(11, "Building React app (npm run build)...")
            if not self.build_react_app(output_dir):
                return
                
            # Step 12: Sync Capacitor
            self.update_step(12, "Syncing to Android...")
            if not self.sync_capacitor(output_dir):
                return
                
            # Step 13: Build APK
            self.update_step(13, "Building APK (this takes time)...")
            apk_path = self.build_apk(output_dir, app_name)
            
            if not apk_path:
                return
                
            # Step 14: Complete
            self.update_step(14, "✅ Conversion complete!")
            
            self.log("="*60)
            self.log("🎉 SUCCESS! APK CREATED")
            self.log(f"📱 APK: {apk_path.name}")
            self.log(f"📂 Location: {apk_path.parent}")
            self.log("="*60)
            
            if self.is_building:
                self.show_success(apk_path)
                
        except Exception as e:
            self.log(f"❌ UNEXPECTED ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())
            
            if self.is_building:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Unexpected error:\n{e}\n\nCheck logs for details."))
        finally:
            self.is_building = False
            self.root.after(0, self.reset_ui)
            
    def run_command(self, cmd, cwd=None, timeout=300):
        """Run command and return success"""
        if not self.is_building:
            return False
            
        try:
            self.log(f"💻 Running: {cmd}")
            
            process = subprocess.Popen(
                cmd, cwd=cwd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True
            )
            
            start_time = time.time()
            output_lines = []
            
            while True:
                if not self.is_building:
                    process.terminate()
                    return False
                    
                if time.time() - start_time > timeout:
                    self.log(f"⏱️ Command timed out after {timeout}s")
                    process.terminate()
                    return False
                    
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                    
                if output and output.strip():
                    line = output.strip()
                    if self.debug_mode.get() or "error" in line.lower() or "warn" in line.lower():
                        self.log(f"  {line}")
                    output_lines.append(line)
                    
                time.sleep(0.05)
                
            returncode = process.poll()
            
            if returncode == 0:
                self.log(f"✅ Command completed successfully")
                return True
            else:
                self.log(f"❌ Command failed with code: {returncode}")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            return False
            
    def check_prerequisites(self):
        """Check required tools"""
        self.log("Checking Node.js...")
        if not self.run_command("node --version", timeout=30):
            messagebox.showerror("Error", "Node.js is required!\nInstall from https://nodejs.org")
            return False
            
        self.log("Checking npm...")
        if not self.run_command("npm --version", timeout=30):
            messagebox.showerror("Error", "npm is required!")
            return False
            
        self.log("✅ Prerequisites OK")
        return True
        
    def copy_react_project(self, src, dst):
        """Copy React project to output directory"""
        try:
            if dst.exists():
                if not messagebox.askyesno("Warning", 
                    f"Directory {dst} exists. Delete it?"):
                    return False
                shutil.rmtree(dst)
                
            self.log(f"Copying project from {src} to {dst}...")
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                'node_modules', '.git', 'dist', 'build', 'android', 'ios'
            ))
            self.log("✅ Project copied")
            return True
        except Exception as e:
            self.log(f"❌ Copy failed: {e}")
            return False
            
    def install_dependencies(self, project_dir):
        """Install npm dependencies"""
        return self.run_command("npm install", cwd=project_dir, timeout=600)
        
    def install_capacitor(self, project_dir, app_name, app_id):
        """Install Capacitor"""
        os.chdir(project_dir)
        
        if not self.run_command("npm install @capacitor/core@^7.0.0", timeout=180):
            return False
        if not self.run_command("npm install -D @capacitor/cli@^7.0.0", timeout=180):
            return False
            
        # Initialize Capacitor
        self.log("Initializing Capacitor...")
        config_content = f'''import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: '{app_id}',
  appName: '{app_name}',
  webDir: 'dist',
  server: {{
    androidScheme: 'https'
  }}
}};

export default config;
'''
        
        with open(project_dir / "capacitor.config.ts", "w") as f:
            f.write(config_content)
            
        self.log("✅ Capacitor initialized")
        return True
        
    def setup_firebase(self, project_dir):
        """Setup Firebase configuration"""
        os.chdir(project_dir)
        
        # Install Firebase
        if not self.run_command("npm install firebase", timeout=180):
            return False
            
        # Create firebase.js
        firebase_js = f'''import {{ initializeApp }} from 'firebase/app';
import {{ getAuth }} from 'firebase/auth';
import {{ getFirestore }} from 'firebase/firestore';
import {{ getStorage }} from 'firebase/storage';

const firebaseConfig = {{
  apiKey: "{self.firebase_api_key_var.get()}",
  authDomain: "{self.firebase_auth_domain_var.get()}",
  projectId: "{self.firebase_project_id_var.get()}",
  storageBucket: "{self.firebase_storage_bucket_var.get()}",
  messagingSenderId: "{self.firebase_messaging_sender_id_var.get()}",
  appId: "{self.firebase_app_id_var.get()}"
}};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
'''
        
        src_dir = project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        with open(src_dir / "firebase.js", "w") as f:
            f.write(firebase_js)
            
        self.log("✅ Firebase configured")
        return True
        
    def check_and_fix_tailwind(self, project_dir):
        """Check and fix Tailwind CSS setup"""
        try:
            package_json = project_dir / "package.json"
            with open(package_json, 'r') as f:
                data = json.load(f)
                
            if 'tailwindcss' in str(data.get('dependencies', {})) or \
               'tailwindcss' in str(data.get('devDependencies', {})):
                self.log("Tailwind CSS detected, ensuring proper setup...")
                
                # Install if missing
                self.run_command("npm install -D tailwindcss postcss autoprefixer", 
                               cwd=project_dir, timeout=120)
                
                # Check for config
                if not (project_dir / "tailwind.config.js").exists():
                    self.log("Creating tailwind.config.js...")
                    config = '''export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}'''
                    with open(project_dir / "tailwind.config.js", "w") as f:
                        f.write(config)
                        
                self.log("✅ Tailwind CSS configured")
        except Exception as e:
            self.log(f"⚠️ Tailwind check: {e}")
            
    def install_plugins(self, project_dir):
        """Install essential Capacitor plugins"""
        os.chdir(project_dir)
        
        for plugin in self.essential_plugins:
            if not self.is_building:
                return False
            self.log(f"Installing {plugin}...")
            if not self.run_command(f"npm install {plugin}@^7.0.0", timeout=120):
                self.log(f"⚠️ Failed to install {plugin}, continuing...")
                
        self.log("✅ Plugins installed")
        return True
        
    def add_android_platform(self, project_dir):
        """Add Android platform"""
        os.chdir(project_dir)
        
        if not self.run_command("npm install @capacitor/android@^7.0.0", timeout=180):
            return False
        if not self.run_command("npx cap add android", timeout=180):
            return False
            
        self.log("✅ Android platform added")
        return True
        
    def configure_capacitor(self, project_dir, app_name, app_id):
        """Update Capacitor configuration"""
        try:
            config_file = project_dir / "capacitor.config.ts"
            
            config = f'''import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: '{app_id}',
  appName: '{app_name}',
  webDir: 'dist',
  server: {{
    androidScheme: 'https',
    cleartext: true
  }},
  android: {{
    buildOptions: {{
      releaseType: 'APK'
    }}
  }}
}};

export default config;
'''
            
            with open(config_file, 'w') as f:
                f.write(config)
                
            self.log("✅ Capacitor configured")
            return True
        except Exception as e:
            self.log(f"❌ Config failed: {e}")
            return False
            
    def update_android_manifest(self, project_dir):
        """Update AndroidManifest.xml with permissions"""
        try:
            manifest_path = project_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
            
            if not manifest_path.exists():
                self.log("⚠️ AndroidManifest.xml not found yet")
                return
                
            with open(manifest_path, 'r') as f:
                content = f.read()
                
            # Add internet permission if not present
            if 'android.permission.INTERNET' not in content:
                content = content.replace('</manifest>', 
                    '    <uses-permission android:name="android.permission.INTERNET" />\n</manifest>')
                
            with open(manifest_path, 'w') as f:
                f.write(content)
                
            self.log("✅ AndroidManifest updated")
        except Exception as e:
            self.log(f"⚠️ Manifest update: {e}")
            
    def build_react_app(self, project_dir):
        """Build React app"""
        return self.run_command("npm run build", cwd=project_dir, timeout=600)
        
    def sync_capacitor(self, project_dir):
        """Sync Capacitor to Android"""
        return self.run_command("npx cap sync android", cwd=project_dir, timeout=300)
        
    def build_apk(self, project_dir, app_name):
        """Build APK"""
        android_dir = project_dir / "android"
        if not android_dir.exists():
            self.log("❌ Android directory not found")
            return None
            
        os.chdir(android_dir)
        
        gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
        
        # Make gradlew executable on Unix
        if os.name != 'nt':
            try:
                os.chmod(android_dir / "gradlew", 0o755)
            except:
                pass
                
        self.log("Cleaning previous build...")
        self.run_command(f"{gradle_cmd} clean", timeout=180)
        
        self.log("Building APK (this takes several minutes)...")
        if not self.run_command(f"{gradle_cmd} assembleDebug", timeout=900):
            return None
            
        # Find APK
        apk_paths = list((android_dir / "app" / "build" / "outputs" / "apk" / "debug").rglob("*.apk"))
        
        if not apk_paths:
            self.log("❌ APK not found")
            return None
            
        apk_path = apk_paths[0]
        
        # Copy to project root
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_name = f"{app_name}_{timestamp}.apk"
        final_path = project_dir / final_name
        
        shutil.copy2(apk_path, final_path)
        
        size_mb = final_path.stat().st_size / (1024 * 1024)
        self.log(f"✅ APK: {final_name} ({size_mb:.1f} MB)")
        
        return final_path
        
    def show_success(self, apk_path):
        """Show success dialog"""
        self.root.after(0, lambda: self._show_success_dialog(apk_path))
        
    def _show_success_dialog(self, apk_path):
        """Show success dialog in main thread"""
        messagebox.showinfo(
            "🎉 Success!",
            f"APK δημιουργήθηκε επιτυχώς!\n\n"
            f"📱 File: {apk_path.name}\n"
            f"📂 Location: {apk_path.parent}\n\n"
            f"Μπορείς να το εγκαταστήσεις σε Android συσκευή!"
        )
        
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main entry point"""
    app = ReactToAPKConverter()
    app.run()

if __name__ == "__main__":
    main()