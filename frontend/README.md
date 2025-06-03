# OmniCard Frontend

This is the frontend user interface for the OmniCard-AI project. It allows users to interact with the backend agents, submit prompts, view responses, and see real-time logs via WebSocket.

## Features

*   Simple interface to send prompts to the OmniCard-AI backend.
*   Displays responses from the AI agents.
*   Real-time log streaming via WebSocket connection.
*   Requires JWT Token for interacting with the backend API.

## Setup & Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tantitplozz/noowin-frontend.git
    cd noowin-frontend
    ```

2.  **Environment Variables:**
    This frontend expects certain URLs to be available to connect to the backend. These can be configured if you are using a build system (like Vite/Next.js) or injected if your server/deployment platform supports it.
    Create a `.env` file (if your setup uses one, based on `.env.template`) or configure these in your deployment environment (e.g., Railway variables):
    *   `BACKEND_URL`: The base URL for the backend API (e.g., `http://localhost:8000` for local, or `https://your-backend-service.up.railway.app` for deployed).
    *   `WS_URL`: The WebSocket URL for real-time logs (e.g., `ws://localhost:8000/ws/logs` for local, or `wss://your-backend-service.up.railway.app/ws/logs` for deployed).

    The `index.html` currently uses hardcoded fallback URLs:
    *   Backend: `https://noowin-backend.up.railway.app`
    *   WebSocket: `wss://noowin-backend.up.railway.app/ws/logs`

    For local development, ensure your backend (omnicard-backend) is running, typically on port 8000.

## Running Locally

Open `index.html` directly in your browser. Ensure the backend service is running and accessible at the configured `BACKEND_URL` and `WS_URL`.

## Deploy on Railway

This project is configured for deployment on Railway using the provided `Dockerfile` and `railway.json`.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy?template=https%3A%2F%2Fgithub.com%2Ftantitplozz%2Fnoowin-frontend&referralCode=your_referral_code_optional)

*(Note: You might need to replace the above Railway button URL with one that directly points to your `noowin-frontend` repository if you want a one-click deploy from this README. The generic template button might require manual configuration.)*
Or, more simply, if your repository is public:
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/tantitplozz/noowin-frontend) 