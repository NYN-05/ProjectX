import logging
import re
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

SOURCE_COUNTRY_MAP = {
    "BBC News": "GB",
    "BBC": "GB",
    "CNN": "US",
    "Al Jazeera": "QA",
    "NY Times": "US",
    "New York Times": "US",
    "The Guardian": "GB",
    "CNBC": "US",
    "ABC News": "US",
    "Fox News": "US",
    "WSJ": "US",
    "Wall Street Journal": "US",
    "Reuters": "GB",
    "NDTV": "IN",
    "The Times of India": "IN",
    "India Today": "IN",
    "The Hindu": "IN",
    "The Indian Express": "IN",
    "Hindustan Times": "IN",
    "Zee News": "IN",
    "The Print": "IN",
    "News18": "IN",
    "Business Standard": "IN",
    "The Washington Post": "US",
    "USA Today": "US",
    "Los Angeles Times": "US",
    "Bloomberg": "US",
    "Forbes": "US",
    "TechCrunch": "US",
    "The Verge": "US",
    "Wired": "US",
    "Ars Technica": "US",
    "Engadget": "US",
    "The Hindu": "IN",
    "Deccan Chronicle": "IN",
    "The Telegraph": "GB",
    "Daily Mail": "GB",
    "The Sun": "GB",
    "Sky News": "GB",
    " ITV": "GB",
    "Channel 4": "GB",
    "Euronews": "FR",
    "France 24": "FR",
    "Le Monde": "FR",
    "Der Spiegel": "DE",
    "Die Zeit": "DE",
    "Tagesschau": "DE",
    "Süddeutsche Zeitung": "DE",
    "El País": "ES",
    "ABC": "ES",
    "La Vanguardia": "ES",
    "Corriere della Sera": "IT",
    "La Repubblica": "IT",
    "ANSA": "IT",
    "Rai News": "IT",
    "TASS": "RU",
    "RT": "RU",
    "Kommersant": "RU",
    "Xinhua": "CN",
    "CCTV": "CN",
    "People's Daily": "CN",
    "Global Times": "CN",
    "Nikkei": "JP",
    "Yomiuri Shimbun": "JP",
    "Asahi Shimbun": "JP",
    "Mainichi": "JP",
    "Korea Herald": "KR",
    "Korea Times": "KR",
    "Yonhap": "KR",
    "The Star": "MY",
    "Malaysiakini": "MY",
    "Straits Times": "SG",
    "The Nation": "TH",
    "Bangkok Post": "TH",
    "Vietnam News": "VN",
    "Tuổi Trẻ": "VN",
    "The Australian": "AU",
    "ABC Australia": "AU",
    "BBC News": "GB",
    "CBC": "CA",
    "The Globe and Mail": "CA",
    "La Presse": "CA",
    "El Universal": "MX",
    "Reforma": "MX",
    "Folha de S.Paulo": "BR",
    "O Globo": "BR",
    "Estadao": "BR",
    "Clarín": "AR",
    "La Nación": "AR",
    "El Tiempo": "CO",
    "Publimetro": "CL",
    "La Tercera": "CL",
    "The New Arab": "EG",
    "Ahram Online": "EG",
    "Gulf News": "AE",
    "The National": "AE",
    "Arab News": "SA",
    "Saudi Gazette": "SA",
    "Times of Israel": "IL",
    "Haaretz": "IL",
    "The Jerusalem Post": "IL",
    "Daily Nation": "KE",
    "The Standard": "KE",
    "Mail & Guardian": "ZA",
    "Business Day": "ZA",
}

