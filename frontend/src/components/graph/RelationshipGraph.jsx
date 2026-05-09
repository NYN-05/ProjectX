import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3-force';
import { ZoomIn, ZoomOut, RefreshCw, Loader } from 'lucide-react';

const IMPACT_COLORS = {
  positive: '#7DC97D',
  negative: '#E85D4C',
  neutral: '#8B8B8B',
  mixed: '#D97D9B'
};

const SECTOR_COLORS = {
  technology: '#9B7DD4',
  finance: '#4A90D9',
  defense: '#D97D7D',
  trade: '#D97D9B',
  diplomacy: '#7DC97D',
  politics: '#D97D7D',
  health: '#D97D9B',
  security: '#E85D4C',
  general: '#6B6459'
};

export function RelationshipGraph({ graphData, onNodeSelect, loading }) {
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [hoveredNode, setHoveredNode] = useState(null);
  const simulationRef = useRef(null);

  useEffect(() => {
    if (!graphData?.nodes?.length || !containerRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();
    setDimensions({ width: rect.width || 800, height: rect.height || 500 });

    const graphNodes = graphData.nodes.map(n => ({
      id: n.id,
      label: n.label,
      type: n.event_type,
      sector: n.sector,
      impact: n.impact,
      severity: n.severity,
      countries: n.countries || [],
      industries: n.industries || []
    }));

    const nodeIds = new Set(graphNodes.map(n => n.id));
    const graphLinks = (graphData.edges || [])
      .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
      .map(l => ({
        source: l.source,
        target: l.target,
        type: l.type,
        strength: l.strength
      }));

    const simulation = d3.forceSimulation(graphNodes)
      .force('link', d3.forceLink(graphLinks).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .force('collision', d3.forceCollide().radius(30));

    simulation.on('tick', () => {
      setNodes([...graphNodes]);
      setLinks([...graphLinks]);
    });

    simulationRef.current = simulation;

    return () => simulation.stop();
  }, [graphData, dimensions.width, dimensions.height]);

  const handleZoomIn = () => {
    const container = containerRef.current;
    if (container) {
      const currentTransform = container.style.transform;
      container.style.transform = `scale(${1.2})`;
    }
  };

  const handleNodeClick = (node) => {
    if (onNodeSelect) {
      onNodeSelect(node.id);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: 'var(--bg-surface)' }}>
        <div className="text-center">
          <Loader size={32} className="animate-spin" style={{ color: 'var(--accent)', margin: '0 auto 12px' }} />
          <p style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
            Building intelligence graph...
          </p>
        </div>
      </div>
    );
  }

  if (!graphData?.nodes?.length) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: 'var(--bg-surface)' }}>
        <div className="text-center">
          <p style={{ fontSize: 14, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
            No graph data available
          </p>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
            Build the graph to visualize relationships
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relationship-graph" style={{ position: 'relative', width: '100%', height: '100%', minHeight: 400 }}>
      {/* Controls */}
      <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 10, display: 'flex', gap: 8 }}>
        <button onClick={handleZoomIn} className="btn-ghost" style={{ padding: 6 }}>
          <ZoomIn size={14} />
        </button>
        <button onClick={() => window.location.reload()} className="btn-ghost" style={{ padding: 6 }}>
          <RefreshCw size={14} />
        </button>
      </div>

      {/* Legend */}
      <div style={{ position: 'absolute', bottom: 10, left: 10, zIndex: 10, background: 'var(--bg-elevated)', padding: 12, border: '1px solid var(--border)' }}>
        <p style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          Impact
        </p>
        <div className="flex gap-3">
          {Object.entries(IMPACT_COLORS).map(([impact, color]) => (
            <div key={impact} className="flex items-center gap-1">
              <div style={{ width: 8, height: 8, background: color, borderRadius: '50%' }} />
              <span style={{ fontSize: 9, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{impact}</span>
            </div>
          ))}
        </div>
      </div>

      <svg
        ref={containerRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{ background: 'var(--bg-surface)' }}
      >
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="20" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="var(--border)" />
          </marker>
        </defs>

        {/* Links */}
        {links.map((link, i) => {
          const source = typeof link.source === 'object' ? link.source : nodes.find(n => n.id === link.source);
          const target = typeof link.target === 'object' ? link.target : nodes.find(n => n.id === link.target);
          
          if (!source || !target) return null;
          
          return (
            <line
              key={`link-${i}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="var(--border)"
              strokeWidth={Math.max(1, (link.strength || 0.5) * 2)}
              strokeOpacity={0.6}
              markerEnd="url(#arrowhead)"
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => (
          <g
            key={node.id}
            transform={`translate(${node.x || 0}, ${node.y || 0})`}
            onClick={() => handleNodeClick(node)}
            onMouseEnter={() => setHoveredNode(node)}
            onMouseLeave={() => setHoveredNode(null)}
            style={{ cursor: 'pointer' }}
          >
            <circle
              r={node.severity === 'critical' ? 20 : node.severity === 'high' ? 16 : 12}
              fill={IMPACT_COLORS[node.impact] || IMPACT_COLORS.neutral}
              fillOpacity={0.8}
              stroke="var(--bg-base)"
              strokeWidth={2}
            />
            <circle
              r={6}
              fill="var(--bg-base)"
            />
            <text
              dy={30}
              textAnchor="middle"
              style={{
                fontSize: 9,
                fill: 'var(--text-secondary)',
                fontFamily: 'DM Mono, monospace'
              }}
            >
              {node.label?.slice(0, 20)}
            </text>
          </g>
        ))}
      </svg>

      {/* Hover Tooltip */}
      {hoveredNode && (
        <div
          style={{
            position: 'absolute',
            top: hoveredNode.y + 20,
            left: hoveredNode.x + 20,
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            padding: 12,
            zIndex: 20,
            maxWidth: 250,
            pointerEvents: 'none'
          }}
        >
          <p style={{ fontSize: 11, color: 'var(--text-primary)', fontFamily: 'DM Mono, monospace', fontWeight: 500 }}>
            {hoveredNode.label?.slice(0, 50)}
          </p>
          <div className="flex gap-2 mt-2">
            <span className="keyword-tag">{hoveredNode.type}</span>
            <span className="keyword-tag" style={{ color: IMPACT_COLORS[hoveredNode.impact] }}>{hoveredNode.impact}</span>
          </div>
          <p style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 8 }}>
            {hoveredNode.sector} • {hoveredNode.countries?.join(', ') || 'Global'}
          </p>
        </div>
      )}
    </div>
  );
}

export default RelationshipGraph;