# 📊 Relatório de Análise Técnica — Agent Harness

> **Data:** 2025-07-16
> **Versão Analisada:** 0.1.0
> **Avaliador:** K-Claw — Engenheiro de Software Sênior
> **Escopo:** Todos os módulos-fonte (12 arquivos `.py`), arquivos de configuração, testes e scripts auxiliares.

---

## 📋 Resumo Executivo

O **Agent Harness** é um framework de orquestração multi-agente em Python (≥3.12) que implementa uma arquitetura **Agente Pai (Orquestrador) + Sub-Agentes Especialistas** via LangGraph. O sistema possui memória em camadas (L1 cache → L2 FTS5 + busca vetorial → L3 detalhe completo), suporte a múltiplos providers de LLM (OpenAI, Anthropic, Google, OpenRouter), interface CLI com Rich, API REST com FastAPI, e mecanismos de segurança como Human-in-the-Loop (HITL), redação de segredos e modo incógnito.

### Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.13+ |
| Orquestração | LangGraph (StateGraph) |
| LLM | LangChain + Multi-Provider (OpenAI, Anthropic, Google, OpenRouter) |
| Memória | SQLite + FTS5 + sqlite-vec (384 dims, all-MiniLM-L6-v2) |
| ORM | SQLAlchemy 2.0 |
| CLI | Rich (REPL interativo) |
| API | FastAPI + Uvicorn |
| Qualidade | pre-commit, pytest, uv |
| Segurança | Human-in-the-Loop, Secret Redaction, Classificação Dinâmica de Comandos |
| Gerenciamento | uv (package manager) |

### Avaliação por Eixo

| Eixo | Status | Nota |
|------|--------|------|
| 🏗️ Arquitetura | 🟡 Bom, com pontos de melhoria | 7/10 |
| ✅ Qualidade de Código | 🟡 Aceitável, needs polish | 6/10 |
| 🧪 Testes | 🟡 Estrutura ok, pouca cobertura real | 5/10 |
| 🔒 Segurança | 🟡 Boas bases, falhas relevantes | 6/10 |
| 📚 Documentação | 🟢 Excelente | 9/10 |
| ⚙️ DevOps/Config | 🟢 Muito bom | 8/10 |

---

## 🏗️ Anquitetural Analysis

### Diagrama Textual

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERFACE LAYER                              │
│  ┌──────────────┐              ┌──────────────┐                     │
│  │  cli.py      │              │  api.py      │                     │
│  │  (Rich REPL) │              │  (FastAPI)   │                     │
│  └──────┬───────┘              └──────┬───────┘                     │
│         │ UIInterface (abstract)       │ UIInterface (abstract)       │
├─────────┼──────────────────────────────┼─────────────────────────────┤
│         ▼         ORCHESTRATION LAYER  ▼                             │
│  ┌─────────────────────────────────────────┐                         │
│  │  harness.py  (LangGraph StateGraph)     │                         │
│  │  Nodes: agent → tools → compact         │                         │
│  └──────┬──────────────┬──────────────┬────┘                         │
│         │              │              │                               │
│  ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼────────┐                    │
│  │  logic.py   │ │  tools.py  │ │  hooks.py    │                    │
│  │  call_model │ │  ToolReg.  │ │  HookManager │                    │
│  │  should_    │ │  8 tools   │ │  Pre/Post    │                    │
│  │  continue   │ │            │ │              │                    │
│  │  exec_tools │ │            │ │              │                    │
│  │  compact    │ │            │ │              │                    │
│  └─────────────┘ └────────────┘ └──────────────┘                     │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │  agent_loader.py │  │  state.py        │                         │
│  │  YAML→AgentDef   │  │  HarnessState    │                         │
│  └──────────────────┘  └──────────────────┘                         │
├─────────────────────────────────────────────────────────────────────┤
│                       PERSISTENCE LAYER                              │
│  ┌─────────────────┐  ┌──────────────────┐                          │
│  │  persistence.py  │  │  persistence_db  │                         │
│  │  SessionLogger   │  │  SQLAlchemy ORM  │                         │
│  │  Hybrid Search   │  │  SQLite+FTS5+vec │                         │
│  └─────────────────┘  └──────────────────┘                          │
├─────────────────────────────────────────────────────────────────────┤
│                      CROSS-CUTTING                                   │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐            │
│  │  utils.py   │  │ ui_interface │  │  system.log      │            │
│  │  PathFilter │  │ ContextVar   │  │  stderr/stdout   │            │
│  │  get_model  │  │ _UI_VAR      │  │  (dinâmico)      │            │
│  └────────────┘  └──────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### Padrões Arquiteturais Identificados

