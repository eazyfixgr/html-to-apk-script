#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android Splash Screen Tool - Smart Edition
Αυτόματη προσθήκη splash screen σε Android project με έξυπνες ρυθμίσεις
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import json
from pathlib import Path

class AndroidSplashTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Splash Screen Tool - Smart Edition")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Config file path
        self.config_file = os.path.join(os.path.expanduser("~"), ".android_splash_tool_config.json")
        
        # Μεταβλητές
        self.portrait_image_path = tk.StringVar()
        self.landscape_image_path = tk.StringVar()
        self.project_path = tk.StringVar()
        
        # Splash screen αναλύσεις για Android
        # Βασικές αναλύσεις (portrait)
        self.resolutions_portrait = {
            'drawable': (480, 800),           # Generic fallback
            'drawable-mdpi': (320, 480),      # ~160dpi
            'drawable-hdpi': (480, 800),      # ~240dpi
            'drawable-xhdpi': (720, 1280),    # ~320dpi
            'drawable-xxhdpi': (1080, 1920),  # ~480dpi
            'drawable-xxxhdpi': (1440, 2560), # ~640dpi
            'drawable-v24': (1080, 1920),     # Android 7.0+
        }
        
        # Landscape orientations
        self.resolutions_landscape = {
            'drawable-land-mdpi': (480, 320),
            'drawable-land-hdpi': (800, 480),
            'drawable-land-xhdpi': (1280, 720),
            'drawable-land-xxhdpi': (1920, 1080),
            'drawable-land-xxxhdpi': (2560, 1440),
        }
        
        # Portrait orientations (explicit)
        self.resolutions_port = {
            'drawable-port-mdpi': (320, 480),
            'drawable-port-hdpi': (480, 800),
            'drawable-port-xhdpi': (720, 1280),
            'drawable-port-xxhdpi': (1080, 1920),
            'drawable-port-xxxhdpi': (1440, 2560),
        }
        
        # Load saved settings
        self.load_settings()
        
        self.create_widgets()
        
        # Bind close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Κεντρικό frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Τίτλος
        title_label = ttk.Label(main_frame, text="Android Splash Screen Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Portrait Image Section
        portrait_frame = ttk.LabelFrame(main_frame, text="📱 Portrait Εικόνα", padding="10")
        portrait_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(portrait_frame, text="Εικόνα:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(portrait_frame, textvariable=self.portrait_image_path, width=45).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(portrait_frame, text="Επιλογή", command=self.select_portrait_image).grid(row=0, column=2, pady=5)
        
        self.portrait_preview_label = ttk.Label(portrait_frame, text="Δεν έχει επιλεγεί εικόνα", 
                                                foreground="gray")
        self.portrait_preview_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Landscape Image Section
        landscape_frame = ttk.LabelFrame(main_frame, text="🔄 Landscape Εικόνα (προαιρετικό)", padding="10")
        landscape_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(landscape_frame, text="Εικόνα:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(landscape_frame, textvariable=self.landscape_image_path, width=45).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(landscape_frame, text="Επιλογή", command=self.select_landscape_image).grid(row=0, column=2, pady=5)
        
        self.landscape_preview_label = ttk.Label(landscape_frame, text="Δεν έχει επιλεγεί εικόνα", 
                                                  foreground="gray")
        self.landscape_preview_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        ttk.Label(landscape_frame, text="💡 Αν δεν επιλέξετε landscape εικόνα, θα χρησιμοποιηθεί η portrait", 
                 foreground="blue", font=('Arial', 8)).grid(row=2, column=0, columnspan=3, pady=2)
        
        # Android project
        ttk.Label(main_frame, text="Android Project:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.project_path, width=45).grid(row=3, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Επιλογή", command=self.select_project).grid(row=3, column=2, pady=5)
        
        # Όνομα αρχείου splash
        ttk.Label(main_frame, text="Όνομα αρχείου:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.filename_var = tk.StringVar(value=self.settings.get('filename', 'splash_screen'))
        ttk.Entry(main_frame, textvariable=self.filename_var, width=45).grid(row=4, column=1, pady=5, padx=5)
        ttk.Label(main_frame, text=".png").grid(row=4, column=2, sticky=tk.W, pady=5)
        
        # Επιλογές orientation
        options_frame = ttk.LabelFrame(main_frame, text="Επιλογές Δημιουργίας", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.include_explicit_portrait = tk.BooleanVar(value=self.settings.get('explicit_portrait', True))
        self.use_padding = tk.BooleanVar(value=self.settings.get('use_padding', True))
        
        ttk.Checkbutton(options_frame, text="Δημιουργία explicit portrait variants (drawable-port-*)", 
                       variable=self.include_explicit_portrait).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Χρήση padding για διατήρηση aspect ratio", 
                       variable=self.use_padding).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Κουμπί δημιουργίας
        self.generate_btn = ttk.Button(main_frame, text="🚀 Δημιουργία Splash Screens", 
                                       command=self.generate_splash)
        self.generate_btn.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Έτοιμο", foreground="blue")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Πληροφορίες
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Πληροφορίες", padding="10")
        info_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        info_text = """✨ Έξυπνη δημιουργία splash screens:
• Portrait εικόνα → drawable, drawable-v24, drawable-mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi
• Landscape εικόνα → drawable-land-* (όλες οι αναλύσεις)
• Explicit portrait → drawable-port-* (προαιρετικό)
• Αυτόματη αποθήκευση ρυθμίσεων"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=('Arial', 9)).pack()
    
    def load_settings(self):
        """Φόρτωση αποθηκευμένων ρυθμίσεων"""
        self.settings = {
            'last_project_path': '',
            'last_portrait_image': '',
            'last_landscape_image': '',
            'filename': 'splash_screen',
            'explicit_portrait': True,
            'use_padding': True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
            except Exception as e:
                print(f"Σφάλμα φόρτωσης ρυθμίσεων: {e}")
    
    def save_settings(self):
        """Αποθήκευση τρεχουσών ρυθμίσεων"""
        self.settings['last_project_path'] = self.project_path.get()
        self.settings['last_portrait_image'] = self.portrait_image_path.get()
        self.settings['last_landscape_image'] = self.landscape_image_path.get()
        self.settings['filename'] = self.filename_var.get()
        self.settings['explicit_portrait'] = self.include_explicit_portrait.get()
        self.settings['use_padding'] = self.use_padding.get()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Σφάλμα αποθήκευσης ρυθμίσεων: {e}")
    
    def on_closing(self):
        """Κλείσιμο εφαρμογής με αποθήκευση ρυθμίσεων"""
        self.save_settings()
        self.root.destroy()
    
    def select_portrait_image(self):
        initial_dir = os.path.dirname(self.settings.get('last_portrait_image', '')) or None
        filename = filedialog.askopenfilename(
            title="Επιλογή Portrait Εικόνας",
            initialdir=initial_dir,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.portrait_image_path.set(filename)
            # Preview info
            try:
                img = Image.open(filename)
                self.portrait_preview_label.config(
                    text=f"✓ {os.path.basename(filename)} ({img.width}x{img.height}px)",
                    foreground="green"
                )
            except:
                self.portrait_preview_label.config(
                    text=f"✓ {os.path.basename(filename)}",
                    foreground="green"
                )
    
    def select_landscape_image(self):
        initial_dir = os.path.dirname(self.settings.get('last_landscape_image', '')) or None
        filename = filedialog.askopenfilename(
            title="Επιλογή Landscape Εικόνας",
            initialdir=initial_dir,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.landscape_image_path.set(filename)
            # Preview info
            try:
                img = Image.open(filename)
                self.landscape_preview_label.config(
                    text=f"✓ {os.path.basename(filename)} ({img.width}x{img.height}px)",
                    foreground="green"
                )
            except:
                self.landscape_preview_label.config(
                    text=f"✓ {os.path.basename(filename)}",
                    foreground="green"
                )
    
    def select_project(self):
        initial_dir = self.settings.get('last_project_path', '') or None
        dirname = filedialog.askdirectory(
            title="Επιλογή Android Project Folder",
            initialdir=initial_dir
        )
        if dirname:
            self.project_path.set(dirname)
            self.status_label.config(text=f"✓ Project: {os.path.basename(dirname)}", foreground="green")
    
    def generate_splash(self):
        # Έλεγχος εισόδων
        if not self.portrait_image_path.get():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε τουλάχιστον μια portrait εικόνα!")
            return
        
        if not self.project_path.get():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε Android project folder!")
            return
        
        if not os.path.exists(self.portrait_image_path.get()):
            messagebox.showerror("Σφάλμα", "Η portrait εικόνα δεν βρέθηκε!")
            return
        
        if not os.path.exists(self.project_path.get()):
            messagebox.showerror("Σφάλμα", "Το Android project δεν βρέθηκε!")
            return
        
        # Έλεγχος landscape εικόνας (προαιρετικό)
        has_landscape = bool(self.landscape_image_path.get() and 
                           os.path.exists(self.landscape_image_path.get()))
        
        try:
            # Disable button κατά τη διάρκεια της επεξεργασίας
            self.generate_btn.config(state='disabled')
            self.progress['value'] = 0
            self.root.update()
            
            # Άνοιγμα portrait εικόνας
            self.status_label.config(text="Φόρτωση portrait εικόνας...", foreground="blue")
            self.root.update()
            portrait_image = Image.open(self.portrait_image_path.get())
            
            # Μετατροπή σε RGB αν χρειάζεται
            if portrait_image.mode != 'RGB' and portrait_image.mode != 'RGBA':
                portrait_image = portrait_image.convert('RGB')
            
            # Άνοιγμα landscape εικόνας αν υπάρχει
            landscape_image = None
            if has_landscape:
                self.status_label.config(text="Φόρτωση landscape εικόνας...", foreground="blue")
                self.root.update()
                landscape_image = Image.open(self.landscape_image_path.get())
                if landscape_image.mode != 'RGB' and landscape_image.mode != 'RGBA':
                    landscape_image = landscape_image.convert('RGB')
            
            filename = self.filename_var.get() + ".png"
            
            # Υπολογισμός συνόλου βημάτων
            total_steps = len(self.resolutions_portrait)
            total_steps += len(self.resolutions_landscape)
            if self.include_explicit_portrait.get():
                total_steps += len(self.resolutions_port)
            
            current_step = 0
            created_files = 0
            
            # 1. Δημιουργία βασικών portrait drawables
            self.status_label.config(text="Δημιουργία portrait drawables...", foreground="blue")
            self.root.update()
            
            for drawable_folder, (width, height) in self.resolutions_portrait.items():
                self.status_label.config(text=f"Δημιουργία {drawable_folder}...", foreground="blue")
                self.root.update()
                
                # Δημιουργία φακέλου αν δεν υπάρχει
                res_path = os.path.join(self.project_path.get(), 'app', 'src', 'main', 'res', drawable_folder)
                os.makedirs(res_path, exist_ok=True)
                
                # Resize εικόνας
                if self.use_padding.get():
                    resized_image = self.resize_with_padding(portrait_image, (width, height))
                else:
                    resized_image = portrait_image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Αποθήκευση
                output_path = os.path.join(res_path, filename)
                resized_image.save(output_path, 'PNG', quality=95, optimize=True)
                created_files += 1
                
                # Update progress
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.root.update()
            
            # 2. Δημιουργία landscape drawables
            self.status_label.config(text="Δημιουργία landscape drawables...", foreground="blue")
            self.root.update()
            
            # Χρήση landscape εικόνας αν υπάρχει, αλλιώς portrait
            source_image = landscape_image if has_landscape else portrait_image
            
            for drawable_folder, (width, height) in self.resolutions_landscape.items():
                self.status_label.config(text=f"Δημιουργία {drawable_folder}...", foreground="blue")
                self.root.update()
                
                # Δημιουργία φακέλου αν δεν υπάρχει
                res_path = os.path.join(self.project_path.get(), 'app', 'src', 'main', 'res', drawable_folder)
                os.makedirs(res_path, exist_ok=True)
                
                # Resize εικόνας
                if self.use_padding.get():
                    resized_image = self.resize_with_padding(source_image, (width, height))
                else:
                    resized_image = source_image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Αποθήκευση
                output_path = os.path.join(res_path, filename)
                resized_image.save(output_path, 'PNG', quality=95, optimize=True)
                created_files += 1
                
                # Update progress
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.root.update()
            
            # 3. Δημιουργία explicit portrait drawables (αν επιλέχθηκε)
            if self.include_explicit_portrait.get():
                self.status_label.config(text="Δημιουργία explicit portrait drawables...", foreground="blue")
                self.root.update()
                
                for drawable_folder, (width, height) in self.resolutions_port.items():
                    self.status_label.config(text=f"Δημιουργία {drawable_folder}...", foreground="blue")
                    self.root.update()
                    
                    # Δημιουργία φακέλου αν δεν υπάρχει
                    res_path = os.path.join(self.project_path.get(), 'app', 'src', 'main', 'res', drawable_folder)
                    os.makedirs(res_path, exist_ok=True)
                    
                    # Resize εικόνας
                    if self.use_padding.get():
                        resized_image = self.resize_with_padding(portrait_image, (width, height))
                    else:
                        resized_image = portrait_image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # Αποθήκευση
                    output_path = os.path.join(res_path, filename)
                    resized_image.save(output_path, 'PNG', quality=95, optimize=True)
                    created_files += 1
                    
                    # Update progress
                    current_step += 1
                    self.progress['value'] = (current_step / total_steps) * 100
                    self.root.update()
            
            # Αποθήκευση ρυθμίσεων
            self.save_settings()
            
            self.progress['value'] = 100
            self.status_label.config(text="✓ Ολοκληρώθηκε επιτυχώς!", foreground="green")
            
            # Δημιουργία λεπτομερούς μηνύματος
            message = f"Το splash screen δημιουργήθηκε επιτυχώς!\n\n"
            message += f"📊 Στατιστικά:\n"
            message += f"• Δημιουργήθηκαν {created_files} εικόνες\n"
            message += f"• Portrait drawables: {len(self.resolutions_portrait)}\n"
            message += f"• Landscape drawables: {len(self.resolutions_landscape)}"
            if has_landscape:
                message += " (από ξεχωριστή εικόνα)"
            else:
                message += " (από portrait εικόνα)"
            if self.include_explicit_portrait.get():
                message += f"\n• Explicit portrait: {len(self.resolutions_port)}"
            
            messagebox.showinfo("Επιτυχία", message)
            
        except Exception as e:
            self.status_label.config(text="✗ Σφάλμα!", foreground="red")
            messagebox.showerror("Σφάλμα", f"Προέκυψε σφάλμα:\n{str(e)}")
        
        finally:
            self.generate_btn.config(state='normal')
    
    def resize_with_padding(self, image, target_size):
        """Resize εικόνας με padding για να διατηρηθεί το aspect ratio"""
        target_width, target_height = target_size
        img_width, img_height = image.size
        
        # Υπολογισμός aspect ratios
        img_ratio = img_width / img_height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Η εικόνα είναι πιο wide
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Η εικόνα είναι πιο tall
            new_height = target_height
            new_width = int(target_height * img_ratio)
        
        # Resize
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Δημιουργία νέας εικόνας με padding
        # Υποστήριξη RGBA για διαφάνεια
        if image.mode == 'RGBA':
            new_image = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 255))
        else:
            new_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Κέντρο της εικόνας
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        new_image.paste(resized, (paste_x, paste_y))
        
        return new_image


def main():
    root = tk.Tk()
    app = AndroidSplashTool(root)
    
    # Φόρτωση προηγούμενων επιλογών αν υπάρχουν
    if app.settings.get('last_project_path'):
        app.project_path.set(app.settings['last_project_path'])
    if app.settings.get('last_portrait_image') and os.path.exists(app.settings['last_portrait_image']):
        app.portrait_image_path.set(app.settings['last_portrait_image'])
        try:
            img = Image.open(app.settings['last_portrait_image'])
            app.portrait_preview_label.config(
                text=f"✓ {os.path.basename(app.settings['last_portrait_image'])} ({img.width}x{img.height}px)",
                foreground="green"
            )
        except:
            pass
    if app.settings.get('last_landscape_image') and os.path.exists(app.settings['last_landscape_image']):
        app.landscape_image_path.set(app.settings['last_landscape_image'])
        try:
            img = Image.open(app.settings['last_landscape_image'])
            app.landscape_preview_label.config(
                text=f"✓ {os.path.basename(app.settings['last_landscape_image'])} ({img.width}x{img.height}px)",
                foreground="green"
            )
        except:
            pass
    
    root.mainloop()


if __name__ == "__main__":
    main()
