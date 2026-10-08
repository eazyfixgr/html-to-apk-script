# Android Splash Screen Tool - Smart Edition 🚀📱

Έξυπνο εργαλείο με GUI για αυτόματη προσθήκη splash screen σε Android projects με ξεχωριστές portrait και landscape εικόνες και αυτόματη αποθήκευση ρυθμίσεων.

## Χαρακτηριστικά ✨

- 🎨 Ξεχωριστές εικόνες για portrait και landscape orientation
- 💾 Αυτόματη αποθήκευση και φόρτωση ρυθμίσεων
- 📱 Δημιουργία για όλες τις αναλύσεις Android (mdpi έως xxxhdpi)
- 🔄 Έξυπνη τοποθέτηση εικόνων ανάλογα με orientation
- ⚙️ Προαιρετικά explicit portrait variants
- 📐 Διατήρηση aspect ratio με padding
- 🎯 Απλό και φιλικό γραφικό περιβάλλον
- 🔍 Preview επιλεγμένων εικόνων με διαστάσεις

## Εγκατάσταση 🔧

1. Βεβαιωθείτε ότι έχετε Python 3.7+ εγκατεστημένο
2. Εγκαταστήστε τις απαραίτητες βιβλιοθήκες:

```bash
pip install -r requirements.txt
```

Ή απευθείας:

```bash
pip install Pillow
```

## Χρήση 🚀

1. Εκτελέστε το script:

```bash
python android_splash_screen_tool.py
```

2. Στο παράθυρο που ανοίγει:
   
   **Portrait Εικόνα (υποχρεωτική):**
   - Πατήστε "Επιλογή" στο Portrait section
   - Διαλέξτε την εικόνα για κάθετο προσανατολισμό
   - Θα δείτε preview με το όνομα και τις διαστάσεις
   
   **Landscape Εικόνα (προαιρετική):**
   - Πατήστε "Επιλογή" στο Landscape section
   - Διαλέξτε την εικόνα για οριζόντιο προσανατολισμό
   - Αν δεν επιλέξετε, θα χρησιμοποιηθεί η portrait εικόνα
   
   **Android Project:**
   - Πατήστε "Επιλογή" και διαλέξτε το φάκελο του Android project σας
   
   **Επιλογές:**
   - Όνομα αρχείου (default: splash_screen)
   - Explicit portrait variants (drawable-port-*)
   - Χρήση padding για aspect ratio
   
   - Πατήστε "🚀 Δημιουργία Splash Screens"

3. Το εργαλείο θα δημιουργήσει έξυπνα τις εικόνες:
   
   **Portrait εικόνα → Portrait Drawables:**
   - drawable (480x800px)
   - drawable-v24 (1080x1920px)
   - drawable-mdpi (320x480px)
   - drawable-hdpi (480x800px)
   - drawable-xhdpi (720x1280px)
   - drawable-xxhdpi (1080x1920px)
   - drawable-xxxhdpi (1440x2560px)
   - drawable-port-* (αν ενεργοποιηθεί)
   
   **Landscape εικόνα (ή portrait) → Landscape Drawables:**
   - drawable-land-mdpi (480x320px)
   - drawable-land-hdpi (800x480px)
   - drawable-land-xhdpi (1280x720px)
   - drawable-land-xxhdpi (1920x1080px)
   - drawable-land-xxxhdpi (2560x1440px)

4. Οι ρυθμίσεις σας αποθηκεύονται αυτόματα! Την επόμενη φορά που ανοίξετε το εργαλείο, θα βρείτε τις τελευταίες επιλογές σας.

## Δομή Φακέλων 📁

Οι εικόνες τοποθετούνται αυτόματα στη σωστή δομή Android:

