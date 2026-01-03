import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert } from '@/types';
import { AlertTriangle, XCircle } from 'lucide-react';
interface AlertsPanelProps {
  className?: string;
}
export const AlertsPanel = ({ className }: AlertsPanelProps) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const pushAlert = useCallback((alert: Alert) => {
    setAlerts((prev) => [alert, ...prev].slice(0, 50)); 
  }, []);
  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);
  useEffect(() => {
    (window as any).alertsPanel = {
      pushAlert,
      clearAlerts,
    };
    return () => {
      delete (window as any).alertsPanel;
    };
  }, [pushAlert, clearAlerts]);
  return (
    <div className={className}>
      <Card className="h-full bg-card border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-warning" />
            Security Alerts
          </h2>
          <p className="text-sm text-muted-foreground">Suspicious activity detected</p>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-3">
            {alerts.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No alerts</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded-lg border-2 ${
                    alert.severity === 'critical' 
                      ? 'bg-destructive/10 border-destructive' 
                      : 'bg-warning/10 border-warning'
                  } animate-fade-in`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 ${
                      alert.severity === 'critical' ? 'text-destructive' : 'text-warning'
                    }`}>
                      {alert.severity === 'critical' ? (
                        <XCircle className="w-5 h-5" />
                      ) : (
                        <AlertTriangle className="w-5 h-5" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className={`text-sm font-bold ${
                          alert.severity === 'critical' ? 'text-destructive' : 'text-warning'
                        }`}>
                          {alert.title}
                        </h3>
                        <span className="text-xs text-muted-foreground font-mono">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-foreground mb-2">{alert.description}</p>
                      {alert.containerName && (
                        <span className="text-xs px-2 py-1 rounded bg-muted text-muted-foreground font-mono">
                          {alert.containerName}
                        </span>
                      )}
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
export default AlertsPanel;
