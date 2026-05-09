import React, { createContext, useContext, useState, useCallback } from 'react';

// Create the context
const NewsContext = createContext(null);

// Provider component
export function NewsProvider({ children }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [limit, setLimit] = useState(10);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [stats, setStats] = useState({
    totalArticles: 0,
    categories: {},
    sentiment: { positive: 0, negative: 0, neutral: 0 }
  });
  const [storageMode, setStorageMode] = useState('mongodb');
  const [logs, setLogs] = useState([]);

  // Fetch news from API
  const fetchNews = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/news?${new URLSearchParams(params).toString()}`);
      const data = await response.json();
      const articles = data.data || data || [];
      setNews(articles);
      setLastUpdated(new Date());
      setHasMore(articles.length > limit);
      setError(null);
      return articles;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [limit]);

  // Search news
  const searchNews = useCallback(async (query, limit = 50) => {
    if (!query || !query.trim()) {
      setSearchResults([]);
      setSearching(false);
      return;
    }

    setSearching(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=${limit}`);
      const data = await response.json();
      setSearchResults(data.data || data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setSearching(false);
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch('/api/categories');
      const data = await response.json();
      setCategories(data.data || data || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  }, []);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      const statsData = data.data || data;
      setStorageMode(statsData.storage_mode || 'mongodb');
      setStats({
        totalArticles: statsData.total_articles || 0,
        categories: statsData.categories || {},
        sentiment: statsData.sentiment || { positive: 0, negative: 0, neutral: 0 }
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  // Log utility
  const addLog = useCallback((message) => {
    setLogs(prev => [...prev.slice(-15), { timestamp: new Date().toLocaleTimeString(), msg: message }]);
  }, []);

  // Clear logs
  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults([]);
    setHasMore(true);
  }, []);

  // Context value
  const contextValue = {
    // State
    news,
    loading,
    error,
    searchQuery,
    searchResults,
    searching,
    categories,
    selectedCategory,
    limit,
    skip,
    hasMore,
    lastUpdated,
    stats,
    storageMode,
    logs,

    // Actions
    fetchNews,
    searchNews,
    fetchCategories,
    fetchStats,
    setSelectedCategory,
    setLimit,
    setSkip,
    addLog,
    clearLogs,
    clearSearch,
    setError
  };

  return (
    <NewsContext.Provider value={contextValue}>
      {children}
    </NewsContext.Provider>
  );
}

// Custom hook to use the context
export function useNews() {
  const context = useContext(NewsContext);
  if (!context) {
    throw new Error('useNews must be used within a NewsProvider');
  }
  return context;
}
