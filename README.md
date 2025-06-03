# OmniCard AI

ระบบ AI Agent สำหรับการวิเคราะห์และประมวลผลข้อมูล โดยใช้ Multi-Agent Architecture

## 🚀 Features

- Multi-Agent System ที่แต่ละ Agent มีบทบาทเฉพาะ
- ใช้ Local LLM (Ollama) และ Gemini API
- Real-time WebSocket สำหรับการแสดงผล
- ระบบ Logging และ Monitoring แบบครบวงจร
- Docker-based deployment พร้อม auto-scaling

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **LLM**: Ollama (Local) + Gemini API
- **Database**: MongoDB + Redis + ChromaDB
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## 📦 Requirements

- Docker และ Docker Compose
- Node.js 18+
- Python 3.11+
- 16GB RAM ขึ้นไป (สำหรับ Local LLM)

## 🚀 Quick Start

1. Clone repository:
```bash
git clone https://github.com/yourusername/omnicard.git
cd omnicard
```

2. สร้างไฟล์ .env:
```bash
cp .env.example .env
# แก้ไขค่าต่างๆ ใน .env ตามต้องการ
```

3. รันระบบ:
```bash
# รันทั้งระบบ
make up

# รันเฉพาะ Frontend
make frontend

# รันเฉพาะ Backend
make backend

# รันพร้อม Monitoring
make monitoring
```

4. เข้าถึงระบบ:
- Web UI: http://localhost:8080
- API Docs: http://localhost:8001/docs
- Monitoring:
  * Grafana: http://localhost:3000
  * Prometheus: http://localhost:9090
- Development Tools:
  * MongoDB Express: http://localhost:8081
  * Redis Commander: http://localhost:8082
  * RabbitMQ Management: http://localhost:15672

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork repository
2. สร้าง feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. สร้าง Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## AutoBuyer Agent

The AutoBuyer Agent, likely located in `autobuyer_project/`, uses the MetaGPT framework to simulate human browsing behavior for tasks like cookie collection and e-commerce interactions.

### Setup (AutoBuyer)

1.  Navigate to the autobuyer directory:
    ```bash
    cd autobuyer_project
    ```

2.  Install its specific dependencies (if any beyond the main `requirements.txt`):
    ```bash
    # pip install -r requirements.txt # if it has its own
    playwright install --with-deps chromium # Example if Playwright is used
    ```

3.  Configure the agent (check for a `config.yaml` or similar in its directory):
    ```bash
    # cp config.example.yaml config.yaml # If applicable
    # Edit its configuration file with necessary API keys and settings
    ```

4.  Run the AutoBuyer agent (this might be integrated into the main system or run standalone):
    ```bash
    # python autobuyer_main.py # Or however it's invoked
    ```

## Project Structure Overview

```
omnicard-ai/ (or MEEMEE/)
├── .git/                    # Git repository data
├── .github/                 # GitHub specific files (e.g., workflows)
├── .vscode/                 # VS Code settings
├── api/                     # FastAPI server code (e.g., server.py)
├── agents/                  # Core agent implementations
├── agent_prompts/           # Prompts for agents
├── autobuyer_project/       # AutoBuyer agent module
├── clients/                 # Clients for external services (e.g., LLM APIs)
├── config/                  # Application configuration files
├── data/                    # Persistent data (e.g., ChromaDB, logs if not in root `logs`)
│   └── chromadb/
├── frontend/                # Frontend application (e.g., React, Vue)
├── knowledge_bases/         # Knowledge base files for agents
├── loggers/                 # Logging utilities
├── memory/                  # Memory management components
├── metagpt/                 # MetaGPT framework related code (if customized or vendored)
├── metagpt_integration/     # Integration code with MetaGPT
├── scripts/                 # Utility and standalone scripts
├── static/                  # Static assets for the web server (CSS, JS, images)
├── templates/               # HTML templates for FastAPI
├── tests/                   # Test suite
├── utils/                   # Utility functions and classes
├── workflow/                # Workflow definitions and management
├── .env                     # Local environment variables (GITIGNORED)
├── .env.example             # Example environment variables
├── .gitignore               # Specifies intentionally untracked files that Git should ignore
├── .pylintrc                # Pylint configuration
├── CODE_OF_CONDUCT.md       # Code of Conduct for contributors
├── CONTRIBUTING.md          # Guidelines for contributing
├── Dockerfile               # Docker build instructions for the main application
├── LICENSE                  # Project license (e.g., MIT)
├── main.py                  # Main entry point for the application
├── pyproject.toml           # Python project configuration (packaging, tools)
├── README.md                # This file: Project overview and instructions
└── requirements.txt         # Python dependencies
```

This structure is a general guideline and might vary based on the actual project layout.

## ENV Configs (for .env file)

- `GEMINI_API_URL`: (Optional) URL ของ Gemini API (เช่น `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY`). ถ้ามี, `router_agent` จะพยายามเรียก Gemini ก่อน หากไม่มีหรือเรียกไม่สำเร็จ จะ fallback ไป Ollama.
- `OLLAMA_BASE_URL`: URL สำหรับ Ollama local (เช่น `http://localhost:11434`). `router_agent` จะใช้เป็น fallback หรือ primary หาก Gemini ไม่มี URL.
- `OLLAMA_MODEL_NAME`: (Optional) ชื่อโมเดล Ollama ที่จะใช้ (เช่น `llama2`, `llama3`). ค่าเริ่มต้นใน `router_agent` คือ `llama2`.
- `MONGODB_URI`: (Optional) MongoDB connection string (เช่น `mongodb://localhost:27017/`). ถ้ามี, `dataset_logger` จะพยายาม log prompt/response ไปยัง collection `logs` ใน database `omnicard`.
- `OMNICARD_JWT_SECRET_KEY`: Secret key สำหรับ JWT token ที่ใช้ใน `auth/jwt_auth.py`. ค่าที่ hardcode ไว้ชั่วคราวคือ `omnicard-secret-key`. **ควรเปลี่ยนเป็นค่าที่ปลอดภัยและเก็บใน `.env` สำหรับ production.**

## Endpoints (via `ui_server.py`)

- **`POST /run_graph`**: 
    - **Description**: ส่ง prompt เพื่อให้ agent ประมวลผลและรับผลลัพธ์กลับมา
    - **Request Body**: JSON object ที่มี key `prompt` (e.g., `{"prompt": "Your question here"}`)
    - **Headers**: ต้องมี `Authorization: Bearer <YOUR_TOKEN>` โดย `<YOUR_TOKEN>` คือค่าที่ตรงกับ `OMNICARD_JWT_SECRET_KEY` (ปัจจุบันคือ `omnicard-secret-key`)
    - **Response**: JSON object ที่มี key `result` (e.g., `{"result": "Agent's response"}`)

- **`WebSocket /ws/logs`**: 
    - **Description**: Endpoint สำหรับ WebSocket เพื่อรับ log การทำงาน (prompt และ response) แบบ real-time ที่ถูก broadcast จาก server หลังจาก `/run_graph` ทำงานเสร็จ
    - **Usage**: Client เชื่อมต่อ WebSocket ไปยัง URL นี้ (เช่น `ws://localhost:8000/ws/logs`) แล้วรอรับ message ที่ server ส่งมา 