import { useEffect, useState, useRef } from 'react';

export interface WebSocketEvent {
  type: 'RECORD_INGESTED' | 'AGENT_TASK_CREATED' | 'AUDIT_LOG_ADDED';
  data: any;
}

export function useWebSocket(url: string = 'ws://localhost:8000/api/v1/ws/events') {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<WebSocketEvent | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimer: NodeJS.Timeout;

    function connect() {
      try {
        const ws = new WebSocket(url);
        socketRef.current = ws;

        ws.onopen = () => {
          console.log('⚡ Connected to NexusOps Real-time Event Stream WebSocket');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const parsed: WebSocketEvent = JSON.parse(event.data);
            setLastEvent(parsed);
          } catch (e) {
            console.error('Error parsing WebSocket JSON:', e);
          }
        };

        ws.onclose = () => {
          console.warn('Disconnected from WebSocket. Reconnecting in 3s...');
          setIsConnected(false);
          reconnectTimer = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket Error:', error);
          ws.close();
        };
      } catch (err) {
        console.error('WebSocket Exception:', err);
        reconnectTimer = setTimeout(connect, 3000);
      }
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [url]);

  return { isConnected, lastEvent };
}