```
YourAndroidProject/
└── app/
    └── src/
        └── main/
            └── res/
                ├── drawable/
                │   └── splash_screen.png
                ├── drawable-v24/
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
                ├── drawable-land-mdpi/
                │   └── splash_screen.png
                ├── drawable-land-hdpi/
                │   └── splash_screen.png
                ├── drawable-land-xhdpi/
                │   └── splash_screen.png
                ├── drawable-land-xxhdpi/
                │   └── splash_screen.png
                ├── drawable-land-xxxhdpi/
                │   └── splash_screen.png
                ├── drawable-port-mdpi/
                │   └── splash_screen.png
                ├── drawable-port-hdpi/
                │   └── splash_screen.png
                ├── drawable-port-xhdpi/
                │   └── splash_screen.png
                ├── drawable-port-xxhdpi/
                │   └── splash_screen.png
                └── drawable-port-xxxhdpi/
                    └── splash_screen.png
```

## Αποθηκευμένες Ρυθμίσεις 💾

Το εργαλείο αποθηκεύει αυτόματα τις ρυθμίσεις σας σε:
- **Linux/Mac**: `~/.android_splash_tool_config.json`
- **Windows**: `C:\Users\[YourUsername]\.android_splash_tool_config.json`

**Τι αποθηκεύεται:**
- Τελευταίο Android project path
- Τελευταία portrait εικόνα
- Τελευταία landscape εικόνα
- Όνομα αρχείου
- Επιλογές (explicit portrait, padding)

Οι ρυθμίσεις φορτώνονται αυτόματα κάθε φορά που ανοίγετε το εργαλείο!

## Τύποι Drawables 📱

### Βασικά Drawables
- **drawable**: Generic φάκελος, χρησιμοποιείται ως fallback όταν δεν βρεθεί συγκεκριμένη ανάλυση
- **drawable-v24**: Ειδικά για Android 7.0 (API 24) και πάνω
- **drawable-mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi**: Διαφορετικές πυκνότητες οθόνης

### Orientation-Specific Drawables
- **drawable-land-***: Ειδικά για landscape mode (οριζόντιος προσανατολισμός)
- **drawable-port-***: Ειδικά για portrait mode (κάθετος προσανατολισμός)

Το Android επιλέγει αυτόματα το σωστό drawable ανάλογα με:
1. Την πυκνότητα της οθόνης (dpi)
2. Τον προσανατολισμό της συσκευής
3. Την έκδοση του Android

## Χρήση του Splash Screen στο Android Project 📝

Μετά τη δημιουργία των εικόνων, μπορείτε να χρησιμοποιήσετε το splash screen στο Android project σας:

### 1. Δημιουργήστε ένα Splash Activity

Στο `AndroidManifest.xml`:

```xml
<activity
    android:name=".SplashActivity"
    android:theme="@style/SplashTheme"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### 2. Δημιουργήστε το theme στο `res/values/styles.xml`:

```xml
<style name="SplashTheme" parent="Theme.AppCompat.NoActionBar">
    <item name="android:windowBackground">@drawable/splash_screen</item>
