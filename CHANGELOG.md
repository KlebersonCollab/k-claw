# 📜 Changelog — Agent Harness

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [0.1.0] — 2026-01-17

### ✨ Funcionalidades

- **Orquestração Delegativa** — Agente Pai (K-Claw) delega para especialistas; nunca executa diretamente.
- **Memória em 3 Camadas** — L1: Cache de Sessão → L2: FTS5 + Busca Vetorial → L3: Detalhe Completo sob Demanda.
- **Busca Híbrida** — FTS5 (palavra-chave exata) + sqlite-vec (similaridade semântica com cosseno, 384 dims).
- **Human-in-the-Loop (HITL)** — Portas de aprovação interativas antes de operações destrutivas.
- **Modo Incógnito** — Suspende toda persistência; nenhum log é gravado no SQLite.
- **Redação de Segredos** — Chaves de API e secrets são automaticamente mascarados via regex.
- **Compactação de Contexto** — Geração automática de "State Memo" quando o orçamento de contexto é excedido.
- **Carregamento Dinâmico** — Sub-agentes definidos em `.md` com YAML frontmatter; skills injetados na delegação.
- **Multi-Provider LLM** — Suporte para OpenAI, Anthropic (Claude), Google, OpenRouter e Ollama (local).
- **Life Cycle Hooks** — Pre-tool e post-tool hooks para extensibilidade sem tocar no harness.
- **Loop de Correção** — Orquestrador com loop coder → verifier com max retries e decisão DELIVER/ESCALATE.
- **CLI Interativa** — REPL com Rich (tabelas, cores, prompts, status) + opção de retomar sessões.
- **REST API** — Endpoints FastAPI: `/chat`, `/approve`, `/stream`, `/status`, `/health`.
- **Telegram Bot** — Integração completa com Telegram, incluindo autorização por user ID.
- **Classificação de Comandos Shell** — Risco avaliado antes da execução (read/write/full).
- **Pre-commit Hooks** — Verificação de segredos, formatação, YAML, chaves privadas.

### 🧪 Testes

- Estrutura completa de testes: `unit/`, `integration/`, `e2e/`, `edge_cases/`.
- 9 arquivos de teste na raiz cobrindo FTS5, guardrails, HITL, incognito, layered search, recursive prompt, safety, sub-agents e verifier flow.
- Configuração pytest com `asyncio_mode=auto`.
- Cobertura mínima exigida: 90%.

### 📚 Documentação

- `README.md` — Documentação principal com badges, features, arquitetura, instalação e uso.
- `ARCH.md` — Documentação técnica detalhada (688+ linhas) com diagramas Mermaid.
- `AGENTS.md` — Catálogo de agentes com regras de engajamento e fluxo de delegação.
- `TOOLS.md` — Manual completo de 11 ferramentas com permissões e exemplos.
- `REPORT.md` — Análise técnica com avaliações por eixo e plano de melhorias.
- `CONTRIBUTING.md` — Guia de contribuição com padrões de qualidade.
- `CHANGELOG.md` — Este arquivo.

### 🔒 Segurança

- Controle de permissões hierárquico (read → write → execute).
- Human-in-the-Loop para operações destrutivas.
- Redação automática de segredos via regex.
- Classificação dinâmica de comandos shell.
- Pre-commit hooks com verificação de secrets.
- Life Cycle Hooks para extensibilidade segura.

---

## [0.0.1] — 2025-07-16

### 🎉 Início do Projeto

- Estrutura inicial do framework.
- Implementação básica do LangGraph StateGraph.
- CLI interativa com Rich.
- Persistência SQLite com SQLAlchemy.
- Suporte multi-provider LLM.
