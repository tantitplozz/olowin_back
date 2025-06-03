# clients/ollama_client.py
import requests
import os
import json

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nous-hermes2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434") # Changed default to ollama service name for docker

def call_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, # Added stream: False
            timeout=60 # Added timeout
        )
        response.raise_for_status() # Raise an exception for HTTP errors
        # Ensure the response is parsed correctly if it's a stream of JSON objects
        # For non-streaming, it should be a single JSON object.
        # Ollama's non-streaming response for /api/generate gives a JSON object with a 'response' key.
        return response.json().get("response", "[Ollama Error: No 'response' key in JSON]")
    except requests.exceptions.RequestException as e:
        return f"[Ollama Error] Request failed: {e}"
    except json.JSONDecodeError as e: # More specific error for JSON parsing
        return f"[Ollama Error] Failed to parse JSON response: {response.text if 'response' in locals() else 'No response text'} (Error: {e})"
    except Exception as e:
        return f"[Ollama Error] An unexpected error occurred: {response.text if 'response' in locals() else str(e)}" 