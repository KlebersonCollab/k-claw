/** Mission control component for sending missions to agents */

import { useState } from 'react';
import type { AgentType } from '../types';

interface MissionControlProps {
  workspaceId: string;
  onSendMission: (mission: string, agentId: AgentType) => Promise<void>;
}

const AGENTS: { id: AgentType; name: string; description: string; icon: string }[] = [
  { id: 'coder', name: 'Coder', description: 'Escrita de código, refatoração e correção de bugs', icon: '💻' },
  { id: 'researcher', name: 'Researcher', description: 'Busca semântica e análise de documentos', icon: '🔍' },
  { id: 'verifier', name: 'Verifier', description: 'Verificação de código, testes e validação', icon: '✅' },
];

export function MissionControl({ workspaceId, onSendMission }: MissionControlProps) {
  const [mission, setMission] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('coder');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!mission.trim()) {
      setError('Descreva a missão');
      return;
    }

    setIsLoading(true);
    try {
      await onSendMission(mission.trim(), selectedAgent);
      setSuccess('Missão enviada com sucesso!');
      setMission('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar missão');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-k-claw-400 mb-4">🎯 Enviar Missão</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Agent Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Agente
          </label>
          <div className="grid grid-cols-3 gap-2">
            {AGENTS.map((agent) => (
              <button
                key={agent.id}
                type="button"
                onClick={() => setSelectedAgent(agent.id)}
                className={`p-3 rounded border text-left transition-colors ${
                  selectedAgent === agent.id
                    ? 'border-k-claw-500 bg-k-claw-900/30'
                    : 'border-gray-600 hover:border-gray-500'
                }`}
              >
                <div className="text-xl mb-1">{agent.icon}</div>
                <div className="text-sm font-medium text-gray-200">{agent.name}</div>
                <div className="text-xs text-gray-500">{agent.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Mission Input */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Missão
          </label>
          <textarea
            value={mission}
            onChange={(e) => setMission(e.target.value)}
            placeholder="Descreva o que você quer que o agente faça..."
            rows={4}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-500 focus:outline-none focus:border-k-claw-500 resize-none"
            disabled={isLoading}
          />
        </div>

        {/* Messages */}
        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 border border-red-800 rounded p-2">
            {error}
          </div>
        )}
        {success && (
          <div className="text-green-400 text-sm bg-green-900/20 border border-green-800 rounded p-2">
            {success}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          className="w-full px-4 py-2 bg-k-claw-600 hover:bg-k-claw-500 rounded font-medium transition-colors disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Enviando...' : '🚀 Enviar Missão'}
        </button>
      </form>
    </div>
  );
}
