import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatWindow } from './components/ChatWindow';
import { InputBar } from './components/InputBar';

// Get API URL from environment variable or default to localhost for testing
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function App() {
  const [messages, setMessages] = useState([
    {
      text: "**Welcome!** I'm your UTI Mutual Fund Assistant.\n\nI can help you with factual information about UTI funds including NAV, expense ratios, P/E ratios, fund managers, and more. What would you like to know?",
      sender: 'bot',
      sources: []
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Auto-open sidebar on first mobile visit
  useEffect(() => {
    const isMobile = window.innerWidth < 768; // md breakpoint
    const hasSeenSidebar = localStorage.getItem('chat_side_seen');
    
    if (isMobile && !hasSeenSidebar) {
      setSidebarOpen(true);
      localStorage.setItem('chat_side_seen', 'true');
    }
  }, []);

  const handleSendMessage = async (text) => {
    // Close sidebar on mobile
    setSidebarOpen(false);
    
    // Add user message
    setMessages(prev => [...prev, { text, sender: 'user', sources: [] }]);
    setLoading(true);

    try {
      // Call backend API
      const response = await axios.post(`${API_URL}/ask`, {
        question: text
      });

      // Add bot response
      setMessages(prev => [
        ...prev,
        {
          text: response.data.response,
          sender: 'bot',
          sources: response.data.sources || []
        }
      ]);
    } catch (error) {
      console.error('Error:', error);
      console.error('Response:', error.response?.data);
      setMessages(prev => [
        ...prev,
        {
          text: `Sorry, there was an error processing your request. ${error.response?.data?.error || error.message}`,
          sender: 'bot',
          sources: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleQuestion = (question) => {
    setTimeout(() => handleSendMessage(question), 100);
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#F6F8FA' }}>
      {/* Sidebar */}
      <Sidebar 
        onExampleQuestion={handleExampleQuestion}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Banner - Fixed on mobile */}
        <div className="md:static fixed top-0 left-0 right-0 z-30" style={{
          background: 'linear-gradient(135deg, #F2C94C 0%, #FFD700 100%)',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '13px',
          fontWeight: '500',
          color: '#12346A',
          borderBottom: '1px solid rgba(0, 0, 0, 0.08)'
        }}>
          <span style={{ fontSize: '16px' }}>⚠️</span>
          <span>FACTS-ONLY. NO INVESTMENT ADVICE.</span>
        </div>

        {/* Mobile Header - Fixed on mobile */}
        <div className="md:hidden fixed left-0 right-0 z-30" style={{
          top: '44px', /* Below top banner */
          background: '#FFFFFF',
          padding: '16px 24px',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <button
            onClick={() => setSidebarOpen(true)}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer',
              color: '#12346A'
            }}
          >
            ☰
          </button>
          <h2 style={{ fontSize: '16px', fontWeight: '600', color: '#12346A' }}>
            Mutual Fund Assistant
          </h2>
          <div style={{ width: '32px' }}></div>
        </div>

        {/* Spacer for fixed headers on mobile */}
        <div className="md:hidden" style={{ height: '104px' }}></div>

        <ChatWindow messages={messages} loading={loading} />
        <InputBar onSend={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}
