import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { api, BackendEvent } from '@/lib/api';
import { Calendar, Search, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
interface HistoricalViewProps {
  className?: string;
}
export const HistoricalView = ({ className }: HistoricalViewProps) => {
  const [events, setEvents] = useState<BackendEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [total, setTotal] = useState(0);
  const { toast } = useToast();
  const fetchHistory = async (search?: string) => {
    setLoading(true);
    try {
      const data = await api.getEvents({
        search: search || undefined,
        limit: 50
      });
      setEvents(data.events);
      setTotal(data.total);
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
  const handleSearch = () => {
    fetchHistory(searchTerm);
  };
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };
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
                {total > 0 ? `${total} events found` : 'Browse past security events'}
              </p>
            </div>
            <Button
              onClick={() => fetchHistory(searchTerm)}
              disabled={loading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          <div className="relative flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search by container, command, or argv..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={handleKeyDown}
                className="pl-10"
              />
            </div>
            <Button onClick={handleSearch} variant="secondary" disabled={loading}>
              Search
            </Button>
          </div>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-4">
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
                <p className="text-muted-foreground">Loading historical data...</p>
              </div>
            ) : events.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No historical events found</p>
                <p className="text-sm mt-2">
                  {searchTerm ? 'Try a different search term' : 'Events will appear here once the backend starts sending data'}
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {events.map((event) => (
                  <Card
                    key={event.id}
                    className="p-4 bg-secondary border-border hover:border-primary transition-smooth"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-foreground font-mono">
                          {event.container_name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded font-mono ${
                            event.monitor_type === 'network' 
                              ? 'bg-primary/20 text-primary' 
                              : 'bg-accent/20 text-accent-foreground'
                          }`}>
                            {event.monitor_type}
                          </span>
                          {event.risk_score >= 7 && (
                            <span className="text-xs px-2 py-0.5 rounded bg-destructive/20 text-destructive font-mono">
                              Risk: {event.risk_score}
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-muted-foreground font-mono">
                        {new Date(event.timestamp_iso).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground mt-2 font-mono">
                      <p><span className="text-foreground">Command:</span> {event.comm}</p>
                      {event.argv && <p><span className="text-foreground">Args:</span> {event.argv}</p>}
                      {event.event_type && <p><span className="text-foreground">Type:</span> {event.event_type}</p>}
                      {event.dest_ip && (
                        <p><span className="text-foreground">Dest:</span> {event.dest_ip}:{event.dest_port}</p>
                      )}
                    </div>
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
