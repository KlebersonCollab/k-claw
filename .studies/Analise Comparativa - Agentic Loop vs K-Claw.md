# 🔍 Análise Comparativa: Agentic Loop vs K-Claw

> **Base:** Vídeo "What is a Loop" (YouTube) + Arquitetura K-Claw (ARCH.md + código)
> **Data:** 2025-07-14

---

## Premissas do Vídeo (Agentic Loop)

O vídeo define um **Agentic Loop** como um sistema com os seguintes pilares:

| # | Premissa | Descrição no vídeo |
|---|----------|--------------------|
| 1 | **While Loop (Iteração)** | Loop externo que lê prompt → decide tool → executa → alimenta resultado → repete até critério de parada |
| 2 | **Context Management** | Decidir o que manter verbatim, o que sumarizar e o que descartar quando o contexto cresce |
| 3 | **Skills e Tools** | Tools = primitivas universais (read, edit, bash). Skills = conhecimento organizacional específico |
| 4 | **Sub-Agent Management** | Quando a tarefa é grande/paralelizável, criar sub-agentes isolados com sessão própria e tools restritos |
| 5 | **Built-in Skills** | Skills que o harness traz out-of-the-box (file ops, git, PR, testes) |
| 6 | **Session Persistence / Memory** | Estado em disco (append-only JSON/Markdown) para recuperar de falhas e continuar sessões |
| 7 | **System Prompt Assembly** | Prompt não é string estática — é pipeline que busca instruções em diretórios ancestrais |
| 8 | **Life Cycle Hooks** | Injetar lógica customizada antes/depois de tool runs sem tocar no harness |
| 9 | **Permissions and Safety** | Hierarquia de permissões (read → write → exec), classificação dinâmica de comandos, aprovação interativa |
| 10 | **Verification Step** | Verificador independente — quem escreve código não deve se auto-avaliar |
| 11 | **Orchestration Tax** | Seu limite é sua banda de revisão, não a ferramenta |
| 12 | **Custo Controlado** | Limite rígido de gastos/tokens — loops podem ficar caros rapidamente |
| 13 | **Prompt Inicial Preciso** | A semente importa mais — specs vagas = suposições erradas repetidas |

---

## Mapeamento K-Claw vs Premissas

### ✅ ATENDE (Total ou Parcialmente)

| Premissa | Status | Evidência no K-Claw |
|----------|--------|---------------------|
| **1. While Loop** | ✅ Total | `harness.py` implementa `StateGraph` com ciclo `agent → tools → agent` via LangGraph. `dialog_control.py` (`should_continue`) decide entre `tools`, `compact` ou `__end__`. `max_iterations` com default de 50. |
| **2. Context Management** | ✅ Total | `compaction.py` — quando tokens > 35K ou mensagens > `context_budget`, dispara compactação. Mantém últimas 10 mensagens, sumariza o resto em "State Memo" (DECISIONS, STATUS, PENDING, CONTEXT). |
| **3. Skills e Tools** | ✅ Total | `tools.py` (ToolRegistry com 8 ferramentas built-in). `agent_loader.py` carrega skills de `.agents/skills/*.md`. AGENTS.md define `coder` e `researcher` como especialistas. |
| **4. Sub-Agent Management** | ✅ Total | `delegate_to_agent` cria sub-agentes com `session_id` prefixado `sub-`, permissões restritas, e mission específica. Sub-agentes rodam em contexto isolado. |
| **5. Built-in Skills** | ✅ Total | Ferramentas built-in: `read_file`, `write_file`, `grep_search`, `glob_search`, `list_directory`, `run_shell`, `search_memory`, `fetch_memory_detail`, `delegate_to_agent`. |
| **6. Session Persistence / Memory** | ✅ Total | `persistence.py` (SessionLogger) + `persistence_db.py` (SQLite + FTS5 + vec0). Memória em 3 camadas (L1 índice → L2 busca híbrida → L3 detalhe). Append-only. Modo incógnito opcional. |
| **7. System Prompt Assembly** | ✅ Total | `prompt_builder.py` — monta prompt dinamicamente. Busca `AGENTS.md` via `recursive_load_context`. Cache de prompt por `(session_id, permissions, context_summary)`. Diferencia orchestrator de sub-agent. |
| **8. Life Cycle Hooks** | ✅ Total | `hooks.py` — `HookManager` com `pre_tool_hooks` (allow/deny/modify) e `post_tool_hooks` (audit/observability). Protocolo com `HookResult`. |
| **9. Permissions and Safety** | ✅ Total | Hierarquia `read → write → exec`. HITL (Human-in-the-Loop) para `write_file`, `run_shell`, `forget_session`. Redação de secrets via regex. |
| **10. Verification Step** | ⚠️ Parcial | O Agente Pai delega para especialistas e revisa relatórios. **Porém não há um verificador formalmente independente** — o orquestrador é quem avalia o output do sub-agente. |

