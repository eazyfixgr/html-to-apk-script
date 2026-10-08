// src/firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// ΑΝΤΙΚΑΤΕΣΤΗΣΕ με το δικό σου firebaseConfig από το Firebase Console
const firebaseConfig = {

  apiKey: "AIzaSyDCY5-6jbKsMAUDg6w2lgEdejJnn5Z8LBk",

  authDomain: "collabhub-bbdcf.firebaseapp.com",

  projectId: "collabhub-bbdcf",

  storageBucket: "collabhub-bbdcf.firebasestorage.app",

  messagingSenderId: "441831307347",

  appId: "1:441831307347:web:568fa68bf305866c0eeea6"

};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app;