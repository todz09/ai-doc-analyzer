import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import upload, chat
from services.rag_engine import RAGEngine
from models.schemas import HealthCheckResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global RAG engine instance
rag_engine = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_engine
    
    # Startup
    logger.info("Starting AI Document Analyzer API...")
    
    # Validate environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please create a .env file with your Groq API key. "
            "Get one free at: https://console.groq.com"
        )
    
    # Initialize RAG engine
    rag_engine = RAGEngine(
        groq_api_key=groq_api_key,
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    )
    
    logger.info("RAG Engine initialized successfully")
    logger.info("API is ready to receive requests")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="AI Document Analyzer API",
    description="Intelligent document analysis with RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Document Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    uptime = time.time() - start_time
    
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=round(uptime, 2)
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
