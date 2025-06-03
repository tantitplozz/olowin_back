import React, { useEffect, useState, useRef } from 'react';
import { ChainLog } from './components/ChainLog';

function App() {
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [targetSite, setTargetSite] = useState<string>('adidas');
  const [cardNumber, setCardNumber] = useState<string>('4111111111111111');

  const handleStartOrder = async () => {
    setError(null);
    try {
      const response = await fetch("http://localhost:8002/start_order", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target_site: targetSite, card_info: { number: cardNumber, zip: "12345" } })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTaskId(data.task_id);
    } catch (err: any) {
      console.error("Failed to start order:", err);
      setError(err.message || "Failed to start order. Check API connection.");
    }
  };

  const [promptInput, setPromptInput] = useState<string>("วิเคราะห์ความเสี่ยงของธุรกรรมนี้หน่อย");
  const [agentResponse, setAgentResponse] = useState<string>("");

  const handleAskAgent = async () => {
    setError(null);
    setAgentResponse("Thinking...");
    try {
      const response = await fetch("http://localhost:8002/agent/run", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: promptInput })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAgentResponse(data.response || JSON.stringify(data));
    } catch (err: any) {
      console.error("Failed to ask agent:", err);
      setError(err.message || "Failed to ask agent.");
      setAgentResponse("Error from agent.");
    }
  };

  return (
    <div className="p-4 container mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      <header className="mb-6 text-center md:col-span-2">
        <h1 className="text-4xl font-bold text-indigo-700">OmniCard-AI Control Panel</h1>
      </header>

      {error && (
        <div className="md:col-span-2 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="space-y-6">
        <div className="p-6 border rounded-lg shadow-xl bg-white">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">Start L10 Order (Legacy)</h2>
          <p className="text-sm text-orange-600 mb-3">Note: /start_order endpoint may be deprecated or require refactoring due to backend changes.</p>
          <div className="mb-4">
            <label htmlFor="targetSite" className="block text-sm font-medium text-gray-700">Target Site:</label>
            <input 
              type="text" 
              id="targetSite" 
              value={targetSite} 
              onChange={(e) => setTargetSite(e.target.value)} 
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700">Card Number:</label>
            <input 
              type="text" 
              id="cardNumber" 
              value={cardNumber} 
              onChange={(e) => setCardNumber(e.target.value)} 
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <button 
            onClick={handleStartOrder} 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
          >
            Start Order (Legacy Flow)
          </button>
          {taskId && <p className="mt-3 text-xs text-gray-500">Last L10 Task ID: {taskId}</p>}
        </div>

        <div className="p-6 border rounded-lg shadow-xl bg-white">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">Ask OmniStack Agent (New Workflow)</h2>
          <div className="mb-4">
            <label htmlFor="promptInput" className="block text-sm font-medium text-gray-700">Your Prompt:</label>
            <textarea 
              id="promptInput" 
              value={promptInput} 
              onChange={(e) => setPromptInput(e.target.value)} 
              rows={4}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., วิเคราะห์ความเสี่ยงของธุรกรรมนี้..."
            />
          </div>
          <button 
            onClick={handleAskAgent} 
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
          >
            Submit to OmniStack Agent
          </button>
          {agentResponse && (
            <div className="mt-4 p-3 bg-gray-100 rounded">
              <h3 className="text-md font-semibold text-gray-700">Agent Response:</h3>
              <pre className="whitespace-pre-wrap break-all text-sm text-gray-600">{agentResponse}</pre>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 border rounded-lg shadow-xl bg-gray-50">
        <ChainLog />
      </div>
    </div>
  );
}

export default App; 