/** API client for K-Claw WebUI */

import type { Workspace, WorkspaceCreate, MissionRequest, LogEntry, FileEntry } from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Workspaces
  listWorkspaces: (): Promise<Workspace[]> =>
    fetchJson<Workspace[]>(`${API_BASE}/workspaces`),

  getWorkspace: (id: string): Promise<Workspace> =>
    fetchJson<Workspace>(`${API_BASE}/workspaces/${id}`),

  createWorkspace: (data: WorkspaceCreate): Promise<Workspace> =>
    fetchJson<Workspace>(`${API_BASE}/workspaces`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteWorkspace: (id: string): Promise<{ message: string }> =>
    fetchJson<{ message: string }>(`${API_BASE}/workspaces/${id}`, {
      method: 'DELETE',
    }),

  // Files
  listFiles: (workspaceId: string, path: string = ''): Promise<FileEntry[]> =>
    fetchJson<FileEntry[]>(`${API_BASE}/workspaces/${workspaceId}/files?path=${encodeURIComponent(path)}`),

  // Missions
  runMission: (workspaceId: string, data: MissionRequest): Promise<{ message: string }> =>
    fetchJson<{ message: string }>(`${API_BASE}/workspaces/${workspaceId}/mission`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Logs
  getLogs: (workspaceId: string, limit: number = 100): Promise<LogEntry[]> =>
    fetchJson<LogEntry[]>(`${API_BASE}/workspaces/${workspaceId}/logs?limit=${limit}`),

  // Health
  healthCheck: (): Promise<{ status: string; version: string }> =>
    fetchJson<{ status: string; version: string }>(`${API_BASE}/health`),
};
