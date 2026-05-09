import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(`API Error [${error.response.status}]:`, error.response.data);
    } else if (error.request) {
      console.error('API Request failed:', error.request);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Request interceptor for adding auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add timestamp for cache busting
    config.params = config.params || {};
    config.params._ts = new Date().getTime();
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const newsAPI = {
  /**
   * Get latest news articles with optional filters
   * @param {Object} params - Query parameters
   * @param {string} params.country - Country code (default: 'us')
   * @param {number} params.limit - Number of articles (default: 50)
   * @param {number} params.skip - Pagination offset (default: 0)
   * @param {string} params.category - Category filter (optional)
   * @param {string} params.from_date - Start date filter (optional)
   * @param {string} params.to_date - End date filter (optional)
   */
  getNews: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const url = `/news${query ? `?${query}` : ''}`;
    return api.get(url);
  },

  /**
   * Get a specific article by ID
   * @param {string} articleId - Article ID (MongoDB ObjectId or URL)
   */
  getArticle: (articleId) => {
    if (!articleId) {
      return Promise.reject(new Error('Article ID is required'));
    }
    return api.get(`/news/${encodeURIComponent(articleId)}`);
  },

  /**
   * Search for news articles
   * @param {string} query - Search query
   * @param {number} limit - Number of results (default: 50)
   * @param {number} skip - Pagination offset (default: 0)
   */
  getSearch: (query, limit = 50, skip = 0) => {
    if (!query || !query.trim()) {
      return Promise.reject(new Error('Search query cannot be empty'));
    }
    return api.get(`/search?q=${encodeURIComponent(query)}&limit=${limit}&skip=${skip}`);
  },

  /**
   * Get list of available categories
   */
  getCategories: () => {
    return api.get('/categories');
  },

  /**
   * Get news filtered by category
   * @param {string} category - Category name
   * @param {number} limit - Number of articles (default: 50)
   * @param {number} skip - Pagination offset (default: 0)
   */
  getCategory: (category, limit = 50, skip = 0) => {
    if (!category) {
      return Promise.reject(new Error('Category name is required'));
    }
    return api.get(`/category/${encodeURIComponent(category)}?limit=${limit}&skip=${skip}`);
  },

  /**
   * Get statistics about the news data
   */
  getStats: () => {
    return api.get('/stats');
  },

  /**
   * Trigger a one-time news fetch
   */
  fetchNow: () => {
    return api.get('/fetch');
  },

  /**
   * Get RSS feed status
   */
  getRssStatus: () => {
    return api.get('/rss/status');
  },

  /**
   * Get health check status
   */
  getHealth: () => {
    return api.get('/health');
  },

  /**
   * Batch fetch multiple pages
   * @param {Object} params - Fetch parameters
   * @param {number} pages - Number of pages to fetch
   */
  fetchPages: async (params, pages = 3) => {
    const results = [];
    for (let i = 0; i < pages; i++) {
      try {
        const response = await newsAPI.getNews({
          ...params,
          skip: i * params.limit,
        });
        results.push(...(response.data.data || response.data));
      } catch (error) {
        console.warn(`Failed to fetch page ${i + 1}:`, error);
        break;
      }
    }
    return results;
  },
};

export default api;
