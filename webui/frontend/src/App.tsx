/** Main App component for K-Claw WebUI */

import { useState, useEffect, useCallback } from 'react';
import type { Workspace, FileEntry, AgentType } from './types';
import { api } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { CreateWorkspaceModal } from './components/CreateWorkspaceModal';
import { MissionControl } from './components/MissionControl';
import { LiveLogs } from './components/LiveLogs';

function App() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // WebSocket for live logs
  const { logs, isConnected, clearLogs } = useWebSocket({
    workspaceId: selectedWorkspace?.id || '',
  });

  // Load workspaces
  const loadWorkspaces = useCallback(async () => {
    try {
      const data = await api.listWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      console.error('Failed to load workspaces:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load files for selected workspace
  const loadFiles = useCallback(async (workspaceId: string) => {
    try {
      const data = await api.listFiles(workspaceId);
      setFiles(data);
    } catch (err) {
      console.error('Failed to load files:', err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadWorkspaces();
  }, [loadWorkspaces]);

  // Handle workspace selection
  const handleSelectWorkspace = async (id: string) => {
    try {
      const workspace = await api.getWorkspace(id);
      setSelectedWorkspace(workspace);
      clearLogs();
      await loadFiles(id);
    } catch (err) {
      console.error('Failed to select workspace:', err);
    }
  };

  // Handle workspace creation
  const handleCreateWorkspace = async (name: string, description: string) => {
    await api.createWorkspace({ name, description });
    await loadWorkspaces();
    await handleSelectWorkspace(name.toLowerCase());
  };

  // Handle workspace deletion
  const handleDeleteWorkspace = async (id: string) => {
    if (!confirm(`Tem certeza que deseja deletar o workspace "${id}"?`)) return;

    try {
      await api.deleteWorkspace(id);
      if (selectedWorkspace?.id === id) {
        setSelectedWorkspace(null);
        setFiles([]);
        clearLogs();
      }
      await loadWorkspaces();
    } catch (err) {
      console.error('Failed to delete workspace:', err);
    }
  };

  // Handle mission submission
  const handleSendMission = async (mission: string, agentId: AgentType) => {
    if (!selectedWorkspace) return;
    await api.runMission(selectedWorkspace.id, { mission, agent_id: agentId });
  };

  // Handle file navigation
  const handleNavigate = async (path: string) => {
    if (!selectedWorkspace) return;
    try {
      const data = await api.listFiles(selectedWorkspace.id, path);
      setFiles(data);
    } catch (err) {
      console.error('Failed to navigate:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <span className="text-4xl animate-pulse">🦾</span>
          <p className="text-gray-400 mt-2">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-900 text-white">
      {/* Sidebar */}
      <Sidebar
        workspaces={workspaces}
        selectedId={selectedWorkspace?.id || null}
        onSelect={handleSelectWorkspace}
        onCreateClick={() => setIsModalOpen(true)}
        onRefresh={loadWorkspaces}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Dashboard */}
        <Dashboard
          workspace={selectedWorkspace}
          files={files}
          onDelete={handleDeleteWorkspace}
          onNavigate={handleNavigate}
        />

        {/* Bottom Panel */}
        {selectedWorkspace && (
          <div className="border-t border-gray-700 p-4 grid grid-cols-2 gap-4">
            <MissionControl
              workspaceId={selectedWorkspace.id}
              onSendMission={handleSendMission}
            />
            <LiveLogs
              logs={logs}
              isConnected={isConnected}
              onClear={clearLogs}
            />
          </div>
        )}
      </div>

      {/* Modal */}
      <CreateWorkspaceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateWorkspace}
      />
    </div>
  );
}

export default App;
