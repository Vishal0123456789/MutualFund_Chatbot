import React, { useState } from 'react';
import axios from 'axios';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatWindow } from './components/ChatWindow';
import { InputBar } from './components/InputBar';

// Get API URL from environment variable or default to relative path
const API_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm your UTI Mutual Fund Factual Assistant. Ask me anything about UTI AMC schemes.",
      sender: 'bot',
      sources: []
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (text) => {
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
    <div className="flex flex-col h-screen bg-soft-blue">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar onExampleQuestion={handleExampleQuestion} />

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
        <ChatWindow messages={messages} loading={loading} />
        <InputBar onSend={handleSendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  );
}
