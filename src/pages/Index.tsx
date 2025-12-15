import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import GraphView from '@/components/GraphView';
import EventTimeline from '@/components/EventTimeline';
import AlertsPanel from '@/components/AlertsPanel';
import FiltersPanel from '@/components/FiltersPanel';
import HistoricalView from '@/components/HistoricalView';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Shield } from 'lucide-react';

const Index = () => {
  const [activeTab, setActiveTab] = useState('live');

  // WebSocket connection for real-time events
  const { isConnected } = useWebSocket({
    url: 'ws://localhost:8000/ws',
    onMessage: (message) => {
      console.log('Received WebSocket message:', message);
      
      // Handle different message types
      switch (message.type) {
        case 'node':
          (window as any).graphView?.addNode(message.data);
          break;
        case 'edge':
          (window as any).graphView?.addEdge(message.data);
          break;
        case 'event':
          (window as any).eventTimeline?.addEvent(message.data);
          break;
        case 'alert':
          (window as any).alertsPanel?.pushAlert(message.data);
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    },
    onConnect: () => {
      console.log('Connected to WebSocket server');
    },
    onDisconnect: () => {
      console.log('Disconnected from WebSocket server');
    },
    autoReconnect: true,
  });

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
            <ConnectionStatus isConnected={isConnected} />
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
                <FiltersPanel className="h-full" />
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
