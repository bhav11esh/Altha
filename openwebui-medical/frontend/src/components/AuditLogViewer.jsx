import React, { useState, useEffect } from 'react';
import { ChevronDown, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AuditLogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [expandedLogId, setExpandedLogId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/audit-logs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLogs(response.data);
    } catch (err) {
      setError('Failed to load audit logs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    const colors = {
      message_sent: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
      phi_detected: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300',
      anonymized: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300',
      model_changed: 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300',
    };
    return colors[action] || 'bg-gray-100 dark:bg-gray-900 text-gray-700 dark:text-gray-300';
  };

  const getActionIcon = (action) => {
    const icons = {
      message_sent: '💬',
      phi_detected: '⚠️',
      anonymized: '🔒',
      model_changed: '🤖',
    };
    return icons[action] || '📋';
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Clock size={28} className="text-blue-600" />
          Audit Log
        </h2>
        <button
          onClick={fetchAuditLogs}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-2">
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <p className="text-gray-600 dark:text-gray-400 mb-2">
                No audit log entries yet
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Your actions will appear here
              </p>
            </div>
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden"
            >
              <button
                onClick={() =>
                  setExpandedLogId(
                    expandedLogId === log.id ? null : log.id
                  )
                }
                className={`w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition ${getActionColor(
                  log.action
                )}`}
              >
                <div className="flex items-center gap-3 text-left">
                  <span className="text-xl">
                    {getActionIcon(log.action)}
                  </span>
                  <div>
                    <p className="font-semibold text-sm capitalize">
                      {log.action.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs opacity-70">
                      {formatDistanceToNow(new Date(log.timestamp), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>

                <ChevronDown
                  size={20}
                  className={`transition-transform ${
                    expandedLogId === log.id ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {expandedLogId === log.id && (
                <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                        Timestamp
                      </p>
                      <p className="text-sm text-gray-900 dark:text-white">
                        {new Date(log.timestamp).toLocaleString()}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                        Details
                      </p>
                      <pre className="text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-200 overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AuditLogViewer;
