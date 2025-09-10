import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { ZoomIn, ZoomOut, RotateCcw, Settings } from 'lucide-react';

const ConceptGraph = ({ 
  data, 
  onNodeClick, 
  onNodeHover,
  width = 800, 
  height = 600,
  showControls = true 
}) => {
  const fgRef = useRef();
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState(null);
  const [graphConfig, setGraphConfig] = useState({
    nodeSize: 5,
    linkWidth: 1,
    chargeStrength: -300,
    linkDistance: 50,
    showLabels: true,
    colorByCategory: true
  });

  // Color scheme for different concept categories
  const categoryColors = {
    'interaction_design': '#3b82f6',
    'usability': '#10b981',
    'cognitive_psychology': '#8b5cf6',
    'input_methods': '#f59e0b',
    'evaluation_methods': '#ef4444',
    'design_principles': '#06b6d4',
    'accessibility': '#84cc16',
    'mobile_computing': '#f97316',
    'social_computing': '#ec4899',
    'visualization': '#6366f1',
    'extracted': '#6b7280',
    'statistical': '#9ca3af',
    'default': '#64748b'
  };

  const getNodeColor = (node) => {
    if (graphConfig.colorByCategory && node.category) {
      return categoryColors[node.category] || categoryColors.default;
    }
    return categoryColors.default;
  };

  const getNodeSize = (node) => {
    const baseSize = graphConfig.nodeSize;
    const sizeMultiplier = node.size ? Math.sqrt(node.size) / 2 : 1;
    return Math.max(baseSize * sizeMultiplier, baseSize);
  };

  const getLinkWidth = (link) => {
    const baseWidth = graphConfig.linkWidth;
    return link.width ? link.width * baseWidth : baseWidth;
  };

  const handleNodeClick = (node, event) => {
    if (onNodeClick) {
      onNodeClick(node, event);
    }
    
    // Highlight connected nodes
    const connectedNodes = new Set();
    const connectedLinks = new Set();
    
    if (data.edges) {
      data.edges.forEach(link => {
        if (link.source === node.id || link.target === node.id) {
          connectedLinks.add(link);
          connectedNodes.add(link.source);
          connectedNodes.add(link.target);
        }
      });
    }
    
    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
  };

  const handleNodeHover = (node) => {
    setHoverNode(node);
    if (onNodeHover) {
      onNodeHover(node);
    }
  };

  const handleZoomIn = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() * 1.5);
    }
  };

  const handleZoomOut = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() / 1.5);
    }
  };

  const handleReset = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());
    setHoverNode(null);
  };

  const nodeCanvasObject = (node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    
    // Node circle
    const nodeSize = getNodeSize(node);
    const nodeColor = getNodeColor(node);
    
    // Highlight if connected to hovered/clicked node
    const isHighlighted = highlightNodes.has(node.id);
    const isHovered = hoverNode && hoverNode.id === node.id;
    
    ctx.fillStyle = isHighlighted || isHovered ? nodeColor : nodeColor + '80';
    ctx.strokeStyle = isHighlighted || isHovered ? '#000' : 'transparent';
    ctx.lineWidth = 2 / globalScale;
    
    ctx.beginPath();
    ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
    ctx.fill();
    ctx.stroke();
    
    // Node label
    if (graphConfig.showLabels && (globalScale > 0.5 || isHighlighted || isHovered)) {
      const textWidth = ctx.measureText(label).width;
      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);
      
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.fillRect(
        node.x - bckgDimensions[0] / 2,
        node.y - bckgDimensions[1] / 2,
        ...bckgDimensions
      );
      
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#333';
      ctx.fillText(label, node.x, node.y);
    }
  };

  const linkCanvasObject = (link, ctx, globalScale) => {
    const isHighlighted = highlightLinks.has(link);
    
    ctx.strokeStyle = isHighlighted ? '#333' : '#ccc';
    ctx.lineWidth = getLinkWidth(link) / globalScale;
    ctx.globalAlpha = isHighlighted ? 1 : 0.6;
    
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();
    
    ctx.globalAlpha = 1;
  };

  useEffect(() => {
    if (fgRef.current && data.nodes && data.nodes.length > 0) {
      // Auto-fit the graph when data changes
      setTimeout(() => {
        fgRef.current.zoomToFit(400);
      }, 100);
    }
  }, [data]);

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg"
        style={{ width, height }}
      >
        <div className="text-center">
          <div className="text-gray-400 mb-2">
            <Settings className="h-12 w-12 mx-auto" />
          </div>
          <p className="text-gray-500">No concept data available</p>
          <p className="text-sm text-gray-400">Upload documents to see concept relationships</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Graph Controls */}
      {showControls && (
        <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
            title="Reset View"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Graph Configuration Panel */}
      {showControls && (
        <div className="absolute top-4 left-4 z-10 bg-white rounded-lg shadow-md p-4 max-w-xs">
          <h4 className="font-medium text-gray-900 mb-3">Graph Settings</h4>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-700 mb-1">Node Size</label>
              <input
                type="range"
                min="2"
                max="10"
                value={graphConfig.nodeSize}
                onChange={(e) => setGraphConfig(prev => ({ ...prev, nodeSize: parseInt(e.target.value) }))}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-700 mb-1">Link Width</label>
              <input
                type="range"
                min="0.5"
                max="3"
                step="0.1"
                value={graphConfig.linkWidth}
                onChange={(e) => setGraphConfig(prev => ({ ...prev, linkWidth: parseFloat(e.target.value) }))}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={graphConfig.showLabels}
                  onChange={(e) => setGraphConfig(prev => ({ ...prev, showLabels: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Show Labels</span>
              </label>
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={graphConfig.colorByCategory}
                  onChange={(e) => setGraphConfig(prev => ({ ...prev, colorByCategory: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Color by Category</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Hover Info */}
      {hoverNode && (
        <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-md p-3 max-w-sm">
          <h4 className="font-medium text-gray-900">{hoverNode.name}</h4>
          {hoverNode.category && (
            <p className="text-sm text-gray-600">Category: {hoverNode.category}</p>
          )}
          {hoverNode.frequency && (
            <p className="text-sm text-gray-600">Frequency: {hoverNode.frequency}</p>
          )}
        </div>
      )}

      {/* Force Graph */}
      <ForceGraph2D
        ref={fgRef}
        graphData={{
          nodes: data.nodes || [],
          links: data.edges || []
        }}
        width={width}
        height={height}
        nodeCanvasObject={nodeCanvasObject}
        linkCanvasObject={linkCanvasObject}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        onBackgroundClick={() => {
          setHighlightNodes(new Set());
          setHighlightLinks(new Set());
          setHoverNode(null);
        }}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        d3Force={{
          charge: { strength: graphConfig.chargeStrength },
          link: { distance: graphConfig.linkDistance }
        }}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
      />

      {/* Legend */}
      {graphConfig.colorByCategory && (
        <div className="absolute bottom-4 right-4 z-10 bg-white rounded-lg shadow-md p-3">
          <h4 className="font-medium text-gray-900 mb-2">Categories</h4>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {Object.entries(categoryColors).map(([category, color]) => {
              const hasNodes = data.nodes?.some(node => node.category === category);
              if (!hasNodes && category !== 'default') return null;
              
              return (
                <div key={category} className="flex items-center text-xs">
                  <div 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-gray-700 capitalize">
                    {category.replace(/_/g, ' ')}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConceptGraph;