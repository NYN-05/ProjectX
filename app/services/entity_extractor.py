import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

COUNTRY_PATTERNS = {
    "United States": ["usa", "america", "american", "us ", "u.s.", "united states", "washington", "white house", "congress", "senate", "state department"],
    "United Kingdom": ["uk", "britain", "british", "england", "london", "parliament", "westminster", "downing street"],
    "China": ["china", "chinese", "beijing", "xi jinping", "cpc", "communist party", "shanghai"],
    "Russia": ["russia", "russian", "moscow", "kremlin", "putin", "foreign ministry"],
    "India": ["india", "indian", "delhi", "new delhi", "mumbai", "modi", "parliament"],
    "Germany": ["germany", "german", "berlin", "bundestag", "chancellor"],
    "France": ["france", "french", "paris", "elysee", "macron"],
    "Japan": ["japan", "japanese", "tokyo", "prime minister"],
    "South Korea": ["south korea", "korean", "seoul", "president"],
    "Canada": ["canada", "canadian", "ottawa", "toronto"],
    "Australia": ["australia", "australian", "sydney", "canberra"],
    "Brazil": ["brazil", "brazilian", "brasilia", "sao paulo"],
    "Mexico": ["mexico", "mexican", "mexico city"],
    "Italy": ["italy", "italian", "rome", "vatican"],
    "Spain": ["spain", "spanish", "madrid"],
    "Ukraine": ["ukraine", "ukrainian", "kyiv", "kiev"],
    "Israel": ["israel", "israeli", "tel aviv", "jerusalem"],
    "Iran": ["iran", "iranian", "tehran", "persian"],
    "Saudi Arabia": ["saudi", "saudi arabia", "riyadh"],
    "Turkey": ["turkey", "turkish", "ankara", "istanbul"],
    "Pakistan": ["pakistan", "pakistani", "islamabad"],
    "Indonesia": ["indonesia", "indonesian", "jakarta"],
    "Thailand": ["thailand", "thai", "bangkok"],
    "Vietnam": ["vietnam", "vietnamese", "hanoi"],
    "Nigeria": ["nigeria", "nigerian", "lagos", "abuja"],
    "South Africa": ["south africa", "south african", "johannesburg", "pretoria"],
    "Egypt": ["egypt", "egyptian", "cairo"],
    "Argentina": ["argentina", "argentinian", "buenos aires"],
}

TECHNOLOGY_KEYWORDS = {
    "ai": ["artificial intelligence", "ai", "machine learning", "ml", "deep learning", "neural network", "chatgpt", "gpt", "llm"],
    "semiconductor": ["chip", "semiconductor", "nvidia", "intel", "amd", "tsmc", "processor", "gpu", "tpu"],
    "cybersecurity": ["cyber", "security", "hack", "breach", "malware", "ransomware", "phishing"],
    "cloud": ["cloud", "aws", "azure", "google cloud", "kubernetes", "docker"],
    "quantum": ["quantum", "quantum computing", "qubit"],
    "blockchain": ["blockchain", "crypto", "bitcoin", "ethereum", "nft", "web3"],
    "5g": ["5g", "6g", "telecom", "wireless"],
    "space": ["space", "nasa", "spacex", "satellite", "mars", "rocket"],
    "biotech": ["biotech", "vaccine", "gene", "crispr", "pharma"],
    "energy": ["solar", "wind", "battery", "ev", "electric vehicle", "tesla", "nuclear"],
}

INDUSTRY_KEYWORDS = {
    "finance": ["bank", "stock", "market", "finance", "investment", "wall street", "federal reserve", "inflation", "recession", "gdp"],
    "energy": ["oil", "gas", "petroleum", "energy", "opec", "crude"],
    "technology": ["tech", "software", "digital", "startup", "silicon valley"],
    "healthcare": ["hospital", "doctor", "medical", "health", "patient", "treatment"],
    "automotive": ["car", "automotive", "vehicle", "ford", "toyota", "gm"],
    "retail": ["retail", "amazon", "walmart", "shop", "store"],
    "media": ["media", "news", "journalist", "broadcast", "streaming"],
    "defense": ["military", "defense", "army", "navy", "air force", "weapon", "missile"],
    "agriculture": ["farm", "agriculture", "crop", "food", "wheat", "corn"],
    "real_estate": ["real estate", "property", "housing", "mortgage"],
}

GOVERNMENT_KEYWORDS = {
    "election": ["election", "vote", "voter", "ballot", "campaign"],
    "policy": ["policy", "law", "regulation", "bill", "legislation"],
    "summit": ["summit", "meeting", "conference", "g20", "g7"],
    "treaty": ["treaty", "agreement", "deal", "accord"],
    "sanction": ["sanction", "embargo", "restriction"],
    "war": ["war", "conflict", "battle", "invasion", "military operation"],
    "protest": ["protest", "demonstration", "rally", "march"],
    "crisis": ["crisis", "emergency", "disaster"],
}

PERSON_TITLE_PATTERNS = [
    r"\b(president|prime minister|chancellor|governor|senator|minister|secretary)\s+(\w+\s+){0,2}\w+",
    r"\b(ceo|cto|cfo|coo|cmo)\s+(\w+\s+){0,2}\w+",
    r"\b(dr\.|mr\.|mrs\.|ms\.)\s+(\w+\s+){1,2}\w+",
    r"\b(\w+)\s+(said|announced|confirmed|revealed|stated|declared)",
    r"\b(sources|sources\s+(say|tell|reveal|inform))",
]


