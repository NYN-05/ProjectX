import React from 'react';
import { X, ExternalLink, Globe, Building2, Users, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

const IMPACT_COLORS = {
  positive: 'var(--positive)',
  negative: 'var(--danger)',
  neutral: 'var(--neutral)',
  mixed: '#D97D9B'
};

const SEVERITY_LEVELS = {
  critical: { color: '#E85D4C', label: 'Critical' },
  high: { color: '#D97D7D', label: 'High' },
  medium: { color: '#D97D9B', label: 'Medium' },
  low: { color: 'var(--text-muted)', label: 'Low' }
};

export function IntelligencePanel({ event, relatedEvents, onClose }) {
  if (!event) return null;

  const severity = SEVERITY_LEVELS[event.severity] || SEVERITY_LEVELS.low;

  return (
    <div
      className="intelligence-panel"
      style={{
        position: 'absolute',
        top: 60,
        right: 20,
        width: 360,
        maxHeight: 'calc(100vh - 100px)',
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        zIndex: 30,
        overflow: 'auto',
        animation: 'fadeSlideUp 0.3s ease'
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-center gap-2">
          <AlertTriangle size={14} style={{ color: severity.color }} />
          <span style={{ fontSize: 10, color: severity.color, fontFamily: 'DM Mono, monospace', textTransform: 'uppercase' }}>
            {severity.label}
          </span>
        </div>
        <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
          <X size={16} />
        </button>
      </div>

      {/* Event Title */}
      <div className="p-4">
        <h3 style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 18, color: 'var(--text-primary)', letterSpacing: '0.05em', lineHeight: 1.3 }}>
          {event.title}
        </h3>
        
        <div className="flex items-center gap-2 mt-3">
          <span 
            className="badge"
            style={{ 
              background: IMPACT_COLORS[event.impact] || IMPACT_COLORS.neutral, 
              color: 'var(--bg-base)',
              fontSize: 9
            }}
          >
            {event.impact}
          </span>
          <span className="badge badge-category">{event.sector}</span>
        </div>
      </div>

      {/* Metadata */}
      <div className="px-4 pb-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="grid grid-cols-2 gap-3">
          {event.countries?.length > 0 && (
            <div>
              <div className="flex items-center gap-1 mb-1">
                <Globe size={10} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Countries</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {event.countries.map(c => (
                  <span key={c} className="keyword-tag">{c}</span>
                ))}
              </div>
            </div>
          )}

          {event.companies?.length > 0 && (
            <div>
              <div className="flex items-center gap-1 mb-1">
                <Building2 size={10} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Companies</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {event.companies.slice(0, 3).map(c => (
                  <span key={c} className="keyword-tag">{c}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Source & Link */}
      <div className="p-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock size={10} style={{ color: 'var(--text-muted)' }} />
            <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
              {event.timestamp ? new Date(event.timestamp).toLocaleDateString() : 'Unknown'}
            </span>
          </div>
          <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{event.source}</span>
        </div>
        
        {event.url && (
          <a
            href={event.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 mt-3"
            style={{ color: 'var(--accent)', fontSize: 11, textDecoration: 'none' }}
          >
            View Original <ExternalLink size={10} />
          </a>
        )}
      </div>

      {/* Related Events */}
      {relatedEvents && relatedEvents.length > 0 && (
        <div className="p-4">
          <p className="section-title mb-3">Related Events</p>
          <div className="space-y-3">
            {relatedEvents.slice(0, 5).map((rel, i) => (
              <div 
                key={i}
                className="p-3"
                style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
              >
                <p style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {rel.event?.title?.slice(0, 60)}...
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="keyword-tag" style={{ fontSize: 8 }}>{rel.event?.sector}</span>
                  <span 
                    className="keyword-tag" 
                    style={{ fontSize: 8, color: IMPACT_COLORS[rel.event?.impact] }}
                  >
                    {rel.relationship?.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default IntelligencePanel;