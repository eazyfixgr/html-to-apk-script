#!/usr/bin/env python3
"""
Firebase Setup Assistant for Capacitor Android Projects
Provides step-by-step instructions and code snippets for Firebase integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font
from pathlib import Path
import subprocess
import json
import os

class FirebaseSetupAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Firebase Setup Assistant for Capacitor")
        self.root.geometry("1000x700")
        
        self.project_path = tk.StringVar()
        self.firebase_config = {
            'apiKey': tk.StringVar(),
            'authDomain': tk.StringVar(),
            'projectId': tk.StringVar(),
            'storageBucket': tk.StringVar(),
            'messagingSenderId': tk.StringVar(),
            'appId': tk.StringVar()
        }
        
        self.completed_steps = set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup tabs
        self.setup_overview_tab(notebook)
        self.setup_firebase_console_tab(notebook)
        self.setup_project_config_tab(notebook)
        self.setup_code_snippets_tab(notebook)
        self.setup_gradle_tab(notebook)
        self.setup_checklist_tab(notebook)
        
    def setup_overview_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📋 Overview")
        
        # Title
        title_font = Font(size=16, weight="bold")
        title = ttk.Label(frame, text="Firebase Cloud Backup Setup for Capacitor", font=title_font)
        title.pack(pady=(0, 20))
        
        # Project selection
        project_frame = ttk.LabelFrame(frame, text="Select Your Capacitor Project", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(project_frame, text="Project Directory:").pack(anchor=tk.W)
        path_frame = ttk.Frame(project_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(path_frame, textvariable=self.project_path, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Browse", command=self.browse_project).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="Analyze", command=self.analyze_project).pack(side=tk.LEFT, padx=(5, 0))
        
        # Steps overview
        steps_frame = ttk.LabelFrame(frame, text="Setup Steps", padding="10")
        steps_frame.pack(fill=tk.BOTH, expand=True)
        
        steps_text = scrolledtext.ScrolledText(steps_frame, wrap=tk.WORD, height=20)
        steps_text.pack(fill=tk.BOTH, expand=True)
        
        overview = """
FIREBASE SETUP STEPS OVERVIEW
========================================

This assistant will guide you through setting up Firebase Authentication 
and Cloud Storage for your Capacitor Android app.

WHAT YOU'LL NEED:
- A Firebase account (free)
- Your Capacitor project (already created)
- Android Studio installed
- About 30 minutes

THE PROCESS:

1. FIREBASE CONSOLE SETUP (Tab 2)
   - Create Firebase project
   - Add Android app
   - Configure Authentication
   - Setup Firestore
   - Add SHA-1 fingerprint

2. PROJECT CONFIGURATION (Tab 3)
   - Install Firebase plugin
   - Update capacitor.config.ts
   - Add google-services.json

3. CODE INTEGRATION (Tab 4)
   - Copy Firebase initialization code
   - Add authentication functions
   - Implement offline-first storage

4. GRADLE FILES (Tab 5)
   - Update build.gradle files
   - Add Firebase dependencies

5. FINAL CHECKLIST (Tab 6)
   - Verify all steps completed
   - Test the app

CLICK ANALYZE to scan your project and get personalized instructions!
========================================
"""
        steps_text.insert(1.0, overview)
        steps_text.config(state=tk.DISABLED)
        
    def setup_firebase_console_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔥 Firebase Console")
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        instructions = """
FIREBASE CONSOLE SETUP GUIDE
========================================

STEP 1: CREATE FIREBASE PROJECT
--------------------------------
1. Go to: https://console.firebase.google.com/
2. Click "Add project"
3. Enter project name (e.g., "my-app")
4. Enable/disable Google Analytics (optional)
5. Click "Create project"

STEP 2: ADD ANDROID APP
------------------------
1. In your Firebase project, click "Add app" → Android icon
2. Fill in the form:
   
   Android package name: com.yourcompany.yourapp
   (IMPORTANT: Must match the appId in capacitor.config.ts)
   
   App nickname: My App (optional)
   
3. Click "Register app"