1. **Harness Pattern** — Orquestração via LangGraph com ciclo `agent → tools → agent` e compactação condicional
2. **Registry Pattern** — `ToolRegistry` com registros tipados (`ToolDescriptor`) e checagem hierárquica de permissões
3. **Strategy Pattern** — `UIInterface` com implementações `CLIInterface`, `APIInterface`
4. **Observer Pattern** — Sistema de eventos via `UIInterface.on_event()` e `HookManager` pre/post tool
5. **Repository Pattern** — `SessionLogger` abstraindo o acesso ao banco
6. **Template Method** — Assinatura fixa dos hooks (pre_tool/post_tool)
7. **Lazy Initialization** — Model cache (`_MODEL_CACHE`) e embeddings (`_EMBEDDINGS_MODEL`)

### Análise de Acoplamento e Coesão

| Módulo | Responsabilidade Única | Acoplamento | Observação |
|--------|----------------------|-------------|------------|
| `harness.py` | Orquestração do grafo | 🟢 Baixo | Bem isolado |
| `logic.py` | Nós do grafo + prompts | 🟡 Médio | Muitas responsabilidades (cache, eventos, sanitização) |
| `tools.py` | Registro e execução de ferramentas | 🟢 Baixo | Registry bem desenhado |
| `state.py` | Definição de estado do grafo | 🟢 Baixo | TypedDict limpo |
| `persistence.py` | CRUD + busca híbrida | 🟡 Médio | Mistura logging com busca vetorial |
| `persistence_db.py` | Modelos ORM | 🟢 Baixo | Bem definido |
| `hooks.py` | Extensibility pipeline | 🟢 Baixo | Design limpo |
| `agent_loader.py` | Parse de YAML/MD | 🟢 Baixo | Bom isolamento |
| `utils.py` | Utilitários + logging + PathFilter | 🔴 ALTO | God Object — faz path filtering, logging, model factory, redação de secrets |
| `ui_interface.py` | Abstração UI | 🟢 Baixo | ContextVar thread-safe |
| `cli.py` | Interface interativa | 🟡 Médio | Mistura parsing, display, e loop de execução |
| `api.py` | Endpoints REST/SSE | 🟡 Médio | Hardcodes `permissions: "execute"` e `context_budget: 10` |

### Grafo de Dependências

```
harness.py ──→ logic.py, tools.py, state.py
logic.py   ──→ tools.py, state.py, utils.py, persistence.py, agent_loader.py, hooks.py, ui_interface.py
tools.py   ──→ utils.py
cli.py     ──→ harness.py, persistence.py, ui_interface.py
api.py     ──→ harness.py, persistence.py, ui_interface.py
persistence.py ──→ persistence_db.py
```

**⚠️ Conclusão:** `utils.py` é Hub/Spoke central — alteração nele impacta quase tudo.

---

## ✅ Pontos Fortes

1. **🎯 Arquitetura de Orquestração Delegativa Bem Definida**
   - O padrão "Orquestrador nunca executa, apenas delega" via `delegate_to_agent` é uma forte separação de responsabilidades.

2. **🔒 Mecanismo de Segurança Human-in-the-Loop (HITL)**
   - Portas de aprovação interativas com apresentação clara (tool args em painel Rich).
   - Classificação dinâmica de risco de comandos shell em 3 níveis (read/write/full).

3. **🧠 Memória em Camadas com Busca Híbrida**
   - Implementação sofisticada: L1 (cache de sessão), L2 (FTS5 + vetorial), L3 (detalhe completo sob demanda).
   - FTS5 para buscas exatas e sqlite-vec para similaridade semântica.

4. **🛡️ Redação Automática de Segredos**
   - Regex-based redaction de API keys antes da persistência.

5. **🔁 Suporte Multi-Provider LLM**
   - OpenAI, Anthropic, Google, OpenRouter via LangChain com configuração via env vars.

6. **📂 Carregamento Dinâmico de Sub-Agentes via Markdown**
   - Definições `.md` com YAML frontmatter — extensível sem recompilar.

7. **🧩 Hooks Extensibility Pipeline**
   - Pre-tool hooks podem *allow, deny, ou modificar* calls.
   - Post-tool hooks para audit/observabilidade.
   - Design inspirado em boas práticas de harness da indústria.

8. **📊 Ferramentas de Desenvolvimento Maduras**
   - `uv`, `pre-commit` (check-secrets, detect-private-key), `pytest` com `asyncio_mode=auto`, `.python-version`.

