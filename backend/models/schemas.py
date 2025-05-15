from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    doc_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages/chunks")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: str = Field(..., description="Upload timestamp")


class ChatRequest(BaseModel):
    """Request model for chat/query"""
    doc_id: str = Field(..., description="Document ID to query against")
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    chat_history: Optional[List[dict]] = Field(default=[], description="Previous chat messages")


class SourceChunk(BaseModel):
    """Source chunk from retrieval"""
    page: int = Field(..., description="Page number or chunk index")
    content: str = Field(..., description="Relevant text content")
    relevance_score: float = Field(..., description="Similarity score (0-1)")


class ChatResponse(BaseModel):
    """Response model for chat/query"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[SourceChunk] = Field(..., description="Retrieved source chunks")
    doc_id: str = Field(..., description="Document ID queried")
    processing_time_ms: int = Field(..., description="Response generation time")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    uptime_seconds: float
