import { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape, { Core, NodeSingular } from 'cytoscape';
import { Card } from '@/components/ui/card';
import { ContainerNode, ContainerEdge } from '@/types';

interface GraphViewProps {
  className?: string;
}

export const GraphView = ({ className }: GraphViewProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<ContainerNode | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => {
              const risk = ele.data('riskLevel');
              if (risk === 'critical') return '#ef4444';
              if (risk === 'warning') return '#f59e0b';
              return '#10b981';
            },
            'label': 'data(name)',
            'color': '#f0f9ff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-family': 'Inter, sans-serif',
            'width': '60px',
            'height': '60px',
            'border-width': '2px',
            'border-color': '#1e293b',
            'text-outline-color': '#1e293b',
            'text-outline-width': '2px',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '4px',
            'border-color': '#06b6d4',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': (ele) => ele.data('weight') || 2,
            'line-color': (ele) => {
              const type = ele.data('type');
              if (type === 'network') return '#06b6d4';
              if (type === 'syscall') return '#a855f7';
              return '#64748b';
            },
            'target-arrow-color': (ele) => {
              const type = ele.data('type');
              if (type === 'network') return '#06b6d4';
              if (type === 'syscall') return '#a855f7';
              return '#64748b';
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.6,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'opacity': 1,
            'width': 4,
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        fit: true,
        padding: 50,
      },
    });

    // Handle node selection
    cyRef.current.on('tap', 'node', (event) => {
      const node = event.target;
      setSelectedNode({
        id: node.data('id'),
        name: node.data('name'),
        image: node.data('image'),
        riskLevel: node.data('riskLevel'),
        cpu: node.data('cpu'),
        memory: node.data('memory'),
        io: node.data('io'),
      });
    });

    // Handle background tap to deselect
    cyRef.current.on('tap', (event) => {
      if (event.target === cyRef.current) {
        setSelectedNode(null);
      }
    });

    return () => {
      cyRef.current?.destroy();
    };
  }, []);

  // Public API methods - memoized with useCallback for stability
  const addNode = useCallback((node: ContainerNode) => {
    if (!cyRef.current) return;
    
    try {
      const exists = cyRef.current.getElementById(node.id).length > 0;
      if (exists) {
        // Update existing node
        cyRef.current.getElementById(node.id).data(node);
      } else {
        // Add new node
        cyRef.current.add({
          group: 'nodes',
          data: node,
        });
        cyRef.current.layout({ name: 'cose', animate: true }).run();
      }
    } catch (error) {
      console.error('Error adding node:', error);
    }
  }, []);

  const addEdge = useCallback((edge: ContainerEdge) => {
    if (!cyRef.current) return;
    
    try {
      const exists = cyRef.current.getElementById(edge.id).length > 0;
      if (!exists) {
        cyRef.current.add({
          group: 'edges',
          data: edge,
        });
      }
    } catch (error) {
      console.error('Error adding edge:', error);
    }
  }, []);

  const removeNode = useCallback((nodeId: string) => {
    if (!cyRef.current) return;
    try {
      cyRef.current.getElementById(nodeId).remove();
    } catch (error) {
      console.error('Error removing node:', error);
    }
  }, []);

  const clearGraph = useCallback(() => {
    if (!cyRef.current) return;
    try {
      cyRef.current.elements().remove();
    } catch (error) {
      console.error('Error clearing graph:', error);
    }
  }, []);

  const highlightNode = useCallback((nodeId: string) => {
    if (!cyRef.current) return;
    try {
      const node = cyRef.current.getElementById(nodeId);
      cyRef.current.elements().removeClass('highlighted');
      node.addClass('highlighted');
      node.neighborhood().addClass('highlighted');
    } catch (error) {
      console.error('Error highlighting node:', error);
    }
  }, []);

  // Expose methods via ref
  useEffect(() => {
    (window as any).graphView = {
      addNode,
      addEdge,
      removeNode,
      clearGraph,
      highlightNode,
    };
    return () => {
      delete (window as any).graphView;
    };
  }, [addNode, addEdge, removeNode, clearGraph, highlightNode]);

  return (
    <div className={className}>
      <Card className="h-full bg-card border-border overflow-hidden">
        <div ref={containerRef} className="w-full h-full" />
        
        {selectedNode && (
          <Card className="absolute bottom-4 right-4 w-80 p-4 bg-card border-primary shadow-glow">
            <h3 className="text-lg font-semibold mb-2 text-foreground">{selectedNode.name}</h3>
            <div className="space-y-2 text-sm font-mono">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Image:</span>
                <span className="text-foreground">{selectedNode.image}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Risk Level:</span>
                <span className={`font-semibold ${
                  selectedNode.riskLevel === 'critical' ? 'text-destructive' :
                  selectedNode.riskLevel === 'warning' ? 'text-warning' :
                  'text-success'
                }`}>
                  {selectedNode.riskLevel.toUpperCase()}
                </span>
              </div>
              {selectedNode.cpu !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">CPU:</span>
                  <span className="text-foreground">{selectedNode.cpu.toFixed(1)}%</span>
                </div>
              )}
              {selectedNode.memory !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Memory:</span>
                  <span className="text-foreground">{selectedNode.memory.toFixed(1)} MB</span>
                </div>
              )}
              {selectedNode.io !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">I/O:</span>
                  <span className="text-foreground">{selectedNode.io.toFixed(1)} KB/s</span>
                </div>
              )}
            </div>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default GraphView;
