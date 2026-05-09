import React from 'react';
import { ExternalLink, Clock, Tag, BarChart2, Hash, Fingerprint, ShieldAlert, Eye, Lock, Globe } from 'lucide-react';

const SENTIMENT_STYLES = {
  positive: 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5',
  negative: 'text-rose-500 border-rose-500/20 bg-rose-500/5',
  neutral: 'text-slate-500 border-slate-500/20 bg-slate-500/5'
};

function NewsList({ articles, loading }) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="animate-pulse flex gap-6 p-4 border border-slate-900 bg-slate-900/20 rounded">
            <div className="flex-1 space-y-4">
              <div className="h-2 bg-slate-800 rounded w-1/6"></div>
              <div className="h-4 bg-slate-800 rounded w-3/4"></div>
              <div className="h-3 bg-slate-800 rounded w-full"></div>
            </div>
            <div className="w-32 h-20 bg-slate-800 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!articles || articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-600">
        <Eye className="w-16 h-16 mb-4 opacity-20" />
        <p className="text-sm font-mono">NO SIGNALS DETECTED</p>
        <p className="text-xs mt-2 text-slate-700">Try adjusting your filters or wait for new data</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {articles.map((article, index) => {
        const sentiment = article.sentiment?.score || 'neutral';
        const style = SENTIMENT_STYLES[sentiment];
        const serialId = `SIG-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;

        const glowStyle = sentiment === 'positive'
          ? 'hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] hover:border-emerald-500/50'
          : sentiment === 'negative'
          ? 'hover:shadow-[0_0_20px_rgba(244,63,94,0.15)] hover:border-rose-500/50'
          : 'hover:border-indigo-500/30';

        const sourceName = article.source?.name || 'UNKNOWN_NODE';
        const sourceIcon = sourceName.length > 10 ? <Lock className="w-3 h-3" /> : <Globe className="w-3 h-3" />;

        return (
          <article
            key={index}
            className={`group relative flex flex-col md:flex-row gap-6 p-5 border border-slate-800/40 bg-slate-900/10 transition-all duration-500 ${glowStyle}`}
          >
            {/* Tactical Decor */}
            <div className={`absolute top-0 left-0 w-1 h-full transition-colors ${
              sentiment === 'positive' ? 'bg-emerald-500/30 group-hover:bg-emerald-500' :
              sentiment === 'negative' ? 'bg-rose-500/30 group-hover:bg-rose-500' :
              'bg-slate-800 group-hover:bg-indigo-500/50'
            }`} />

            <div className="flex-1 min-w-0 font-mono">
              {/* Header Metadata */}
              <div className="flex flex-wrap items-center gap-4 mb-3">
                <div className="flex items-center gap-1.5 text-[10px] text-indigo-400 font-bold tracking-tighter">
                  <Fingerprint className="w-3 h-3" />
                  <span>{serialId}</span>
                </div>
                <div className="flex items-center gap-1.5 text-[9px] text-slate-500 uppercase tracking-widest">
                  <Clock className="w-3 h-3" />
                  {new Date(article.publishedAt || Date.now()).toLocaleTimeString()}
                </div>
                <span className="h-3 w-px bg-slate-800" />
                <div className="flex items-center gap-1.5 text-[9px] text-slate-400 font-bold uppercase">
                  <Hash className="w-3 h-3" />
                  <span className="truncate max-w-[120px]">{sourceName}</span>
                </div>
                <span className="h-3 w-px bg-slate-800" />
                <div className={`px-2 py-0.5 border rounded-sm text-[8px] font-black uppercase tracking-[0.2em] ${style}`}>
                  {sentiment}
                </div>
              </div>

              {/* Title & Body */}
              <div className="space-y-2">
                <h3 className="text-base font-bold text-slate-200 group-hover:text-white transition-colors leading-tight tracking-tight">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start gap-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(article.url, '_blank');
                    }}
                  >
                    <span className="opacity-40 select-none">»</span>
                    {article.title}
                    <ExternalLink className="w-3 h-3 mt-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-indigo-400" />
                  </a>
                </h3>

                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed font-sans">
                  {article.description || 'No description available.'}
                </p>
              </div>

              {/* Footer Metadata */}
              <div className="flex flex-wrap items-center gap-4 mt-4 pt-4 border-t border-slate-800/50">
                <div className="flex items-center gap-1.5">
                  <Tag className="w-3 h-3 text-indigo-500" />
                  <span className="text-[9px] text-indigo-400/80 font-bold uppercase tracking-widest">
                    {(article.category || 'general')}
                  </span>
                </div>

                <div className="flex gap-2">
                  {article.keywords?.slice(0, 3).map((keyword, ki) => (
                    <span
                      key={ki}
                      className="text-[8px] text-slate-600 bg-slate-950 px-2 py-0.5 rounded-sm border border-slate-800/50 uppercase font-bold"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>

                <div className="ml-auto flex items-center gap-4">
                  <div className="flex items-center gap-2 text-[9px] font-bold">
                    <BarChart2 className="w-3 h-3 text-slate-600" />
                    <span className="text-slate-500">CONF:</span>
                    <span className="text-indigo-400">{(article.sentiment?.confidence || 0.85).toFixed(2)}</span>
                  </div>
                  {sentiment === 'negative' && (
                    <div className="flex items-center gap-1 text-[9px] text-rose-500 animate-pulse">
                      <ShieldAlert className="w-3 h-3" />
                      <span>THREAT_DETECTED</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {article.urlToImage && (
              <div className="md:w-40 md:h-28 w-full h-40 shrink-0 relative group-hover:scale-[1.02] transition-transform duration-500">
                <div className="absolute inset-0 bg-indigo-500/10 mix-blend-overlay z-10" />
                <div className="absolute inset-0 border border-slate-800 z-20" />
                <img
                  src={article.urlToImage}
                  alt=""
                  className="w-full h-full object-cover grayscale opacity-60 group-hover:opacity-100 group-hover:grayscale-0 transition-all duration-700"
                  onError={(e) => e.target.style.display = 'none'}
                />
                {/* Tactical Corners */}
                <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-indigo-500/50 z-30" />
                <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-indigo-500/50 z-30" />
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}

export default NewsList;
