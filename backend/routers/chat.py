from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import logging

from models.schemas import ChatRequest, ChatResponse
from services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def get_rag_engine():
    """Dependency to get RAG engine instance"""
    from main import rag_engine
    return rag_engine


@router.post("", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    rag_engine: RAGEngine = Depends(get_rag_engine)
) -> ChatResponse:
    """
    Ask a question about an uploaded document
    
    Uses RAG to retrieve relevant context and generate an answer
    """
    try:
        # Import document store to check if doc exists
        from routers.upload import document_store
        
        if request.doc_id not in document_store:
            raise HTTPException(
                status_code=404,
                detail="Document not found. Please upload a document first."
            )
        
        logger.info(f"Processing query for doc: {request.doc_id}")
        logger.info(f"Question: {request.question}")
        
        # Query RAG engine
        result = rag_engine.query(request.doc_id, request.question)
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            doc_id=request.doc_id,
            processing_time_ms=result["processing_time_ms"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/health")
async def chat_health_check():
    """Health check for chat endpoint"""
    return {
        "status": "healthy",
        "service": "chat",
        "message": "Chat service is running"
    }
