import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import {
  Activity, Search, TrendingUp, Globe, AlertCircle,
  RefreshCw, Database, Wifi, TrendingDown, Filter, ArrowUpCircle,
  Loader, Clock, Tag, ExternalLink, Hash, ChevronDown, X, Zap, BarChart2
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { newsAPI } from './services/api';

const SENTIMENT_COLORS = {
  positive: '#7DC97D',
  negative: '#E85D4C',
  neutral: '#8B8B8B'
};

const CATEGORY_COLORS = {
  business: '#4A90D9',
  technology: '#9B7DD4',
  health: '#D97D9B',
  sports: '#7DC97D',
  entertainment: '#D97DC9',
  science: '#7DD9D9',
  politics: '#D97D7D',
  crime: '#8B8B8B',
  general: '#6B6459'
};

function App() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [displayCount, setDisplayCount] = useState(8);
  const [activeView, setActiveView] = useState('feed');
  const [stats, setStats] = useState({
    totalArticles: 0,
    categories: {},
    sentiment: { positive: 0, negative: 0, neutral: 0 }
  });
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchNews();
    fetchCategories();
    fetchStats();
    const interval = setInterval(fetchNews, 300000);
    return () => clearInterval(interval);
  }, []);

  const sentimentStats = useMemo(() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    news.forEach(article => {
      const s = article.sentiment?.score || 'neutral';
      counts[s] = (counts[s] || 0) + 1;
    });
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    return Object.keys(counts).map(key => ({
      name: key,
      value: counts[key],
      percent: total ? Math.round((counts[key] / total) * 100) : 0,
      color: SENTIMENT_COLORS[key]
    }));
  }, [news]);

  const categoryStats = useMemo(() => {
    const counts = {};
    news.forEach(article => {
      const c = article.category || 'general';
      counts[c] = (counts[c] || 0) + 1;
    });
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value, percent: total ? Math.round((value / total) * 100) : 0 }))
      .sort((a, b) => b.value - a.value);
  }, [news]);

  const topKeywords = useMemo(() => {
    const freq = {};
    news.forEach(a => {
      (a.keywords || []).forEach(kw => {
        freq[kw] = (freq[kw] || 0) + 1;
      });
    });
    return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([kw]) => kw);
  }, [news]);

  const activeNews = useMemo(() => {
    if (searchQuery && searchResults.length > 0) return searchResults;
    if (selectedCategory) return news.filter(a => (a.category || 'general') === selectedCategory);
    return news;
  }, [searchQuery, searchResults, news, selectedCategory]);

  const displayedNews = useMemo(() => activeNews.slice(0, displayCount), [activeNews, displayCount]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const response = await newsAPI.getNews({ limit: 50, skip: 0 });
      const articles = response.data.data || [];
      setNews(articles);
      setLastUpdated(new Date());
      setHasMore(articles.length > displayCount);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await newsAPI.getCategories();
      setCategories(response.data.data || []);
    } catch (err) { /* silent */ }
  };

  const fetchStats = async () => {
    try {
      const response = await newsAPI.getStats();
      const data = response.data.data || response.data;
      setStats({
        totalArticles: data.total_articles || 0,
        categories: data.categories || {},
        sentiment: data.sentiment || { positive: 0, negative: 0, neutral: 0 }
      });
    } catch (err) { /* silent */ }
  };

  const handleSearch = useCallback(async (query) => {
    setSearchQuery(query);
    if (!query.trim()) { setSearchResults([]); return; }
    setSearching(true);
    try {
      const response = await newsAPI.getSearch(query, 50, 0);
      setSearchResults(response.data.data || []);
    } catch (err) { setError(err.message); }
    finally { setSearching(false); }
  }, []);

  const handleCategorySelect = (cat) => {
    setSelectedCategory(cat === selectedCategory ? null : cat);
    setActiveView('feed');
  };

  const handleRefresh = async () => {
    await fetchNews();
    await fetchStats();
  };

  const handleLoadMore = () => setDisplayCount(prev => prev + 8);

  const handleFetchNow = async () => {
    await newsAPI.fetchNow();
    await fetchNews();
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-base)' }}>
      {/* Header */}
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border)' }}>
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div>
                <h1 className="text-3xl text-[var(--text-primary)]" style={{ fontFamily: 'Bebas Neue, sans-serif', letterSpacing: '0.08em' }}>
                  THE WIRE
                </h1>
                <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-[0.3em] mt-1" style={{ fontFamily: 'DM Mono, monospace' }}>
                  News Intelligence Platform
                </p>
              </div>
              <div className="h-10 w-px" style={{ background: 'var(--border)' }} />
              <div className="flex items-center gap-2">
                <Wifi size={14} style={{ color: 'var(--positive)' }} />
                <span className="text-[11px]" style={{ color: 'var(--text-secondary)', fontFamily: 'DM Mono, monospace' }}>
                  {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Connecting...'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={handleRefresh} disabled={loading} className="btn-ghost flex items-center gap-2">
                <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
                Refresh
              </button>
              <button onClick={handleFetchNow} className="btn-primary">Fetch Now</button>
            </div>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      <div className="max-w-7xl mx-auto px-6 py-5">
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search articles, topics, sources..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input pl-12"
            style={{ fontSize: 14 }}
          />
          {searching && (
            <Loader size={14} style={{ position: 'absolute', right: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--accent)', animation: 'spin 1s linear infinite' }} />
          )}
        </div>
      </div>

      {/* Stats Strip */}
      <div className="max-w-7xl mx-auto px-6 pb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Articles', value: stats.totalArticles || news.length, color: 'var(--text-primary)' },
            { label: 'Positive', value: stats.sentiment.positive || 0, color: 'var(--positive)' },
            { label: 'Negative', value: stats.sentiment.negative || 0, color: 'var(--danger)' },
            { label: 'Neutral', value: stats.sentiment.neutral || 0, color: 'var(--neutral)' },
          ].map((s, i) => (
            <div key={i} className="card p-4">
              <p className="stat-number" style={{ color: s.color }}>{s.value}</p>
              <p className="stat-label mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Main Column */}
          <div className="lg:col-span-8 space-y-6">

            {/* Category Pills */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => { setSelectedCategory(null); setActiveView('feed'); }}
                className={`badge ${!selectedCategory ? 'badge-category' : ''}`}
                style={{ background: !selectedCategory ? 'var(--accent)' : 'var(--bg-surface)', color: !selectedCategory ? 'var(--bg-base)' : 'var(--text-secondary)', borderColor: !selectedCategory ? 'var(--accent)' : 'var(--border)' }}
              >
                All
              </button>
              {categoryStats.map(cat => (
                <button
                  key={cat.name}
                  onClick={() => handleCategorySelect(cat.name)}
                  className="badge"
                  style={{
                    background: selectedCategory === cat.name ? CATEGORY_COLORS[cat.name] || 'var(--accent)' : 'var(--bg-surface)',
                    color: selectedCategory === cat.name ? 'var(--bg-base)' : (CATEGORY_COLORS[cat.name] || 'var(--text-secondary)'),
                    borderColor: selectedCategory === cat.name ? 'transparent' : 'var(--border)',
                  }}
                >
                  {cat.name} <span style={{ opacity: 0.7 }}>({cat.value})</span>
                </button>
              ))}
            </div>

            {/* Error Banner */}
            {error && (
              <div className="card p-4 flex items-center gap-3" style={{ borderLeftColor: 'var(--danger)', borderLeftWidth: 3 }}>
                <AlertCircle size={16} style={{ color: 'var(--danger)' }} />
                <span style={{ color: 'var(--danger)', fontSize: 12 }}>{error}</span>
                <button onClick={() => setError(null)} style={{ marginLeft: 'auto' }}>
                  <X size={14} style={{ color: 'var(--text-muted)' }} />
                </button>
              </div>
            )}

            {/* Articles */}
            {loading && news.length === 0 ? (
              <div className="space-y-4">
                {[1,2,3,4].map(i => (
                  <div key={i} className="card p-5 skeleton" style={{ height: 140 }} />
                ))}
              </div>
            ) : displayedNews.length === 0 ? (
              <div className="card p-12 text-center">
                <Search size={40} style={{ color: 'var(--text-muted)', margin: '0 auto 16px' }} />
                <p style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 20, color: 'var(--text-secondary)' }}>No articles found</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>Try a different search term or category</p>
              </div>
            ) : (
              <div className="space-y-4">
                {displayedNews.map((article, i) => (
                  <ArticleCard key={i} article={article} index={i} />
                ))}

                {hasMore && activeNews.length > displayCount && (
                  <button onClick={handleLoadMore} className="btn-ghost w-full" style={{ padding: '16px 0' }}>
                    Load More ({activeNews.length - displayCount} remaining)
                  </button>
                )}

                {displayedNews.length === 0 && !loading && (
                  <div className="card p-8 text-center">
                    <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No signals detected in this category</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-6">

            {/* Sentiment Donut */}
            <div className="card p-5">
              <p className="section-title mb-4">Sentiment Breakdown</p>
              <div style={{ height: 200, position: 'relative' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentStats}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {sentimentStats.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 0, fontSize: 11, fontFamily: 'DM Mono, monospace' }}
                      itemStyle={{ color: 'var(--text-primary)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                  <p style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 28, color: 'var(--text-primary)' }}>{news.length}</p>
                  <p style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em' }}>articles</p>
                </div>
              </div>
              <div className="flex justify-around mt-4 pt-4" style={{ borderTop: '1px solid var(--border)' }}>
                {sentimentStats.map(s => (
                  <div key={s.name} className="text-center">
                    <p style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 18, color: s.color }}>{s.value}</p>
                    <p style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 2 }}>{s.name}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Category Bars */}
            <div className="card p-5">
              <p className="section-title mb-4">Coverage by Category</p>
              <div style={{ height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryStats.slice(0, 6)} layout="vertical" margin={{ left: 0, right: 10 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }} tickLine={false} axisLine={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 0, fontSize: 11, fontFamily: 'DM Mono, monospace' }}
                      itemStyle={{ color: 'var(--text-primary)' }}
                      formatter={(v, n) => [v, 'Articles']}
                    />
                    <Bar dataKey="value" radius={[0, 2, 2, 0]} barSize={10}>
                      {categoryStats.slice(0, 6).map((entry, i) => (
                        <Cell key={i} fill={CATEGORY_COLORS[entry.name] || 'var(--accent)'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Top Keywords */}
            <div className="card p-5">
              <p className="section-title mb-4">Trending Keywords</p>
              <div className="flex flex-wrap gap-2">
                {topKeywords.map(kw => (
                  <span key={kw} className="keyword-tag">#{kw}</span>
                ))}
                {topKeywords.length === 0 && (
                  <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>Keywords appear as articles load</p>
                )}
              </div>
            </div>

            {/* Sources */}
            <div className="card p-5">
              <p className="section-title mb-4">Top Sources</p>
              {Object.entries(
                news.reduce((acc, a) => {
                  const s = a.source?.name || 'Unknown';
                  acc[s] = (acc[s] || 0) + 1;
                  return acc;
                }, {})
              ).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([name, count]) => (
                <div key={name} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{name}</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ArticleCard({ article, index }) {
  const sentiment = article.sentiment?.score || 'neutral';
  const sentimentClass = `sentiment-${sentiment}`;

  return (
    <article
      className="article-enter card"
      style={{ animationDelay: `${Math.min(index * 50, 400)}ms`, borderLeftWidth: 3, borderLeftColor: SENTIMENT_COLORS[sentiment] }}
    >
      <div className="p-6">
        {/* Meta row */}
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <div className="flex items-center gap-2">
            <Globe size={11} style={{ color: 'var(--text-muted)' }} />
            <span style={{ fontSize: 10, color: 'var(--text-secondary)', fontFamily: 'DM Mono, monospace' }}>
              {article.source?.name || 'Unknown Source'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={11} style={{ color: 'var(--text-muted)' }} />
            <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
              {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'No date'}
            </span>
          </div>
          <span className={`badge badge-${sentiment}`}>
            {sentiment}
          </span>
        </div>

        {/* Headline */}
        <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
          <h2 className="headline text-xl mb-3 leading-tight">
            {article.title}
          </h2>
        </a>

        {/* Description */}
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 16, fontFamily: 'Fraunces, Georgia, serif', fontWeight: 300 }}>
          {article.description || 'No description available.'}
        </p>

        {/* Footer */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="badge badge-category">
              <Tag size={9} />
              {article.category || 'general'}
            </span>
            <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
              CONF: {(article.sentiment?.confidence || 0.85).toFixed(2)}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {(article.keywords || []).slice(0, 3).map(kw => (
              <span key={kw} className="keyword-tag">#{kw}</span>
            ))}
            <a href={article.url} target="_blank" rel="noopener noreferrer" className="keyword-tag" style={{ cursor: 'pointer' }}>
              Read <ExternalLink size={8} style={{ display: 'inline', marginLeft: 3 }} />
            </a>
          </div>
        </div>
      </div>

      {/* Image */}
      {article.urlToImage && (
        <div style={{ margin: '0 24px 24px', borderRadius: 0, overflow: 'hidden', maxHeight: 200 }}>
          <img
            src={article.urlToImage}
            alt=""
            style={{ width: '100%', height: 200, objectFit: 'cover', filter: 'grayscale(30%)', transition: 'filter 0.5s ease' }}
            onError={(e) => { e.target.style.display = 'none'; }}
            onMouseOver={(e) => e.target.style.filter = 'grayscale(0%)'}
            onMouseOut={(e) => e.target.style.filter = 'grayscale(30%)'}
          />
        </div>
      )}
    </article>
  );
}

export default App;
