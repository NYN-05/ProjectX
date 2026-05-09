import React from 'react';
import { ExternalLink, Globe, Tag } from 'lucide-react';

export function CountryTooltip({ country, onClose }) {
  if (!country) return null;

  const categoryColors = {
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

  return (
    <div 
      className="country-tooltip"
      style={{
        position: 'absolute',
        top: '50%',
        right: 20,
        width: 320,
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        padding: 20,
        zIndex: 20,
        transform: 'translateY(-50%)',
        animation: 'fadeSlideUp 0.3s ease'
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Globe size={14} style={{ color: 'var(--accent)' }} />
          <h3 style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 18, color: 'var(--text-primary)', letterSpacing: '0.1em' }}>
            {country.country}
          </h3>
        </div>
        <button 
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
        >
          ✕
        </button>
      </div>

      <div className="mb-4" style={{ padding: '12px 0', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-baseline gap-2">
          <span style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 36, color: 'var(--accent)' }}>
            {country.count}
          </span>
          <span style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em' }}>
            articles
          </span>
        </div>
      </div>

      {country.categories && Object.keys(country.categories).length > 0 && (
        <div className="mb-4">
          <p style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 8 }}>
            Categories
          </p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(country.categories)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 4)
              .map(([cat, count]) => (
                <span 
                  key={cat}
                  style={{ 
                    fontSize: 9, 
                    padding: '2px 8px',
                    background: categoryColors[cat] || 'var(--accent-dim)',
                    color: 'var(--bg-base)',
                    borderRadius: 2,
                    fontFamily: 'DM Mono, monospace',
                    textTransform: 'uppercase'
                  }}
                >
                  {cat} ({count})
                </span>
              ))}
          </div>
        </div>
      )}

      {country.articles && country.articles.length > 0 && (
        <div>
          <p style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 8 }}>
            Latest Headlines
          </p>
          <div className="space-y-2">
            {country.articles.map((article, i) => (
              <a
                key={i}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block"
                style={{ textDecoration: 'none' }}
              >
                <div 
                  className="keyword-tag"
                  style={{ 
                    background: 'var(--bg-base)', 
                    border: '1px solid var(--border)',
                    borderRadius: 2,
                    padding: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 4,
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent)';
                    e.currentTarget.style.color = 'var(--accent)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border)';
                    e.currentTarget.style.color = 'var(--text-muted)';
                  }}
                >
                  <span style={{ fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {article.title}
                  </span>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="badge badge-category" style={{ fontSize: 8, padding: '1px 6px' }}>
                      <Tag size={7} />
                      {article.category}
                    </span>
                    <ExternalLink size={8} style={{ color: 'var(--text-muted)' }} />
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CountryTooltip;