COUNTRY_DATA = {
    "GB": {"name": "United Kingdom", "lat": 55.3781, "lng": -3.4360},
    "US": {"name": "United States", "lat": 37.0902, "lng": -95.7129},
    "IN": {"name": "India", "lat": 20.5937, "lng": 78.9629},
    "QA": {"name": "Qatar", "lat": 25.3548, "lng": 51.1839},
    "FR": {"name": "France", "lat": 46.2276, "lng": 2.2137},
    "DE": {"name": "Germany", "lat": 51.1657, "lng": 10.4515},
    "ES": {"name": "Spain", "lat": 40.4637, "lng": -3.7492},
    "IT": {"name": "Italy", "lat": 41.8719, "lng": 12.5674},
    "RU": {"name": "Russia", "lat": 61.5240, "lng": 105.3188},
    "CN": {"name": "China", "lat": 35.8617, "lng": 104.1954},
    "JP": {"name": "Japan", "lat": 36.2048, "lng": 138.2529},
    "KR": {"name": "South Korea", "lat": 35.9078, "lng": 127.7669},
    "MY": {"name": "Malaysia", "lat": 4.2105, "lng": 101.9758},
    "SG": {"name": "Singapore", "lat": 1.3521, "lng": 103.8198},
    "TH": {"name": "Thailand", "lat": 15.8700, "lng": 100.9925},
    "VN": {"name": "Vietnam", "lat": 14.0583, "lng": 108.2772},
    "AU": {"name": "Australia", "lat": -25.2744, "lng": 133.7751},
    "CA": {"name": "Canada", "lat": 56.1304, "lng": -106.3468},
    "MX": {"name": "Mexico", "lat": 23.6345, "lng": -102.5528},
    "BR": {"name": "Brazil", "lat": -14.2350, "lng": -51.9253},
    "AR": {"name": "Argentina", "lat": -38.4161, "lng": -63.6167},
    "CO": {"name": "Colombia", "lat": 4.5709, "lng": -74.2973},
    "CL": {"name": "Chile", "lat": -35.6751, "lng": -71.5430},
    "EG": {"name": "Egypt", "lat": 26.8206, "lng": 30.8025},
    "AE": {"name": "United Arab Emirates", "lat": 23.4241, "lng": 53.8478},
    "SA": {"name": "Saudi Arabia", "lat": 23.8859, "lng": 45.0792},
    "IL": {"name": "Israel", "lat": 31.0461, "lng": 34.8516},
    "KE": {"name": "Kentha", "lat": -0.0236, "lng": 37.9062},
    "ZA": {"name": "South Africa", "lat": -30.5595, "lng": 22.9375},
    "NG": {"name": "Nigeria", "lat": 9.0820, "lng": 8.6753},
    "PK": {"name": "Pakistan", "lat": 30.3753, "lng": 69.3451},
    "BD": {"name": "Bangladesh", "lat": 23.6850, "lng": 90.3563},
    "ID": {"name": "Indonesia", "lat": -0.7893, "lng": 113.9213},
    "PH": {"name": "Philippines", "lat": 12.8797, "lng": 121.7740},
    "TR": {"name": "Turkey", "lat": 38.9637, "lng": 35.2433},
    "NL": {"name": "Netherlands", "lat": 52.1326, "lng": 5.2913},
    "BE": {"name": "Belgium", "lat": 50.5039, "lng": 4.4699},
    "SE": {"name": "Sweden", "lat": 60.1282, "lng": 18.6435},
    "NO": {"name": "Norway", "lat": 60.4720, "lng": 8.4689},
    "DK": {"name": "Denmark", "lat": 56.2639, "lng": 9.5018},
    "FI": {"name": "Finland", "lat": 61.9241, "lng": 25.7482},
    "CH": {"name": "Switzerland", "lat": 46.8182, "lng": 8.2275},
    "AT": {"name": "Austria", "lat": 47.5162, "lng": 14.5501},
    "PL": {"name": "Poland", "lat": 51.9194, "lng": 19.1451},
    "PT": {"name": "Portugal", "lat": 39.3999, "lng": -8.2245},
    "GR": {"name": "Greece", "lat": 39.0742, "lng": 21.8243},
    "IE": {"name": "Ireland", "lat": 53.1424, "lng": -7.6921},
    "NZ": {"name": "New Zealand", "lat": -40.9006, "lng": 174.8860},
}

FALLBACK_COUNTRY = "US"
FALLBACK_COUNTRY_DATA = COUNTRY_DATA.get(FALLBACK_COUNTRY, {"name": "United States", "lat": 37.0902, "lng": -95.7129})


