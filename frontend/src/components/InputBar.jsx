import React from 'react';

export const InputBar = ({ onSend, disabled = false }) => {
  const [input, setInput] = React.useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      background: '#FFFFFF',
      padding: '16px 24px',
      borderTop: '1px solid #E5E7EB',
      display: 'flex',
      gap: '12px',
      alignItems: 'flex-end'
    }}>
      <div style={{
        flex: 1,
        display: 'flex',
        gap: '8px',
        alignItems: 'center',
        background: '#F6F8FA',
        border: '1px solid #E5E7EB',
        borderRadius: '24px',
        padding: '0 16px',
        transition: 'all 0.2s ease'
      }}
      className="input-wrapper"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about NAV, Returns, or Managers..."
          disabled={disabled}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            fontSize: '14px',
            padding: '12px 0',
            fontFamily: 'Inter, Roboto, sans-serif',
            color: '#1F2937'
          }}
        />
      </div>
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        style={{
          minWidth: '80px',
          height: '40px',
          background: disabled || !input.trim() ? '#9CA3AF' : 'linear-gradient(135deg, #2B6CB0 0%, #12346A 100%)',
          border: 'none',
          borderRadius: '20px',
          color: '#FFFFFF',
          fontSize: '14px',
          fontWeight: '600',
          cursor: disabled || !input.trim() ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          padding: '0 16px',
          flexShrink: 0
        }}
        className="send-btn"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Send
      </button>
    </div>
  );
};