class EntityExtractor:
    def __init__(self):
        self._country_cache = {}
        self._company_patterns = self._compile_company_patterns()
    
    def _compile_company_patterns(self) -> List[Tuple[str, re.Pattern]]:
        companies = [
            "Apple", "Microsoft", "Google", "Amazon", "Meta", "Facebook", "Tesla", "Nvidia",
            "Intel", "AMD", "Qualcomm", "TSMC", "Samsung", "Sony", "IBM", "Oracle", "Salesforce",
            "Netflix", "Disney", "Warner", "Universal", "Tencent", "Alibaba", "ByteDance",
            "OpenAI", "Anthropic", "Midjourney", "Stability AI", "Adobe", "Autodesk",
            "Goldman Sachs", "Morgan Stanley", "JPMorgan", "Citigroup", "Bank of America",
            "Exxon", "Shell", "BP", "Chevron", "TotalEnergies", "OPEC",
            "Pfizer", "Moderna", "Johnson & Johnson", "Merck", "Novartis", "Roche",
            "Toyota", "Honda", "Ford", "GM", "Volkswagen", "BMW", "Mercedes", "Hyundai",
            "United Nations", "NATO", "EU", "World Bank", "IMF", "WHO", "FDA",
        ]
        return [(name, re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)) for name in companies]
    
    def extract_all(self, article: dict) -> dict:
        """Extract all entities from an article."""
        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
        
        return {
            "countries": self.extract_countries(text),
            "companies": self.extract_companies(text),
            "people": self.extract_people(text),
            "industries": self.extract_industries(text),
            "technologies": self.extract_technologies(text),
            "topics": self.extract_topics(text),
            "governments": self.extract_government_entities(text),
        }
    
    def extract_countries(self, text: str) -> List[Dict[str, str]]:
        """Extract country mentions with ISO codes."""
        text_lower = text.lower()
        found = []
        seen = set()
        
        for country, keywords in COUNTRY_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower and country not in seen:
                    iso = self._get_country_iso(country)
                    found.append({"name": country, "iso": iso, "mention": keyword})
                    seen.add(country)
                    break
        
        return found
    
    def _get_country_iso(self, country_name: str) -> str:
        iso_map = {
            "United States": "US", "United Kingdom": "GB", "China": "CN", "Russia": "RU",
            "India": "IN", "Germany": "DE", "France": "FR", "Japan": "JP", "South Korea": "KR",
            "Canada": "CA", "Australia": "AU", "Brazil": "BR", "Mexico": "MX", "Italy": "IT",
            "Spain": "ES", "Ukraine": "UA", "Israel": "IL", "Iran": "IR", "Saudi Arabia": "SA",
            "Turkey": "TR", "Pakistan": "PK", "Indonesia": "ID", "Thailand": "TH", "Vietnam": "VN",
            "Nigeria": "NG", "South Africa": "ZA", "Egypt": "EG", "Argentina": "AR",
        }
        return iso_map.get(country_name, "XX")
    
    def extract_companies(self, text: str) -> List[Dict[str, str]]:
        """Extract company mentions."""
        found = []
        seen = set()
        
        for name, pattern in self._company_patterns:
            if pattern.search(text) and name not in seen:
                found.append({"name": name, "type": "company"})
                seen.add(name)
        
        return found
    
    def extract_people(self, text: str) -> List[str]:
        """Extract person names using patterns."""
        people = []
        
        for pattern in PERSON_TITLE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    name = " ".join(m for m in match if m and len(m) > 2)
                    if name and name not in people:
                        people.append(name[:50])
                elif match and len(match) > 3:
                    if match not in people:
                        people.append(match[:50])
        
        return list(set(people))[:10]
    
    def extract_industries(self, text: str) -> List[str]:
        """Extract industry mentions."""
        text_lower = text.lower()
        industries = []
        
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    industries.append(industry)
                    break
        
        return list(set(industries))
    
    def extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions."""
        text_lower = text.lower()
        technologies = []
        
        for tech, keywords in TECHNOLOGY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    technologies.append(tech)
                    break
        
        return list(set(technologies))
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract topic keywords."""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in GOVERNMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    topics.append(topic)
                    break
        
        return list(set(topics))
    
    def extract_government_entities(self, text: str) -> List[str]:
        """Extract government/international organization references."""
        text_lower = text.lower()
        entities = []
        
        org_patterns = [
            r"\b(United Nations|UN)\b",
            r"\b(NATO)\b",
            r"\b(European Union|EU)\b",
            r"\b(World Trade Organization|WTO)\b",
            r"\b(International Monetary Fund|IMF)\b",
            r"\b(World Bank)\b",
            r"\b(Federal Reserve|Fed)\b",
            r"\b(OPEC)\b",
            r"\b(WHO|World Health Organization)\b",
            r"\b(FDA)\b",
            r"\b(Central Bank)\b",
            r"\b(Securities and Exchange Commission|SEC)\b",
            r"\b(Justice Department|DOJ)\b",
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 1:
                    entities.append(match)
        
        return list(set(entities))[:10]
    
    def get_entity_summary(self, article: dict) -> dict:
        """Get a summary of all extracted entities."""
        entities = self.extract_all(article)
        
        return {
            "entity_count": sum(len(v) if isinstance(v, list) else 1 for v in entities.values()),
            "has_countries": len(entities.get("countries", [])) > 0,
            "has_companies": len(entities.get("companies", [])) > 0,
            "has_people": len(entities.get("people", [])) > 0,
            "primary_industries": entities.get("industries", [])[:3],
            "primary_technologies": entities.get("technologies", [])[:3],
            "primary_topics": entities.get("topics", [])[:3],
        }


entity_extractor = EntityExtractor()