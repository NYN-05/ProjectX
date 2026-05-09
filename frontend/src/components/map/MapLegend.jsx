import React from 'react';

export function MapLegend({ totalArticles, totalCountries }) {
  return (
    <div 
      className="map-legend"
      style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        zIndex: 10
      }}
    >
      <div>
        <p style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 2 }}>
          Total Coverage
        </p>
        <p style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 20, color: 'var(--text-primary)' }}>
          {totalArticles || 0} <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>articles</span>
        </p>
      </div>
      
      <div style={{ width: 1, height: 30, background: 'var(--border)' }} />
      
      <div>
        <p style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 2 }}>
          Countries
        </p>
        <p style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 20, color: 'var(--text-primary)' }}>
          {totalCountries || 0} <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>active</span>
        </p>
      </div>
      
      <div style={{ width: 1, height: 30, background: 'var(--border)' }} />
      
      <div className="flex items-center gap-2">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 10, height: 10, background: 'var(--accent)', borderRadius: '50%' }} />
          <span style={{ fontSize: 9, color: 'var(--text-secondary)', fontFamily: 'DM Mono, monospace' }}>
            High Activity
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 10, height: 10, background: 'var(--accent-dim)', borderRadius: '50%' }} />
          <span style={{ fontSize: 9, color: 'var(--text-secondary)', fontFamily: 'DM Mono, monospace' }}>
            Low Activity
          </span>
        </div>
      </div>
    </div>
  );
}

export default MapLegend;