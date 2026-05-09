import React, { useState, useEffect, useCallback } from 'react';
import { Filter, TrendingUp, TrendingDown, Activity, Clock, Search, ChevronRight, RefreshCw, Globe } from 'lucide-react';
import { newsAPI } from '../services/api';

const SENTIMENT_COLORS = {
  positive: '#10b981',
  negative: '#f43f5e',
  neutral: '#64748b'
};

function CategoryFilter({ news, onCategorySelect, activeCategory }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get unique categories from news
  const filteredCategories = React.useMemo(() => {
    const categoryCounts = {};
    news.forEach(article => {
      const cat = article.category || 'general';
      categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
    });
    return Object.entries(categoryCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => ({ name, count }));
  }, [news]);

  const handleCategoryClick = (category) => {
    if (onCategorySelect) {
      onCategorySelect(category);
    }
  };

  return (
    <div className="space-y-4">
      <div className="glass-card tactical-border p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em] flex items-center gap-2">
            <Filter className="w-4 h-4" />
            CATEGORY SELECTION
          </h3>
          <span className="text-[10px] font-mono text-slate-500">{filteredCategories.length} ACTIVE</span>
        </div>

        <div className="space-y-2">
          <button
            onClick={() => onCategorySelect(null)}
            className={`w-full flex items-center justify-between p-3 rounded text-[10px] font-mono transition-all ${
              activeCategory === null
                ? 'bg-indigo-600 text-white border-indigo-500'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-indigo-500/30'
            }`}
          >
            <span className="flex items-center gap-2">
              <Globe className="w-3 h-3" />
              ALL CATEGORIES
            </span>
            <span className="bg-slate-800 px-2 py-0.5 rounded text-[9px]">{news.length}</span>
          </button>

          {filteredCategories.slice(0, 15).map((cat, i) => (
            <button
              key={i}
              onClick={() => handleCategoryClick(cat.name)}
              className={`w-full flex items-center justify-between p-3 rounded text-[10px] font-mono transition-all ${
                activeCategory === cat.name
                  ? 'bg-indigo-600 text-white border-indigo-500'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-indigo-500/30'
              }`}
            >
              <span className="flex items-center gap-2 capitalize">
                <Activity className="w-3 h-3" />
                {cat.name}
              </span>
              <span className="bg-slate-800 px-2 py-0.5 rounded text-[9px]">{cat.count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Category Sentiment Breakdown */}
      {activeCategory && (
        <div className="glass-card tactical-border p-5">
          <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em] mb-4">
            {activeCategory.toUpperCase()} ANALYTICS
          </h3>

          {/* Placeholder for category-specific analytics */}
          <div className="space-y-4">
            <div className="text-center py-8 text-slate-600">
              <Activity className="w-10 h-10 mx-auto mb-2 opacity-20" />
              <p className="text-[10px] font-mono">Category analytics loading...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SignalTracking({ news }) {
  const [sortBy, setSortBy] = useState('date');
  const [filterSentiment, setFilterSentiment] = useState('all');

  const filteredNews = React.useMemo(() => {
    let result = [...news];

    if (filterSentiment !== 'all') {
      result = result.filter(a => (a.sentiment?.score || 'neutral') === filterSentiment);
    }

    if (sortBy === 'date') {
      result.sort((a, b) => new Date(b.publishedAt || 0) - new Date(a.publishedAt || 0));
    } else if (sortBy === 'confidence') {
      result.sort((a, b) => (b.sentiment?.confidence || 0) - (a.sentiment?.confidence || 0));
    }

    return result;
  }, [news, sortBy, filterSentiment]);

  return (
    <div className="glass-card tactical-border p-5 h-[650px] overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em]">
          SIGNAL_TRACKING
        </h3>
        <span className="text-[10px] font-mono text-slate-500">{filteredNews.length} SIGNALS</span>
      </div>

      <div className="flex gap-2 mb-4">
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded text-[10px] px-2 py-1 text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="date">Sort by Date</option>
          <option value="confidence">Sort by Confidence</option>
        </select>
        <select
          value={filterSentiment}
          onChange={(e) => setFilterSentiment(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded text-[10px] px-2 py-1 text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="all">All Sentiments</option>
          <option value="positive">Positive Only</option>
          <option value="negative">Negative Only</option>
          <option value="neutral">Neutral Only</option>
        </select>
      </div>

      <div className="space-y-3">
        {filteredNews.slice(0, 20).map((article, i) => (
          <article key={i} className="p-3 rounded border border-slate-800 bg-slate-900/30">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h4 className="text-xs font-bold text-slate-200 truncate">{article.title}</h4>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-500 font-mono">
                  <span className="text-indigo-400">{article.source?.name}</span>
                  <span>•</span>
                  <span>{new Date(article.publishedAt || 0).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                  (article.sentiment?.score) === 'positive' ? 'bg-emerald-500/10 text-emerald-500' :
                  (article.sentiment?.score) === 'negative' ? 'bg-rose-500/10 text-rose-500' :
                  'bg-slate-500/10 text-slate-500'
                }`}>
                  {(article.sentiment?.score).toUpperCase()}
                </span>
                <span className="text-[8px] text-slate-600 font-mono">
                  CONF: {(article.sentiment?.confidence || 0).toFixed(2)}
                </span>
              </div>
            </div>
          </article>
        ))}
        {filteredNews.length === 0 && (
          <div className="text-center py-8 text-slate-600 text-sm">
            No signals matching criteria
          </div>
        )}
      </div>
    </div>
  );
}

function MarketSentiment({ news }) {
  const sentimentCounts = React.useMemo(() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    news.forEach(a => {
      const s = a.sentiment?.score || 'neutral';
      counts[s] = (counts[s] || 0) + 1;
    });
    return counts;
  }, [news]);

  const total = Object.values(sentimentCounts).reduce((a, b) => a + b, 0);
  const percentages = {
    positive: total ? Math.round((sentimentCounts.positive / total) * 100) : 0,
    negative: total ? Math.round((sentimentCounts.negative / total) * 100) : 0,
    neutral: total ? Math.round((sentimentCounts.neutral / total) * 100) : 0,
  };

  return (
    <div className="glass-card tactical-border p-5">
      <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em] mb-4">
        MARKET_SENTIMENT
      </h3>

      {/* Overall Status */}
      <div className="text-center py-6 mb-6">
        <div className="text-4xl font-black font-mono mb-2">
          {percentages.positive > percentages.negative ? 'BULLISH' :
           percentages.negative > percentages.positive ? 'BEARISH' : 'NEUTRAL'}
        </div>
        <div className="text-xs text-slate-500 font-mono">
          {total} ARTICLES ANALYZED
        </div>
      </div>

      {/* Sentiment Distribution */}
      <div className="space-y-4">
        {['positive', 'negative', 'neutral'].map((sent) => (
          <div key={sent}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[9px] font-mono text-slate-500 uppercase">{sent}</span>
              <span className="text-[9px] font-mono text-indigo-400">{percentages[sent]}%</span>
            </div>
            <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  sent === 'positive' ? 'bg-emerald-500' :
                  sent === 'negative' ? 'bg-rose-500' : 'bg-slate-500'
                }`}
                style={{ width: `${percentages[sent]}%` }}
              />
            </div>
            <div className="flex justify-between text-[8px] text-slate-600 mt-1 font-mono">
              <span>{sentimentCounts[sent]} ARTICLES</span>
            </div>
          </div>
        ))}
      </div>

      {/* Trend Chart */}
      <div className="mt-6 p-3 bg-slate-950/30 rounded border border-slate-800">
        <h4 className="text-[9px] font-mono text-slate-500 mb-3">SENTIMENT TRENDS</h4>
        <div className="flex items-end gap-2 h-24">
          {[65, 45, 75, 55, 80, 60, 40, 50, 65, 70, 55, 45].map((h, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-indigo-500/30 rounded-t hover:bg-indigo-500/50 transition-all"
                style={{ height: `${h}%` }}
              />
              <span className="text-[7px] text-slate-600 font-mono">
                {['M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F'][i]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ArchiveQuery({ news }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [dateRange, setDateRange] = useState('all');

  const sources = React.useMemo(() => {
    const sourceCounts = {};
    news.forEach(a => {
      const s = a.source?.name || 'Unknown';
      sourceCounts[s] = (sourceCounts[s] || 0) + 1;
    });
    return Object.entries(sourceCounts).map(([name, count]) => ({ name, count }));
  }, [news]);

  const filteredNews = React.useMemo(() => {
    let result = [...news];
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      result = result.filter(a =>
        a.title?.toLowerCase().includes(q) ||
        a.description?.toLowerCase().includes(q)
      );
    }
    if (selectedSource) {
      result = result.filter(a => a.source?.name === selectedSource);
    }
    return result.slice(0, 30);
  }, [news, searchTerm, selectedSource]);

  return (
    <div className="glass-card tactical-border p-5 h-[650px] overflow-y-auto">
      <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em] mb-4">
        ARCHIVE_QUERY
      </h3>

      {/* Search and Filters */}
      <div className="space-y-3 mb-4">
        <input
          type="text"
          placeholder="SEARCH ARCHIVE..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-black/40 border border-slate-800 rounded px-3 py-2 text-[10px] text-indigo-100 placeholder-slate-700 focus:outline-none focus:border-indigo-500/30 uppercase tracking-widest"
        />
        <div className="grid grid-cols-2 gap-2">
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded px-2 py-1.5 text-[10px] text-slate-300 focus:outline-none"
          >
            <option value="">ALL SOURCES</option>
            {sources.slice(0, 8).map((s, i) => (
              <option key={i} value={s.name}>{s.name}</option>
            ))}
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded px-2 py-1.5 text-[10px] text-slate-300 focus:outline-none"
          >
            <option value="all">ALL TIME</option>
            <option value="24h">LAST 24H</option>
            <option value="7d">LAST 7 DAYS</option>
            <option value="30d">LAST 30 DAYS</option>
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-2">
        {filteredNews.map((article, i) => (
          <article key={i} className="p-3 rounded border border-slate-800 bg-slate-900/20 hover:bg-slate-900/40 transition-colors">
            <div className="flex items-start gap-3">
              <div className="flex-1 min-w-0">
                <h4 className="text-xs font-bold text-slate-200 truncate">{article.title}</h4>
                <p className="text-[9px] text-slate-500 line-clamp-2 mt-1">{article.description}</p>
                <div className="flex items-center gap-3 mt-2 text-[9px] text-slate-600 font-mono">
                  <span>{article.source?.name || 'Unknown'}</span>
                  <span>•</span>
                  <span>{new Date(article.publishedAt || 0).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </article>
        ))}
        {filteredNews.length === 0 && (
          <div className="text-center py-8 text-slate-600">
            <Search className="w-8 h-8 mx-auto mb-2 opacity-20" />
            <p className="text-[10px]">No archive entries found</p>
          </div>
        )}
      </div>
    </div>
  );
}

function SecurityLogs({ logs }) {
  const errorLogs = logs.filter(l => l.msg.includes('ERROR') || l.msg.includes('CRITICAL'));
  const warningLogs = logs.filter(l => l.msg.includes('WARNING') || l.msg.includes('WARN'));
  const infoLogs = logs.filter(l => !l.msg.includes('ERROR') && !l.msg.includes('WARNING'));

  const severityCounts = {
    critical: errorLogs.length,
    warning: warningLogs.length,
    info: infoLogs.length,
  };

  return (
    <div className="glass-card tactical-border p-5 h-[650px] overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em]">
          SECURITY_LOGS
        </h3>
        <span className="text-[10px] font-mono text-slate-500">{logs.length} EVENTS</span>
      </div>

      {/* Severity Summary */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-3 rounded bg-rose-500/5 border border-rose-500/20">
          <div className="text-2xl font-black text-rose-500">{severityCounts.critical}</div>
          <div className="text-[8px] text-rose-500/80 uppercase font-bold">Critical</div>
        </div>
        <div className="p-3 rounded bg-amber-500/5 border border-amber-500/20">
          <div className="text-2xl font-black text-amber-500">{severityCounts.warning}</div>
          <div className="text-[8px] text-amber-500/80 uppercase font-bold">Warning</div>
        </div>
        <div className="p-3 rounded bg-emerald-500/5 border border-emerald-500/20">
          <div className="text-2xl font-black text-emerald-500">{severityCounts.info}</div>
          <div className="text-[8px] text-emerald-500/80 uppercase font-bold">Info</div>
        </div>
      </div>

      {/* Logs */}
      <div className="font-mono text-[10px] space-y-1">
        {logs.slice().reverse().map((log, i) => (
          <div key={i} className={`p-2 rounded border-l-2 ${
            log.msg.includes('ERROR') ? 'bg-rose-950/20 border-rose-500' :
            log.msg.includes('WARNING') ? 'bg-amber-950/20 border-amber-500' :
            'bg-slate-900/30 border-indigo-500/30'
          }`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-slate-500">[{log.timestamp}]</span>
              <span className="text-[8px] font-bold uppercase tracking-wider">
                {log.msg.includes('ERROR') ? 'CRITICAL' :
                 log.msg.includes('WARNING') ? 'WARNING' : 'INFO'}
              </span>
            </div>
            <div className={log.msg.includes('ERROR') ? 'text-rose-400' : 'text-indigo-400/80'}>
              {log.msg}
            </div>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-center py-8 text-slate-600">
            <Shield className="w-8 h-8 mx-auto mb-2 opacity-20" />
            <p className="text-[10px]">No security events logged</p>
          </div>
        )}
      </div>
    </div>
  );
}

function DataAnalytics({ news, stats }) {
  return (
    <div className="glass-card tactical-border p-5 h-[650px] overflow-y-auto">
      <h3 className="text-[10px] font-mono font-black text-slate-500 tracking-[0.2em] mb-4">
        DATA_ANALYTICS
      </h3>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="p-3 rounded bg-indigo-500/5 border border-indigo-500/20">
          <div className="text-[9px] text-indigo-400 uppercase mb-1">Total Articles</div>
          <div className="text-xl font-bold font-mono">{stats.totalArticles || news.length}</div>
        </div>
        <div className="p-3 rounded bg-emerald-500/5 border border-emerald-500/20">
          <div className="text-[9px] text-emerald-400 uppercase mb-1">Categories</div>
          <div className="text-xl font-bold font-mono">{Object.keys(stats.categories || {}).length}</div>
        </div>
      </div>

      {/* Top Keywords */}
      <div className="mb-6">
        <h4 className="text-[9px] font-mono text-slate-500 mb-3 uppercase">Top Keywords</h4>
        <div className="flex flex-wrap gap-2">
          {['tech', 'ai', 'market', 'growth', 'data', 'future', 'innovation', 'digital'].map((kw, i) => (
            <span key={i} className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-[9px] text-indigo-400 font-bold">
              #{kw.toUpperCase()}
            </span>
          ))}
        </div>
      </div>

      {/* Category Breakdown */}
      <div>
        <h4 className="text-[9px] font-mono text-slate-500 mb-3 uppercase">Content Distribution</h4>
        <div className="space-y-2">
          {Object.entries(stats.categories || {}).slice(0, 8).map(([cat, count], i) => (
            <div key={i} className="flex items-center gap-3">
              <span className="text-[9px] font-mono text-slate-500 w-20">{cat}</span>
              <div className="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500"
                  style={{ width: `${(count / (Object.values(stats.categories || {})[0] || 1)) * 100}%` }}
                />
              </div>
              <span className="text-[9px] font-mono text-indigo-400 w-12 text-right">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Re-exports
export { CategoryFilter, SignalTracking, MarketSentiment, ArchiveQuery, SecurityLogs, DataAnalytics };
