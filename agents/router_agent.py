# agents/router_agent.py
from typing import Literal

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

def route_model(prompt: str) -> Literal["gemini", "ollama"]:
    """ตัดสินใจเลือกโมเดลจากเนื้อหาใน prompt"""
    prompt_lower = prompt.lower()
    
    if any(keyword in prompt_lower for keyword in GEMINI_KEYWORDS):
        return "gemini"
    
    if any(keyword in prompt_lower for keyword in OLLAMA_KEYWORDS):
        return "ollama"

    # ค่า Default: ใช้ Gemini หากไม่มี keyword ตรง
    return "gemini" 