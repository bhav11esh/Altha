import React from 'react';
import { Brain } from 'lucide-react';

const AgentReasoningDisplay = ({ reasoning }) => {
  if (!reasoning || reasoning.length === 0) return null;

  const getAgentColor = (agentName) => {
    const colors = {
      'Diagnostic': 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-700',
      'Evidence': 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700',
      'Pharmacology': 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700',
      'Risk Assessment': 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700',
      'Treatment': 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700',
    };
    return colors[agentName] || 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700';
  };

  return (
    <div className="space-y-2 mt-2">
      {reasoning.map((agent, idx) => (
        <div
          key={idx}
          className={`border rounded p-3 ${getAgentColor(agent.agent_name)}`}
        >
          <div className="flex items-center gap-2 mb-1">
            <Brain size={16} />
            <h4 className="font-semibold text-sm">
              {agent.agent_name}
            </h4>
            {agent.confidence_score && (
              <span className="text-xs opacity-70">
                ({agent.confidence_score}% confidence)
              </span>
            )}
          </div>
          <p className="text-sm text-opacity-90">
            {agent.reasoning_text}
          </p>
        </div>
      ))}
    </div>
  );
};

export default AgentReasoningDisplay;
