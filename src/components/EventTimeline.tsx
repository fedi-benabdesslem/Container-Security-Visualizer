import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { SecurityEvent } from '@/types';
import { Activity, Network, FileText, Terminal } from 'lucide-react';

interface EventTimelineProps {
  className?: string;
}

export const EventTimeline = ({ className }: EventTimelineProps) => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'network':
        return <Network className="w-4 h-4" />;
      case 'syscall':
        return <Terminal className="w-4 h-4" />;
      case 'file':
        return <FileText className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-destructive border-destructive';
      case 'warning':
        return 'text-warning border-warning';
      default:
        return 'text-primary border-primary';
    }
  };

  const addEvent = useCallback((event: SecurityEvent) => {
    setEvents((prev) => [event, ...prev].slice(0, 100)); // Keep last 100 events
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  // Expose methods globally
  useEffect(() => {
    (window as any).eventTimeline = {
      addEvent,
      clearEvents,
    };
    return () => {
      delete (window as any).eventTimeline;
    };
  }, [addEvent, clearEvents]);

  return (
    <div className={className}>
      <Card className="h-full bg-card border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Event Timeline</h2>
          <p className="text-sm text-muted-foreground">Real-time system events</p>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-2">
            {events.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Waiting for events...</p>
              </div>
            ) : (
              events.map((event) => (
                <div
                  key={event.id}
                  className={`p-3 rounded-lg bg-secondary border-l-4 ${getSeverityColor(event.severity)} transition-smooth hover:bg-secondary/80`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 ${getSeverityColor(event.severity)}`}>
                      {getEventIcon(event.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-foreground">
                          {event.containerName}
                        </span>
                        <span className="text-xs text-muted-foreground font-mono">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{event.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground font-mono">
                          {event.type}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                          event.severity === 'critical' ? 'bg-destructive/20 text-destructive' :
                          event.severity === 'warning' ? 'bg-warning/20 text-warning' :
                          'bg-primary/20 text-primary'
                        }`}>
                          {event.severity}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </Card>
    </div>
  );
};

export default EventTimeline;