class GeolocationProcessor:
    def __init__(self):
        self._country_cache = {}
    
    def detect_country(self, source_name: str, article_title: str = "", article_description: str = "") -> Dict:
        """
        Detect country from article source and content.
        Returns country code, name, lat, lng, and confidence.
        """
        cache_key = source_name
        if cache_key in self._country_cache:
            return self._country_cache[cache_key]
        
        country_code = self._map_source_to_country(source_name)
        
        if not country_code:
            country_code = self._extract_country_from_content(article_title, article_description)
        
        if not country_code:
            country_code = FALLBACK_COUNTRY
        
        country_data = COUNTRY_DATA.get(country_code, FALLBACK_COUNTRY_DATA)
        
        result = {
            "country": country_data["name"],
            "country_code": country_code,
            "latitude": country_data["lat"],
            "longitude": country_data["lng"],
            "confidence": 0.9 if country_code != FALLBACK_COUNTRY else 0.3
        }
        
        self._country_cache[cache_key] = result
        return result
    
    def _map_source_to_country(self, source_name: str) -> Optional[str]:
        """Map source name to country code."""
        if not source_name:
            return None
        
        source_normalized = source_name.strip()
        
        if source_normalized in SOURCE_COUNTRY_MAP:
            return SOURCE_COUNTRY_MAP[source_normalized]
        
        for known_source, country_code in SOURCE_COUNTRY_MAP.items():
            if known_source.lower() in source_normalized.lower():
                return country_code
        
        return None
    
    def _extract_country_from_content(self, title: str, description: str) -> Optional[str]:
        """Extract country from article content using keyword matching."""
        if not title and not description:
            return None
        
        text = f"{title} {description}".lower()
        
        country_keywords = {
            "india": "IN", "indian": "IN", "delhi": "IN", "mumbai": "IN", "kolkata": "IN",
            "china": "CN", "beijing": "CN", "shanghai": "CN",
            "uk": "GB", "britain": "GB", "british": "GB", "london": "GB", "england": "GB",
            "usa": "US", "america": "US", "american": "US", "washington": "US", "new york": "US",
            "russia": "RU", "moscow": "RU", "russian": "RU",
            "japan": "JP", "tokyo": "JP", "japanese": "JP",
            "korea": "KR", "seoul": "KR", "korean": "KR",
            "france": "FR", "paris": "FR", "french": "FR",
            "germany": "DE", "berlin": "DE", "german": "DE",
            "brazil": "BR", "brasília": "BR", "brazilian": "BR",
            "australia": "AU", "sydney": "AU", "australian": "AU",
            "canada": "CA", "ottawa": "CA", "canadian": "CA",
            "mexico": "MX", "mexican": "MX",
            "italy": "IT", "rome": "IT", "italian": "IT",
            "spain": "ES", "madrid": "ES", "spanish": "ES",
            "pakistan": "PK", "pakistani": "PK",
            "israel": "IL", "tel aviv": "IL", "israeli": "IL",
            "egypt": "EG", "cairo": "EG", "egyptian": "EG",
            "south africa": "ZA", "johannesburg": "ZA",
            "nigeria": "NG", "lagos": "NG",
            "indonesia": "ID", "jakarta": "ID",
            "thailand": "TH", "bangkok": "TH",
            "vietnam": "VN", "hanoi": "VN",
            "singapore": "SG", "singaporean": "SG",
            "malaysia": "MY", "kuala lumpur": "MY",
            "philippines": "PH", "manila": "PH",
            "netherlands": "NL", "amsterdam": "NL",
            "switzerland": "CH", "zurich": "CH",
        }
        
        for keyword, country_code in country_keywords.items():
            if keyword in text:
                return country_code
        
        return None
    
    def process_article(self, article: dict) -> dict:
        """Add geolocation data to an article."""
        source_name = article.get("source", {}).get("name", "")
        title = article.get("title", "")
        description = article.get("description", "")
        
        geo = self.detect_country(source_name, title, description)
        
        article["country"] = geo["country"]
        article["country_code"] = geo["country_code"]
        article["latitude"] = geo["latitude"]
        article["longitude"] = geo["longitude"]
        article["geo_confidence"] = geo["confidence"]
        
        return article
    
    def process_batch(self, articles: list) -> list:
        """Process a batch of articles."""
        return [self.process_article(article) for article in articles]
    
    def get_country_stats(self, articles: list) -> Dict:
        """Get aggregated country statistics from articles."""
        country_counts = {}
        
        for article in articles:
            code = article.get("country_code", FALLBACK_COUNTRY)
            country_counts[code] = country_counts.get(code, 0) + 1
        
        result = {}
        for code, count in country_counts.items():
            data = COUNTRY_DATA.get(code, FALLBACK_COUNTRY_DATA)
            result[code] = {
                "country": data["name"],
                "count": count,
                "latitude": data["lat"],
                "longitude": data["lng"]
            }
        
        return result


geolocation_processor = GeolocationProcessor()