/** Live logs component with WebSocket connection */

import { useEffect, useRef } from 'react';
import type { LogEntry } from '../types';

interface LiveLogsProps {
  logs: LogEntry[];
  isConnected: boolean;
  onClear: () => void;
}

const LEVEL_COLORS: Record<string, string> = {
  INFO: 'text-blue-400',
  WARNING: 'text-yellow-400',
  ERROR: 'text-red-400',
  DEBUG: 'text-gray-500',
};

export function LiveLogs({ logs, isConnected, onClear }: LiveLogsProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm font-medium text-gray-300">Live Logs</span>
          <span className="text-xs text-gray-500">({logs.length})</span>
        </div>
        <button
          onClick={onClear}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          Limpar
        </button>
      </div>

      {/* Logs Container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto p-2 font-mono text-xs space-y-1"
        style={{ maxHeight: '300px' }}
      >
        {logs.length === 0 ? (
          <div className="text-gray-500 text-center py-4">
            Aguardando logs...
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="flex gap-2 hover:bg-gray-700/30 px-1 rounded">
              <span className="text-gray-600 shrink-0">{formatTime(log.timestamp)}</span>
              <span className={`shrink-0 ${LEVEL_COLORS[log.level] || 'text-gray-400'}`}>
                [{log.level}]
              </span>
              <span className="text-gray-500 shrink-0">({log.source})</span>
              <span className="text-gray-300 break-all">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
