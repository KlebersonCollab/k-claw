/** Dashboard component for workspace overview */

import type { Workspace, FileEntry } from '../types';
import { WorkspaceCard } from './WorkspaceCard';

interface DashboardProps {
  workspace: Workspace | null;
  files: FileEntry[];
  onDelete: (id: string) => void;
  onNavigate: (path: string) => void;
}

export function Dashboard({ workspace, files, onDelete, onNavigate }: DashboardProps) {
  if (!workspace) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl">🦾</span>
          <h2 className="text-2xl font-bold text-gray-400 mt-4">Bem-vindo ao K-Claw</h2>
          <p className="text-gray-500 mt-2">
            Selecione um workspace ou crie um novo para começar
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-k-claw-400">{workspace.name}</h2>
        <p className="text-gray-400">Visão geral do workspace</p>
      </div>

      {/* Workspace Info */}
      <div className="mb-6">
        <WorkspaceCard workspace={workspace} onDelete={onDelete} />
      </div>

      {/* Files */}
      <div>
        <h3 className="text-lg font-semibold text-gray-300 mb-3">Arquivos</h3>
        {files.length === 0 ? (
          <p className="text-gray-500 text-sm">Nenhum arquivo encontrado</p>
        ) : (
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-700/50">
                <tr>
                  <th className="text-left px-4 py-2 text-gray-400">Nome</th>
                  <th className="text-left px-4 py-2 text-gray-400">Tipo</th>
                  <th className="text-right px-4 py-2 text-gray-400">Tamanho</th>
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr
                    key={file.path}
                    className="border-t border-gray-700 hover:bg-gray-700/30 cursor-pointer"
                    onClick={() => file.is_dir && onNavigate(file.path)}
                  >
                    <td className="px-4 py-2">
                      <span className="mr-2">{file.is_dir ? '📁' : '📄'}</span>
                      <span className={file.is_dir ? 'text-k-claw-400' : 'text-gray-300'}>
                        {file.name}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-gray-500">
                      {file.is_dir ? 'Diretório' : 'Arquivo'}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-500">
                      {file.is_dir ? '-' : formatSize(file.size)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
