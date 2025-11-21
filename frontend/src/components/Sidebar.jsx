import React from 'react';

export const Sidebar = ({ onExampleQuestion }) => {
  const examples = [
    "What is the expense ratio of UTI ELSS Tax Saver Fund?",
    "What is the P/B ratio of UTI India Consumer Fund Direct Growth?",
    "Who is the fund manager of UTI India Consumer Fund Direct Growth?"
  ];

  return (
    <aside className="w-1/3 bg-white p-6 border-r border-gray-200 overflow-y-auto">
      {/* Warning Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
        <p className="text-sm text-yellow-800 font-semibold">
          ⚠️ FACTS-ONLY. NO INVESTMENT ADVICE.
        </p>
      </div>

      {/* Info Section Title */}
      <h2 className="text-lg font-bold text-text-dark mb-4">Info Section</h2>

      {/* Welcome Message */}
      <div className="bg-soft-gray rounded-lg p-4 mb-6">
        <p className="text-sm text-text-dark leading-relaxed">
          <span className="text-lg">👋</span> <strong>Welcome!</strong><br />
          I'm your Mutual Fund FAQ Assistant. I can help you find specific, factual answers about UTI AMC schemes.
        </p>
      </div>

      {/* Example Questions */}
      <div className="bg-soft-gray rounded-lg p-4">
        <h3 className="text-sm font-bold text-text-dark mb-3">❓ Example Questions</h3>
        <ul className="space-y-2">
          {examples.map((example, idx) => (
            <li key={idx}>
              <button
                onClick={() => onExampleQuestion(example)}
                className="text-sm text-accent-blue hover:underline text-left w-full break-words"
              >
                • {example}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
};
