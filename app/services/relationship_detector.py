import logging
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

RELATIONSHIP_TYPES = {
    "causes": {
        "keywords": ["causes", "triggers", "leads to", "results in", "drives", "spurs", "prompts"],
        "bidirectional": False
    },
    "affects": {
        "keywords": ["affects", "impacts", "influences", "shapes", "determines"],
        "bidirectional": False
    },
    "correlates_with": {
        "keywords": ["coincides", "correlates", "aligns", "matches", "similar to"],
        "bidirectional": True
    },
    "escalates": {
        "keywords": ["escalates", "worsens", "intensifies", "aggravates", "exacerbates"],
        "bidirectional": False
    },
    "supports": {
        "keywords": ["supports", "backs", "reinforces", "confirms", "validates"],
        "bidirectional": False
    },
    "contradicts": {
        "keywords": ["contradicts", "conflicts", "opposes", "disputes", "denies"],
        "bidirectional": True
    },
    "depends_on": {
        "keywords": ["depends on", "relies on", "requires", "needs", "conditional"],
        "bidirectional": False
    },
    "precedes": {
        "keywords": ["precedes", "precedes", "comes before", "ahead of", "prior to"],
        "bidirectional": False
    },
    "follows": {
        "keywords": ["follows", "comes after", "subsequent", "later", "ensues"],
        "bidirectional": False
    },
    "same_topic": {
        "keywords": [],
        "bidirectional": True
    },
    "same_actor": {
        "keywords": [],
        "bidirectional": True
    },
    "same_region": {
        "keywords": [],
        "bidirectional": True
    },
}