4. DOWNLOAD google-services.json
   - Click "Download google-services.json"
   - Save it to your desktop (you'll copy it later)

5. Click "Next" (skip the SDK setup steps for now)
6. Click "Continue to console"

STEP 3: ENABLE AUTHENTICATION
------------------------------
1. In left sidebar, click "Authentication"
2. Click "Get started"
3. Click "Sign-in method" tab
4. Click "Google" in the providers list
5. Toggle "Enable"
6. Enter project support email
7. Click "Save"

STEP 4: CREATE FIRESTORE DATABASE
----------------------------------
1. In left sidebar, click "Firestore Database"
2. Click "Create database"
3. Select location (choose closest to your users)
4. Start in "production mode" (we'll set rules next)
5. Click "Create"

6. IMPORTANT: Set Security Rules
   Click "Rules" tab and paste this:

----------------------------------------
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
----------------------------------------

7. Click "Publish"

STEP 5: GET SHA-1 FINGERPRINT
------------------------------
This is CRITICAL for Google Sign-In to work on Android!

1. Open terminal/command prompt
2. Navigate to your project's android folder:
   cd path/to/your/project/android

3. Run this command:
   
   Windows:
   gradlew signingReport
   
   Mac/Linux:
   ./gradlew signingReport

4. Look for output like this:
   
   Variant: debug
   Config: debug
   Store: C:\\Users\\...
   Alias: AndroidDebugKey
   MD5: XX:XX:XX...
   SHA1: 27:20:31:22:A2:B0:6F:A2:70:0C:86:A2:0B:5A:93:07:E5:46:7D:C7
   SHA-256: ...
   
5. COPY the SHA-1 value (the long hex string)

6. Go back to Firebase Console
7. Project Settings (gear icon) → Your apps → Android app
8. Scroll down to "SHA certificate fingerprints"
9. Click "Add fingerprint"
10. Paste your SHA-1
11. Click "Save"

STEP 6: ADD AUTHORIZED DOMAINS
-------------------------------
1. Go to Authentication → Settings → Authorized domains
2. Make sure these domains are listed:
   - localhost
   - your-project-id.firebaseapp.com
   - your-project-id.web.app

3. Add if missing: com.yourcompany.yourapp

STEP 7: GET YOUR FIREBASE CONFIG
---------------------------------
1. Project Settings (gear icon) → General
2. Scroll to "Your apps" → Web app section
3. If no web app exists, click "Add app" → Web
4. Copy these values (you'll need them in Tab 3):
   
   apiKey: "..."
   authDomain: "..."
   projectId: "..."
   storageBucket: "..."
   messagingSenderId: "..."
   appId: "..."

========================================
DONE WITH FIREBASE CONSOLE!
Next: Go to Tab 3 (Project Configuration)
========================================
"""
        text.insert(1.0, instructions)
        text.config(state=tk.DISABLED)
        
        # Copy button
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="Copy Firestore Rules", 
                  command=lambda: self.copy_to_clipboard("""rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /{document=**} {
      allow read, write: if false;
    }
  }
}""")).pack(side=tk.LEFT, padx=5)
        
    def setup_project_config_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="⚙️ Project Config")
        
        # Firebase config inputs
        config_frame = ttk.LabelFrame(frame, text="Firebase Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        for key, label in [
            ('apiKey', 'API Key'),
            ('authDomain', 'Auth Domain'),
            ('projectId', 'Project ID'),
            ('storageBucket', 'Storage Bucket'),
            ('messagingSenderId', 'Messaging Sender ID'),
            ('appId', 'App ID')
        ]:
            row = ttk.Frame(config_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=self.firebase_config[key], width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(config_frame, text="Generate Config Code", 
                  command=self.generate_firebase_config).pack(pady=10)
        
        # Instructions
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        instructions = """
PROJECT CONFIGURATION
========================================

STEP 1: INSTALL FIREBASE PLUGIN
--------------------------------
1. Open terminal in your project directory
2. Run this command:

npm install @capacitor-firebase/authentication

3. Then run:

npx cap sync


STEP 2: UPDATE CAPACITOR.CONFIG.TS
-----------------------------------
Open: capacitor.config.ts

Add this to your config (merge with existing):

----------------------------------------
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.yourcompany.yourapp',
  appName: 'Your App Name',
  webDir: 'www',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    FirebaseAuthentication: {
      skipNativeAuth: false,
      providers: ["google.com"]
    }
  }
};

export default config;
----------------------------------------


STEP 3: ADD GOOGLE-SERVICES.JSON
---------------------------------
1. Copy the google-services.json you downloaded from Firebase
2. Paste it here:
   
   your-project/android/app/google-services.json

3. Verify the file is in the correct location!


STEP 4: UPDATE MAINACTIVITY.JAVA
---------------------------------
Location: android/app/src/main/java/com/yourcompany/yourapp/MainActivity.java

REPLACE the entire file with this:

----------------------------------------
package com.yourcompany.yourapp;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
----------------------------------------

IMPORTANT: Replace "com.yourcompany.yourapp" with your actual package name!

