const form = document.getElementById("prompt-form");
const promptInput = document.getElementById("prompt");
const responseBox = document.getElementById("response");
const tokenInput = document.getElementById("authToken");
const logBox = document.getElementById("chain-log");

// Attempt to get URLs from Vite/Next.js like build env vars first, then fallback to window scope or defaults
const BACKEND_URL = typeof import.meta.env !== 'undefined' ? import.meta.env.VITE_BACKEND_URL : window.BACKEND_URL || 'https://noowin-backend.up.railway.app';
const WS_URL = typeof import.meta.env !== 'undefined' ? import.meta.env.VITE_WS_URL : window.WS_URL || 'wss://noowin-backend.up.railway.app/ws/logs';

if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const prompt = promptInput.value.trim();
      const token = tokenInput.value.trim();

      if (!prompt) {
        alert("Please enter a prompt.");
        return;
      }
      if (!token) {
        alert("Please enter a JWT token.");
        return;
      }

      responseBox.textContent = "Processing...";
      logBox.value += `[Request] Sending prompt: ${prompt}\n`;

      try {
        const res = await fetch(`${BACKEND_URL}/run_graph`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ prompt }),
        });

        if (!res.ok) {
            let errorDetail = res.statusText;
            try {
                const errorData = await res.json();
                errorDetail = errorData.detail || res.statusText;
            } catch (jsonError) { /* Ignore if response is not JSON */ }
            throw new Error(`HTTP error! Status: ${res.status}. Message: ${errorDetail}`);
        }

        const result = await res.json();
        responseBox.textContent = JSON.stringify(result, null, 2);
      } catch (error) {
        console.error("Error submitting prompt:", error);
        responseBox.textContent = `Error: ${error.message}`;
        logBox.value += `[Error] Failed to process prompt: ${error.message}\n`;
      }
    });
} else {
    console.error("Prompt form not found in the DOM.");
}

// WebSocket log
if (WS_URL) {
    try {
        const ws = new WebSocket(WS_URL);
        ws.onopen = () => {
            console.log("WebSocket connected to log server");
            if(logBox) logBox.value += "[System] WebSocket connected to log server.\n";
        };
        ws.onmessage = (event) => {
            console.log("Received log: ", event.data);
            if(logBox) logBox.value += event.data + "\n";
            if(logBox) logBox.scrollTop = logBox.scrollHeight; // Scroll to bottom
        };
        ws.onclose = () => {
            console.log("WebSocket disconnected. Attempting to reconnect...");
            if(logBox) logBox.value += "[System] WebSocket disconnected. Attempting to reconnect in 3s...\n";
            // Simple reconnect logic - consider more robust solutions for production
            // setTimeout(() => new WebSocket(WS_URL), 3000); // This creates a new WebSocket but doesn't re-assign to `ws` or re-attach handlers
        };
        ws.onerror = (error) => {
            console.error("WebSocket Error: ", error);
            if(logBox) logBox.value += `[System] WebSocket error. Check console. Disconnected.\n`;
        };
    } catch (e) {
        console.error("Failed to initialize WebSocket:", e);
        if(logBox) logBox.value += "[System] Failed to initialize WebSocket. Check console.\n";
    }
} else {
    console.warn("WS_URL is not defined. WebSocket for logs will not be connected.");
    if(logBox) logBox.value += "[System] WebSocket URL not configured. Logs will not be displayed in real-time.\n";
} 