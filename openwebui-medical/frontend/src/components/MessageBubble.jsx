import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import AgentReasoningDisplay from './AgentReasoningDisplay';

const MessageBubble = ({ message }) => {
  const [showReasoning, setShowReasoning] = useState(false);
  const isUser = message.role === 'user';

  const formatTime = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return '';
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-3`}>
      <div
        className={`max-w-xl ${
          isUser
            ? 'bg-blue-600 text-white rounded-lg rounded-tr-none'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg rounded-tl-none'
        } px-4 py-3`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </p>

        {!isUser && message.model_used && (
          <p className="text-xs opacity-70 mt-2">
            Model: {message.model_used}
          </p>
        )}

        <p className={`text-xs mt-2 ${isUser ? 'opacity-70' : 'opacity-60'}`}>
          {formatTime(message.created_at)}
        </p>
      </div>

      {/* Agent Reasoning Pills */}
      {!isUser && message.agent_reasoning && (
        <div className="flex-1">
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline mb-2"
          >
            {showReasoning ? '▼' : '▶'} Agent Reasoning
          </button>

          {showReasoning && (
            <AgentReasoningDisplay reasoning={message.agent_reasoning} />
          )}
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
