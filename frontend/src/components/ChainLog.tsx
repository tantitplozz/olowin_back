import React, { useEffect, useState } from "react";

export function ChainLog() {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    // Ensure the WebSocket URL matches the FastAPI server's host and port
    // If FastAPI is running on host port 8002 (from Docker mapping)
    const ws = new WebSocket("ws://localhost:8002/ws"); 

    ws.onopen = () => {
      console.log("[ChainLog] WebSocket connection established");
    };

    ws.onmessage = (event) => {
      // Assuming the server sends plain text messages
      const message = event.data;
      setLogs((prevLogs) => [...prevLogs, message]);
    };

    ws.onerror = (error) => {
      console.error("[ChainLog] WebSocket error:", error);
      // Optionally display an error message in the log viewer itself
      setLogs((prevLogs) => [...prevLogs, "[WebSocket Error: Connection failed or interrupted]"]);
    };

    ws.onclose = (event) => {
      console.log("[ChainLog] WebSocket connection closed:", event.reason);
      // Optionally display a message about the connection closing
      if (!event.wasClean) {
        setLogs((prevLogs) => [...prevLogs, `[WebSocket Closed: ${event.reason || 'Connection lost'}]`]);
      }
    };

    // Cleanup function to close the WebSocket connection when the component unmounts
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      console.log("[ChainLog] WebSocket connection closed on component unmount.");
    };
  }, []); // Empty dependency array means this effect runs once on mount and cleans up on unmount

  return (
    <div className="p-4 bg-black text-green-400 font-mono rounded-xl h-96 overflow-y-auto text-sm shadow-lg">
      <h2 className="text-xl font-bold text-white mb-2 sticky top-0 bg-black py-2">🔗 Chain Log</h2>
      {logs.map((log, i) => (
        <div key={i} className="whitespace-pre-wrap break-all">{log}</div>
      ))}
    </div>
  );
} 