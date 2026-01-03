import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
interface UseHealthCheckOptions {
  pollInterval?: number;
}
export const useHealthCheck = ({ pollInterval = 5000 }: UseHealthCheckOptions = {}) => {
  const [isHealthy, setIsHealthy] = useState(false);
  const [version, setVersion] = useState<string | null>(null);
  const checkHealth = useCallback(async () => {
    try {
      const response = await api.checkHealth();
      setIsHealthy(response.status === 'healthy');
      setVersion(response.version);
    } catch (error) {
      setIsHealthy(false);
      setVersion(null);
    }
  }, []);
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, pollInterval);
    return () => clearInterval(interval);
  }, [checkHealth, pollInterval]);
  return { isHealthy, version, checkHealth };
};
