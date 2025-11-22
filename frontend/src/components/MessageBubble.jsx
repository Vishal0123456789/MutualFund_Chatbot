import React from 'react';

export const MessageBubble = ({ text, sender, sources = [] }) => {
  const isUser = sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div style={{
          background: '#2B6CB0',
          color: '#FFFFFF',
          padding: '16px',
          borderRadius: '20px',
          maxWidth: '70%',
          fontSize: '14px',
          lineHeight: '1.6',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
        }}>
          {text}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      {/* Bot Avatar */}
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

      {/* Message Content */}
      <div className="flex-1">
        <div style={{
          background: '#FFFFFF',
          padding: '16px',
          borderRadius: '12px',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
          maxWidth: '70%',
          fontSize: '14px',
          lineHeight: '1.6',
          color: '#1F2937',
          whiteSpace: 'pre-wrap'
        }}>
          {text}
        </div>
        
        {/* Sources */}
        {sources && sources.length > 0 && (
          <div style={{
            marginTop: '12px',
            marginLeft: '0',
            fontSize: '12px',
            color: '#6B7280'
          }}>
            <strong>Sources:</strong>
            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#2B6CB0',
                    textDecoration: 'none'
                  }}
                  className="hover:underline"
                >
                  {source.fund_name} ({source.type.replace('_', ' ')})
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
