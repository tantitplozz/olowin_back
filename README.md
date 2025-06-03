# OmniCard AI

Multi-Agent System for AI-powered data processing

## Description

OmniCard AI เป็นระบบ Multi-Agent ที่ใช้ AI ในการประมวลผลข้อมูลหลากหลายรูปแบบ โดยมีโครงสร้างพื้นฐานที่แยกส่วนเป็น Backend, Frontend และระบบ Monitoring

## Features

- ระบบ Multi-Agent ที่ทำงานร่วมกันแบบ workflow
- API ที่พัฒนาด้วย FastAPI
- รองรับการเชื่อมต่อกับ MongoDB
- ระบบ Authentication และ Authorization
- ระบบ Monitoring ด้วย Prometheus และ Grafana
- WebSocket สำหรับการติดตามการทำงานแบบ real-time

## Project Structure

```
backend/
  ├── requirements/     # แยกไฟล์ requirements ตามหมวดหมู่
  ├── src/
  │   ├── api/          # API endpoints
  │   ├── db/           # Database connections
  │   ├── models/       # Pydantic models
  │   └── main.py       # FastAPI application
frontend/
  ├── public/           # Static files
  ├── src/              # React components
  │   ├── components/   # UI components
  │   └── pages/        # Page components
monitoring/
  ├── prometheus/       # Prometheus configuration
  ├── grafana/          # Grafana dashboards
  └── elasticsearch/    # Elasticsearch configuration
```

## Installation

### Requirements

- Python 3.8+
- MongoDB
- Node.js 16+ (สำหรับ Frontend)
- Docker (optional)

### Setup

1. โคลนโปรเจค

```bash
git clone https://github.com/yourusername/omnicard-ai.git
cd omnicard-ai
```

2. ติดตั้ง dependencies

```bash
pip install -r backend/requirements/base.txt
```

3. สร้างไฟล์ .env (ดูตัวอย่างจาก .env.example)

4. รัน Backend

```bash
python -m uvicorn backend.src.main:app --reload
```

5. ทดสอบ API ที่ http://localhost:8000/docs

## Development

### Backend

การพัฒนา Backend ใช้ FastAPI และ MongoDB โดยมีโครงสร้างไฟล์หลักที่สำคัญดังนี้:

- `backend/src/main.py`: FastAPI application หลัก
- `backend/src/api/`: API routers
- `backend/src/models/`: Pydantic models
- `backend/src/db/`: Database connections

### Testing

```bash
pytest tests/
```

## Deployment

### Docker

```bash
docker-compose up -d
```

## License

MIT License

## ENV Configs (for .env file)

- `GEMINI_API_URL`: (Optional) URL ของ Gemini API (เช่น `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY`). ถ้ามี, `router_agent` จะพยายามเรียก Gemini ก่อน หากไม่มีหรือเรียกไม่สำเร็จ จะ fallback ไป Ollama.
- `OLLAMA_BASE_URL`: URL สำหรับ Ollama local (เช่น `http://localhost:11434`). `router_agent`