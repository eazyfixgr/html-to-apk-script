# Γρήγορη Εκκίνηση 🚀

## Εγκατάσταση (1 λεπτό)

```bash
# Εγκατάσταση βιβλιοθήκης
pip install Pillow

# Εκτέλεση
python android_splash_screen_tool.py
```

## Πώς να το χρησιμοποιήσεις (30 δευτερόλεπτα)

### Βήμα 1: Portrait Εικόνα ✅
```
Πάτα "Επιλογή" στο "📱 Portrait Εικόνα"
→ Διάλεξε την εικόνα σου (π.χ. logo.png)
→ Θα δεις: ✓ logo.png (1080x1920px)
```

### Βήμα 2: Landscape Εικόνα (Προαιρετικό) 🔄
```
Πάτα "Επιλογή" στο "🔄 Landscape Εικόνα"
→ Διάλεξε landscape εικόνα
→ ΄Η άφησέ το κενό για να χρησιμοποιηθεί η portrait
```

### Βήμα 3: Android Project 📁
```
Πάτα "Επιλογή" στο "Android Project"
→ Διάλεξε το φάκελο του project σου
→ π.χ. /home/user/AndroidStudio/MyApp
```

### Βήμα 4: Πάτα το Κουμπί! 🎯
```
Πάτα "🚀 Δημιουργία Splash Screens"
→ Περίμενε (10-30 δευτερόλεπτα)
→ ✓ Έτοιμο!
```

## Τι θα δεις μετά:

```
YourAndroidProject/
└── app/src/main/res/
    ├── drawable/
    │   └── splash_screen.png
    ├── drawable-mdpi/
    │   └── splash_screen.png
    ├── drawable-hdpi/
    │   └── splash_screen.png
    ├── drawable-xhdpi/
    │   └── splash_screen.png
    ├── drawable-xxhdpi/
    │   └── splash_screen.png
    ├── drawable-xxxhdpi/
    │   └── splash_screen.png
    ├── drawable-v24/
    │   └── splash_screen.png
    ├── drawable-land-mdpi/
    │   └── splash_screen.png
    ├── drawable-land-hdpi/
    │   └── splash_screen.png
    ├── drawable-land-xhdpi/
    │   └── splash_screen.png
    ├── drawable-land-xxhdpi/
    │   └── splash_screen.png
    └── drawable-land-xxxhdpi/
        └── splash_screen.png
```

## Συμβουλές Express ⚡

### Για πρώτη φορά:
- Βάλε μόνο portrait εικόνα
- Άφησε όλα τα checkboxes όπως είναι
- Πάτα το κουμπί!

### Για professional result:
- Φτιάξε 2 εικόνες: μία portrait (1080x1920) και μία landscape (1920x1080)
- Βάλε και τις δύο
- Ενεργοποίησε "explicit portrait variants"
- Κράτα το padding ενεργό

### Για γρήγορη δουλειά:
- Το εργαλείο θυμάται τις επιλογές σου!
- Την επόμενη φορά απλά:
  1. Άνοιξε το
  2. Πάτα το κουμπί
  3. Done! ✅

## Ερωτήσεις;

**Χρειάζομαι landscape εικόνα;**
→ Όχι! Αν δεν έχεις, άφησε το κενό.

**Τι διαστάσεις πρέπει να έχει η εικόνα;**
→ Portrait: 1080x1920 ή μεγαλύτερη
→ Landscape: 1920x1080 ή μεγαλύτερη

**Πού αποθηκεύονται οι ρυθμίσεις;**
→ Στο ~/.android_splash_tool_config.json

**Μπορώ να το τρέξω ξανά;**
→ Ναι! Θα αντικαταστήσει τις παλιές εικόνες.

---

**Γρήγορο παράδειγμα για copy-paste:**

```bash
# 1. Εγκατάσταση
pip install Pillow

# 2. Εκτέλεση
python android_splash_screen_tool.py

# 3. Επιλογή portrait image
# 4. Επιλογή project folder
# 5. Πάτα το κουμπί
# 6. Done! 🎉
```

---

**Αυτό ήταν! Πιο εύκολο δεν γίνεται! 🚀**
