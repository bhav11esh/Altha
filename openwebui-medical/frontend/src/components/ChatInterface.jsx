import React, { useState, useEffect, useRef } from 'react';
import { Send, Upload, AlertCircle } from 'lucide-react';
import MessageBubble from './MessageBubble';
import PHIDetectionModal from './PHIDetectionModal';
import ContextDisplay from './ContextDisplay';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ChatInterface = ({ conversationId, model, onConversationUpdate }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [phi, setPhi] = useState(null);
  const [showPHIModal, setShowPHIModal] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const [context, setContext] = useState([]);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (conversationId) {
      fetchConversation();
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversation = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/conversations/${conversationId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
      setError('Failed to load conversation');
    }
  };

  const detectPHI = async (text) => {
    try {
      const response = await axios.post(
        `${API_BASE}/phi/detect`,
        { text }
      );
      return response.data;
    } catch (error) {
      console.error('PHI detection failed:', error);
      return null;
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Check for PHI
    const phiDetection = await detectPHI(inputValue);

    if (phiDetection?.has_phi) {
      setPhi(phiDetection);
      setShowPHIModal(true);
      return;
    }

    // Send message
    await sendMessage();
  };

  const sendMessage = async (shouldAnonymize = false) => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${API_BASE}/chat`,
        {
          content: inputValue,
          role: 'user',
          model,
          conversation_id: conversationId,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Add user message to conversation
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: inputValue,
        created_at: new Date().toISOString(),
      };

      setMessages([...messages, userMessage, response.data]);
      setInputValue('');
      setShowPHIModal(false);
      setPhi(null);

      // Fetch updated conversation
      if (conversationId) {
        fetchConversation();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }

    try {
      const response = await axios.post(
        `${API_BASE}/files/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      const fileRef = `[File uploaded: ${file.name}]`;
      setInputValue((prev) => (prev ? `${prev}\n${fileRef}` : fileRef));
    } catch (error) {
      setError('Failed to upload file');
    }
  };

  const fetchContext = async () => {
    if (!conversationId) return;

    try {
      const response = await axios.get(
        `${API_BASE}/conversations/${conversationId}/context`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setContext(response.data.context);
      setShowContext(true);
    } catch (error) {
      console.error('Failed to fetch context:', error);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* PHI Detection Modal */}
      {showPHIModal && phi && (
        <PHIDetectionModal
          phi={phi}
          onAnonymize={() => {
            // Set to anonymize flag
            sendMessage(true);
          }}
          onContinue={() => {
            sendMessage(false);
          }}
          onCancel={() => {
            setShowPHIModal(false);
            setPhi(null);
          }}
        />
      )}

      {/* Error Banner */}
      {error && (
        <div className="bg-red-100 dark:bg-red-900 border-b border-red-400 dark:border-red-700 p-4 flex items-center gap-2">
          <AlertCircle size={20} className="text-red-600 dark:text-red-400" />
          <span className="text-red-700 dark:text-red-200">{error}</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Welcome to Medical AI
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                HIPAA-compliant healthcare assistant
              </p>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <p>✓ Detects and protects patient data (PHI)</p>
                <p>✓ Multi-agent medical reasoning</p>
                <p>✓ Comprehensive audit logging</p>
                <p>✓ Secure encrypted storage</p>
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Context Toggle */}
      {conversationId && messages.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-800">
          <button
            onClick={fetchContext}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
          >
            {showContext ? '← Hide' : 'Show'} previous context
          </button>
          {showContext && context.length > 0 && (
            <ContextDisplay context={context} />
          )}
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4">
        <div className="flex gap-2">
          <label className="flex items-center gap-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer transition">
            <Upload size={20} />
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".pdf,.jpg,.jpeg,.png,.csv"
              className="hidden"
            />
          </label>

          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !loading) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask a medical question... (Shift+Enter for new line)"
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            disabled={loading}
          />

          <button
            onClick={handleSendMessage}
            disabled={loading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-700 text-white rounded-lg transition flex items-center gap-2"
          >
            <Send size={20} />
            {loading ? 'Sending...' : ''}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