class RelationshipDetector:
    """
    Detects semantic and contextual relationships between intelligence events.
    Uses entity overlap, temporal proximity, semantic similarity, and topic modeling.
    """
    
    def __init__(self, similarity_threshold: float = 0.25, temporal_window_days: int = 7):
        self.similarity_threshold = similarity_threshold
        self.temporal_window_days = temporal_window_days
    
    def detect_all_relationships(self, events: List[dict], embeddings: List[np.ndarray] = None) -> List[Dict]:
        """Detect all relationships between events."""
        relationships = []
        n = len(events)
        
        for i in range(n):
            for j in range(i + 1, n):
                rel = self.detect_relationship(events[i], events[j], embeddings[i] if embeddings else None, embeddings[j] if embeddings else None)
                if rel:
                    relationships.append(rel)
        
        logger.info(f"Detected {len(relationships)} relationships from {n} events")
        return relationships
    
    def detect_relationship(self, event1: dict, event2: dict, embedding1: np.ndarray = None, embedding2: np.ndarray = None) -> Optional[Dict]:
        """Detect relationship between two events."""
        relationship_score = 0
        relationship_type = None
        confidence = 0.0
        reasons = []
        
        entity_overlap = self._check_entity_overlap(event1, event2)
        if entity_overlap["score"] > 0:
            relationship_score += entity_overlap["score"] * 0.4
            reasons.extend(entity_overlap["reasons"])
        
        temporal_proximity = self._check_temporal_proximity(event1, event2)
        if temporal_proximity["score"] > 0:
            relationship_score += temporal_proximity["score"] * 0.2
            reasons.extend(temporal_proximity["reasons"])
        
        topic_similarity = self._check_topic_similarity(event1, event2)
        if topic_similarity["score"] > 0:
            relationship_score += topic_similarity["score"] * 0.3
            reasons.extend(topic_similarity["reasons"])
        
        semantic_similarity = 0
        if embedding1 is not None and embedding2 is not None:
            semantic_similarity = self._compute_embedding_similarity(embedding1, embedding2)
            if semantic_similarity > self.similarity_threshold:
                relationship_score += semantic_similarity * 0.3
                reasons.append(f"semantic similarity: {semantic_similarity:.2f}")
        
        if relationship_score >= self.similarity_threshold:
            relationship_type = self._infer_relationship_type(event1, event2, reasons)
            
            confidence = min(relationship_score, 1.0)
            
            return {
                "source_id": event1.get("event_id"),
                "target_id": event2.get("event_id"),
                "type": relationship_type,
                "strength": relationship_score,
                "confidence": confidence,
                "reasons": reasons[:5],
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def _check_entity_overlap(self, event1: dict, event2: dict) -> Dict:
        """Check for overlapping entities between events."""
        score = 0
        reasons = []
        
        event1_countries = set(event1.get("countries", []))
        event2_countries = set(event2.get("countries", []))
        country_overlap = event1_countries & event2_countries
        if country_overlap:
            score += 0.3 * len(country_overlap)
            reasons.append(f"shared countries: {', '.join(country_overlap)}")
        
        event1_companies = set(event1.get("companies", []))
        event2_companies = set(event2.get("companies", []))
        company_overlap = event1_companies & event2_companies
        if company_overlap:
            score += 0.4 * len(company_overlap)
            reasons.append(f"shared companies: {', '.join(company_overlap)}")
        
        event1_people = set(event1.get("people", []))
        event2_people = set(event2.get("people", []))
        people_overlap = event1_people & event2_people
        if people_overlap:
            score += 0.3 * len(people_overlap)
            reasons.append(f"shared people: {', '.join(people_overlap)}")
        
        return {"score": min(score, 1.0), "reasons": reasons}
    
    def _check_temporal_proximity(self, event1: dict, event2: dict) -> Dict:
        """Check temporal proximity between events."""
        try:
            ts1 = event1.get("timestamp", "")
            ts2 = event2.get("timestamp", "")
            
            if not ts1 or not ts2:
                return {"score": 0, "reasons": []}
            
            if "T" in ts1:
                dt1 = datetime.fromisoformat(ts1.replace("Z", "+00:00"))
            else:
                return {"score": 0, "reasons": []}
            
            if "T" in ts2:
                dt2 = datetime.fromisoformat(ts2.replace("Z", "+00:00"))
            else:
                return {"score": 0, "reasons": []}
            
            days_diff = abs((dt1 - dt2).days)
            
            if days_diff == 0:
                score = 1.0
                reason = "same day"
            elif days_diff <= 1:
                score = 0.8
                reason = "within 1 day"
            elif days_diff <= self.temporal_window_days:
                score = 0.5 * (1 - days_diff / self.temporal_window_days)
                reason = f"within {days_diff} days"
            else:
                score = 0
                reason = None
            
            return {"score": score, "reasons": [f"temporal: {reason}"]} if reason else {"score": 0, "reasons": []}
        
        except Exception:
            return {"score": 0, "reasons": []}
    
    def _check_topic_similarity(self, event1: dict, event2: dict) -> Dict:
        """Check topic similarity between events."""
        score = 0
        reasons = []
        
        industries1 = set(event1.get("industries", []))
        industries2 = set(event2.get("industries", []))
        if industries1 & industries2:
            score += 0.4
            reasons.append(f"shared industries: {', '.join(industries1 & industries2)}")
        
        technologies1 = set(event1.get("technologies", []))
        technologies2 = set(event2.get("technologies", []))
        if technologies1 & technologies2:
            score += 0.4
            reasons.append(f"shared technologies: {', '.join(technologies1 & technologies2)}")
        
        topics1 = set(event1.get("topics", []))
        topics2 = set(event2.get("topics", []))
        if topics1 & topics2:
            score += 0.2
            reasons.append(f"shared topics: {', '.join(topics1 & topics2)}")
        
        if event1.get("sector") == event2.get("sector"):
            score += 0.2
            reasons.append(f"same sector: {event1.get('sector')}")
        
        return {"score": min(score, 1.0), "reasons": reasons}
    
    def _compute_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings."""
        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return float(dot / (norm1 * norm2))
    
    def _infer_relationship_type(self, event1: dict, event2: dict, reasons: List[str]) -> str:
        """Infer the type of relationship based on event characteristics."""
        if event1.get("impact") == "negative" and event2.get("impact") == "negative":
            if "escalates" in str(reasons).lower():
                return "escalates"
        
        if event1.get("event_type") == event2.get("event_type"):
            return "same_topic"
        
        if event1.get("sector") == event2.get("sector"):
            return "same_topic"
        
        return "correlates_with"
    
    def rank_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Rank relationships by strength and confidence."""
        return sorted(relationships, key=lambda r: (r.get("strength", 0), r.get("confidence", 0)), reverse=True)
    
    def filter_relationships(self, relationships: List[Dict], min_confidence: float = 0.3, max_relationships: int = 100) -> List[Dict]:
        """Filter relationships by confidence threshold."""
        filtered = [r for r in relationships if r.get("confidence", 0) >= min_confidence]
        return filtered[:max_relationships]


relationship_detector = RelationshipDetector()