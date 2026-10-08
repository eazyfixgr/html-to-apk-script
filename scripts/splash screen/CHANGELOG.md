# Changelog

Όλες οι σημαντικές αλλαγές στο Android Splash Screen Tool θα καταγράφονται εδώ.

## [2.0.0] - Smart Edition - 2025-10-27

### ✨ Προσθήκες
- **Ξεχωριστά inputs για Portrait & Landscape εικόνες**
  - Δύο ανεξάρτητα sections για επιλογή εικόνων
  - Έξυπνη τοποθέτηση στους σωστούς φακέλους
  - Fallback σε portrait εικόνα αν δεν υπάρχει landscape

- **Αυτόματη αποθήκευση ρυθμίσεων**
  - Αποθήκευση σε JSON config file (~/.android_splash_tool_config.json)
  - Αυτόματη φόρτωση κατά την εκκίνηση
  - Remember last used paths και επιλογές

- **Preview λειτουργικότητα**
  - Εμφάνιση ονόματος αρχείου και διαστάσεων
  - Visual feedback για επιλεγμένες εικόνες
  - Color-coded status messages

- **Βελτιωμένη υποστήριξη εικόνων**
  - RGBA support για διαφάνεια
  - Καλύτερη βελτιστοποίηση PNG (optimize=True)
  - Έξυπνο resize με ή χωρίς padding

- **Enhanced UI/UX**
  - Μεγαλύτερο παράθυρο (700x650)
  - Εμφάνιση εμοτικόνων στο interface
  - Λεπτομερές progress tracking
  - Καλύτερα οργανωμένο layout με LabelFrames

### 🔄 Αλλαγές
- Αντικατάσταση single image input με dual inputs (portrait/landscape)
- Νέα λογική δημιουργίας που διαχωρίζει portrait/landscape drawables
- Βελτιωμένα μηνύματα επιτυχίας με στατιστικά
- Προσθήκη initial directory support σε file dialogs

### 🐛 Διορθώσεις
- Καλύτερος χειρισμός RGBA εικόνων
- Σωστή διαχείριση padding με διάφανες εικόνες
- Improved error handling

### 📚 Ενημερώσεις Documentation
- Ολοκληρωτική ανανέωση README
- Προσθήκη παραδειγμάτων χρήσης
- Προσθήκη troubleshooting section
- Προσθήκη example config file

---

## [1.0.0] - Αρχική Έκδοση - 2025-10-27

### ✨ Αρχικά Χαρακτηριστικά
- Βασικό GUI με tkinter
- Δημιουργία splash screens για όλες τις αναλύσεις Android
- Υποστήριξη drawable, drawable-v24, mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi
- Υποστήριξη landscape και explicit portrait variants
- Resize με padding για διατήρηση aspect ratio
- Progress bar για παρακολούθηση
- Βασική επιλογή εικόνας και project folder
