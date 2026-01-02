import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { api, HistoricalEvent } from '@/lib/api';
import { Calendar, Search, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface HistoricalViewProps {
  className?: string;
}

export const HistoricalView = ({ className }: HistoricalViewProps) => {
  const [events, setEvents] = useState<HistoricalEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const { toast } = useToast();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory();
      setEvents(data);
    } catch (error) {
      console.error('Failed to fetch history:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch historical data. Make sure the backend is running.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredEvents = events.filter(
    (event) =>
      event.containerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className={className}>
      <Card className="h-full bg-card border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                Historical Events
              </h2>
              <p className="text-sm text-muted-foreground">
                Browse past security events
              </p>
            </div>
            <Button
              onClick={fetchHistory}
              disabled={loading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by container or event type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4">
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
                <p className="text-muted-foreground">Loading historical data...</p>
              </div>
            ) : filteredEvents.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No historical events found</p>
                <p className="text-sm mt-2">
                  {searchTerm ? 'Try a different search term' : 'Events will appear here once the backend starts sending data'}
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredEvents.map((event) => (
                  <Card
                    key={event.id}
                    className="p-4 bg-secondary border-border hover:border-primary transition-smooth"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-foreground font-mono">
                          {event.containerName}
                        </h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground font-mono">
                          {event.type}
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground font-mono">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <pre className="text-xs font-mono text-muted-foreground mt-2 overflow-x-auto">
                      {JSON.stringify(event.data, null, 2)}
                    </pre>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </Card>
    </div>
  );
};

export default HistoricalView;
