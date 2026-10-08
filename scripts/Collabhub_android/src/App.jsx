// src/App.jsx
import React, { useState, useEffect } from 'react';
import { auth, db, storage } from './firebase';
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail
} from 'firebase/auth';
import {
  collection,
  addDoc,
  doc,
  setDoc,
  getDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  query,
  where,
  onSnapshot,
  orderBy,
  serverTimestamp,
  arrayUnion,
  arrayRemove
} from 'firebase/firestore';
import {
  ref,
  uploadBytes,
  getDownloadURL,
  deleteObject
} from 'firebase/storage';
import { 
  Menu, X, Send, Paperclip, FileImage, Plus, Search, 
  MoreVertical, Pin, Calendar, StickyNote, LayoutDashboard,
  Download, Settings, Users, MessageSquare, Moon, Sun, 
  LogOut, Trash2, Shield
} from 'lucide-react';

const translations = {
  en: {
    appName: 'CollabHub',
    login: 'Login',
    register: 'Register',
    username: 'Username',
    password: 'Password',
    displayName: 'Display Name',
    forgotPassword: 'Forgot Password?',
    createAccount: 'Create Account',
    chatrooms: 'Chatrooms',
    friends: 'Friends',
    settings: 'Settings',
    logout: 'Logout',
    createChatroom: 'Create Chatroom',
    chatroomName: 'Chatroom Name',
    privateRoom: 'Private',
    publicRoom: 'Public',
    sendMessage: 'Type a message...',
    checklist: 'Tasks',
    gallery: 'Gallery',
    overview: 'Overview',
    addTask: 'Add Task',
    taskName: 'Task Name',
    taskDescription: 'Description',
    quickNotes: 'Quick Notes',
    online: 'Online',
    offline: 'Offline',
    darkMode: 'Dark Mode',
    language: 'Language',
    storageUsed: 'Storage Used',
    admin: 'Admin',
    members: 'members'
  },
  el: {
    appName: 'CollabHub',
    login: 'Σύνδεση',
    register: 'Εγγραφή',
    username: 'Όνομα Χρήστη',
    password: 'Κωδικός',
    displayName: 'Εμφανιζόμενο Όνομα',
    forgotPassword: 'Ξέχασα τον κωδικό;',
    createAccount: 'Δημιουργία Λογαριασμού',
    chatrooms: 'Δωμάτια',
    friends: 'Φίλοι',
    settings: 'Ρυθμίσεις',
    logout: 'Αποσύνδεση',
    createChatroom: 'Νέο Δωμάτιο',
    chatroomName: 'Όνομα',
    privateRoom: 'Ιδιωτικό',
    publicRoom: 'Δημόσιο',
    sendMessage: 'Μήνυμα...',
    checklist: 'Εργασίες',
    gallery: 'Εικόνες',
    overview: 'Επισκόπηση',
    addTask: 'Νέα Εργασία',
    taskName: 'Όνομα',
    taskDescription: 'Περιγραφή',
    quickNotes: 'Σημειώσεις',
    online: 'Ενεργός',
    offline: 'Ανενεργός',
    darkMode: 'Σκούρο Θέμα',
    language: 'Γλώσσα',
    storageUsed: 'Αποθήκευση',
    admin: 'Διαχείριση',
    members: 'μέλη'
  }
};

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [chatrooms, setChatrooms] = useState([]);
  const [selectedChatroom, setSelectedChatroom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [chatTab, setChatTab] = useState(0);
  const [quickNote, setQuickNote] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Dialogs
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [showAddTask, setShowAddTask] = useState(false);
  
  // Form states
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerDisplayName, setRegisterDisplayName] = useState('');
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomPrivate, setNewRoomPrivate] = useState(true);
  const [taskName, setTaskName] = useState('');
  const [taskDescription, setTaskDescription] = useState('');

  const t = translations[language];

  // Auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setCurrentUser(user);
        // Load user profile
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        if (userDoc.exists()) {
          setUserProfile(userDoc.data());
          setCurrentView('overview');
        }
      } else {
        setCurrentUser(null);
        setUserProfile(null);
        setCurrentView('login');
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Load chatrooms
  useEffect(() => {
    if (!currentUser) return;

    const q = query(
      collection(db, 'chatrooms'),
      where('members', 'array-contains', currentUser.uid)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const rooms = [];
      snapshot.forEach((doc) => {
        rooms.push({ id: doc.id, ...doc.data() });
      });
      setChatrooms(rooms);
    });

    return () => unsubscribe();
  }, [currentUser]);

  // Load messages for selected chatroom
  useEffect(() => {
    if (!selectedChatroom) return;

    const q = query(
      collection(db, 'chatrooms', selectedChatroom.id, 'messages'),
      orderBy('timestamp', 'asc')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const msgs = [];
      snapshot.forEach((doc) => {
        msgs.push({ id: doc.id, ...doc.data() });
      });
      setMessages(msgs);
    });

    return () => unsubscribe();
  }, [selectedChatroom]);

  // Load tasks for selected chatroom
  useEffect(() => {
    if (!selectedChatroom) return;

    const unsubscribe = onSnapshot(
      collection(db, 'chatrooms', selectedChatroom.id, 'tasks'),
      (snapshot) => {
        const taskList = [];
        snapshot.forEach((doc) => {
          taskList.push({ id: doc.id, ...doc.data() });
        });
        setTasks(taskList);
      }
    );

    return () => unsubscribe();
  }, [selectedChatroom]);

  // Check for new messages every 30 seconds
  useEffect(() => {
    if (currentUser) {
      const interval = setInterval(() => {
        console.log('Checking for updates...');
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [currentUser]);

  const showAlert = (msg) => {
    setNotificationMessage(msg);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  // Register handler
  const handleRegister = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        registerEmail,
        registerPassword
      );
      
      // Create user profile in Firestore
      await setDoc(doc(db, 'users', userCredential.user.uid), {
        displayName: registerDisplayName,
        email: registerEmail,
        isAdmin: false,
        storageUsed: 0,
        storageLimit: 100 * 1024 * 1024, // 100MB
        online: true,
        createdAt: serverTimestamp()
      });

      showAlert('Account created successfully!');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Login handler
  const handleLogin = async () => {
    try {
      await signInWithEmailAndPassword(auth, loginEmail, loginPassword);
      
      // Update online status
      await updateDoc(doc(db, 'users', auth.currentUser.uid), {
        online: true
      });
      
      showAlert('Logged in successfully!');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Logout handler
  const handleLogout = async () => {
    try {
      await updateDoc(doc(db, 'users', currentUser.uid), {
        online: false
      });
      await signOut(auth);
      showAlert('Logged out successfully!');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Create chatroom
  const handleCreateChatroom = async () => {
    try {
      const chatroomData = {
        name: newRoomName || 'New Project',
        isPrivate: newRoomPrivate,
        members: [currentUser.uid],
        createdBy: currentUser.uid,
        createdAt: serverTimestamp()
      };

      await addDoc(collection(db, 'chatrooms'), chatroomData);
      setNewRoomName('');
      setShowCreateRoom(false);
      showAlert('Chatroom created!');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Send message
  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedChatroom) return;

    try {
      await addDoc(collection(db, 'chatrooms', selectedChatroom.id, 'messages'), {
        text: messageInput,
        sender: userProfile.displayName,
        senderId: currentUser.uid,
        timestamp: serverTimestamp(),
        pinned: false
      });

      setMessageInput('');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Add task
  const handleAddTask = async () => {
    if (!taskName.trim() || !selectedChatroom) return;

    try {
      await addDoc(collection(db, 'chatrooms', selectedChatroom.id, 'tasks'), {
        name: taskName,
        description: taskDescription,
        completed: false,
        createdBy: currentUser.uid,
        createdAt: serverTimestamp()
      });

      setTaskName('');
      setTaskDescription('');
      setShowAddTask(false);
      showAlert('Task added!');
    } catch (error) {
      showAlert(error.message);
    }
  };

  // Toggle task completion
  const handleToggleTask = async (taskId, currentStatus) => {
    try {
      await updateDoc(
        doc(db, 'chatrooms', selectedChatroom.id, 'tasks', taskId),
        { completed: !currentStatus }
      );
    } catch (error) {
      showAlert(error.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  // Login/Register Screen
  const LoginRegister = () => {
    const [isLogin, setIsLogin] = useState(true);

    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className={`w-full max-w-md p-8 rounded-lg shadow-xl ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <h1 className={`text-3xl font-bold text-center mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {t.appName}
          </h1>
          <h2 className={`text-xl text-center mb-6 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {isLogin ? t.login : t.register}
          </h2>
          
          <div className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={isLogin ? loginEmail : registerEmail}
              onChange={(e) => isLogin ? setLoginEmail(e.target.value) : setRegisterEmail(e.target.value)}
              className={`w-full px-4 py-3 rounded-lg border ${
                darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            
            {!isLogin && (
              <input
                type="text"
                placeholder={t.displayName}
                value={registerDisplayName}
                onChange={(e) => setRegisterDisplayName(e.target.value)}
                className={`w-full px-4 py-3 rounded-lg border ${
                  darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
            )}
            
            <input
              type="password"
              placeholder={t.password}
              value={isLogin ? loginPassword : registerPassword}
              onChange={(e) => isLogin ? setLoginPassword(e.target.value) : setRegisterPassword(e.target.value)}
              className={`w-full px-4 py-3 rounded-lg border ${
                darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            
            <button
              onClick={isLogin ? handleLogin : handleRegister}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-semibold transition"
            >
              {isLogin ? t.login : t.createAccount}
            </button>
            
            <button
              onClick={() => setIsLogin(!isLogin)}
              className={`w-full text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} hover:underline`}
            >
              {isLogin ? t.createAccount : t.login}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Sidebar
  const Sidebar = () => (
    <div className={`fixed inset-0 z-50 ${drawerOpen ? 'block' : 'hidden'}`}>
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setDrawerOpen(false)} />
      <div className={`absolute left-0 top-0 bottom-0 w-80 ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-xl`}>
        <div className={`p-6 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {userProfile?.displayName}
          </h3>
          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            {currentUser?.email}
          </p>
        </div>
        
        <div className="p-4 space-y-2">
          {[
            { icon: LayoutDashboard, label: t.overview, view: 'overview' },
            { icon: MessageSquare, label: t.chatrooms, view: 'chatrooms' },
            { icon: Settings, label: t.settings, view: 'settings' },
          ].map((item) => (
            <button
              key={item.view}
              onClick={() => {
                setCurrentView(item.view);
                setDrawerOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                currentView === item.view
                  ? 'bg-purple-600 text-white'
                  : darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
        
        <div className={`absolute bottom-0 left-0 right-0 p-4 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <button
            onClick={handleLogout}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
              darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <LogOut size={20} />
            <span>{t.logout}</span>
          </button>
        </div>
      </div>
    </div>
  );

  // Overview
  const OverviewView = () => (
    <div className="p-6">
      <h2 className={`text-3xl font-bold mb-6 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
        {t.overview}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={`p-6 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-lg`}>
          <h3 className={`text-sm font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Active Projects
          </h3>
          <p className="text-3xl font-bold mt-2 text-purple-600">{chatrooms.length}</p>
        </div>
      </div>
    </div>
  );

  // Chatrooms List
  const ChatroomsView = () => (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          {t.chatrooms}
        </h2>
        <button
          onClick={() => setShowCreateRoom(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          {t.createChatroom}
        </button>
      </div>
      
      {chatrooms.map((room) => (
        <button
          key={room.id}
          onClick={() => {
            setSelectedChatroom(room);
            setCurrentView('chat');
          }}
          className={`w-full p-4 mb-3 rounded-lg shadow ${
            darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-gray-50'
          }`}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              {room.name[0]}
            </div>
            <div className="flex-1 text-left">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                {room.name}
              </h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {room.members?.length || 0} {t.members}
              </p>
            </div>
          </div>
        </button>
      ))}

      {showCreateRoom && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className={`w-full max-w-md p-6 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className={`text-xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {t.createChatroom}
            </h3>
            <input
              type="text"
              placeholder={t.chatroomName}
              value={newRoomName}
              onChange={(e) => setNewRoomName(e.target.value)}
              className={`w-full px-4 py-2 mb-4 rounded-lg border ${
                darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
              }`}
            />
            <div className="flex gap-2">
              <button
                onClick={() => setShowCreateRoom(false)}
                className={`flex-1 px-4 py-2 rounded-lg ${
                  darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                }`}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateChatroom}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Chat View
  const ChatView = () => (
    <div className="flex flex-col h-screen">
      <div className={`flex items-center justify-between p-4 border-b ${
        darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
      }`}>
        <div className="flex items-center gap-3">
          <button onClick={() => setCurrentView('chatrooms')}>
            <X size={24} />
          </button>
          <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {selectedChatroom?.name}
          </h2>
        </div>
      </div>

      <div className={`flex border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        {['Chat', t.checklist].map((tab, idx) => (
          <button
            key={idx}
            onClick={() => setChatTab(idx)}
            className={`flex-1 py-3 font-medium ${
              chatTab === idx ? 'border-b-2 border-purple-600 text-purple-600' : ''
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className={`flex-1 overflow-y-auto p-4 ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        {chatTab === 0 && (
          <div className="space-y-3">
            {messages.map((msg) => (
              <div key={msg.id} className="flex justify-start">
                <div className={`max-w-md px-4 py-2 rounded-lg ${
                  darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
                }`}>
                  <span className="text-xs font-bold">{msg.sender}</span>
                  <p>{msg.text}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {chatTab === 1 && (
          <div>
            <button
              onClick={() => setShowAddTask(true)}
              className="w-full mb-4 px-4 py-3 border-2 border-dashed border-purple-600 text-purple-600 rounded-lg"
            >
              <Plus className="inline mr-2" size={20} />
              {t.addTask}
            </button>
            {tasks.map((task) => (
              <div key={task.id} className={`p-4 mb-2 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggleTask(task.id, task.completed)}
                    className="mt-1 w-5 h-5"
                  />
                  <div>
                    <p className={`font-medium ${task.completed ? 'line-through' : ''}`}>
                      {task.name}
                    </p>
                    {task.description && <p className="text-sm text-gray-600">{task.description}</p>}
                  </div>
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      {chatTab === 0 && (
        <div className={`p-4 border-t ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={t.sendMessage}
              className={`flex-1 px-4 py-2 rounded-lg ${
                darkMode ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-900'
              }`}
            />
            <button
              onClick={handleSendMessage}
              className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded-lg"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      )}

      {showAddTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className={`w-full max-w-md p-6 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className={`text-xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {t.addTask}
            </h3>
            <input
              type="text"
              placeholder={t.taskName}
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              className={`w-full px-4 py-2 mb-3 rounded-lg border ${
                darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
              }`}
            />
            <textarea
              placeholder={t.taskDescription}
              rows="3"
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              className={`w-full px-4 py-2 mb-4 rounded-lg border ${
                darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
              }`}
            />
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddTask(false)}
                className={`flex-1 px-4 py-2 rounded-lg ${
                  darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                }`}
              >
                Cancel
              </button>
              <button
                onClick={handleAddTask}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (!currentUser) {
    return <LoginRegister />;
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {currentView !== 'chat' && (
        <div className={`sticky top-0 z-40 ${darkMode ? 'bg-gray-800' : 'bg-purple-600'} shadow-lg`}>
          <div className="flex items-center justify-between px-4 py-3">
            <button onClick={() => setDrawerOpen(true)} className="text-white">
              <Menu size={24} />
            </button>
            <h1 className="text-xl font-bold text-white">{t.appName}</h1>
            <div className="w-6" />
          </div>
        </div>
      )}

      <Sidebar />

      {currentView === 'overview' && <OverviewView />}
      {currentView === 'chatrooms' && <ChatroomsView />}
      {currentView === 'chat' && <ChatView />}

      {showNotification && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          {notificationMessage}
        </div>
      )}
    </div>
  );
}