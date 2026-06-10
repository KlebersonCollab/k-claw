# 🦾 K-Claw WebUI

Interface web para gerenciar workspaces e enviar missões para os agentes do K-Claw.

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Acessar
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

## 📁 Estrutura

```
webui/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── workspace_manager.py # CRUD de workspaces
│   ├── agent_runner.py      # Executor de agentes
│   ├── models.py            # Pydantic models
│   ├── requirements.txt     # Dependências Python
│   └── templates/
│       └── agents_template.md
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API client
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔌 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/workspaces` | Listar workspaces |
| POST | `/api/workspaces` | Criar workspace |
| GET | `/api/workspaces/{id}` | Detalhes do workspace |
| DELETE | `/api/workspaces/{id}` | Deletar workspace |
| GET | `/api/workspaces/{id}/files` | Listar arquivos |
| POST | `/api/workspaces/{id}/mission` | Enviar missão |
| GET | `/api/workspaces/{id}/logs` | Logs históricos |
| WS | `/ws/{workspace_id}` | WebSocket para logs |

## 📋 Workspaces

Cada workspace é uma pasta isolada em `workspaces/` com a seguinte estrutura:

```
workspaces/{nome}/
├── AGENTS.md          # Diretrizes do agente
├── README.md          # Documentação do projeto
├── pyproject.toml     # Configuração Python
├── src/               # Código fonte
└── tests/             # Testes
    ├── unit/
    ├── integration/
    ├── e2e/
    └── edge_cases/
```
