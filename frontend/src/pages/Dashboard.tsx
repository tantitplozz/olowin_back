import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface AgentResponse {
  status: string;
  message: string;
  data: {
    input: any;
    output: string;
  };
}

const Dashboard: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const navigate = useNavigate();

  // WebSocket connection for real-time logs
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws/logs';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'agent_update') {
          setLogs((prevLogs) => [...prevLogs, data.data]);
        }
      } catch (e) {
        setLogs((prevLogs) => [...prevLogs, event.data]);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      const response = await axios.post<AgentResponse>(
        `${apiUrl}/api/agents/process`,
        { prompt }
      );
      setResponse(response.data);
    } catch (error) {
      console.error('Error submitting prompt:', error);
      setLogs((prevLogs) => [...prevLogs, `Error: ${error instanceof Error ? error.message : String(error)}`]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">OmniCard AI Dashboard</h1>
        <p className="text-gray-600">
          Multi-Agent System for AI-powered data processing
        </p>
        <div className="mt-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${wsConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {wsConnected ? 'WebSocket Connected' : 'WebSocket Disconnected'}
          </span>
        </div>
      </header>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 mb-6">
            <div className="mb-4">
              <label htmlFor="prompt" className="block text-gray-700 text-sm font-bold mb-2">
                Enter your prompt:
              </label>
              <textarea
                id="prompt"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder="What would you like to process today?"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isLoading ? 'Processing...' : 'Submit'}
            </button>
          </form>

          {response && (
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Response</h2>
              <div className="bg-gray-100 p-4 rounded-md">
                <pre className="whitespace-pre-wrap">{JSON.stringify(response, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Agent Logs</h2>
          <div className="bg-black text-green-400 p-4 rounded-md h-96 overflow-y-auto font-mono text-sm">
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  &gt; {log}
                </div>
              ))
            ) : (
              <div className="italic text-gray-500">No logs yet. Submit a prompt to see agent activity.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 