import React from 'react';

export const Sidebar = ({ onExampleQuestion, isOpen, onClose }) => {
  const examples = [
    "What is the expense ratio of UTI ELSS Tax Saver Fund?",
    "What is the P/E ratio of UTI India Consumer Fund Direct Growth?",
    "Who is the fund manager of UTI MNC Fund Direct Growth?",
    "What is NAV of UTI Large & Mid Cap Fund Direct Growth?",
    "Exit Load of UTI Infrastructure Fund Direct Growth?"
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-80 md:w-80 bg-white border-r border-gray-200 
          transform transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          flex flex-col overflow-y-auto
        `}
        style={{
          padding: '24px',
          gap: '24px'
        }}
      >
        {/* Close button for mobile only */}
        <div className="md:hidden" style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10 }}>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#6B7280',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ×
          </button>
        </div>

        {/* Sidebar Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{
            width: '40px',
            height: '40px',
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
          <h1 style={{ fontSize: '18px', fontWeight: '600', color: '#12346A' }}>
            Mutual Fund Assistant
          </h1>
        </div>

        {/* Welcome Message */}
        <div style={{
          background: '#F6F8FA',
          padding: '16px',
          borderRadius: '12px',
          fontSize: '14px',
          lineHeight: '1.5',
          color: '#1F2937'
        }}>
          Hello! I'm your UTI Factual Assistant. Ask me anything about UTI AMC schemes.
        </div>

        {/* Suggestions Section */}
        <div>
          <p style={{
            fontSize: '12px',
            fontWeight: '600',
            textTransform: 'uppercase',
            color: '#6B7280',
            marginBottom: '12px'
          }}>
            Suggested Questions
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {examples.map((example, idx) => (
              <button
                key={idx}
                onClick={() => onExampleQuestion(example)}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  padding: '12px',
                  background: '#F6F8FA',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  fontSize: '13px',
                  lineHeight: '1.4',
                  color: '#1F2937',
                  textAlign: 'left'
                }}
                className="suggestion-btn"
              >
                <span style={{ color: '#EAAA08', marginTop: '2px' }}>❔</span>
                <span>{example}</span>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};
