"""Legal Knowledge Base Module for Nilaayam AI.

Provides pgvector-backed semantic storage and retrieval of legal provisions,
with seamless in-memory fallback using cosine similarity when Supabase is not configured.
"""

import os
import uuid
import logging
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime

import numpy as np

# Try importing Google Generative AI
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    genai = None
    HAS_GENAI = False

# Try importing backend config and database
try:
    from backend.config import settings
    from backend.database import get_supabase
except ImportError:
    settings = None
    get_supabase = lambda: None

logger = logging.getLogger(__name__)


def _compute_fallback_embedding(text: str, dim: int = 768) -> List[float]:
    """Computes a deterministic, normalized pseudo-embedding for fallback when Gemini is unavailable.
    
    Uses hash-based feature representation with sliding character 3-grams
    to allow meaningful cosine similarity calculation on text overlap.
    """
    vec = np.zeros(dim, dtype=np.float32)
    clean_text = text.lower().strip()
    words = clean_text.split()
    
    # Word level hashes
    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % dim
        vec[h] += 2.0
        
    # Character 3-gram hashes
    for i in range(len(clean_text) - 2):
        trigram = clean_text[i:i + 3]
        h = int(hashlib.sha256(trigram.encode("utf-8")).hexdigest(), 16) % dim
        vec[h] += 1.0
        
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class LegalKnowledgeBase:
    """Legal Knowledge Base supporting Supabase pgvector and in-memory fallback."""

    def __init__(self):
        """Initializes Supabase client and Gemini embedding client."""
        self.supabase = None
        try:
            if callable(get_supabase):
                self.supabase = get_supabase()
        except Exception as e:
            logger.warning(f"Could not initialize Supabase client: {e}. Falling back to in-memory mode.")

        # Embedding model setup
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key and settings and getattr(settings, "gemini_api_key", None):
            self.api_key = settings.gemini_api_key

        self.embedding_model = "models/text-embedding-004"
        if settings and getattr(settings, "embedding_model", None):
            self.embedding_model = settings.embedding_model

        self.genai_ready = False
        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.genai_ready = True
                logger.info("Gemini embedding client configured successfully.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API: {e}. Falling back to deterministic embeddings.")
        else:
            logger.info("Gemini API key not configured or package missing. Using deterministic fallback embeddings.")

        # In-memory document storage for fallback and demo mode
        self._memory_docs: List[Dict[str, Any]] = []

    def _embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a given text snippet."""
        if self.genai_ready and genai:
            try:
                response = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                embedding = response.get("embedding", [])
                if embedding:
                    return embedding
            except Exception as e:
                logger.warning(f"Gemini embedding API call failed: {e}. Using fallback embedding.")

        return _compute_fallback_embedding(text)

    def _embed_query(self, query: str) -> List[float]:
        """Generates embedding vector for a retrieval query."""
        if self.genai_ready and genai:
            try:
                response = genai.embed_content(
                    model=self.embedding_model,
                    content=query,
                    task_type="retrieval_query"
                )
                embedding = response.get("embedding", [])
                if embedding:
                    return embedding
            except Exception as e:
                logger.warning(f"Gemini query embedding failed: {e}. Using fallback embedding.")

        return _compute_fallback_embedding(query)

    def add_document(
        self,
        title: str,
        authority: str,
        url: Optional[str],
        section: Optional[str],
        text: str,
        is_binding: bool = True,
        publication_date: Optional[str] = None,
        last_verified: Optional[str] = None,
        verification_note: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> List[str]:
        """Chunks text into 500-char chunks with 50-char overlap, embeds each, and stores them.
        
        Stores in Supabase if configured; also maintains in-memory copy for fast offline retrieval.
        Returns list of generated reference chunk IDs.
        """
        chunk_size = 500
        overlap = 50
        step = chunk_size - overlap
        
        chunks: List[str] = []
        if len(text) <= chunk_size:
            chunks.append(text)
        else:
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                if end >= len(text):
                    break
                start += step

        chunk_ids: List[str] = []

        for idx, chunk in enumerate(chunks):
            ref_id = f"ref_{uuid.uuid4().hex[:12]}"
            chunk_ids.append(ref_id)
            embedding = self._embed_text(chunk)

            doc_entry = {
                "id": ref_id,
                "ref_id": ref_id,
                "title": title,
                "authority": authority,
                "url": url,
                "section": section,
                "excerpt": chunk,
                "text": chunk,
                "embedding": embedding,
                "is_binding": is_binding,
                "publication_date": publication_date or datetime.utcnow().strftime("%Y-%m-%d"),
                "last_verified": last_verified or datetime.utcnow().strftime("%Y-%m-%d"),
                "verification_note": verification_note,
                "doc_type": doc_type or "general",
                "chunk_index": idx,
            }

            # Always save to memory for resilient demo & fallback
            self._memory_docs.append(doc_entry)

            # Persist to Supabase if client is connected
            if self.supabase:
                try:
                    self.supabase.table("legal_references").insert({
                        "id": ref_id,
                        "title": title,
                        "authority": authority,
                        "url": url,
                        "section": section,
                        "excerpt": chunk,
                        "embedding": embedding,
                        "is_binding": is_binding,
                        "publication_date": doc_entry["publication_date"],
                        "last_verified": doc_entry["last_verified"],
                        "verification_note": verification_note,
                        "doc_type": doc_entry["doc_type"],
                    }).execute()
                except Exception as e:
                    logger.debug(f"Supabase insertion for reference {ref_id} failed: {e}. Saved in memory.")

        return chunk_ids

    def search(self, query: str, doc_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Embeds query and executes cosine similarity search in pgvector or in-memory fallback.
        
        Returns top_k results with metadata and relevance scores.
        """
        query_vec = self._embed_query(query)

        # Attempt Supabase pgvector RPC search if available
        if self.supabase:
            try:
                rpc_params = {
                    "query_embedding": query_vec,
                    "match_threshold": 0.1,
                    "match_count": top_k * 2,
                }
                if doc_type:
                    rpc_params["filter_doc_type"] = doc_type

                response = self.supabase.rpc("match_legal_references", rpc_params).execute()
                if response.data:
                    results = []
                    for row in response.data[:top_k]:
                        results.append({
                            "ref_id": row.get("id") or row.get("ref_id"),
                            "title": row.get("title", ""),
                            "authority": row.get("authority", ""),
                            "url": row.get("url"),
                            "section": row.get("section"),
                            "excerpt": row.get("excerpt", ""),
                            "is_binding": row.get("is_binding", True),
                            "publication_date": row.get("publication_date"),
                            "last_verified": row.get("last_verified"),
                            "verification_note": row.get("verification_note"),
                            "relevance_score": float(row.get("similarity", row.get("score", 0.0))),
                            "doc_type": row.get("doc_type"),
                        })
                    return results
            except Exception as e:
                logger.debug(f"Supabase RPC match_legal_references failed or not present: {e}. Falling back to in-memory.")

        # In-memory cosine similarity search
        return self._search_memory(query_vec, doc_type=doc_type, top_k=top_k)

    def _search_memory(self, query_vec: List[float], doc_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Calculates cosine similarity across in-memory document vectors."""
        if not self._memory_docs:
            return []

        q_vec = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        scored_candidates = []
        for doc in self._memory_docs:
            if doc_type and doc.get("doc_type") and doc["doc_type"] != doc_type and doc["doc_type"] != "general":
                continue

            doc_vec = np.array(doc["embedding"], dtype=np.float32)
            d_norm = np.linalg.norm(doc_vec)
            if d_norm == 0:
                score = 0.0
            else:
                score = float(np.dot(q_vec, doc_vec) / (q_norm * d_norm))

            scored_candidates.append((score, doc))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, doc in scored_candidates[:top_k]:
            results.append({
                "ref_id": doc.get("ref_id") or doc.get("id"),
                "title": doc.get("title", ""),
                "authority": doc.get("authority", ""),
                "url": doc.get("url"),
                "section": doc.get("section"),
                "excerpt": doc.get("excerpt") or doc.get("text", ""),
                "is_binding": doc.get("is_binding", True),
                "publication_date": doc.get("publication_date"),
                "last_verified": doc.get("last_verified"),
                "verification_note": doc.get("verification_note"),
                "relevance_score": round(max(0.0, min(1.0, score)), 4),
                "doc_type": doc.get("doc_type"),
            })

        return results

    def get_all_references(
        self,
        doc_type_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lists all references, with optional doc_type filtering and pagination."""
        if self.supabase:
            try:
                query = self.supabase.table("legal_references").select("*")
                if doc_type_filter:
                    query = query.eq("doc_type", doc_type_filter)
                res = query.range(offset, offset + limit - 1).execute()
                if res.data:
                    return [
                        {
                            "ref_id": r.get("id") or r.get("ref_id"),
                            "title": r.get("title", ""),
                            "authority": r.get("authority", ""),
                            "url": r.get("url"),
                            "section": r.get("section"),
                            "excerpt": r.get("excerpt", ""),
                            "is_binding": r.get("is_binding", True),
                            "publication_date": r.get("publication_date"),
                            "last_verified": r.get("last_verified"),
                            "verification_note": r.get("verification_note"),
                            "doc_type": r.get("doc_type"),
                        }
                        for r in res.data
                    ]
            except Exception as e:
                logger.debug(f"Supabase select failed: {e}. Falling back to memory list.")

        # In-memory list
        filtered = [
            {
                "ref_id": d.get("ref_id") or d.get("id"),
                "title": d.get("title", ""),
                "authority": d.get("authority", ""),
                "url": d.get("url"),
                "section": d.get("section"),
                "excerpt": d.get("excerpt") or d.get("text", ""),
                "is_binding": d.get("is_binding", True),
                "publication_date": d.get("publication_date"),
                "last_verified": d.get("last_verified"),
                "verification_note": d.get("verification_note"),
                "doc_type": d.get("doc_type"),
            }
            for d in self._memory_docs
            if not doc_type_filter or d.get("doc_type") == doc_type_filter or d.get("doc_type") == "general"
        ]

        return filtered[offset:offset + limit]
