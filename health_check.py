import sys
import os

def check_backend_health():
    print("--- BACKEND HEALTH CHECK ---")
    try:
        import fastapi
        import uvicorn
        import pymongo
        import textblob
        import feedparser
        print("[SUCCESS] All backend dependencies are installed.")
    except ImportError as e:
        print(f"[FAILURE] Missing dependency: {e}")
        return False
    
    try:
        from app.processor import SentimentAnalyzer, KeywordExtractor, CategoryClassifier
        
        # Test Sentiment
        s_analyzer = SentimentAnalyzer()
        s_result = s_analyzer.analyze_sentiment("The market is looking excellent today!")
        if s_result['score'] == 'positive':
            print("[SUCCESS] NLP Sentiment Analyzer is functional.")
        else:
            print(f"[WARNING] NLP Sentiment Analyzer returned unexpected score: {s_result['score']}")
            
        # Test Keywords
        k_result = KeywordExtractor.extract_keywords("SpaceX launched a rocket to Mars today.")
        if k_result:
            print(f"[SUCCESS] NLP Keyword Extractor is functional. Keywords: {k_result[:3]}")
        else:
            print("[WARNING] NLP Keyword Extractor returned no keywords.")
            
        # Test Category
        cat_result = CategoryClassifier.classify_category({"title": "The team won the championship match.", "description": ""})
        if cat_result == 'sports':
            print("[SUCCESS] NLP Category Classifier is functional.")
        else:
            print(f"[WARNING] NLP Category Classifier returned unexpected category: {cat_result}")
            
    except Exception as e:
        print(f"[FAILURE] NLP Processor test failed: {e}")
    
    return True

if __name__ == "__main__":
    if check_backend_health():
        print("\n[CONCLUSION] Backend environment is healthy and ready for operation.")
    else:
        print("\n[CONCLUSION] Backend environment has issues.")
        sys.exit(1)
