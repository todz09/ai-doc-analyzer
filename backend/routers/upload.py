import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict
import logging

from models.schemas import DocumentUploadResponse
from services.document_processor import DocumentProcessor
from services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Global storage
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Document storage (in production, use a database)
document_store: Dict[str, dict] = {}


async def get_rag_engine():
    """Dependency to get RAG engine instance"""
    from main import rag_engine
    return rag_engine


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag_engine: RAGEngine = Depends(get_rag_engine)
) -> DocumentUploadResponse:
    """
    Upload and process a document
    
    Supports: PDF, DOCX, TXT
    """
    try:
        # Validate file type
        extension = Path(file.filename).suffix.lower()
        allowed_extensions = ['.pdf', '.docx', '.txt']
        
        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save file temporarily
        file_path = UPLOAD_DIR / f"{doc_id}{extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        logger.info(f"File saved: {file_path} ({file_size} bytes)")
        
        # Process document
        chunks = DocumentProcessor.process_document(str(file_path))
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        # Index into RAG engine
        indexed_count = rag_engine.index_document(doc_id, chunks)
        
        # Store metadata
        document_store[doc_id] = {
            "filename": file.filename,
            "doc_id": doc_id,
            "file_path": str(file_path),
            "extension": extension,
            "size_bytes": file_size,
            "pages": len(chunks),
            "uploaded_at": datetime.now().isoformat(),
            "indexed_chunks": indexed_count
        }
        
        logger.info(f"Document processed successfully: {doc_id}")
        
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            pages=len(chunks),
            size_bytes=file_size,
            uploaded_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return {
        "documents": [
            {
                "doc_id": doc["doc_id"],
                "filename": doc["filename"],
                "pages": doc["pages"],
                "uploaded_at": doc["uploaded_at"]
            }
            for doc in document_store.values()
        ],
        "total": len(document_store)
    }


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """Delete a document"""
    if doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from RAG engine
        rag_engine.delete_document(doc_id)
        
        # Delete file
        file_path = document_store[doc_id]["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from store
        del document_store[doc_id]
        
        return {"message": "Document deleted successfully", "doc_id": doc_id}
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
