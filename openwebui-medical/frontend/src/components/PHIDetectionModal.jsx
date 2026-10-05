import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const PHIDetectionModal = ({ phi, onAnonymize, onContinue, onCancel }) => {
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    generatePreview();
  }, []);

  const generatePreview = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/phi/preview`, {
        params: { text: phi.text },
      });
      setPreview(response.data.anonymized);
    } catch (error) {
      console.error('Failed to generate preview:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPhi = (phi.phi.names?.length || 0) +
    (phi.phi.ids?.length || 0) +
    (phi.phi.emails?.length || 0) +
    (phi.phi.phones?.length || 0) +
    (phi.phi.medical_records?.length || 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle size={24} className="text-yellow-600 dark:text-yellow-400" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Protected Health Information Detected
            </h2>
          </div>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            <X size={20} className="text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* PHI Summary */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
              Found {totalPhi} item(s) of PHI:
            </h3>

            <div className="grid grid-cols-2 gap-3">
              {phi.phi.names?.length > 0 && (
                <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded p-3">
                  <p className="text-xs font-semibold text-red-700 dark:text-red-300">
                    PATIENT NAMES ({phi.phi.names.length})
                  </p>
                  <ul className="text-sm text-red-600 dark:text-red-400 mt-1 space-y-1">
                    {phi.phi.names.map((name, idx) => (
                      <li key={idx} className="truncate">
                        • {name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {phi.phi.emails?.length > 0 && (
                <div className="bg-orange-50 dark:bg-orange-900 border border-orange-200 dark:border-orange-800 rounded p-3">
                  <p className="text-xs font-semibold text-orange-700 dark:text-orange-300">
                    EMAILS ({phi.phi.emails.length})
                  </p>
                  <ul className="text-sm text-orange-600 dark:text-orange-400 mt-1 space-y-1">
                    {phi.phi.emails.map((email, idx) => (
                      <li key={idx} className="truncate">
                        • {email}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {phi.phi.ids?.length > 0 && (
                <div className="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-800 rounded p-3">
                  <p className="text-xs font-semibold text-yellow-700 dark:text-yellow-300">
                    IDS ({phi.phi.ids.length})
                  </p>
                  <ul className="text-sm text-yellow-600 dark:text-yellow-400 mt-1 space-y-1">
                    {phi.phi.ids.map((id, idx) => (
                      <li key={idx} className="truncate">
                        • {id}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {phi.phi.phones?.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-800 rounded p-3">
                  <p className="text-xs font-semibold text-green-700 dark:text-green-300">
                    PHONES ({phi.phi.phones.length})
                  </p>
                  <ul className="text-sm text-green-600 dark:text-green-400 mt-1 space-y-1">
                    {phi.phi.phones.map((phone, idx) => (
                      <li key={idx} className="truncate">
                        • {phone}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Preview */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              Anonymized Preview:
            </h3>
            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                {loading ? 'Generating preview...' : preview}
              </p>
            </div>
          </div>

          {/* Warning */}
          <div className="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-800 rounded p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>HIPAA Notice:</strong> All protected health information will be
              encrypted and stored securely. You can choose to anonymize this data before
              submission.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="sticky bottom-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 p-6 flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition font-medium"
          >
            Cancel
          </button>

          <button
            onClick={onAnonymize}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition font-medium"
          >
            Anonymize & Submit
          </button>

          <button
            onClick={onContinue}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium"
          >
            Continue Without Anonymizing
          </button>
        </div>
      </div>
    </div>
  );
};

export default PHIDetectionModal;
