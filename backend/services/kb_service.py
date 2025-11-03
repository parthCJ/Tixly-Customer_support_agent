"""
Knowledge Base Service - RAG (Retrieval-Augmented Generation)
Handles document storage, embedding generation, and semantic search
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from datetime import datetime


class KnowledgeBaseService:
    """
    Manages the knowledge base using ChromaDB for vector storage
    and semantic search
    """
    
    def __init__(self, persist_directory: str = "./chroma_data"):
        """
        Initialize ChromaDB and embedding model
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client (local storage)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (runs locally, no API needed)
        print("🔄 Loading embedding model (this may take a moment on first run)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        # This model is:
        # - Small (80MB)
        # - Fast (good for real-time)
        # - Accurate enough for support tickets
        # - Runs locally (no API calls)
        print("✅ Embedding model loaded!")
        
        # Get or create collection for KB articles
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "Customer support knowledge base articles"}
        )
        
        print(f"📚 Knowledge Base ready! ({self.collection.count()} articles loaded)")
    
    def add_article(
        self,
        article_id: str,
        title: str,
        content: str,
        category: str = "general",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Add a knowledge base article
        
        Args:
            article_id: Unique identifier for the article
            title: Article title
            content: Article content (will be embedded)
            category: Article category (shipping, billing, etc.)
            metadata: Additional metadata
        
        Returns:
            True if successful
        """
        try:
            # Combine title and content for better search
            full_text = f"{title}\n\n{content}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(full_text).tolist()
            
            # Prepare metadata
            article_metadata = {
                "title": title,
                "category": category,
                "added_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Add to ChromaDB
            self.collection.add(
                ids=[article_id],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[article_metadata]
            )
            
            print(f"✅ Added article: {title} ({article_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding article {article_id}: {str(e)}")
            return False
    
    def add_articles_bulk(self, articles: List[Dict[str, Any]]) -> int:
        """
        Add multiple articles at once
        
        Args:
            articles: List of article dictionaries with keys:
                     article_id, title, content, category, metadata
        
        Returns:
            Number of articles successfully added
        """
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for article in articles:
            try:
                full_text = f"{article['title']}\n\n{article['content']}"
                embedding = self.embedding_model.encode(full_text).tolist()
                
                ids.append(article['article_id'])
                embeddings.append(embedding)
                documents.append(full_text)
                metadatas.append({
                    "title": article['title'],
                    "category": article.get('category', 'general'),
                    "added_at": datetime.utcnow().isoformat(),
                    **(article.get('metadata', {}))
                })
            except Exception as e:
                print(f"❌ Error processing article {article.get('article_id', 'unknown')}: {str(e)}")
        
        if ids:
            try:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"✅ Added {len(ids)} articles to knowledge base")
                return len(ids)
            except Exception as e:
                print(f"❌ Error bulk adding articles: {str(e)}")
                return 0
        
        return 0
    
    def search(
        self,
        query: str,
        n_results: int = 3,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant articles
        
        Args:
            query: Search query (ticket subject + description)
            n_results: Number of results to return
            category_filter: Optional category to filter by
        
        Returns:
            List of relevant articles with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build filter if category specified
            where_filter = None
            if category_filter:
                where_filter = {"category": category_filter}
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            articles = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    articles.append({
                        "article_id": results['ids'][0][i],
                        "title": results['metadatas'][0][i].get('title', 'Untitled'),
                        "content": results['documents'][0][i],
                        "category": results['metadatas'][0][i].get('category', 'general'),
                        "relevance_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "metadata": results['metadatas'][0][i]
                    })
            
            return articles
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return []
    
    def search_for_ticket(
        self,
        subject: str,
        description: str,
        category: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search KB for articles relevant to a support ticket
        
        Args:
            subject: Ticket subject
            description: Ticket description
            category: Ticket category (if known)
            n_results: Number of articles to return
        
        Returns:
            List of relevant KB articles
        """
        # Combine subject and description for better search
        query = f"{subject}\n{description}"
        
        # Search with category filter if available
        return self.search(
            query=query,
            n_results=n_results,
            category_filter=category
        )
    
    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID"""
        try:
            result = self.collection.get(
                ids=[article_id],
                include=["documents", "metadatas"]
            )
            
            if result['ids']:
                return {
                    "article_id": result['ids'][0],
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0]
                }
            return None
            
        except Exception as e:
            print(f"❌ Error getting article {article_id}: {str(e)}")
            return None
    
    def delete_article(self, article_id: str) -> bool:
        """Delete an article from the knowledge base"""
        try:
            self.collection.delete(ids=[article_id])
            print(f"✅ Deleted article: {article_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting article {article_id}: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all articles (use with caution!)"""
        try:
            self.client.delete_collection("knowledge_base")
            self.collection = self.client.create_collection(
                name="knowledge_base",
                metadata={"description": "Customer support knowledge base articles"}
            )
            print("✅ Knowledge base cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing knowledge base: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            count = self.collection.count()
            
            # Get all metadatas to calculate categories
            if count > 0:
                all_data = self.collection.get(include=["metadatas"])
                categories = {}
                for metadata in all_data['metadatas']:
                    cat = metadata.get('category', 'general')
                    categories[cat] = categories.get(cat, 0) + 1
            else:
                categories = {}
            
            return {
                "total_articles": count,
                "categories": categories,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            return {"total_articles": 0, "categories": {}}


# Global KB service instance
_kb_service = None


def get_kb_service() -> KnowledgeBaseService:
    """Get or create the global KB service instance"""
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service


def search_knowledge_base(
    subject: str,
    description: str,
    category: Optional[str] = None,
    n_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Convenience function to search the knowledge base
    
    Usage:
        articles = search_knowledge_base(
            subject="Order hasn't shipped",
            description="My order was placed 5 days ago...",
            category="shipping"
        )
        
        for article in articles:
            print(f"{article['title']}: {article['relevance_score']:.2%}")
    """
    kb = get_kb_service()
    return kb.search_for_ticket(subject, description, category, n_results)
