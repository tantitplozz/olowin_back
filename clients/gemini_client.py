# clients/gemini_client.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        print("[Gemini Client] Initialized successfully.")
    except Exception as e:
        print(f"[Gemini Client Error] Failed to initialize gemini-pro model: {e}")
        model = None
else:
    print("[Gemini Client Warning] GEMINI_API_KEY not found in environment. Gemini client will not be functional.")
    model = None

def call_gemini(prompt: str) -> str:
    """เรียกใช้ Gemini API และส่ง prompt"""
    if not model:
        return "[Gemini Error] Gemini model not initialized. Check API Key or initialization errors."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Log the full error for debugging if needed
        # print(f"[Gemini Error - Full Trace]: {traceback.format_exc()}")
        return f"[Gemini Error] Failed to generate content: {str(e)}" 