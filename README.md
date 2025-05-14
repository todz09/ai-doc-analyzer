# 🚀 AI Document Analyzer

**A production-ready full-stack application for intelligent document analysis with RAG (Retrieval-Augmented Generation)**

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-demo-link.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🎯 What This Does

Upload PDF/DOCX/TXT documents and get intelligent answers powered by AI. Perfect for:
- Contract analysis
- Research paper summaries
- Legal document review
- Technical documentation Q&A

## ✨ Features

### 🎨 Frontend (React + Vite)
- **Drag & Drop Upload** - Multi-file support with progress indicators
- **Real-time Chat Interface** - Conversational AI responses
- **Document Preview** - View uploaded documents inline
- **Export Functionality** - Download chat history as PDF/JSON
- **Responsive Design** - Works on mobile, tablet, desktop

### ⚡ Backend (FastAPI)
- **RAG Pipeline** - LangChain + ChromaDB for semantic search
- **Multi-Format Support** - PDF, DOCX, TXT processing
- **Streaming Responses** - Real-time AI output
- **Vector Storage** - Persistent embeddings with ChromaDB
- **API Documentation** - Auto-generated OpenAPI/Swagger docs

### 🔒 Production Features
- Environment-based configuration
- CORS security
- Error handling & logging
- Rate limiting ready
- Docker containerization
- Health check endpoints

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   React UI      │────────▶│   FastAPI        │────────▶│  Groq LLM       │
│   (Port 5173)   │◀────────│   (Port 8000)    │◀────────│  (Cloud API)    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   ChromaDB       │
                            │   Vector Store   │
                            └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key ([Get one free](https://console.groq.com))

### 1. Clone & Setup

```bash
git clone https://github.com/todz09/ai-document-analyzer.git
cd ai-document-analyzer
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run backend
python main.py
```

Backend runs at: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 📸 Screenshots

### Upload Interface
![Upload](docs/upload-demo.gif)

### Chat Interface
![Chat](docs/chat-demo.gif)

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File uploads

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - LLM orchestration
- **ChromaDB** - Vector database
- **Groq** - Ultra-fast LLM inference
- **PyPDF2/python-docx** - Document parsing
- **Sentence Transformers** - Embeddings

## 📁 Project Structure

```
ai-document-analyzer/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routers/
│   │   ├── upload.py          # File upload endpoints
│   │   └── chat.py            # Chat/query endpoints
│   ├── services/
│   │   ├── document_processor.py  # PDF/DOCX parsing
│   │   └── rag_engine.py      # RAG pipeline logic
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   └── DocumentPreview.jsx
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./chroma_db
MAX_FILE_SIZE=10485760  # 10MB
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

Access:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📊 API Endpoints

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

Response: { "doc_id": "uuid", "filename": "contract.pdf", "pages": 5 }
```

### Ask Question
```http
POST /api/chat
Content-Type: application/json

{
  "doc_id": "uuid",
  "question": "What is the termination clause?"
}

Response: {
  "answer": "The contract can be terminated...",
  "sources": [{"page": 3, "content": "..."}]
}
```

## 🎓 Learning Resources

**What You'll Learn Building This:**
1. Full-stack architecture (React + FastAPI)
2. RAG implementation patterns
3. Vector database usage (ChromaDB)
4. File handling & processing
5. Real-time streaming responses
6. Production deployment practices

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) - RAG framework
- [Groq](https://groq.com) - Lightning-fast LLM inference
- [ChromaDB](https://www.trychroma.com) - Vector database

## 📧 Contact

Tawheed Ahmed Ansari - [GitHub](https://github.com/todz09)

**⭐ Star this repo if it helped you!**
