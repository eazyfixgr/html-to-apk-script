#!/usr/bin/env python3
"""
Simple Android Icon Changer
Αλλάζει το εικονίδιο μιας υπάρχουσας Android εφαρμογής
"""

import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Το Pillow δεν είναι εγκατεστημένο!")
    print("Εγκατέστησε το με: pip install Pillow")

class AndroidIconChanger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Android Icon Changer")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Variables
        self.project_dir_var = tk.StringVar()
        self.icon_file_var = tk.StringVar()
        
        # Android icon sizes (in pixels)
        self.ICON_SIZES = {
            'mdpi': 48,
            'hdpi': 72,
            'xhdpi': 96,
            'xxhdpi': 144,
            'xxxhdpi': 192
        }
        
        # Check PIL
        if not PIL_AVAILABLE:
            messagebox.showerror(
                "Σφάλμα",
                "Το Pillow δεν είναι εγκατεστημένο!\n\n"
                "Εγκατέστησέ το με την εντολή:\n"
                "pip install Pillow"
            )
            self.root.destroy()
            sys.exit(1)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Δημιουργία GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        
        # Τίτλος
        title_font = Font(size=16, weight="bold")
        title = ttk.Label(main_frame, text="🔄 Android Icon Changer", font=title_font)
        title.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, 
                            text="Αλλαγή εικονιδίου Android εφαρμογής",
                            foreground="gray")
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 25))
        
        # Android Project Directory
        ttk.Label(main_frame, text="📁 Android Project:", 
                 font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.project_dir_var, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Επιλογή", command=self.browse_project).grid(
            row=2, column=2, padx=(5, 0), pady=5)
        
        # Πληροφορίες project
        self.project_info = ttk.Label(main_frame, text="", foreground="gray", wraplength=600)
        self.project_info.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # Icon File
        ttk.Label(main_frame, text="🖼️  Νέο Icon:", 
                 font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.icon_file_var, width=50).grid(
            row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Επιλογή", command=self.browse_icon).grid(
            row=4, column=2, padx=(5, 0), pady=5)
        
        # Icon preview
        self.preview_frame = ttk.LabelFrame(main_frame, text="Προεπισκόπηση Icon", padding="15")
        self.preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        self.preview_label = ttk.Label(self.preview_frame, text="Δεν έχει επιλεγεί icon")
        self.preview_label.pack()
        
        # Πληροφορίες
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️  Πληροφορίες", padding="10")
        info_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        info_text = (
            "• Το icon θα πρέπει να είναι τετράγωνο (π.χ. 1024x1024)\n"
            "• Υποστηριζόμενες μορφές: PNG, JPG\n"
            "• Προτείνεται ελάχιστο μέγεθος: 512x512\n"
            "• Θα δημιουργηθούν αυτόματα όλα τα μεγέθη για Android"
        )
        ttk.Label(info_frame, text=info_text, foreground="gray").pack(anchor=tk.W)
        
        # Κουμπιά
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        self.change_button = ttk.Button(button_frame, text="✨ Αλλαγή Icon", 
                                       command=self.change_icon, style="Accent.TButton")
        self.change_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Καθαρισμός", 
                  command=self.clear_form).pack(side=tk.LEFT)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Έτοιμο", 
                                     foreground="green", font=("TkDefaultFont", 9))
        self.status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=(15, 0))
        
        # Traces
        self.project_dir_var.trace_add('write', self.on_project_changed)
        self.icon_file_var.trace_add('write', self.on_icon_changed)
        
    def browse_project(self):
        """Επιλογή Android project directory"""
        directory = filedialog.askdirectory(title="Επιλέξτε το Android Project")
        if directory:
            self.project_dir_var.set(directory)
            
    def browse_icon(self):
        """Επιλογή icon αρχείου"""
        filetypes = [
            ("Εικόνες", "*.png *.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("JPG", "*.jpg *.jpeg"),
            ("Όλα", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Επιλέξτε Icon",
            filetypes=filetypes
        )
        if filename:
            self.icon_file_var.set(filename)
            
    def on_project_changed(self, *args):
        """Ενημέρωση πληροφοριών project"""
        project_path = Path(self.project_dir_var.get().strip())
        
        if not project_path.exists():
            self.project_info.config(text="❌ Ο φάκελος δεν υπάρχει")
            return
            
        # Έλεγχος αν είναι Android project
        android_markers = [
            project_path / "app" / "src" / "main" / "res",
            project_path / "build.gradle",
            project_path / "app" / "build.gradle"
        ]
        
        if any(marker.exists() for marker in android_markers):
            # Βρες το app name αν υπάρχει
            app_name = "Άγνωστο"
            manifest_path = project_path / "app" / "src" / "main" / "AndroidManifest.xml"
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'android:label="' in content:
                            start = content.find('android:label="') + 15
                            end = content.find('"', start)
                            app_name = content[start:end]
                except:
                    pass
            
            self.project_info.config(
                text=f"✅ Έγκυρο Android project | App: {app_name}",
                foreground="green"
            )
        else:
            self.project_info.config(
                text="⚠️ Δεν φαίνεται να είναι Android project",
                foreground="orange"
            )
            
    def on_icon_changed(self, *args):
        """Ενημέρωση preview icon"""
        icon_path = self.icon_file_var.get().strip()
        
        if not icon_path or not Path(icon_path).exists():
            self.preview_label.config(text="Δεν έχει επιλεγεί icon", image="")
            return
            
        try:
            img = Image.open(icon_path)
            
            # Πληροφορίες
            info_text = f"Μέγεθος: {img.width}x{img.height} | Μορφή: {img.format}"
            
            # Προειδοποιήσεις
            warnings = []
            if img.width != img.height:
                warnings.append("⚠️ Δεν είναι τετράγωνο")
            if img.width < 512 or img.height < 512:
                warnings.append("⚠️ Πολύ μικρό (min: 512x512)")
            elif img.width >= 512 and img.height >= 512:
                warnings.append("✅ Καλό μέγεθος")
            
            if warnings:
                info_text += "\n" + " | ".join(warnings)
            
            # Preview
            preview_size = (128, 128)
            img_preview = img.copy()
            img_preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            import io
            import base64
            buffer = io.BytesIO()
            img_preview.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            photo = tk.PhotoImage(data=img_str)
            
            self.preview_label.config(text=info_text, image=photo, compound=tk.TOP)
            self.preview_label.image = photo
            
        except Exception as e:
            self.preview_label.config(text=f"❌ Σφάλμα: {e}", image="")
            
    def clear_form(self):
        """Καθαρισμός φόρμας"""
        self.project_dir_var.set("")
        self.icon_file_var.set("")
        self.status_label.config(text="Έτοιμο", foreground="green")
        
    def validate_input(self):
        """Έλεγχος εισόδου"""
        project_path = Path(self.project_dir_var.get().strip())
        icon_path = Path(self.icon_file_var.get().strip())
        
        if not self.project_dir_var.get().strip():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε Android project")
            return False
            
        if not project_path.exists():
            messagebox.showerror("Σφάλμα", "Το Android project δεν υπάρχει")
            return False
            
        res_path = project_path / "app" / "src" / "main" / "res"
        if not res_path.exists():
            messagebox.showerror("Σφάλμα", 
                "Δεν βρέθηκε φάκελος res.\n\n"
                "Βεβαιωθείτε ότι επιλέξατε το root directory του Android project.")
            return False
            
        if not self.icon_file_var.get().strip():
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε icon αρχείο")
            return False
            
        if not icon_path.exists():
            messagebox.showerror("Σφάλμα", "Το icon αρχείο δεν υπάρχει")
            return False
            
        # Έλεγχος icon
        try:
            img = Image.open(icon_path)
            
            if img.width < 192 or img.height < 192:
                result = messagebox.askyesno("Προειδοποίηση",
                    f"Το icon είναι {img.width}x{img.height}.\n"
                    "Είναι πολύ μικρό (προτείνεται τουλάχιστον 512x512).\n\n"
                    "Θέλετε να συνεχίσετε;")
                if not result:
                    return False
                    
            if img.width != img.height:
                result = messagebox.askyesno("Προειδοποίηση",
                    f"Το icon δεν είναι τετράγωνο ({img.width}x{img.height}).\n"
                    "Μπορεί να μην φαίνεται σωστά.\n\n"
                    "Θέλετε να συνεχίσετε;")
                if not result:
                    return False
                    
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Δεν μπόρεσε να διαβαστεί το icon: {e}")
            return False
            
        return True
        
    def change_icon(self):
        """Αλλαγή icon"""
        if not self.validate_input():
            return
            
        project_path = Path(self.project_dir_var.get().strip())
        icon_path = Path(self.icon_file_var.get().strip())
        
        try:
            self.status_label.config(text="Φόρτωση icon...", foreground="blue")
            self.root.update()
            
            # Φόρτωση icon
            source_img = Image.open(icon_path)
            
            res_path = project_path / "app" / "src" / "main" / "res"
            
            # Δημιουργία icons για κάθε density
            success_count = 0
            for density, size in self.ICON_SIZES.items():
                self.status_label.config(
                    text=f"Δημιουργία {density} icon ({size}x{size})...", 
                    foreground="blue")
                self.root.update()
                
                mipmap_dir = res_path / f"mipmap-{density}"
                mipmap_dir.mkdir(parents=True, exist_ok=True)
                
                # Resize icon
                resized_icon = source_img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Αποθήκευση
                icon_file = mipmap_dir / "ic_launcher.png"
                resized_icon.save(icon_file, "PNG")
                success_count += 1
                
            # Δημιουργία adaptive icons
            self.status_label.config(text="Δημιουργία adaptive icons...", foreground="blue")
            self.root.update()
            
            for density, size in self.ICON_SIZES.items():
                mipmap_dir = res_path / f"mipmap-{density}"
                
                # Background (λευκό)
                bg_img = Image.new('RGB', (size, size), color='#FFFFFF')
                bg_path = mipmap_dir / "ic_launcher_background.png"
                bg_img.save(bg_path, "PNG")
                
                # Foreground (το icon μικρότερο στο κέντρο)
                fg_size = int(size * 0.6)
                padding = (size - fg_size) // 2
                
                fg_img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
                resized_source = source_img.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
                fg_img.paste(resized_source, (padding, padding))
                
                fg_path = mipmap_dir / "ic_launcher_foreground.png"
                fg_img.save(fg_path, "PNG")
            
            self.status_label.config(
                text=f"✅ Επιτυχία! Δημιουργήθηκαν {success_count * 3} αρχεία icon", 
                foreground="green")
            
            messagebox.showinfo("Επιτυχία!",
                f"Το icon άλλαξε με επιτυχία!\n\n"
                f"Δημιουργήθηκαν:\n"
                f"• {success_count} ic_launcher.png\n"
                f"• {success_count} ic_launcher_background.png\n"
                f"• {success_count} ic_launcher_foreground.png\n\n"
                f"Σύνολο: {success_count * 3} αρχεία")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Σφάλμα: {e}", foreground="red")
            messagebox.showerror("Σφάλμα", f"Απέτυχε η αλλαγή του icon:\n\n{e}")
            
    def run(self):
        """Εκτέλεση εφαρμογής"""
        try:
            # Style
            style = ttk.Style()
            style.theme_use('clam')
            
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main function"""
    app = AndroidIconChanger()
    app.run()

if __name__ == "__main__":
    main()