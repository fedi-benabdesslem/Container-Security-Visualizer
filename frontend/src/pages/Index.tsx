import { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import GraphView from '@/components/GraphView';
import EventTimeline from '@/components/EventTimeline';
import AlertsPanel from '@/components/AlertsPanel';
import FiltersPanel from '@/components/FiltersPanel';
import HistoricalView from '@/components/HistoricalView';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useWebSocket, WebSocketMessage } from '@/hooks/useWebSocket';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { api } from '@/lib/api';
import { Shield } from 'lucide-react';
import { Filters } from '@/types';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const [activeTab, setActiveTab] = useState('live');
  const [filters, setFilters] = useState<Filters>({
    showNetwork: true,
    showSyscall: true,
    showSuspicious: false,
  });
  const { toast } = useToast();

  // Health check for connection status
  const { isHealthy } = useHealthCheck({ pollInterval: 5000 });

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message: WebSocketMessage) => {
    console.log('Received WebSocket message:', message);

    // Handle control messages
    if (message.type === 'connected') {
      console.log('WebSocket connected:', message.message);
      return;
    }

    if (message.type === 'pong' || message.type === 'stats') {
      return;
    }

    // Handle event messages - these come directly as event objects
    if (message.id && message.container_id) {
      // Map to container node
      const nodeData = {
        id: message.container_id,
        name: message.container_name || 'Unknown',
        image: message.container_image || '',
        status: message.container_status || 'running',
        riskLevel: message.risk_score && message.risk_score >= 7 ? 'critical' as const :
                   message.risk_score && message.risk_score >= 4 ? 'warning' as const : 'safe' as const,
      };
      (window as any).graphView?.addNode(nodeData);

      // Add event to timeline
      const eventData = {
        id: message.id.toString(),
        timestamp: new Date(message.timestamp_iso || Date.now()).getTime(),
        type: message.monitor_type || 'unknown',
        containerId: message.container_id,
        containerName: message.container_name || 'Unknown',
        data: {
          comm: message.comm,
          argv: message.argv,
          event_type: message.event_type,
          source_ip: message.source_ip,
          dest_ip: message.dest_ip,
          source_port: message.source_port,
          dest_port: message.dest_port,
          risk_score: message.risk_score,
        },
        severity: message.risk_score && message.risk_score >= 7 ? 'critical' as const :
                  message.risk_score && message.risk_score >= 4 ? 'warning' as const : 'info' as const,
      };
      (window as any).eventTimeline?.addEvent(eventData);

      // If high risk, also push to alerts
      if (message.is_security_relevant && message.risk_score && message.risk_score >= 7) {
        const alertData = {
          id: `alert-${message.id}`,
          timestamp: new Date(message.timestamp_iso || Date.now()).getTime(),
          title: `High Risk Event: ${message.comm}`,
          description: message.argv || `${message.event_type || message.monitor_type} event detected`,
          severity: 'critical' as const,
          containerName: message.container_name,
        };
        (window as any).alertsPanel?.pushAlert(alertData);
      }
    }
  }, []);

  // WebSocket connection for real-time events
  const { isConnected } = useWebSocket({
    filters,
    onMessage: handleMessage,
    onConnect: () => {
      console.log('Connected to WebSocket server');
    },
    onDisconnect: () => {
      console.log('Disconnected from WebSocket server');
    },
    autoReconnect: true,
  });

  // Poll alerts periodically
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const alerts = await api.getAlerts(50);
        // Push alerts to panel
        alerts.forEach(alert => {
          (window as any).alertsPanel?.pushAlert({
            id: `api-alert-${alert.id}`,
            timestamp: new Date(alert.timestamp_iso).getTime(),
            title: `Risk Score: ${alert.risk_score}`,
            description: alert.description,
            severity: alert.risk_score >= 8 ? 'critical' as const : 'warning' as const,
            containerName: alert.container_name,
          });
        });
      } catch (error) {
        // Silent fail - alerts will come through WebSocket too
      }
    };

    // Initial fetch
    fetchAlerts();

    // Poll every 10 seconds
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleFiltersChange = (newFilters: Filters) => {
    setFilters(newFilters);
  };

  // Connection status combines health check and WebSocket
  const connectionStatus = isHealthy && isConnected;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  Container Security Visualizer
                </h1>
                <p className="text-sm text-muted-foreground">
                  Real-time container monitoring and threat detection
                </p>
              </div>
            </div>
            <ConnectionStatus isConnected={connectionStatus} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="mb-4">
            <TabsTrigger value="live">Live View</TabsTrigger>
            <TabsTrigger value="history">Historical Data</TabsTrigger>
          </TabsList>

          <TabsContent value="live" className="space-y-4">
            <div className="grid grid-cols-12 gap-4 h-[calc(100vh-16rem)]">
              {/* Left Panel - Filters */}
              <div className="col-span-2">
                <FiltersPanel className="h-full" onFiltersChange={handleFiltersChange} />
              </div>

              {/* Center - Graph View */}
              <div className="col-span-7">
                <GraphView className="h-full" />
              </div>

              {/* Right Panel - Events & Alerts */}
              <div className="col-span-3 space-y-4 h-full">
                <div className="h-1/2">
                  <AlertsPanel className="h-full" />
                </div>
                <div className="h-1/2">
                  <EventTimeline className="h-full" />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="history" className="h-[calc(100vh-16rem)]">
            <HistoricalView className="h-full" />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
