import React from 'react';
import { MessageBubble } from './MessageBubble';

export const ChatWindow = ({ messages, loading }) => {
  const endRef = React.useRef(null);

  React.useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 pb-24 bg-white">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full text-gray-500">
          <p className="text-center">Start a conversation by asking a question...</p>
        </div>
      )}
      
      {messages.map((msg, idx) => (
        <MessageBubble
          key={idx}
          text={msg.text}
          sender={msg.sender}
          sources={msg.sources}
        />
      ))}
      
      {loading && (
        <div className="flex justify-start mb-4">
          <div className="bg-soft-gray text-text-dark px-4 py-3 rounded-lg">
            <p className="text-sm animate-pulse">Thinking...</p>
          </div>
        </div>
      )}
      
      <div ref={endRef} />
    </div>
  );
};