9. **💾 Persistência Robusta**
   - SQLite em WAL Mode com timeout de 30s para concorrência CLI+API.
   - `check_same_thread=False` para uso em contextos async.

10. **🖥️ CLI Rico com Rich**
    - Tabelas, cores, prompts, status spinner, aprovação interativa.
    - Retomada de sessão com histórico persistente.

11. **📝 Configuração via `.env` com Template**
    - `.env.template` bem estruturado, `.gitignore` protege `.env`.

12. **🔄 Compactação de Contexto Automática**
    - Geração de "state memo" quando orçamento é excedido — evita overflow de contexto.

13. **🧪 Estrutura de Testes com Casos Reais**
    - 8 arquivos de teste cobrindo FTS5, guardrails, HITL, incognito, layered search, recursive prompt, safety e sub-agents.

---

## ⚠️ Pontos Fracos e Riscos

1. **`utils.py` é um God Object (Anti-pattern)**
   - Responsabilidades misturadas: PathFilter, logging setup, `get_model()`, `redact_sensitive_info()`, `recursive_load_context()`, `estimate_tokens()`, `cap_tool_output()`.
   - **Impacto:** Alta complexidade ciclômica, dificuldade de testar, acoplamento elevado.

2. **🚨 `system.log` na Raiz do Projeto**
   - O `logging.FileHandler("system.log")` em `utils.py` grava logs em arquivo hardcoded na raiz.
   - `system.log` **não** está listado no `.gitignore`.
   - **Impacto:** Logs podem conter conversas sensíveis, keys mascaradas, e história completa de sessões.

3. **🚨 `.pytest_cache/` e `.python-version` Não no `.gitignore`**
   - Cache do pytest versionado acidentalmente.
   - `.python-version` pode variar entre ambientes.

4. **Hardcoded Defaults Críticos em `api.py`**
   ```python
   "permissions": "execute",  # API sempre roda com permissão máxima?
   "context_budget": 10,      # Desalinhado com ARCH.md (20)
   ```
   - API endpoint permite qualquer operação destrutiva sem escopo.

5. **Tratamento de Erros Insuficiente em `cli.py`**
   - O bloco `except SystemExit` silencioso (`pass`) pode mascarar erros críticos.
   - Nenhum `try/except` ao redor do harness invocation no CLI handler.

6. **`get_or_create_session` é Chamado Dentro de Loop de Logging (Race Condition)**
   - Em `SessionLogger.log_event()` e `log_messages()`, cada chamada cria uma nova sessão de DB.
   - Sem connection pooling explícito, múltiplas escritas simultâneas podem causar `database is locked` apesar do WAL.

7. **Regex de Redação de Segredos é Frágil**
   - `redact_sensitive_info()` usa regex estáticas para OpenAI (`sk-...`), Anthropic (`sk-ant-...`).
   - Novos formatos de keys serão vazados silenciosamente.

8. **System Prompt Cache Não Tem TTL/Mecanismo de invalidação por tempo**
   - `_SYS_PROMPT_CACHE` cresce durante a execução sem limite ou expiração.

9. **Duplicação de Lógica entre `cli.py/api.py`**
   - Setup do harness, criação de UI, validação de input — lógica duplicada.

10. **Falta de Validação de Input nos Tool Handlers**
    - `run_shell` executa comandos sem whitelist adicional (apenas classificação de risco).
    - Nenhum rate-limiting ou sandboxing.

11. **Import Circular Potencial**
    - `harness.py` importa de `tools.py`, que importa de `utils.py`, que importa de `logging`/`os` — estrutura ainda ok, mas frágil para crescimento.

12. **Scripts Auxiliares em `scripts/` Não Versionáveis**
    - `run_analysis_wrapper.py`, `run_analysis.sh` — finalidade ambígua, sem documentação.

---

## 🔒 Análise de Segurança

### ✅ O que está protegido

- **`.env`**: Presente no `.gitignore` — expõe apenas `.env.template`.
- **Banco de dados**: `harness.db*` no `.gitignore`.
- **API keys**: Redação via regex antes de persistir.
- **pre-commit**: Hook customizado `check_secrets.py` + `detect-private-key` do pre-commit-hooks.
- **Human-in-the-Loop**: Aprovação interativa para operações destrutivas.

### ⚠️ Riscos identificados

