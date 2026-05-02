'use client';

import { useState } from 'react';

export default function RecipientCard() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [category, setCategory] = useState('All');
  const [showModal, setShowModal] = useState(false);
  const [cardOutput, setCardOutput] = useState('');
  const [subId, setSubId] = useState('');

  const generateCard = (e: React.FormEvent) => {
    e.preventDefault();
    const id = 'REC-' + Math.random().toString(36).substring(2, 10).toUpperCase();
    const output = "# Recipient Subscription Card: " + name + "\n\n## Recipient Details\n- **Full Name**: " + name + "\n- **Email**: " + email + "\n- **Role**: user\n- **Subscription ID**: [Leave blank]\n\n## Subscriptions\n### " + category + "\n- **Subscribed**: Yes\n- **Classifications**: All";
    setSubId(id);
    setCardOutput(output);
    setShowModal(true);
  };

  const copyCard = () => {
    navigator.clipboard.writeText(cardOutput);
    alert("Copied to clipboard!");
  };

  const githubSubmitUrl = "https://github.com/RokctAI/opportunities/new/main?filename=.rokct/recipients/" + subId + ".md&value=" + encodeURIComponent(cardOutput) + "&message=feat:new-subscription";

  return (
    <div className="mt-8 p-6 bg-[#2d2e31] rounded-xl border border-gray-700">
      <h3 className="text-xl font-bold mb-2 flex items-center">
        <span className="mr-2">🚀</span> Join Registry
      </h3>
      <p className="text-gray-400 text-sm mb-4">Generate your PII-protected recipient card to receive tailored notifications.</p>
      <form onSubmit={generateCard} className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full bg-[#202124] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="email"
          placeholder="Email Address"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-[#202124] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full bg-[#202124] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Tenders">Tenders</option>
          <option value="Grants">Grants</option>
          <option value="Equity">Equity</option>
          <option value="All">All Categories</option>
        </select>
        <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg transition">
          Generate Card
        </button>
      </form>

      {showModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#2d2e31] rounded-2xl shadow-2xl max-w-2xl w-full p-8 relative border border-gray-700">
            <button onClick={() => setShowModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl">&times;</button>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Your Subscription Card is Ready!</h2>
              <p className="text-gray-400">Copy the content below and submit it to GitHub.</p>
            </div>
            <pre className="bg-[#202124] rounded-lg p-6 font-mono text-sm text-green-400 overflow-auto max-h-[300px] border border-gray-800">
              {cardOutput}
            </pre>
            <div className="mt-8 flex flex-col md:flex-row gap-4">
              <button onClick={copyCard} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-xl transition">
                Copy Content
              </button>
              <a href={githubSubmitUrl} target="_blank" rel="noopener noreferrer" className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center font-bold py-3 rounded-xl transition">
                Submit via GitHub
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
