/** Types for K-Claw WebUI */

export interface Workspace {
  id: string;
  name: string;
  description: string;
  created_at: string;
  file_count: number;
  agents_md_exists: boolean;
}

export interface WorkspaceCreate {
  name: string;
  description?: string;
}

export interface MissionRequest {
  mission: string;
  agent_id?: string;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

export interface FileEntry {
  name: string;
  path: string;
  is_dir: boolean;
  size: number;
}

export type AgentType = 'coder' | 'researcher' | 'verifier';
