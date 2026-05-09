import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3-force';
import { ZoomIn, ZoomOut, Maximize2, Loader, Move } from 'lucide-react';

const IMPACT_COLORS = {
  positive: '#7DC97D',
  negative: '#E85D4C',
  neutral: '#8B8B8B',
  mixed: '#D97D9B'
};

export function RelationshipGraph({ graphData, onNodeSelect, loading }) {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [draggedNode, setDraggedNode] = useState(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const simulationRef = useRef(null);

  const updateDimensions = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width || 800, height: rect.height || 500 });
    }
  }, []);

  useEffect(() => {
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [updateDimensions]);

  useEffect(() => {
    if (!graphData?.nodes?.length || !containerRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();
    const width = rect.width || 800;
    const height = rect.height || 500;

    const graphNodes = graphData.nodes.map(n => ({
      id: n.id,
      label: n.label,
      type: n.event_type,
      sector: n.sector,
      impact: n.impact,
      severity: n.severity,
      countries: n.countries || [],
      industries: n.industries || [],
      x: width / 2 + (Math.random() - 0.5) * 200,
      y: height / 2 + (Math.random() - 0.5) * 200
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
      .force('link', d3.forceLink(graphLinks).id(d => d.id).distance(100).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05));

    simulation.on('tick', () => {
      setNodes([...graphNodes]);
      setLinks([...graphLinks]);
    });

    simulationRef.current = simulation;

    return () => simulation.stop();
  }, [graphData]);

  const handleZoom = (factor) => {
    setTransform(prev => ({
      ...prev,
      k: Math.max(0.3, Math.min(3, prev.k * factor))
    }));
  };

  const handleReset = () => {
    setTransform({ x: 0, y: 0, k: 1 });
  };

  const handleDragStart = (node, e) => {
    if (simulationRef.current) {
      simulationRef.current.alphaTarget(0.3).restart();
      setDraggedNode(node);
    }
  };

  const handleDrag = (e) => {
    if (!draggedNode || !simulationRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - transform.x) / transform.k;
    const y = (e.clientY - rect.top - transform.y) / transform.k;
    
    draggedNode.fx = x;
    draggedNode.fy = y;
  };

  const handleDragEnd = () => {
    if (simulationRef.current && draggedNode) {
      simulationRef.current.alphaTarget(0);
      draggedNode.fx = null;
      draggedNode.fy = null;
      setDraggedNode(null);
    }
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    handleZoom(factor);
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
          <p style={{ fontSize: 12, color: 'var(--var(--text-muted))', fontFamily: 'DM Mono, monospace' }}>
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
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="relationship-graph"
      style={{ 
        position: 'relative', 
        width: '100%', 
        height: '100%', 
        minHeight: 400,
        cursor: draggedNode ? 'grabbing' : 'grab'
      }}
      onWheel={handleWheel}
      onMouseMove={handleDrag}
      onMouseUp={handleDragEnd}
      onMouseLeave={handleDragEnd}
    >
      {/* Controls */}
      <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 10, display: 'flex', gap: 4 }}>
        <button onClick={() => handleZoom(1.3)} className="btn-ghost" style={{ padding: 6 }} title="Zoom In">
          <ZoomIn size={14} />
        </button>
        <button onClick={() => handleZoom(0.7)} className="btn-ghost" style={{ padding: 6 }} title="Zoom Out">
          <ZoomOut size={14} />
        </button>
        <button onClick={handleReset} className="btn-ghost" style={{ padding: 6 }} title="Reset View">
          <Maximize2 size={14} />
        </button>
      </div>

      {/* Instructions */}
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 10 }}>
        <div className="flex items-center gap-2" style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
          <Move size={10} />
          <span>Drag nodes • Scroll to zoom • Click for details</span>
        </div>
      </div>

      {/* Legend */}
      <div style={{ position: 'absolute', bottom: 10, left: 10, zIndex: 10, background: 'var(--bg-elevated)', padding: 10, border: '1px solid var(--border)' }}>
        <p style={{ fontSize: 8, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          Impact
        </p>
        <div className="flex gap-2 flex-wrap">
          {Object.entries(IMPACT_COLORS).map(([impact, color]) => (
            <div key={impact} className="flex items-center gap-1">
              <div style={{ width: 8, height: 8, background: color, borderRadius: '50%' }} />
              <span style={{ fontSize: 8, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{impact}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div style={{ position: 'absolute', bottom: 10, right: 10, zIndex: 10, background: 'var(--bg-elevated)', padding: 10, border: '1px solid var(--border)' }}>
        <p style={{ fontSize: 8, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>
          {graphData.nodes?.length || 0} nodes • {graphData.edges?.length || 0} connections
        </p>
      </div>

      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{ background: 'var(--bg-surface)' }}
      >
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="20" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="var(--border)" />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.k})`}>
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
                strokeOpacity={0.4}
                markerEnd="url(#arrowhead)"
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => (
            <g
              key={node.id}
              transform={`translate(${node.x || 0}, ${node.y || 0})`}
              onClick={(e) => {
                e.stopPropagation();
                handleNodeClick(node);
              }}
              onMouseDown={(e) => {
                e.stopPropagation();
                handleDragStart(node, e);
              }}
              onMouseEnter={() => setHoveredNode(node)}
              onMouseLeave={() => setHoveredNode(null)}
              style={{ cursor: 'grab', outline: 'none' }}
            >
              {/* Outer glow for highlighted */}
              {hoveredNode?.id === node.id && (
                <circle
                  r={node.severity === 'critical' ? 28 : node.severity === 'high' ? 24 : 18}
                  fill={IMPACT_COLORS[node.impact] || IMPACT_COLORS.neutral}
                  fillOpacity={0.3}
                />
              )}
              
              {/* Main node */}
              <circle
                r={node.severity === 'critical' ? 18 : node.severity === 'high' ? 14 : 10}
                fill={IMPACT_COLORS[node.impact] || IMPACT_COLORS.neutral}
                fillOpacity={hoveredNode?.id === node.id ? 1 : 0.7}
                stroke="var(--bg-base)"
                strokeWidth={2}
                filter={hoveredNode?.id === node.id ? "url(#glow)" : "none"}
              />
              
              {/* Inner circle */}
              <circle
                r={4}
                fill="var(--bg-base)"
              />
              
              {/* Label */}
              <text
                dy={24}
                textAnchor="middle"
                style={{
                  fontSize: 8,
                  fill: 'var(--text-secondary)',
                  fontFamily: 'DM Mono, monospace'
                }}
              >
                {node.label?.slice(0, 15)}
              </text>
            </g>
          ))}
        </g>
      </svg>

      {/* Hover Tooltip */}
      {hoveredNode && (
        <div
          style={{
            position: 'absolute',
            top: Math.min((hoveredNode.y || 0) * transform.k + transform.y + 30, dimensions.height - 150),
            left: Math.min((hoveredNode.x || 0) * transform.k + transform.x + 30, dimensions.width - 200),
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            padding: 12,
            zIndex: 20,
            maxWidth: 220,
            pointerEvents: 'none'
          }}
        >
          <p style={{ fontSize: 11, color: 'var(--text-primary)', fontFamily: 'DM Mono, monospace', fontWeight: 500 }}>
            {hoveredNode.label?.slice(0, 50)}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <span className="keyword-tag" style={{ fontSize: 8 }}>{hoveredNode.type}</span>
            <span 
              className="keyword-tag" 
              style={{ fontSize: 8, color: IMPACT_COLORS[hoveredNode.impact], borderColor: IMPACT_COLORS[hoveredNode.impact] }}
            >
              {hoveredNode.impact}
            </span>
          </div>
          <p style={{ fontSize: 8, color: 'var(--text-muted)', marginTop: 8 }}>
            {hoveredNode.sector} • {hoveredNode.countries?.join(', ') || 'Global'}
          </p>
        </div>
      )}
    </div>
  );
}

export default RelationshipGraph;