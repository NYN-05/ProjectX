# News Aggregation and Intelligence System

## 1. Introduction

The News Aggregation and Intelligence System is a comprehensive data-driven application designed to collect, process, analyze, and present news articles from online sources. Unlike a basic script that simply fetches and stores data, this system incorporates multiple layers including data ingestion, natural language processing (NLP), storage, API services, and visualization.

The objective of this project is to transform raw news data into meaningful insights and provide an interactive interface for users to explore and analyze news trends.

---

## 2. Objectives

- Fetch real-time news data from web APIs
- Store structured data efficiently
- Perform NLP-based analysis (sentiment, categorization)
- Provide search and filtering functionality
- Automate data collection
- Build API endpoints for data access
- Visualize trends and insights

---

## 3. System Architecture

The system follows a modular pipeline architecture:

1. **Data Source**: External news providers (NewsAPI)
2. **Data Fetching Module**: Python-based service using `requests` to pull raw headlines.
3. **Data Processing Layer**: NLP pipeline for cleaning, sentiment analysis, and classification.
4. **Database Storage**: Dual storage strategy using MongoDB (primary) and local JSON (fallback).
5. **Backend API Layer**: FastAPI implementation providing RESTful endpoints.
6. **Frontend Dashboard**: React application for interactive data visualization.

---

## 4. Module Description

### 4.1 Data Collection (`app/fetcher.py`)

- Uses NewsAPI to fetch latest headlines from specific countries or categories.
- Handles API errors and missing fields gracefully.
- Extracts key attributes: title, description, source, author, published date, and URL.

### 4.2 Data Processing (`app/processor.py` & `app/utils.py`)

The system implements a multi-stage NLP pipeline:
- **Text Cleaning**: Normalizes whitespace and removes noise from raw text.
- **Duplicate Removal**: Filters out similar articles based on title and URL comparisons.
- **Sentiment Analysis**: Uses `TextBlob` to calculate polarity and subjectivity, labeling articles as Positive, Neutral, or Negative.
- **Category Classification**: A rule-based classifier that assigns articles to categories (Business, Tech, Health, etc.) based on keyword frequency.
- **Keyword Extraction**: Identifies the most significant terms in each article.

### 4.3 Storage Layer (`app/database.py`)

- **MongoDB**: Primary storage for high performance and scalability. Supports full-text search and indexing.
- **JSON Fallback**: Ensures system availability even if the database is offline by caching articles in a local `news.json` file.
- Handles upserts to prevent duplicate records in the database.

### 4.4 API Layer (`app/api.py`)

Built with **FastAPI**, providing the following endpoints:
- `GET /api/news`: Retrieve the latest processed articles.
- `GET /api/search?q={query}`: Search articles by keyword.
- `GET /api/categories`: List all available news categories.
- `GET /api/category/{name}`: Filter articles by category.
- `GET /api/stats`: Retrieve aggregate statistics (sentiment distribution, category counts).

### 4.5 Automation (`app/scheduler.py`)

- Uses the `schedule` library to run background tasks.
- Periodically fetches new articles (default every hour).
- Performs maintenance tasks like cleaning up old articles from local storage.

### 4.6 Visualization Dashboard (`frontend/`)

A modern **React** dashboard that provides:
- **News Feed**: Real-time display of processed articles with sentiment indicators.
- **Sentiment Distribution**: Pie charts showing the overall mood of the news.
- **Category Breakdown**: Visualization of news volume across different sectors.
- **Search & Filter**: Interactive tools to explore specific topics.
- Built with **Recharts** for responsive and interactive visualizations.

---

## 5. Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js & npm
- MongoDB (optional, fallback to JSON available)
- NewsAPI Key (get one at newsapi.org)

### Backend Setup
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn requests textblob schedule pymongo
   ```
2. Set your API Key:
   ```bash
   # Windows
   set NEWS_API_KEY=your_key_here
   ```
3. Run the backend:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dashboard:
   ```bash
   npm start
   ```

---

## 6. Tools and Technologies

- **Languages**: Python, JavaScript (ES6+)
- **Backend Framework**: FastAPI
- **Frontend Library**: React.js
- **NLP**: TextBlob
- **Database**: MongoDB / JSON
- **Visualization**: Recharts
- **HTTP Client**: Axios (Frontend), Requests (Backend)

---

## 7. Advantages

- **Resilience**: Dual-storage strategy ensures data is always available.
- **Intelligence**: Automatically classifies and analyzes sentiment instead of just displaying text.
- **Scalability**: Modular design allows easy addition of new scrapers or NLP models.
- **User-Centric**: Provides both a raw API for developers and a visual dashboard for end-users.

---

## 8. Limitations

- Dependent on NewsAPI free tier limits (e.g., restricted history).
- Rule-based classification may miss nuance in complex articles.
- Sentiment analysis is focused on English language text.

---

## 9. Future Enhancements

- **LLM Integration**: Use OpenAI or Gemini for automated article summarization.
- **User Accounts**: Personalization and "save for later" functionality.
- **Real-time Updates**: Implement WebSockets for instant news delivery without refreshing.
- **Mobile App**: Develop a Flutter or React Native version for mobile users.

---

## 10. Conclusion

The News Aggregation and Intelligence System demonstrates a complete data lifecycle: from ingestion and automated processing to storage, API delivery, and visual presentation. It serves as a robust foundation for building more advanced media monitoring and intelligence tools.
