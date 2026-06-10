/** Workspace card component */

import type { Workspace } from '../types';

interface WorkspaceCardProps {
  workspace: Workspace;
  onDelete: (id: string) => void;
}

export function WorkspaceCard({ workspace, onDelete }: WorkspaceCardProps) {
  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-k-claw-400">{workspace.name}</h3>
          {workspace.description && (
            <p className="text-sm text-gray-400 mt-1">{workspace.description}</p>
          )}
        </div>
        <button
          onClick={() => onDelete(workspace.id)}
          className="text-gray-500 hover:text-red-400 transition-colors"
          title="Deletar workspace"
        >
          🗑️
        </button>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Criado:</span>
          <span className="ml-2 text-gray-300">{formatDate(workspace.created_at)}</span>
        </div>
        <div>
          <span className="text-gray-500">Arquivos:</span>
          <span className="ml-2 text-gray-300">{workspace.file_count}</span>
        </div>
        <div className="col-span-2">
          <span className="text-gray-500">AGENTS.md:</span>
          <span className={`ml-2 ${workspace.agents_md_exists ? 'text-green-400' : 'text-yellow-400'}`}>
            {workspace.agents_md_exists ? '✓ Presente' : '✗ Ausente'}
          </span>
        </div>
      </div>
    </div>
  );
}
