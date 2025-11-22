import React from 'react';

export const MessageBubble = ({ text, sender, sources = [] }) => {
  const isUser = sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-lg shadow-sm ${
          isUser
            ? 'bg-accent-blue text-white rounded-br-none'
            : 'bg-soft-gray text-text-dark rounded-bl-none border border-gray-200'
        }`}
      >
        <p className="text-sm leading-relaxed">{text}</p>
        
        {/* Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 text-xs">
            <p className="font-semibold mb-2">Sources:</p>
            {sources.map((source, idx) => (
              <div key={idx} className="mb-1">
                <p className="font-medium">{source.fund_name}</p>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent-blue hover:underline break-all"
                >
                  {source.type.replace('_', ' ')}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