</style>
```

### 3. Δημιουργήστε το SplashActivity.java:

```java
public class SplashActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
        finish();
    }
}
```

## Συμβουλές 💡

### Επιλογή Εικόνων
- **Portrait εικόνα**: Χρησιμοποιήστε ανάλυση τουλάχιστον 1080x1920px
- **Landscape εικόνα**: Χρησιμοποιήστε ανάλυση τουλάχιστον 1920x1080px
- **Μονή εικόνα**: Αν έχετε μόνο μία εικόνα, βάλτε την ως portrait - θα χρησιμοποιηθεί για όλα
- **Ξεχωριστές εικόνες**: Για καλύτερη εμφάνιση, χρησιμοποιήστε διαφορετικά designs για portrait/landscape

### Γενικά
- **Aspect Ratio**: Ενεργοποιήστε το padding για να διατηρηθεί το aspect ratio χωρίς παραμόρφωση
- **Μορφή αρχείου**: Υποστηρίζονται PNG, JPG, JPEG, BMP
- **Διαφάνεια**: Αν θέλετε διάφανο background, χρησιμοποιήστε PNG με RGBA
- **Explicit Portrait**: Ενεργοποιήστε το αν θέλετε ξεχωριστούς φακέλους drawable-port-*
- **Βελτιστοποίηση**: Το εργαλείο αποθηκεύει με optimize=True για μικρότερο μέγεθος αρχείων
- **Αυτόματη μνήμη**: Οι ρυθμίσεις σας θυμούνται - απλά ανοίξτε και συνεχίστε!

## Παραδείγματα Χρήσης 📸

### Σενάριο 1: Μόνο Portrait Εικόνα
```
1. Επιλέξτε portrait εικόνα (π.χ. logo_vertical.png)
2. Μην επιλέξετε landscape εικόνα
3. Αποτέλεσμα: Η ίδια εικόνα χρησιμοποιείται παντού με αυτόματο resize
```

### Σενάριο 2: Ξεχωριστές Εικόνες για Portrait & Landscape
```
1. Επιλέξτε portrait εικόνα (π.χ. splash_vertical.png - 1080x1920)
2. Επιλέξτε landscape εικόνα (π.χ. splash_horizontal.png - 1920x1080)
3. Αποτέλεσμα: 
   - drawable, drawable-mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi → portrait εικόνα
   - drawable-land-* → landscape εικόνα
```

### Σενάριο 3: Professional Setup με Explicit Portrait
```
1. Επιλέξτε portrait εικόνα
2. Επιλέξτε landscape εικόνα
3. Ενεργοποιήστε "Δημιουργία explicit portrait variants"
4. Αποτέλεσμα: Πλήρης κάλυψη όλων των φακέλων για maximum compatibility
```

## Απαιτήσεις Συστήματος 💻

- Python 3.7 ή νεότερη έκδοση
- Pillow (PIL Fork)
- tkinter (συνήθως περιλαμβάνεται στην Python)

## Troubleshooting 🔍

**Πρόβλημα**: "No module named 'PIL'"
**Λύση**: Εγκαταστήστε το Pillow με `pip install Pillow`

**Πρόβλημα**: "No module named 'tkinter'"
**Λύση**: 
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: Το tkinter είναι ενσωματωμένο
- Windows: Το tkinter είναι ενσωματωμένο

**Πρόβλημα**: Οι ρυθμίσεις δεν αποθηκεύονται
**Λύση**: Βεβαιωθείτε ότι έχετε δικαιώματα εγγραφής στον home φάκελο σας

**Πρόβλημα**: Η εικόνα φαίνεται παραμορφωμένη
**Λύση**: Ενεργοποιήστε το "Χρήση padding για διατήρηση aspect ratio"

## Νέα Χαρακτηριστικά v2.0 (Smart Edition) 🆕

✨ **Μείζονες αλλαγές:**
- Ξεχωριστά inputs για portrait και landscape εικόνες
- Αυτόματη αποθήκευση και φόρτωση ρυθμίσεων
- Preview επιλεγμένων εικόνων με διαστάσεις
- Έξυπνη τοποθέτηση εικόνων ανάλογα με orientation
- Υποστήριξη RGBA εικόνων με διαφάνεια
- Βελτιωμένη βελτιστοποίηση PNG (optimize=True)
- Λεπτομερές μήνυμα επιτυχίας με στατιστικά
- Remember last used paths για γρήγορη πρόσβαση

## Άδεια Χρήσης 📄

Ελεύθερο για προσωπική και εμπορική χρήση.

## Συγγραφέας ✍️

Δημιουργήθηκε με Claude AI (Sonnet 4.5)

---

🌟 **Tips για Best Results:**
1. Χρησιμοποιήστε ξεχωριστά optimized designs για portrait και landscape
2. Κρατήστε το padding ενεργοποιημένο για consistency
3. Χρησιμοποιήστε PNG με διαφάνεια για modern look
4. Αφήστε το εργαλείο να θυμάται τις ρυθμίσεις σας

Καλή δημιουργία splash screens! 🎨✨