| Risco | Severidade | Local | Descrição |
|-------|-----------|-------|-----------|
| `system.log` não ignorado | 🔴 Alta | `utils.py:55` | Logs persistentes contendo conversas podem ser commitados |
| Permissão hardcoded "execute" na API | 🔴 Alta | `api.py:72` | Usuários da API têm permissão máxima independente de configuração |
| Comandos shell sem sandbox | 🟡 Média | `tools.py` | `run_shell` usa `subprocess` diretamente — risco de injection |
| `pending_approvals` em memória | 🟡 Média | `api.py:20` | Dicionário in-memory pode ser perdido em restart; sem timeout |
| Sem autenticação na API | 🟡 Média | `api.py` | Endpoint `/chat` sem auth — qualquer um com acesso à porta pode usar |
| Regex de secreto limitada | 🟡 Média | `utils.py` | Não cobre todos os formatos possíveis de API keys |
| `.pytest_cache/` rastreado | 🟢 Baixa | Raiz | Cache local versionado acidentalmente |

---

## 🧪 Cobertura e Qualidade de Testes

### Estrutura Atual

```
tests/
├── test_fts5_dots.py          → Validação de FTS5 com nomes com pontos
├── test_guardrails.py         → Testes de guardrails (HITL)
├── test_hitl.py               → Human-in-the-Loop pipeline
├── test_incognito.py          → Modo incógnito (sem persistência)
├── test_layered_search.py     → Busca híbrida L1/L2/L3
├── test_recursive_prompt.py   → Carregamento recursivo de contexto
├── test_safety.py             → Testes de segurança de input
└── test_sub_agents.py         → Integração sub-agentes
```

### Avaliação

| Critério | Status |
|----------|--------|
| Organização | 🟢 Boa — cada arquivo testa um aspecto diferente |
| Fixtures | 🟡 Limitadas — reutilização de fixtures poderia ser melhor |
| Cobertura unitária | 🔴 Insuficiente — tests focam em integração |
| Cobertura de erros | 🔴 Falta — poucos cenários de erro/falha |
| Testes de lógica de negócio | 🔴 Ausente — `should_continue`, `validate_and_sanitize` não testados isoladamente |
| Testes negativos | 🔴 Ausente — nenhum teste de falha esperada |

### O que Falta

- [ ] Testes unitários para `utils.py` (redact_sensitive_info, path_filter, estimate_tokens, cap_tool_output)
- [ ] Testes unitários para `tools.py` (classify_shell_command, ToolRegistry, permission hierarchy)
- [ ] Testes unitários para `logic.py` (should_continue, validate_and_sanitize, cache behavior)
- [ ] Testes para `hooks.py` (HookManager, hook execution order)
- [ ] Testes para `agent_loader.py` (YAML parsing, error handling)
- [ ] Testes para `api.py` (endpoint, validation, edge cases)
- [ ] Testes para `persistence_db.py` (schema, migrations)
- [ ] Testes de concorrência (escritas simultâneas no SQLite)
- [ ] Testes de timeout (`context_budget`, `max_iterations`)
- [ ] Mocks para LLM externo nos testes de sub-agentes

> **Cobertura estimada:** ~25-30% do código de produção.

---

## 📒 Observações sobre Documentação e Configuração

### ✅ Documentação (Excelente)

- **`README.md`** — Completo com badges, features, arquitetura (Mermaid), instalação, uso e contribuição.
- **`ARCH.md`** — 682 linhas de documentação técnica detalhada: diagramas, decisões, estrutura de tabelas, modo de operação.
- **`TOOLS.md`** — Gerado automaticamente a partir de `.agents/tools/`.
- **`tasks.md`** — Roadmap rastreável com status por feature — mostra maturidade.
- **`AGENTS.md`** — Define protocolos de orquestração e permissões de execução.

### ⚙️ Configuração

| Arquivo | Avaliação |
|---------|-----------|
| `pyproject.toml` | 🟢 Limpo, dependências bem separadas (prod/dev) |
| `Makefile` | 🟢 15+ targets, bem documentado, cobre install/run/test/clean/background |
| `pytest.ini` | 🟢 Configuração mínima eficaz |
| `.pre-commit-config.yaml` | 🟢 Hooks relevantes, incluindo check-secrets customizado |
| `.env.template` | 🟢 Completo com todas as variáveis documentadas |
| `LICENSE` | 🟢 MIT — permissivo e corporativo-friendly |

### 🟡 Sugestões

- `ARCH.md` e `README.md` possuem diagramas duplicados (Mermaid idêntico) — considere DRY.
- `make clean` não limpa `system.log` — deveria.
- `make start` usa `api.log` mas o Makefile referencia `api.log` em `logs:` target.

---

## 🛠️ Plano de Melhorias Priorizado

