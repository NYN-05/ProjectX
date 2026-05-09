import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.services.entity_extractor import entity_extractor
from app.services.geolocation_service import geolocation_processor

logger = logging.getLogger(__name__)

EVENT_TYPES = {
    "trade_restriction": {
        "keywords": ["tariff", "trade war", "embargo", "sanction", "ban", "restriction", "blockade", "export control"],
        "impact": "negative",
        "sector": "trade"
    },
    "economic_policy": {
        "keywords": ["interest rate", "fiscal policy", "monetary policy", "stimulus", "tax", "budget", "deficit", "inflation"],
        "impact": "mixed",
        "sector": "finance"
    },
    "conflict": {
        "keywords": ["war", "military operation", "invasion", "attack", "battle", "combat", "clash", "offensive", "defensive"],
        "impact": "negative",
        "sector": "defense"
    },
    "diplomatic": {
        "keywords": ["summit", "meeting", "negotiation", "treaty", "agreement", "deal", "visit", "diplomatic"],
        "impact": "positive",
        "sector": "diplomacy"
    },
    "technology_announcement": {
        "keywords": ["launch", "announce", "release", "unveil", "reveal", "introduce", "new product", "innovation"],
        "impact": "positive",
        "sector": "technology"
    },
    "merger_acquisition": {
        "keywords": ["acquire", "merge", "acquisition", "takeover", "buyout", "deal", "acquisition"],
        "impact": "mixed",
        "sector": "business"
    },
    "regulatory_action": {
        "keywords": ["regulation", "law", "bill", "legislation", "court", "ruling", "verdict", "fine", "penalty"],
        "impact": "negative",
        "sector": "legal"
    },
    "natural_disaster": {
        "keywords": ["earthquake", "flood", "hurricane", "typhoon", "tsunami", "wildfire", "volcano", "disaster"],
        "impact": "negative",
        "sector": "emergency"
    },
    "health_crisis": {
        "keywords": ["pandemic", "epidemic", "outbreak", "virus", "disease", "infection", "quarantine"],
        "impact": "negative",
        "sector": "health"
    },
    "political_event": {
        "keywords": ["election", "vote", "referendum", "protest", "demonstration", "coup", "resignation"],
        "impact": "mixed",
        "sector": "politics"
    },
    "corporate_financial": {
        "keywords": ["revenue", "profit", "loss", "earnings", "quarterly", "fiscal", "stock", "share"],
        "impact": "mixed",
        "sector": "finance"
    },
    "security_threat": {
        "keywords": ["cyber attack", "hack", "breach", "terrorist", "threat", "attack", "security"],
        "impact": "negative",
        "sector": "security"
    },
}

SEVERITY_LEVELS = {
    "critical": ["war", "invasion", "military operation", "pandemic", "nuclear", "terrorist attack"],
    "high": ["sanction", "embargo", "trade war", "major disaster", "coup", "revolution"],
    "medium": ["election", "policy change", "regulatory fine", "protest", "cyber attack"],
    "low": ["announcement", "meeting", "deal", "normal diplomatic visit"],
}


class EventModeler:
    def __init__(self):
        self.entity_extractor = entity_extractor
    
    def model_event(self, article: dict) -> dict:
        """Convert an article into a structured intelligence event."""
        text = f"{article.get('title', '')} {article.get('description', '')}"
        text_lower = text.lower()
        
        event_type = self._detect_event_type(text_lower)
        event_data = EVENT_TYPES.get(event_type, {"impact": "neutral", "sector": "general"})
        
        severity = self._detect_severity(text_lower)
        
        entities = self.entity_extractor.extract_all(article)
        
        actors = self._extract_actors(entities, text)
        
        event = {
            "event_id": self._generate_event_id(article),
            "event_type": event_type,
            "sector": event_data.get("sector", "general"),
            "impact": event_data.get("impact", "neutral"),
            "severity": severity,
            "timestamp": article.get("publishedAt", datetime.now().isoformat()),
            "source": article.get("source", {}).get("name", "Unknown"),
            "title": article.get("title", "")[:200],
            "url": article.get("url", ""),
            "actors": actors,
            "countries": [c["iso"] for c in entities.get("countries", [])],
            "companies": [c["name"] for c in entities.get("companies", [])],
            "industries": entities.get("industries", []),
            "technologies": entities.get("technologies", []),
            "topics": entities.get("topics", []),
            "people": entities.get("people", [])[:5],
            "sentiment": article.get("sentiment", {}).get("score", "neutral"),
            "category": article.get("category", "general"),
            "geolocation": {
                "country": article.get("country"),
                "country_code": article.get("country_code"),
                "latitude": article.get("latitude"),
                "longitude": article.get("longitude"),
            } if article.get("country_code") else None
        }
        
        return event
    
    def _detect_event_type(self, text: str) -> str:
        """Detect the type of event from text."""
        scores = {}
        
        for event_type, data in EVENT_TYPES.items():
            score = 0
            for keyword in data.get("keywords", []):
                if keyword in text:
                    score += 1
            if score > 0:
                scores[event_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "general"
    
    def _detect_severity(self, text: str) -> str:
        """Detect event severity level."""
        for severity, keywords in SEVERITY_LEVELS.items():
            for keyword in keywords:
                if keyword in text:
                    return severity
        
        return "low"
    
    def _extract_actors(self, entities: dict, text: str) -> List[Dict]:
        """Extract primary actors from entities."""
        actors = []
        
        for country in entities.get("countries", [])[:3]:
            actors.append({
                "type": "country",
                "name": country["name"],
                "iso": country["iso"]
            })
        
        for company in entities.get("companies", [])[:3]:
            actors.append({
                "type": "company",
                "name": company["name"]
            })
        
        return actors
    
    def _generate_event_id(self, article: dict) -> str:
        """Generate a unique event ID from article data."""
        url = article.get("url", "")
        title = article.get("title", "")[:30]
        
        import hashlib
        content = f"{url}{title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def model_batch(self, articles: List[dict]) -> List[dict]:
        """Model a batch of articles into events."""
        events = []
        for article in articles:
            try:
                event = self.model_event(article)
                events.append(event)
            except Exception as e:
                logger.warning(f"Failed to model article: {e}")
                continue
        
        return events
    
    def get_event_clusters(self, events: List[dict]) -> Dict[str, List[dict]]:
        """Group events by similarity/relatedness."""
        clusters = {
            "by_industry": {},
            "by_country": {},
            "by_impact": {"positive": [], "negative": [], "neutral": [], "mixed": []},
            "by_severity": {"critical": [], "high": [], "medium": [], "low": []},
        }
        
        for event in events:
            industry = event.get("sector", "general")
            if industry not in clusters["by_industry"]:
                clusters["by_industry"][industry] = []
            clusters["by_industry"][industry].append(event)
            
            for country in event.get("countries", []):
                if country not in clusters["by_country"]:
                    clusters["by_country"][country] = []
                clusters["by_country"][country].append(event)
            
            impact = event.get("impact", "neutral")
            if impact in clusters["by_impact"]:
                clusters["by_impact"][impact].append(event)
            
            severity = event.get("severity", "low")
            if severity in clusters["by_severity"]:
                clusters["by_severity"][severity].append(event)
        
        return event_modeler = EventModeler()