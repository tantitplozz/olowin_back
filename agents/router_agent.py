# agents/router_agent.py
import httpx
import os
from loggers.dataset_logger import logger # Assuming the global logger instance
from typing import Tuple, Optional # Added for type hints

# Keywords ที่สัมพันธ์กับ Gemini (เช่น ใช้ reasoning, วางแผน, วิเคราะห์)
GEMINI_KEYWORDS = [
    "วิเคราะห์", "เหตุผล", "คาดการณ์", "แผน", "เชิงกลยุทธ์",
    "ประเมิน", "เจาะลึก", "จำแนก", "ประมวลผล", "meta", "analyze"
]

# Keywords ที่สัมพันธ์กับ Ollama (เน้น simulation, สร้าง, ทดลอง)
OLLAMA_KEYWORDS = [
    "สุ่ม", "จำลอง", "ทดลอง", "สร้าง", "generate", "ปลอมแปลง",
    "จำลองเหตุการณ์", "simulate", "fake", "mock"
]

# Environment variables (consider using a config management solution for larger apps)
GEMINI_API_URL = os.getenv("GEMINI_API_URL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama2") # Default to llama2 if not set

async def _call_gemini_api(prompt: str, client: httpx.AsyncClient) -> Tuple[Optional[str], Optional[str]]:
    """Helper function to call Gemini API. Returns (response_text, error_message)."""
    if not GEMINI_API_URL:
        msg = "[RouterAgent] GEMINI_API_URL not set. Skipping Gemini."
        print(msg)
        return None, msg
    try:
        payload = {"prompt": prompt}
        print(f"[RouterAgent] Calling Gemini API: {GEMINI_API_URL} with prompt: '{prompt[:50]}...'")
        response = await client.post(GEMINI_API_URL, json=payload, timeout=20.0)
        response.raise_for_status()
        gemini_response_text = response.text 
        print(f"[RouterAgent] Gemini response (status {response.status_code}): '{gemini_response_text[:100]}...'")
        logger.log(prompt=prompt, response=gemini_response_text, agent_name="gemini")
        return gemini_response_text, None
    except httpx.HTTPStatusError as e:
        error_message = f"Gemini API request failed with status {e.response.status_code}: {e.response.text}"
        print(f"[RouterAgent] {error_message}")
        return None, error_message
    except httpx.RequestError as e:
        error_message = f"Gemini API request failed: {str(e)}"
        print(f"[RouterAgent] {error_message}")
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred with Gemini: {str(e)}"
        print(f"[RouterAgent] {error_message}")
        return None, error_message

async def _call_ollama_api(prompt: str, client: httpx.AsyncClient) -> Tuple[Optional[str], Optional[str]]:
    """Helper function to call Ollama API. Returns (response_text, error_message)."""
    if not OLLAMA_BASE_URL:
        error_message = "[RouterAgent] OLLAMA_BASE_URL not set. Cannot call Ollama."
        print(error_message)
        logger.log(prompt=prompt, response=error_message, agent_name="ollama_fallback_error")
        return None, error_message
    try:
        ollama_payload = {"model": OLLAMA_MODEL_NAME, "prompt": prompt, "stream": False}
        ollama_api_url = f"{OLLAMA_BASE_URL}/api/generate"
        print(f"[RouterAgent] Calling Ollama API: {ollama_api_url} with model '{OLLAMA_MODEL_NAME}' prompt: '{prompt[:50]}...'")
        response = await client.post(ollama_api_url, json=ollama_payload, timeout=60.0)
        response.raise_for_status()
        ollama_data = response.json()
        ollama_response_text = ollama_data.get("response", "Error: No response field in Ollama output.")
        print(f"[RouterAgent] Ollama response (status {response.status_code}): '{ollama_response_text[:100]}...'")
        logger.log(prompt=prompt, response=ollama_response_text, agent_name=f"ollama_{OLLAMA_MODEL_NAME}")
        return ollama_response_text, None
    except httpx.HTTPStatusError as e:
        error_message = f"Ollama API request failed with status {e.response.status_code}: {e.response.text}"
        print(f"[RouterAgent] {error_message}")
        logger.log(prompt=prompt, response=error_message, agent_name=f"ollama_{OLLAMA_MODEL_NAME}_error")
        return None, error_message
    except httpx.RequestError as e:
        error_message = f"Ollama API request failed: {str(e)}"
        print(f"[RouterAgent] {error_message}")
        logger.log(prompt=prompt, response=error_message, agent_name=f"ollama_{OLLAMA_MODEL_NAME}_error")
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred with Ollama: {str(e)}"
        print(f"[RouterAgent] {error_message}")
        logger.log(prompt=prompt, response=error_message, agent_name=f"ollama_{OLLAMA_MODEL_NAME}_error")
        return None, error_message

async def route_prompt(prompt: str) -> str:
    """Routes a prompt first to Gemini, then falls back to Ollama if Gemini fails."""
    gemini_response: Optional[str] = None
    gemini_error: Optional[str] = None
    ollama_response: Optional[str] = None
    ollama_error: Optional[str] = None
    
    async with httpx.AsyncClient() as client:
        gemini_response, gemini_error = await _call_gemini_api(prompt, client)
        if gemini_response is not None:
            return gemini_response

        print("[RouterAgent] Falling back to Ollama...")
        ollama_response, ollama_error = await _call_ollama_api(prompt, client)
        if ollama_response is not None:
            return ollama_response
            
    # Construct final error message if both failed
    if gemini_error and ollama_error:
        return f"Gemini failed: {gemini_error}. Ollama also failed: {ollama_error}"
    if gemini_error:
        return f"Gemini failed: {gemini_error}. Ollama fallback did not succeed."
    if ollama_error:
        return f"Ollama failed: {ollama_error}. (Gemini not attempted or had no error report)."
    
    # Default error if all else fails (e.g., both responses and errors are None)
    return "Both Gemini and Ollama calls failed to produce a response or a specific error."

# Placeholder for the old route_model if it was structured differently or if other parts of your system still call it.
# If route_prompt is a direct replacement, you might remove or refactor the old route_model.
# def route_model(user_prompt: str, recalled_memory = None, config = None) -> str:
#    # This function would need to be adapted or replaced by route_prompt
#    # For now, let's assume route_prompt is the new primary way.
#    # You might call route_prompt from here if needed for compatibility.
#    # raise NotImplementedError("route_model needs to be adapted to use new async route_prompt or be replaced.")
#    pass 