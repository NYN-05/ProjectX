import logging
import hashlib
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re
import math

logger = logging.getLogger(__name__)

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'this', 'that', 'these',
    'those', 'it', 'its', 'they', 'them', 'their', 'we', 'our', 'you',
    'your', 'he', 'she', 'him', 'her', 'his', 'as', 'if', 'then', 'so',
    'because', 'when', 'while', 'where', 'how', 'what', 'which', 'who',
    'whom', 'whose', 'can', 'just', 'also', 'now', 'about', 'into', 'over'
}

class EmbeddingService:
    """
    Lightweight embedding service using TF-IDF based feature vectors.
    Uses hash-based vectorization for efficient similarity computation.
    Designed to work offline without external API dependencies.
    """
    
    def __init__(self, vector_size: int = 512):
        self.vector_size = vector_size
        self._vocabulary = {}
        self._document_freq = Counter()
        self._total_docs = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]
    
    def _hash_feature(self, feature: str, seed: int = 0) -> int:
        """Hash a feature to a vector index."""
        hash_input = f"{feature}_{seed}".encode()
        return int(hashlib.md5(hash_input).hexdigest(), 16) % self.vector_size
    
    def _create_vector(self, tokens: List[str]) -> np.ndarray:
        """Create a sparse vector representation from tokens."""
        vector = np.zeros(self.vector_size)
        token_counts = Counter(tokens)
        
        for token, count in token_counts.items():
            idx = self._hash_feature(token)
            tf = count
            idf = math.log((self._total_docs + 1) / (self._document_freq.get(token, 1) + 1)) + 1
            vector[idx] = tf * idf
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def build_vocabulary(self, documents: List[str]) -> None:
        """Build vocabulary from document corpus."""
        all_tokens = set()
        
        for doc in documents:
            tokens = self._tokenize(doc)
            all_tokens.update(tokens)
        
        self._vocabulary = {token: i for i, token in enumerate(list(all_tokens)[:self.vector_size])}
        
        for doc in documents:
            tokens = self._tokenize(doc)
            unique_tokens = set(tokens)
            self._document_freq.update(unique_tokens)
            self._total_docs += 1
        
        logger.info(f"Vocabulary built with {len(self._vocabulary)} terms from {self._total_docs} documents")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text."""
        tokens = self._tokenize(text)
        return self._create_vector(tokens)
    
    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for multiple texts."""
        return [self.get_embedding(text) for text in texts]
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar(self, query: str, documents: List[str], top_k: int = 10, threshold: float = 0.1) -> List[Tuple[int, float]]:
        """Find most similar documents to query."""
        if not documents or not query:
            return []
        
        if self._total_docs == 0:
            self.build_vocabulary(documents)
        
        query_embedding = self.get_embedding(query)
        
        similarities = []
        for i, doc in enumerate(documents):
            doc_embedding = self.get_embedding(doc)
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def compute_similarity_matrix(self, documents: List[str], batch_size: int = 100) -> np.ndarray:
        """Compute pairwise similarity matrix for documents."""
        n = len(documents)
        similarity_matrix = np.zeros((n, n))
        
        if self._total_docs == 0:
            self.build_vocabulary(documents)
        
        embeddings = self.get_embeddings_batch(documents)
        
        for i in range(0, n, batch_size):
            batch_end = min(i + batch_size, n)
            
            for j in range(i, batch_end):
                sim = self.cosine_similarity(embeddings[i], embeddings[j])
                similarity_matrix[i, j] = sim
                similarity_matrix[j, i] = sim
        
        return similarity_matrix
    
    def find_clusters(self, documents: List[str], min_similarity: float = 0.3) -> List[List[int]]:
        """Find clusters of similar documents using greedy clustering."""
        if not documents or self._total_docs == 0:
            self.build_vocabulary(documents)
        
        embeddings = self.get_embeddings_batch(documents)
        n = len(embeddings)
        
        assigned = [False] * n
        clusters = []
        
        for i in range(n):
            if assigned[i]:
                continue
            
            cluster = [i]
            assigned[i] = True
            
            for j in range(i + 1, n):
                if assigned[j]:
                    continue
                
                sim = self.cosine_similarity(embeddings[i], embeddings[j])
                if sim >= min_similarity:
                    cluster.append(j)
                    assigned[j] = True
            
            if len(cluster) > 0:
                clusters.append(cluster)
        
        return clusters
    
    def create_event_embeddings(self, events: List[dict]) -> List[dict]:
        """Create embeddings for events with enriched text."""
        enriched_events = []
        
        for event in events:
            enriched_text = self._enrich_event_text(event)
            embedding = self.get_embedding(enriched_text)
            
            enriched_events.append({
                **event,
                "embedding": embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                "embedding_text": enriched_text[:500]
            })
        
        return enriched_events
    
    def _enrich_event_text(self, event: dict) -> str:
        """Enrich event data into a single text for embedding."""
        parts = []
        
        parts.append(event.get("title", ""))
        
        if event.get("event_type"):
            parts.append(event["event_type"])
        
        if event.get("actors"):
            actor_names = [a.get("name", "") for a in event["actors"][:3]]
            parts.extend(actor_names)
        
        if event.get("industries"):
            parts.extend(event["industries"])
        
        if event.get("technologies"):
            parts.extend(event["technologies"])
        
        if event.get("topics"):
            parts.extend(event["topics"])
        
        return " ".join([p for p in parts if p])


embedding_service = EmbeddingService()