========================================
Next: Go to Tab 4 (Code Snippets)
========================================
"""
        text.insert(1.0, instructions)
        text.config(state=tk.DISABLED)
        
    def setup_code_snippets_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="💻 Code Snippets")
        
        # Buttons for different code sections
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="1. Firebase Init", 
                  command=lambda: self.show_code_snippet('firebase_init')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="2. Auth Functions", 
                  command=lambda: self.show_code_snippet('auth_functions')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="3. Data Sync", 
                  command=lambda: self.show_code_snippet('data_sync')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy All", 
                  command=lambda: self.show_code_snippet('all')).pack(side=tk.LEFT, padx=5)
        
        # Code display
        self.code_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier", 9))
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial instructions
        self.show_code_snippet('firebase_init')
        
    def setup_gradle_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔨 Gradle Files")
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        instructions = """
GRADLE CONFIGURATION
========================================

FILE 1: android/build.gradle (PROJECT LEVEL)
---------------------------------------------
Location: android/build.gradle

Make sure it looks like this:

----------------------------------------
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.7.2'
        classpath 'com.google.gms:google-services:4.4.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
----------------------------------------


FILE 2: android/app/build.gradle (APP LEVEL)
---------------------------------------------
Location: android/app/build.gradle

ADD these lines to the dependencies block:

----------------------------------------
dependencies {
    // ... your existing dependencies
    
    // Firebase
    implementation platform('com.google.firebase:firebase-bom:34.3.0')
    implementation 'com.google.firebase:firebase-analytics'
    implementation 'com.google.android.gms:play-services-auth:20.7.0'
}
----------------------------------------

AT THE VERY END of the file, make sure you have:

----------------------------------------
apply from: 'capacitor.build.gradle'

try {
    def servicesJSON = file('google-services.json')
    if (servicesJSON.text) {
        apply plugin: 'com.google.gms.google-services'
    }
} catch(Exception e) {
    logger.info("google-services.json not found")
}
----------------------------------------


AFTER EDITING GRADLE FILES:
1. Open Android Studio
2. File → Sync Project with Gradle Files
3. Wait for sync to complete
4. Close Android Studio

