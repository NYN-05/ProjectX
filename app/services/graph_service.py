import logging
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class GraphService:
    """
    In-memory graph storage for intelligence events and relationships.
    Provides fast querying and traversal capabilities.
    """
    
    def __init__(self, cache_dir: str = None):
        self._nodes = {}
        self._edges = defaultdict(list)
        self._node_index = defaultdict(set)
        self._event_type_index = defaultdict(set)
        self._country_index = defaultdict(set)
        self._industry_index = defaultdict(set)
        self.cache_dir = cache_dir or "data"
    
    def add_event(self, event: dict) -> None:
        """Add an event as a node in the graph."""
        event_id = event.get("event_id")
        
        node = {
            "id": event_id,
            "type": "event",
            "event_type": event.get("event_type", "general"),
            "title": event.get("title", "")[:100],
            "sector": event.get("sector", "general"),
            "impact": event.get("impact", "neutral"),
            "severity": event.get("severity", "low"),
            "timestamp": event.get("timestamp"),
            "source": event.get("source"),
            "url": event.get("url"),
            "countries": event.get("countries", []),
            "companies": event.get("companies", []),
            "industries": event.get("industries", []),
            "technologies": event.get("technologies", []),
            "actors": event.get("actors", []),
            "geolocation": event.get("geolocation"),
            "embedding_text": event.get("embedding_text", ""),
            "created_at": datetime.now().isoformat()
        }
        
        self._nodes[event_id] = node
        
        self._event_type_index[event.get("event_type", "general")].add(event_id)
        
        for country in event.get("countries", []):
            self._country_index[country].add(event_id)
        
        for industry in event.get("industries", []):
            self._industry_index[industry].add(event_id)
    
    def add_relationship(self, relationship: dict) -> None:
        """Add an edge between events."""
        source_id = relationship.get("source_id")
        target_id = relationship.get("target_id")
        
        if source_id not in self._nodes or target_id not in self._nodes:
            return
        
        edge = {
            "source": source_id,
            "target": target_id,
            "type": relationship.get("type", "related"),
            "strength": relationship.get("strength", 0),
            "confidence": relationship.get("confidence", 0),
            "reasons": relationship.get("reasons", []),
            "timestamp": relationship.get("timestamp", datetime.now().isoformat())
        }
        
        self._edges[source_id].append(edge)
        
        if relationship.get("type") not in ["causes", "depends_on"]:
            self._edges[target_id].append({
                **edge,
                "source": target_id,
                "target": source_id
            })
    
    def add_events_batch(self, events: List[dict]) -> int:
        """Add multiple events to the graph."""
        count = 0
        for event in events:
            self.add_event(event)
            count += 1
        logger.info(f"Added {count} events to graph")
        return count
    
    def add_relationships_batch(self, relationships: List[dict]) -> int:
        """Add multiple relationships to the graph."""
        count = 0
        for rel in relationships:
            self.add_relationship(rel)
            count += 1
        logger.info(f"Added {count} relationships to graph")
        return count
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """Get an event by ID."""
        return self._nodes.get(event_id)
    
    def get_neighbors(self, event_id: str, edge_type: str = None) -> List[Dict]:
        """Get neighboring events."""
        neighbors = []
        
        for edge in self._edges.get(event_id, []):
            if edge_type and edge.get("type") != edge_type:
                continue
            
            neighbor_id = edge.get("target")
            neighbor = self._nodes.get(neighbor_id)
            if neighbor:
                neighbors.append({
                    "event": neighbor,
                    "relationship": edge
                })
        
        return neighbors
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get all events of a specific type."""
        event_ids = self._event_type_index.get(event_type, set())
        return [self._nodes[eid] for eid in event_ids if eid in self._nodes]
    
    def get_events_by_country(self, country_code: str) -> List[Dict]:
        """Get all events involving a country."""
        event_ids = self._country_index.get(country_code, set())
        return [self._nodes[eid] for eid in event_ids if eid in self._nodes]
    
    def get_events_by_industry(self, industry: str) -> List[Dict]:
        """Get all events in an industry."""
        event_ids = self._industry_index.get(industry, set())
        return [self._nodes[eid] for eid in event_ids if eid in self._nodes]
    
    def search_events(self, query: str, limit: int = 20) -> List[Dict]:
        """Search events by title."""
        results = []
        query_lower = query.lower()
        
        for event in self._nodes.values():
            if query_lower in event.get("title", "").lower():
                results.append(event)
        
        return results[:limit]
    
    def get_graph_data(self, limit: int = 100) -> Dict:
        """Get graph data for visualization."""
        nodes = []
        edges = []
        
        for event_id, event in list(self._nodes.items())[:limit]:
            nodes.append({
                "id": event_id,
                "type": "event",
                "label": event.get("title", "")[:50],
                "event_type": event.get("event_type"),
                "sector": event.get("sector"),
                "impact": event.get("impact"),
                "severity": event.get("severity"),
                "countries": event.get("countries", []),
                "industries": event.get("industries", [])
            })
        
        for source_id, edge_list in self._edges.items():
            for edge in edge_list:
                if len(edges) >= limit * 2:
                    break
                
                edges.append({
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "type": edge.get("type"),
                    "strength": edge.get("strength"),
                    "confidence": edge.get("confidence")
                })
            
            if len(edges) >= limit * 2:
                break
        
        return {
            "nodes": nodes[:limit],
            "edges": edges[:limit * 2],
            "stats": {
                "total_nodes": len(self._nodes),
                "total_edges": sum(len(e) for e in self._edges.values()),
                "event_types": len(self._event_type_index),
                "countries": len(self._country_index),
                "industries": len(self._industry_index)
            }
        }
    
    def get_central_events(self, limit: int = 10) -> List[Dict]:
        """Get events with most connections."""
        connection_counts = []
        
        for event_id in self._nodes:
            connections = len(self._edges.get(event_id, []))
            event = self._nodes[event_id]
            connection_counts.append({
                "event": event,
                "connection_count": connections
            })
        
        connection_counts.sort(key=lambda x: x["connection_count"], reverse=True)
        return connection_counts[:limit]
    
    def get_entity_network(self, entity_type: str, entity_name: str) -> Dict:
        """Get network of events related to an entity."""
        if entity_type == "country":
            event_ids = self._country_index.get(entity_name, set())
        elif entity_type == "industry":
            event_ids = self._industry_index.get(entity_name, set())
        else:
            return {"events": [], "relationships": []}
        
        events = [self._nodes[eid] for eid in event_ids if eid in self._nodes]
        
        relationships = []
        for eid in event_ids:
            for edge in self._edges.get(eid, []):
                if edge.get("target") in event_ids:
                    relationships.append(edge)
        
        return {
            "entity_type": entity_type,
            "entity_name": entity_name,
            "events": events,
            "relationships": relationships,
            "event_count": len(events)
        }
    
    def get_temporal_clusters(self, days: int = 7) -> List[List[Dict]]:
        """Get clusters of events that occurred around the same time."""
        pass
    
    def get_impact_analysis(self) -> Dict:
        """Analyze event impact distribution."""
        impacts = defaultdict(int)
        severities = defaultdict(int)
        sectors = defaultdict(int)
        
        for event in self._nodes.values():
            impacts[event.get("impact", "neutral")] += 1
            severities[event.get("severity", "low")] += 1
            sectors[event.get("sector", "general")] += 1
        
        return {
            "by_impact": dict(impacts),
            "by_severity": dict(severities),
            "by_sector": dict(sectors)
        }
    
    def clear(self) -> None:
        """Clear all graph data."""
        self._nodes.clear()
        self._edges.clear()
        self._node_index.clear()
        self._event_type_index.clear()
        self._country_index.clear()
        self._industry_index.clear()
        logger.info("Graph cleared")
    
    def export(self) -> Dict:
        """Export graph data."""
        return {
            "events": list(self._nodes.values()),
            "relationships": [
                {**e, "source": src} 
                for src, edges in self._edges.items() 
                for e in edges
            ],
            "exported_at": datetime.now().isoformat()
        }
    
    def load(self, data: Dict) -> None:
        """Load graph data."""
        self.clear()
        
        for event in data.get("events", []):
            self.add_event(event)
        
        for rel in data.get("relationships", []):
            self.add_relationship(rel)
        
        logger.info(f"Loaded {len(self._nodes)} events and {sum(len(e) for e in self._edges.values())} relationships")
    
    @property
    def node_count(self) -> int:
        """Get total number of nodes."""
        return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        """Get total number of edges."""
        return sum(len(e) for e in self._edges.values())


graph_service = GraphService()