### ⚠️ PONTOS DE MELHORIA

| # | Premissa | Gap | Recomendação |
|---|----------|-----|--------------|
| 1 | **Verification Step** | Não há um "verifier" separado. O orquestrador avalia o trabalho do sub-agente, mas é o mesmo fluxo. | Implementar um padrão de **verificação independente**: após o `coder` gerar código, um passo automático (ou sub-agente `verifier`) roda testes e valida antes de reportar ao orquestrador. O AGENTS.md já exige testes (unitário, integração, e2e, edge case, cobertura ≥90%), mas não há enforcement automático no loop. |
| 2 | **Orchestration Tax** | O K-Claw reconhece o gargalo humano (HITL), mas não tem métricas de "review bandwidth". | Adicionar **telemetria de revisão**: quantos sub-agentes foram disparados, quantos outputs foram revisados pelo humano, tempo médio de revisão. Isso tornaria a "taxa de orquestração" visível. |
| 3 | **Custo Controlado** | Não há um **hard spending limit** explícito de tokens/gastos. O `max_iterations` limita iterações, mas não custos financeiros. | Implementar um **budget tracker** por sessão que acumule tokens estimados e pare o loop quando um limite financeiro for atingido. |
| 4 | **Prompt Inicial Preciso** | O sistema depende da qualidade do prompt inicial do usuário, mas não há validação/enriquecimento automático. | Implementar um **"spec checker"** que analise a clareza do objetivo inicial e sugira melhorias antes de iniciar o loop (ex: detectar ausência de critério de parada, specs vagas). |
| 5 | **Work Trees** | Não há isolamento de work trees (cópias isoladas do repo) para agentes paralelos. | Para cenários de múltiplos agentes paralelos, implementar **work trees isolados** (git worktrees ou cópias) para evitar colisões. |
| 6 | **Connectors** | Não há integração nativa com GitHub (abrir PRs), Jira (atualizar tickets), etc. | Implementar **connectors** como skills: `create_pull_request`, `update_ticket`, etc. |
| 7 | **Dynamic Workflows** | O K-Claw delega para um sub-agente por vez. Não há fan-out nativo para múltiplos sub-agentes em paralelo. | Implementar **parallel delegation** — o orquestrador poder disparar N sub-agentes simultaneamente e agregar resultados (padrão scatter-gather). |

---

## Resumo Visual

```
PREMISSA                    K-CLAW
──────────────────────────  ──────────
1. While Loop               ✅ Total
2. Context Management       ✅ Total
3. Skills e Tools           ✅ Total
4. Sub-Agent Management     ✅ Total
5. Built-in Skills          ✅ Total
6. Session Persistence      ✅ Total
7. System Prompt Assembly   ✅ Total
8. Life Cycle Hooks         ✅ Total
9. Permissions & Safety     ✅ Total
10. Verification Step       ⚠️  Parcial
11. Orchestration Tax       ⚠️  Parcial
12. Custo Controlado        ⚠️  Parcial
13. Prompt Inicial Preciso  ⚠️  Parcial
14. Work Trees              ❌ Ausente
15. Connectors              ❌ Ausente
16. Dynamic Workflows       ❌ Ausente
```

---

## Conclusão

O K-Claw atende **9 das 13 premissas principais** do Agentic Loop de forma total, demonstrando uma arquitetura madura e alinhada com o estado da arte. Os **4 gaps principais** são:

1. **Verificação independente** — o elo mais crítico para loops longos e autônomos
2. **Controle de custos** — essencial para produção
3. **Fan-out paralelo** — necessário para escalar
4. **Connectors** — importante para integração com o ecossistema dev

As melhorias sugeridas são **incrementais** e podem ser implementadas iterativamente sem reestruturação da arquitetura base.
