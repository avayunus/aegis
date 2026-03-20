import { useEffect, useRef, useState, useCallback } from "react";
import type { TelemetryFrame } from "../types";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

/**
 * Hook that maintains a WebSocket connection to the telemetry stream.
 *
 * Returns the latest telemetry frame and the connection status.
 * Automatically reconnects on disconnect with exponential backoff.
 */
export function useWebSocket(url: string) {
  const [frame, setFrame] = useState<TelemetryFrame | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number>(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus("connected");
      retryRef.current = 0; // Reset backoff
    };

    ws.onmessage = (event) => {
      try {
        const data: TelemetryFrame = JSON.parse(event.data);
        setFrame(data);
      } catch {
        console.warn("[WS] Failed to parse telemetry frame");
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      wsRef.current = null;

      // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
      const delay = Math.min(1000 * 2 ** retryRef.current, 30000);
      retryRef.current += 1;
      timerRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      setStatus("error");
      ws.close();
    };

    wsRef.current = ws;
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [connect]);

  return { frame, status };
}
