import { Activity, WifiOff } from 'lucide-react';
import { Card } from '@/components/ui/card';
interface ConnectionStatusProps {
  isConnected: boolean;
  className?: string;
}
export const ConnectionStatus = ({ isConnected, className }: ConnectionStatusProps) => {
  return (
    <Card className={`px-4 py-2 border-border ${className}`}>
      <div className="flex items-center gap-2">
        {isConnected ? (
          <>
            <Activity className="w-4 h-4 text-success animate-pulse" />
            <span className="text-sm font-medium text-foreground">Live</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium text-muted-foreground">Disconnected</span>
          </>
        )}
      </div>
    </Card>
  );
};
