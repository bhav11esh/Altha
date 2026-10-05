import React from 'react';
import { formatDistanceToNow } from 'date-fns';

const ContextDisplay = ({ context }) => {
  if (!context || context.length === 0) {
    return (
      <div className="text-sm text-gray-600 dark:text-gray-400 p-2">
        No context available
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      {context.map((msg, idx) => (
        <div
          key={idx}
          className={`p-3 rounded text-sm ${
            msg.role === 'user'
              ? 'bg-blue-50 dark:bg-blue-900 border-l-4 border-blue-500'
              : 'bg-gray-50 dark:bg-gray-800 border-l-4 border-gray-500'
          }`}
        >
          <p className="font-semibold text-xs opacity-70">
            {msg.role.toUpperCase()} •{' '}
            {formatDistanceToNow(new Date(msg.created_at), {
              addSuffix: true,
            })}
          </p>
          <p className="mt-1 text-gray-800 dark:text-gray-200">
            {msg.content.substring(0, 200)}
            {msg.content.length > 200 ? '...' : ''}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ContextDisplay;
