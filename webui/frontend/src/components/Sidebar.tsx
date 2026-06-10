/** Sidebar component with workspace list */

import type { Workspace } from '../types';

interface SidebarProps {
  workspaces: Workspace[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onCreateClick: () => void;
  onRefresh: () => void;
}

export function Sidebar({ workspaces, selectedId, onSelect, onCreateClick, onRefresh }: SidebarProps) {
  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🦾</span>
          <h1 className="text-xl font-bold text-k-claw-400">K-Claw</h1>
        </div>
        <p className="text-xs text-gray-400 mt-1">Agent Orchestrator</p>
      </div>

      {/* Actions */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        <button
          onClick={onCreateClick}
          className="w-full px-3 py-2 bg-k-claw-600 hover:bg-k-claw-500 rounded text-sm font-medium transition-colors"
        >
          + Novo Workspace
        </button>
        <button
          onClick={onRefresh}
          className="w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
        >
          ↻ Atualizar
        </button>
      </div>

      {/* Workspace List */}
      <div className="flex-1 overflow-y-auto p-2">
        <p className="text-xs text-gray-500 uppercase tracking-wider px-2 mb-2">
          Workspaces ({workspaces.length})
        </p>

        {workspaces.length === 0 ? (
          <p className="text-sm text-gray-500 px-2 py-4 text-center">
            Nenhum workspace criado
          </p>
        ) : (
          <div className="space-y-1">
            {workspaces.map((ws) => (
              <button
                key={ws.id}
                onClick={() => onSelect(ws.id)}
                className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                  selectedId === ws.id
                    ? 'bg-k-claw-700 text-white'
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <div className="font-medium truncate">{ws.name}</div>
                <div className="text-xs text-gray-500">
                  {ws.file_count} arquivos
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-700 text-xs text-gray-500 text-center">
        v0.1.0
      </div>
    </div>
  );
}
