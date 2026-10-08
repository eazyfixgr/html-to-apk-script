#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android Splash Screen Tool
Αυτόματη προσθήκη splash screen σε Android project
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import shutil

class AndroidSplashTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Splash Screen Tool")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Μεταβλητές
        self.image_path = tk.StringVar()
        self.project_path = tk.StringVar()
        
        # Splash screen αναλύσεις για Android
        # Βασικές αναλύσεις (portrait)
        self.resolutions = {
            'drawable': (480, 800),           # Generic fallback
            'drawable-mdpi': (320, 480),      # ~160dpi
            'drawable-hdpi': (480, 800),      # ~240dpi
            'drawable-xhdpi': (720, 1280),    # ~320dpi
            'drawable-xxhdpi': (1080, 1920),  # ~480dpi
            'drawable-xxxhdpi': (1440, 2560), # ~640dpi
            'drawable-v24': (1080, 1920),     # Android 7.0+
        }
        
        # Landscape orientations
        self.resolutions_land = {
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
        
        self.create_widgets()
    
    def create_widgets(self):
        # Κεντρικό frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Τίτλος
        title_label = ttk.Label(main_frame, text="Android Splash Screen Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Επιλογή εικόνας
        ttk.Label(main_frame, text="Εικόνα:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.image_path, width=40).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Επιλογή", command=self.select_image).grid(row=1, column=2, pady=5)
        
        # Επιλογή Android project
        ttk.Label(main_frame, text="Android Project:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.project_path, width=40).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Επιλογή", command=self.select_project).grid(row=2, column=2, pady=5)
        
        # Όνομα αρχείου splash
        ttk.Label(main_frame, text="Όνομα αρχείου:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.filename_var = tk.StringVar(value="splash_screen")
        ttk.Entry(main_frame, textvariable=self.filename_var, width=40).grid(row=3, column=1, pady=5, padx=5)
        ttk.Label(main_frame, text=".png").grid(row=3, column=2, sticky=tk.W, pady=5)
        
        # Επιλογές orientation
        options_frame = ttk.LabelFrame(main_frame, text="Επιλογές", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.include_landscape = tk.BooleanVar(value=True)
        self.include_portrait = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Δημιουργία landscape variants (drawable-land-*)", 
                       variable=self.include_landscape).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Δημιουργία portrait variants (drawable-port-*)", 
                       variable=self.include_portrait).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Κουμπί δημιουργίας
        self.generate_btn = ttk.Button(main_frame, text="Δημιουργία Splash Screen", 
                                       command=self.generate_splash, style='Accent.TButton')
        self.generate_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Πληροφορίες
        info_frame = ttk.LabelFrame(main_frame, text="Πληροφορίες", padding="10")
        info_frame.grid(row=8, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        info_text = """Το εργαλείο δημιουργεί αυτόματα splash screens για όλες τις αναλύσεις:
• Βασικά: drawable, drawable-v24, mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi
• Landscape: drawable-land-* (αν επιλεγεί)
• Portrait: drawable-port-* (αν επιλεγεί)
        
Οι εικόνες τοποθετούνται στο: app/src/main/res/drawable-*"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
    
    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Επιλογή Εικόνας",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.image_path.set(filename)
            self.status_label.config(text=f"Επιλέχθηκε: {os.path.basename(filename)}")
    
    def select_project(self):
        dirname = filedialog.askdirectory(title="Επιλογή Android Project Folder")
        if dirname:
            self.project_path.set(dirname)
            self.status_label.config(text=f"Project: {os.path.basename(dirname)}")
    
    def generate_splash(self):
        # Έλεγχος εισόδων
        if not self.image_path.get():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε μια εικόνα!")
            return
        
        if not self.project_path.get():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε Android project folder!")
            return
        
        if not os.path.exists(self.image_path.get()):
            messagebox.showerror("Σφάλμα", "Η εικόνα δεν βρέθηκε!")
            return
        
        if not os.path.exists(self.project_path.get()):
            messagebox.showerror("Σφάλμα", "Το Android project δεν βρέθηκε!")
            return
        
        try:
            # Disable button κατά τη διάρκεια της επεξεργασίας
            self.generate_btn.config(state='disabled')
            self.progress['value'] = 0
            self.root.update()
            
            # Άνοιγμα εικόνας
            self.status_label.config(text="Φόρτωση εικόνας...")
            self.root.update()
            original_image = Image.open(self.image_path.get())
            
            # Μετατροπή σε RGB αν χρειάζεται
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            filename = self.filename_var.get() + ".png"
            
            # Συλλογή όλων των resolutions που θα δημιουργηθούν
            all_resolutions = dict(self.resolutions)
            
            if self.include_landscape.get():
                all_resolutions.update(self.resolutions_land)
            
            if self.include_portrait.get():
                all_resolutions.update(self.resolutions_port)
            
            total_steps = len(all_resolutions)
            current_step = 0
            
            # Δημιουργία splash screens για κάθε ανάλυση
            for drawable_folder, (width, height) in all_resolutions.items():
                self.status_label.config(text=f"Δημιουργία {drawable_folder}...")
                self.root.update()
                
                # Δημιουργία φακέλου αν δεν υπάρχει
                res_path = os.path.join(self.project_path.get(), 'app', 'src', 'main', 'res', drawable_folder)
                os.makedirs(res_path, exist_ok=True)
                
                # Resize εικόνας διατηρώντας το aspect ratio
                resized_image = self.resize_with_padding(original_image, (width, height))
                
                # Αποθήκευση
                output_path = os.path.join(res_path, filename)
                resized_image.save(output_path, 'PNG', quality=95)
                
                # Update progress
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.root.update()
            
            self.progress['value'] = 100
            self.status_label.config(text="✓ Ολοκληρώθηκε επιτυχώς!", foreground="green")
            messagebox.showinfo("Επιτυχία", 
                              f"Το splash screen δημιουργήθηκε επιτυχώς!\n\n"
                              f"Δημιουργήθηκαν {total_steps} εικόνες σε διαφορετικές αναλύσεις.")
            
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
        new_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Κέντρο της εικόνας
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        new_image.paste(resized, (paste_x, paste_y))
        
        return new_image


def main():
    root = tk.Tk()
    app = AndroidSplashTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()