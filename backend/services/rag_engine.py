import os
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine using ChromaDB and Groq"""

    def __init__(
        self,
        groq_api_key: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chroma_persist_dir: str = "./chroma_db"
    ):
        """
        Initialize RAG engine
        
        Args:
            groq_api_key: Groq API key
            embedding_model: HuggingFace embedding model name
            chroma_persist_dir: Directory for ChromaDB persistence
        """
        self.groq_api_key = groq_api_key
        
        # Initialize embeddings (local, no API needed)
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB
        logger.info(f"Initializing ChromaDB at: {chroma_persist_dir}")
        os.makedirs(chroma_persist_dir, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize Groq LLM (ultra-fast inference)
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model_name="mixtral-8x7b-32768",  # Fast and capable
            temperature=0.3,
            max_tokens=1024
        )
        
        logger.info("RAG Engine initialized successfully")

    def create_collection(self, doc_id: str) -> chromadb.Collection:
        """
        Create or get a ChromaDB collection for a document
        
        Args:
            doc_id: Document identifier
            
        Returns:
            ChromaDB collection
        """
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=f"doc_{doc_id}",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection created/retrieved: doc_{doc_id}")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise

    def index_document(self, doc_id: str, chunks: List[Dict[str, any]]) -> int:
        """
        Index document chunks into ChromaDB
        
        Args:
            doc_id: Document identifier
            chunks: List of text chunks with metadata
            
        Returns:
            Number of chunks indexed
        """
        try:
            collection = self.create_collection(doc_id)
            
            # Prepare data for ChromaDB
            texts = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Generate embeddings and add to collection
            embeddings = self.embeddings.embed_documents(texts)
            
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Indexed {len(chunks)} chunks for doc: {doc_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error indexing document: {str(e)}")
            raise

    def retrieve_relevant_chunks(
        self, 
        doc_id: str, 
        query: str, 
        top_k: int = 4
    ) -> List[Tuple[str, Dict, float]]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            doc_id: Document identifier
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            List of (text, metadata, score) tuples
        """
        try:
            collection = self.chroma_client.get_collection(name=f"doc_{doc_id}")
            
            # Embed query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            chunks = []
            for i in range(len(results['documents'][0])):
                chunks.append((
                    results['documents'][0][i],
                    results['metadatas'][0][i],
                    1 - results['distances'][0][i]  # Convert distance to similarity
                ))
            
            logger.info(f"Retrieved {len(chunks)} chunks for query")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Tuple[str, Dict, float]]
    ) -> str:
        """
        Generate answer using retrieved context and LLM
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            
        Returns:
            Generated answer
        """
        # Build context from chunks
        context = "\n\n".join([
            f"[Source: Page {chunk[1].get('page', 'N/A')}]\n{chunk[0]}"
            for chunk in context_chunks
        ])
        
        # Create prompt
        prompt_template = PromptTemplate(
            template="""You are an intelligent document assistant. Answer the question based on the provided context.

Context from document:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the context provided
- If the answer is not in the context, say "I cannot find this information in the document"
- Be concise but complete
- Cite the page number when possible

Answer:""",
            input_variables=["context", "question"]
        )
        
        formatted_prompt = prompt_template.format(context=context, question=query)
        
        try:
            # Generate response
            response = self.llm.invoke(formatted_prompt)
            answer = response.content
            
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def query(self, doc_id: str, question: str) -> Dict:
        """
        Complete RAG pipeline: retrieve + generate
        
        Args:
            doc_id: Document identifier
            question: User question
            
        Returns:
            Dict with answer and source chunks
        """
        import time
        start_time = time.time()
        
        # Retrieve relevant chunks
        chunks = self.retrieve_relevant_chunks(doc_id, question, top_k=4)
        
        # Generate answer
        answer = self.generate_answer(question, chunks)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "answer": answer,
            "sources": [
                {
                    "page": chunk[1].get('page', 0),
                    "content": chunk[0][:200] + "..." if len(chunk[0]) > 200 else chunk[0],
                    "relevance_score": round(chunk[2], 3)
                }
                for chunk in chunks
            ],
            "processing_time_ms": processing_time
        }

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document collection from ChromaDB
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Success status
        """
        try:
            self.chroma_client.delete_collection(name=f"doc_{doc_id}")
            logger.info(f"Deleted collection: doc_{doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
