import React from 'react';
import { MessageBubble } from './MessageBubble';

export const ChatWindow = ({ messages, loading }) => {
  const endRef = React.useRef(null);

  React.useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto" style={{
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      backgroundColor: '#F6F8FA'
    }}>
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full" style={{ color: '#6B7280' }}>
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
        <div className="flex items-start gap-3">
          <div style={{
            width: '40px',
            height: '40px',
            minWidth: '40px',
            background: 'linear-gradient(135deg, #2B6CB0 0%, #12346A 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontSize: '20px'
          }}>
            🤖
          </div>
          <div style={{
            background: '#FFFFFF',
            padding: '12px 16px',
            borderRadius: '12px',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
            display: 'flex',
            gap: '4px'
          }}>
            <div className="typing-dot" />
            <div className="typing-dot" style={{ animationDelay: '0.2s' }} />
            <div className="typing-dot" style={{ animationDelay: '0.4s' }} />
          </div>
        </div>
      )}
      
      <div ref={endRef} />
    </div>
  );
};