========================================
Next: Go to Tab 6 (Checklist)
========================================
"""
        text.insert(1.0, instructions)
        text.config(state=tk.DISABLED)
        
        # Copy buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Copy Project build.gradle", 
                  command=lambda: self.copy_to_clipboard("""buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.7.2'
        classpath 'com.google.gms:google-services:4.4.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}""")).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Copy App Dependencies", 
                  command=lambda: self.copy_to_clipboard("""    implementation platform('com.google.firebase:firebase-bom:34.3.0')
    implementation 'com.google.firebase:firebase-analytics'
    implementation 'com.google.android.gms:play-services-auth:20.7.0'""")).pack(side=tk.LEFT, padx=5)
        
    def setup_checklist_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="✓ Checklist")
        
        title_font = Font(size=14, weight="bold")
        ttk.Label(frame, text="Final Checklist", font=title_font).pack(pady=(0, 10))
        
        # Checklist items
        self.checklist_vars = {}
        
        sections = [
            ("Firebase Console", [
                "Created Firebase project",
                "Added Android app to project",
                "Downloaded google-services.json",
                "Enabled Google Authentication",
                "Created Firestore database",
                "Set Firestore security rules",
                "Added SHA-1 fingerprint",
                "Verified authorized domains"
            ]),
            ("Project Files", [
                "Installed @capacitor-firebase/authentication",
                "Updated capacitor.config.ts",
                "Copied google-services.json to android/app/",
                "Updated MainActivity.java",
                "Added Firebase config to HTML/JS",
                "Added authentication functions",
                "Added data sync functions"
            ]),
            ("Gradle Files", [
                "Updated android/build.gradle",
                "Updated android/app/build.gradle",
                "Synced project in Android Studio"
            ]),
            ("Testing", [
                "Built APK successfully",
                "Tested Google Sign-In",
                "Tested data sync",
                "Verified offline mode works"
            ])
        ]
        
        # Scrollable frame for checklist
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for section_name, items in sections:
            section_frame = ttk.LabelFrame(scrollable_frame, text=section_name, padding="10")
            section_frame.pack(fill=tk.X, pady=5, padx=5)
            
            for item in items:
                var = tk.BooleanVar()
                self.checklist_vars[item] = var
                ttk.Checkbutton(section_frame, text=item, variable=var).pack(anchor=tk.W, pady=2)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_label = ttk.Label(progress_frame, text="Progress: 0/26 completed")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        ttk.Button(progress_frame, text="Update Progress", 
                  command=self.update_progress).pack(pady=5)
        
    def browse_project(self):
        directory = filedialog.askdirectory(title="Select Capacitor Project Directory")
        if directory:
            self.project_path.set(directory)
            
    def analyze_project(self):
        project_path = Path(self.project_path.get())
        
        if not project_path.exists():
            messagebox.showerror("Error", "Project directory does not exist")
            return
            
        # Check if it's a Capacitor project
        if not (project_path / "capacitor.config.ts").exists() and not (project_path / "capacitor.config.json").exists():
            messagebox.showerror("Error", "Not a valid Capacitor project (capacitor.config.ts not found)")
            return
        
        # Analyze
        analysis = []
        analysis.append("PROJECT ANALYSIS")
        analysis.append("=" * 50)
        
        # Check Android platform
        if (project_path / "android").exists():
            analysis.append("✓ Android platform found")
        else:
            analysis.append("✗ Android platform NOT found - run 'npx cap add android'")
        
        # Check google-services.json
        if (project_path / "android" / "app" / "google-services.json").exists():
            analysis.append("✓ google-services.json found")
        else:
            analysis.append("✗ google-services.json NOT found - download from Firebase Console")
        
        # Check MainActivity
        if (project_path / "android" / "app" / "src" / "main" / "java").exists():
            analysis.append("✓ MainActivity directory found")
        else:
            analysis.append("✗ MainActivity directory NOT found")
        
        # Check node_modules
        if (project_path / "node_modules" / "@capacitor-firebase" / "authentication").exists():
            analysis.append("✓ Firebase Authentication plugin installed")
        else:
            analysis.append("✗ Firebase Authentication plugin NOT installed")
        
        analysis.append("=" * 50)
        
        messagebox.showinfo("Project Analysis", "\n".join(analysis))
        
    def generate_firebase_config(self):
        config_code = f"""const firebaseConfig = {{
    apiKey: "{self.firebase_config['apiKey'].get()}",
    authDomain: "{self.firebase_config['authDomain'].get()}",
    projectId: "{self.firebase_config['projectId'].get()}",
    storageBucket: "{self.firebase_config['storageBucket'].get()}",
    messagingSenderId: "{self.firebase_config['messagingSenderId'].get()}",
    appId: "{self.firebase_config['appId'].get()}"
}};"""
        
        self.copy_to_clipboard(config_code)
        messagebox.showinfo("Success", "Firebase config copied to clipboard!")
        
    def show_code_snippet(self, snippet_type):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete(1.0, tk.END)
        
        if snippet_type == 'firebase_init':
            code = """// PART 1: FIREBASE INITIALIZATION
// Add this to your HTML file inside <script type="module">

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithCredential, 
         onAuthStateChanged, signOut as firebaseSignOut } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { getFirestore, collection, doc, setDoc, getDoc, getDocs, deleteDoc, 
         query, where } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// REPLACE with your actual Firebase config
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",  // NO SPACES!
    projectId: "your-project",
    storageBucket: "your-project.firebasestorage.app",
    messagingSenderId: "123456789",
    appId: "1:123456789:android:abcdef"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

let currentUser = null;

// Listen for auth state changes
onAuthStateChanged(auth, async (user) => {
    if (user) {
        currentUser = user;
        console.log('User signed in:', user.email);
        // Load user data here
    } else {
        currentUser = null;
        console.log('User signed out');
    }
});
"""
            
        elif snippet_type == 'auth_functions':
            code = """// PART 2: AUTHENTICATION FUNCTIONS
// Add these functions to your JavaScript

// Google Sign-In (works on both web and native)
window.signInWithGoogle = async () => {
    try {
        // Check if running in Capacitor native app
        if (window.Capacitor && window.Capacitor.getPlatform() !== 'web') {
            // NATIVE: Use Capacitor plugin
            const { FirebaseAuthentication } = window.Capacitor.Plugins;
            
            if (!FirebaseAuthentication) {
                throw new Error('FirebaseAuthentication plugin not found');
            }
            
            const result = await FirebaseAuthentication.signInWithGoogle();
            const credential = GoogleAuthProvider.credential(result.credential?.idToken);
            await signInWithCredential(auth, credential);
            
            console.log('Native sign-in successful');
        } else {
            // WEB: Use popup
            const provider = new GoogleAuthProvider();
            await signInWithPopup(auth, provider);
            
            console.log('Web sign-in successful');
        }
    } catch (error) {
        console.error('Sign in error:', error);
        alert('Σφάλμα σύνδεσης: ' + error.message);
    }
};

// Sign Out
window.signOut = async () => {
    try {
        await firebaseSignOut(auth);
        console.log('Signed out successfully');
    } catch (error) {
        console.error('Sign out error:', error);
    }
};

// Get current user
window.getCurrentUser = () => {
    return currentUser;
};
"""
            
        elif snippet_type == 'data_sync':
            code = """// PART 3: DATA SYNC (OFFLINE-FIRST)
// Add these functions to handle data storage

// Save data (localStorage first, then cloud)
async function saveData(collectionName, docId, data) {
    const userId = currentUser?.uid || 'guest_local';
    
    // 1. Save to localStorage FIRST
    const storageKey = `app_${collectionName}_${userId}`;
    const allData = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    // Find and update or add new
    const index = allData.findIndex(item => item.id === docId);
    if (index >= 0) {
        allData[index] = { ...data, id: docId, updated_at: new Date().toISOString() };
    } else {
        allData.push({ ...data, id: docId, updated_at: new Date().toISOString() });
    }
    
    localStorage.setItem(storageKey, JSON.stringify(allData));
    console.log('Saved to localStorage');
    
    // 2. Sync to cloud if logged in
    if (currentUser && navigator.onLine) {
        try {
            await setDoc(doc(db, 'users', currentUser.uid, collectionName, docId), {
                ...data,
                updated_at: new Date().toISOString()
            });
            console.log('Synced to cloud');
        } catch (error) {
            console.error('Cloud sync error:', error);
        }
    }
}

// Load data (localStorage first, then sync with cloud)
async function loadData(collectionName) {
    const userId = currentUser?.uid || 'guest_local';
    const storageKey = `app_${collectionName}_${userId}`;
    
    // 1. Load from localStorage FIRST
    const localData = JSON.parse(localStorage.getItem(storageKey) || '[]');
    console.log('Loaded from localStorage:', localData.length, 'items');
    
    // 2. Sync with cloud if logged in
    if (currentUser && navigator.onLine) {
        try {
            const q = query(collection(db, 'users', currentUser.uid, collectionName));
            const snapshot = await getDocs(q);
            
            const cloudData = [];
            snapshot.forEach(doc => {
                cloudData.push({ ...doc.data(), id: doc.id });
            });
            
            console.log('Loaded from cloud:', cloudData.length, 'items');
            
            // Update localStorage with cloud data
            localStorage.setItem(storageKey, JSON.stringify(cloudData));
            return cloudData;
        } catch (error) {
            console.error('Cloud sync error:', error);
            return localData; // Return local data if cloud fails
        }
    }
    
    return localData;
}

// Delete data
async function deleteData(collectionName, docId) {
    const userId = currentUser?.uid || 'guest_local';
    const storageKey = `app_${collectionName}_${userId}`;
    
    // 1. Delete from localStorage
    const allData = JSON.parse(localStorage.getItem(storageKey) || '[]');
    const filtered = allData.filter(item => item.id !== docId);
    localStorage.setItem(storageKey, JSON.stringify(filtered));
    
    // 2. Delete from cloud
    if (currentUser && navigator.onLine) {
        try {
            await deleteDoc(doc(db, 'users', currentUser.uid, collectionName, docId));
            console.log('Deleted from cloud');
        } catch (error) {
            console.error('Cloud delete error:', error);
        }
    }
}

// Example usage:
// await saveData('readings', 'reading_123', { value: 120, date: '2025-01-01' });
// const data = await loadData('readings');
// await deleteData('readings', 'reading_123');
"""
            
        elif snippet_type == 'all':
            # Combine all snippets
            self.show_code_snippet('firebase_init')
            code = self.code_text.get(1.0, tk.END)
            self.show_code_snippet('auth_functions')
            code += "\n" + self.code_text.get(1.0, tk.END)
            self.show_code_snippet('data_sync')
            code += "\n" + self.code_text.get(1.0, tk.END)
            self.code_text.delete(1.0, tk.END)
        
        self.code_text.insert(1.0, code)
        self.code_text.config(state=tk.DISABLED)
        
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        
    def update_progress(self):
        completed = sum(1 for var in self.checklist_vars.values() if var.get())
        total = len(self.checklist_vars)
        percentage = (completed / total) * 100
        
        self.progress_label.config(text=f"Progress: {completed}/{total} completed")
        self.progress_bar['value'] = percentage
        
        if completed == total:
            messagebox.showinfo("Congratulations!", 
                              "You've completed all steps!\n\n"
                              "Your Firebase integration should now be working.\n\n"
                              "Next steps:\n"
                              "1. Build your APK\n"
                              "2. Test on an Android device\n"
                              "3. Verify Google Sign-In works\n"
                              "4. Test offline mode")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FirebaseSetupAssistant()
    app.run()