### 🔴 Curto Prazo (Urgent — 1-2 semanas)

1. **Adicionar `system.log` ao `.gitignore`** e mover logs para `logs/` ou `/tmp`.
2. **Corrigir `permissions` hardcoded em `api.py`** — ler do `.env` ou do request.
3. **Adicionar `.pytest_cache/` ao `.gitignore`**.
4. **Corrigir `except SystemExit: pass`** em cli.py — pelo menos logar o erro.
5. **Adicionar timeout em `pending_approvals`** na API — se ninguém aprovar em 5 min, rejeitar automaticamente.

### 🟡 Médio Prazo (Qualidade — 1 mês)

6. **Refatorar `utils.py` em módulos:**
   - `path_filter.py` → `PathFilter`
   - `logging_config.py` → `setup_logging()`
   - `model_factory.py` → `get_model()`
   - `redaction.py` → `redact_sensitive_info()`
   - `token_utils.py` → `estimate_tokens()`, `cap_tool_output()`
7. **Aumentar cobertura de testes para 70%+** (foco em unit tests).
8. **Abstrair `api.py` e `cli.py`** — extrair lógica de setup para `runner.py` compartilhado.
9. **Adicionar TTL ao `_SYS_PROMPT_CACHE`** — limite de 100 entradas ou 30 min.
10. **Expandir `redact_sensitive_info`** com formatos de keys do Google, HuggingFace, etc.

### 🟢 Longo Prazo (Arquitetura — 3+ meses)

11. **Adicionar autenticação na API** (API Key ou OAuth2).
12. **Implementar sandboxing** para `run_shell` (Docker, bubblewrap, ou jail).
13. **Substituir `pending_approvals` in-memory por Redis** para suporte a múltiplas instâncias.
14. **Adicionar métricas de observabilidade** (Prometheus, OpenTelemetry).
15. **Criar plugin system** para ferramentas customizadas (hooks + registry dinâmico).
16. **Connection pooling** explícito para SQLite no contexto async.
17. **CLI interativo com histórico de comandos** (readline), autocompletar, atalhos.
18. **Multi-tenancy** — isolar sessões por usuário/organização.

---

## 📊 Nota Geral

| Dimensão | Peso | Nota | Ponderada |
|----------|------|------|-----------|
| Arquitetura | 25% | 7.0 | 1.75 |
| Qualidade de Código | 25% | 6.0 | 1.50 |
| Testes | 20% | 5.0 | 1.00 |
| Segurança | 20% | 6.0 | 1.20 |
| Documentação | 10% | 9.0 | 0.90 |
| **TOTAL** | **100%** | | **6.35/10** |

### Nota Final: **6.3 / 10** 🟡

### Justificativa

O **Agent Harness** é um projeto **tecnicamente ambicioso e bem concebido**, com uma arquitetura sólida de orquestração delegativa, memória em camadas e controles de segurança relevantes. A documentação é **excepcional** (raro encontrar ARCH.md tão detalhado em projetos open-source), e as ferramentas de desenvolvimento (uv, pre-commit, Makefile) demonstram maturidade no workflow.

Entretanto, **lacunas significativas** impedem uma nota mais alta:

- **Segurança:** Logs não-ignorados, API sem autenticação, permissões hardcoded, e falta de sandbox para shell execution são riscos reais.
- **Testes:** Cobertura estimada de ~25-30%, com foco excessivo em integração e quase nada em unit tests. `utils.py`, `logic.py` e `hooks.js` estão praticamente sem cobertura.
- **Qualidade de Código:** `utils.py` é um God Object que precisa urgente refatoração. Duplicação entre `cli.py`/`api.py`. Cache sem invalidação proativa.

### Comparativo com a Indústria

| Critério | Agent Harness | Projetos Maduros (LangGraph templates, AutoGen) |
|----------|:---:|:---:|
| Separação de responsabilidades | 🟡 | 🟢 |
| Cobertura de testes | 🔴 | 🟢 |
| Observabilidade | 🟡 | 🟢 |
| Segurança | 🟡 | 🟢 |
| Documentação | 🟢 | 🟡 |
| Extensibilidade (hooks) | 🟢 | 🟡 |
| Multi-provider LLM | 🟢 | 🟡 |

> **Veredito:** Projeto com **base arquitetural forte** e potencial para ser referência em orquestração multi-agente no ecossistema Python. Precisa investir em **testes, refatoração do utils.py, e hardening de segurança** para atingir nível produção.

---

*Relatório gerado por K-Claw — Análise técnica imparcial e acionável.*
