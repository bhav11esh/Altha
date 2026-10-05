import React, { useState, useEffect } from 'react';
import { Menu, LogOut, Home } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import ModelSelector from './components/ModelSelector';
import AuditLogViewer from './components/AuditLogViewer';
import './index.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [selectedModel, setSelectedModel] = useState('mistral');
  const [showAuditLog, setShowAuditLog] = useState(false);
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setUser({ email });
      setIsAuthenticated(true);
      fetchConversations(data.access_token);
    } catch (error) {
      setLoginError(error.message);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoginError('');

    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      // Auto-login after registration
      handleLogin(e);
    } catch (error) {
      setLoginError(error.message);
    }
  };

  const fetchConversations = async (token) => {
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
    setConversations([]);
    setCurrentConversation(null);
  };

  const handleNewConversation = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: 'New Conversation',
          model: selectedModel,
        }),
      });
      const newConv = await response.json();
      setConversations([newConv, ...conversations]);
      setCurrentConversation(newConv);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Medical AI
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            HIPAA-compliant healthcare assistant powered by CrewAI
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
                required
              />
            </div>

            {loginError && (
              <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-2 rounded">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Login
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-300 dark:border-gray-600">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Don't have an account?
            </p>
            <button
              onClick={(e) => {
                setLoginError('');
                handleRegister(e);
              }}
              className="w-full bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Create Account
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Medical AI
              </h2>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              <Menu size={20} className="text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <button
            onClick={handleNewConversation}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition text-sm"
          >
            {sidebarOpen ? '+ New Chat' : '+'}
          </button>

          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 px-2 mt-4">
            {sidebarOpen ? 'CONVERSATIONS' : ''}
          </div>

          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => setCurrentConversation(conv)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                currentConversation?.id === conv.id
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
              title={conv.title}
            >
              {sidebarOpen ? (
                <div className="truncate">{conv.title}</div>
              ) : (
                <div className="w-2 h-2 bg-current rounded-full"></div>
              )}
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
          <button
            onClick={() => setShowAuditLog(!showAuditLog)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            {sidebarOpen ? 'Audit Log' : '📋'}
          </button>

          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            {sidebarOpen ? (theme === 'dark' ? '☀️ Light' : '🌙 Dark') : '🌙'}
          </button>

          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition flex items-center gap-2"
          >
            <LogOut size={16} />
            {sidebarOpen && 'Logout'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Home size={24} className="text-gray-600 dark:text-gray-400" />
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              {currentConversation ? currentConversation.title : 'New Conversation'}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />

            {user && (
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {user.email}
              </span>
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          {showAuditLog ? (
            <AuditLogViewer />
          ) : (
            <ChatInterface
              conversationId={currentConversation?.id}
              model={selectedModel}
              onConversationUpdate={(updatedConv) => {
                setCurrentConversation(updatedConv);
                setConversations(
                  conversations.map((c) =>
                    c.id === updatedConv.id ? updatedConv : c
                  )
                );
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
