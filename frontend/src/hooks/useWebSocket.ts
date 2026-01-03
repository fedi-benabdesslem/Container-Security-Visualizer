import { useEffect, useRef, useState, useCallback } from 'react';
import { Filters } from '@/types';
export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  filters?: Record<string, any>;
  active_connections?: number;
  id?: number;
  timestamp_iso?: string;
  timestamp_ns?: number;
  monitor_type?: 'syscall' | 'network';
  pid?: number;
  uid?: number;
  comm?: string;
  container_id?: string;
  container_name?: string;
  container_image?: string;
  container_status?: string;
  argv?: string;
  event_type?: string;
  source_ip?: string;
  dest_ip?: string;
  source_port?: number;
  dest_port?: number;
  source_container_id?: string;
  dest_container_id?: string;
  source_container_name?: string;
  dest_container_name?: string;
  risk_score?: number;
  categories?: string[];
  is_security_relevant?: boolean;
}
interface UseWebSocketOptions {
  filters?: Filters;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}
const buildWebSocketUrl = (filters?: Filters): string => {
  const baseUrl = 'ws:
  const params = new URLSearchParams();
  if (filters) {
    const types: string[] = [];
    if (filters.showNetwork) types.push('network');
    if (filters.showSyscall) types.push('syscall');
    if (types.length === 1) {
      params.set('monitor_type', types[0]);
    }
    if (filters.showSuspicious) {
      params.set('suspicious_only', 'true');
    }
  }
  const queryString = params.toString();
  return queryString ? `${baseUrl}?${queryString}` : baseUrl;
};
export const useWebSocket = ({
  filters,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const onMessageRef = useRef(onMessage);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onMessageRef.current = onMessage;
    onConnectRef.current = onConnect;
    onDisconnectRef.current = onDisconnect;
    onErrorRef.current = onError;
  }, [onMessage, onConnect, onDisconnect, onError]);
  const filtersKey = JSON.stringify(filters);
  const connect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = undefined;
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    try {
      const url = buildWebSocketUrl(filters);
      console.log('Connecting to WebSocket:', url);
      ws.current = new WebSocket(url);
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        onConnectRef.current?.();
      };
      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessageRef.current?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        setIsConnected(false);
        onDisconnectRef.current?.();
        if (autoReconnect && event.code !== 1000) {
          reconnectTimeout.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, reconnectInterval);
        }
      };
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        onErrorRef.current?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [filtersKey, autoReconnect, reconnectInterval]);
  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = undefined;
    }
    if (ws.current) {
      ws.current.close(1000, 'Client disconnecting');
      ws.current = null;
    }
    setIsConnected(false);
  }, []);
  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);
  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close(1000, 'Component unmounting');
        ws.current = null;
      }
    };
  }, [filtersKey]);
  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
};
