import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const ModelSelector = ({ selectedModel, onModelChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const models = [
    { id: 'mistral', name: 'Mistral 7B', description: 'Fast, accurate' },
    { id: 'llama', name: 'Llama 2 70B', description: 'Powerful, context-aware' },
    { id: 'gpt-4o', name: 'GPT-4 Omni', description: 'State-of-the-art' },
  ];

  const selectedModelObj = models.find((m) => m.id === selectedModel);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
      >
        <span className="text-sm font-medium">
          {selectedModelObj?.name || 'Select Model'}
        </span>
        <ChevronDown size={16} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg z-50">
          <div className="p-2">
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  onModelChange(model.id);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-4 py-3 rounded-lg transition ${
                  selectedModel === model.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
              >
                <div className="font-medium text-sm">{model.name}</div>
                <div className="text-xs opacity-70">{model.description}</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
