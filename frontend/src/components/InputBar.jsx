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
    <div className="fixed bottom-0 left-1/3 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
      <div className="flex gap-2 max-w-full">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your query here..."
          disabled={disabled}
          className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-accent-blue disabled:bg-gray-100"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="bg-accent-blue text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-semibold"
        >
          Send
        </button>
      </div>
    </div>
  );
};
