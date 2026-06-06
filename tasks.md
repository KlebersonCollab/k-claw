# 📋 Agent Harness Evolution Roadmap

Este documento rastreia a evolução do Agent Harness com base nos princípios de "Managed Agents" e "Layered Memory".

## Status Legend
- [ ] **Pendente**: Não iniciado.
- [/] **Em Progresso**: Implementação ou teste em andamento.
- [x] **Concluído**: Implementado, testado e validado.

---

## 🎯 Tasks

### 1. Migração para SQLite (Persistência Estruturada)
- [x] **Definir Schema do Banco**: Criar `persistence_db.py` com tabelas para `sessions`, `messages` e `events`. O esquema deve permitir buscar mensagens por `session_id`.
- [x] **Refatorar SessionLogger**: Alterar o `SessionLogger` em `persistence.py` para salvar no SQLite em vez de JSONL.
- [x] **Implementar Replay via SQL**: Atualizar o método `replay` para extrair o histórico do banco de dados de forma eficiente.
- [x] **Concorrência (WAL Mode)**: Ativado modo WAL e timeout de 30s para evitar locks entre CLI e API.
- [x] **Validação**: Verificar se após um reinício (`make restart`), o histórico de uma sessão específica é recuperado corretamente do SQLite.

### 2. Memória de Longo Prazo (Layered Memory / Hybrid Search)
- [x] **Implementar FTS5 no SQLite**: Criar uma Virtual Table para busca de texto completo (keyword search) em mensagens e resumos.
- [x] **Implementar Vetorização Local**: Adicionada integração com `sentence-transformers` (all-MiniLM-L6-v2) para busca semântica.
- [x] **Sistema de Camadas (FTS5 -> Vector -> Detail)**:
    - Implementada a lógica de busca híbrida: FTS5 para termos exatos, Vetores para conceitos.
- [x] **Ferramenta `search_memory`**: Atualizada para utilizar busca híbrida.
- [x] **Validação**: Testada busca por termo exato (FTS5) e busca por conceito (Vetor). ✅ Sucesso.



### 3. Filtros de Privacidade e Segurança
- [x] **Implementar Redacting Hook**: Criado `redact_sensitive_info` em `logic.py` que mascara chaves OpenAI, Anthropic e Google antes da persistência.
- [x] **Controle de Exclusão de Memória**: Adicionada ferramenta `forget_session` no `tools.py` e método `delete_memory_by_session` no `persistence.py`.
- [x] **Validação**: Verificada a limpeza de chaves fictícias e a exclusão física de dados no SQLite. ✅ Sucesso.

### 4. Interface CLI Avançada (Gestão de Memória)
- [x] **Menu de Seleção de Sessão**: Atualizado `cli.py` para listar sessões existentes (usando `rich.table`) e permitir retomar uma conversa carregando o histórico do SQLite.
- [x] **Exibição de Status de Memória**: O CLI agora diferencia visualmente chamadas de ferramentas de memória (`search_memory`) e exibe o fluxo de mensagens de forma clara.
- [x] **Validação**: Testado o fluxo de "Listar -> Selecionar -> Retomar" com sucesso. ✅ Sucesso.

### 5. Otimização de Tokens (Compaction 2.0)
- [x] **Resumo Semântico**: Atualizado `compact_context` em `logic.py` para gerar um "State Memo" técnico e estruturado (Decisões, Status, Tarefas Pendentes).
- [x] **Persistência de Longo Prazo**: Cada compactação agora salva o State Memo na memória vetorial (SQLite `memories`) para recuperação futura.
- [x] **Validação**: Verificada a geração do State Memo e sua recuperação via busca semântica. ✅ Sucesso.

### 6. Otimização com sqlite-vec (Performance Nativa)
- [x] **Integração sqlite-vec**: Adicionada biblioteca `sqlite-vec` para processamento de vetores no nível do banco de dados (C).
- [x] **Schema vec0**: Criada Virtual Table `memories_vec` para busca de similaridade nativa e eficiente.
- [x] **Busca de Cosseno Nativa**: Refatorado `semantic_search` para usar `vec_distance_cosine` do SQLite, eliminando o processamento manual em Python.
- [x] **Validação**: Verificado que a busca híbrida continua funcionando com performance superior e menor uso de memória. ✅ Sucesso.

---

## 🚀 Fase 2: Arquitetura Avançada (Learnings de Estudos)

### 7. Human-in-the-Loop & Segurança Dinâmica
- [x] **Aprovações Interativas**: Adicionado campo `requires_approval: bool` no `ToolDescriptor` e configurado `write_file`, `run_shell` e `forget_session` para exigir aprovação.
- [x] **Integração no Harness**: Configurado LangGraph com `MemorySaver` e `interrupt_before=["tools"]` para pausar a execução.
- [x] **CLI Atualizado**: O CLI agora intercepta interrupções, exibe os detalhes da ferramenta e solicita confirmação do usuário antes de prosseguir.
- [x] **Validação**: Verificado que o grafo pausa antes de executar ferramentas perigosas. ✅ Sucesso.

### 8. Orquestração de Sub-Agentes
- [x] **Infraestrutura de Markdown/YAML**: Criado `agent_loader.py` para carregar agentes de `.agents/agents/*.md` com Frontmatter YAML.
- [x] **Ferramenta `delegate_to_agent`**: Implementada ferramenta assíncrona que faz o spawn de sub-agentes com contexto isolado e injeção automática de skills.
- [x] **Catálogo AGENTS.md**: O Agente Pai agora lê o catálogo de especialistas dinamicamente no System Prompt.
- [x] **Validação**: Infraestrutura validada com agentes `coder` e `researcher`. ✅ Sucesso.

### 9. Prompt Assembly Dinâmico (Recursive Search)
- [x] **Recursive Loader**: Criada função `recursive_load_context` que busca arquivos `AGENTS.md`, `CONTEXT.md` e `.harness.md` do diretório atual até a raiz.
- [x] **Injeção Inteligente**: Implementada a injeção ordenada (do global para o específico) no System Prompt do orquestrador.
- [x] **Validação**: Testado com sucesso usando diretórios aninhados e arquivos de contexto local. ✅ Sucesso.

### 10. Busca em Camadas (Optimized Retrieval)
- [x] **Layered Search Tool**: Refatorada a ferramenta `search_memory` para retornar apenas IDs e resumos, economizando tokens.
- [x] **Ferramenta `fetch_memory_detail`**: Implementada ferramenta para o agente buscar o conteúdo completo de um ID específico (Layer 2).
- [x] **Vínculo de IDs**: Atualizado o schema do banco para vincular vetores ao `rowid` original da memória.
- [x] **Validação**: Testado o fluxo de "Pesquisa (Resumo) -> Detalhe (Conteúdo)" com sucesso. ✅ Sucesso.

### 11. Controle de Gravação (Modo Incógnito)
- [x] **Flag de Incógnito**: Adicionado campo `incognito: bool` no `HarnessState`.
- [x] **Logging Condicional**: Atualizada a lógica em `logic.py` para suspender toda a persistência (mensagens e eventos) quando o modo incognito está ativo.
- [x] **Comando CLI**: Implementado comando `/incognito` no CLI para alternar o modo de privacidade em tempo real.
- [x] **Validação**: Verificado que nada é gravado no SQLite quando o modo está ativado. ✅ Sucesso.

## 🛡️ Fase 3: Performance & Proteção de Contexto

### 12. Prevenção de Loops e Brute-Force
- [x] **Path Filtering (.gitignore)**: Implementada classe `PathFilter` em `utils.py` que bloqueia acesso a `.venv`, `.git` e outros arquivos ignorados.
- [x] **Ferramenta `list_directory`**: Criada ferramenta inteligente que respeita as regras de exclusão, fornecendo "olhos" aos agentes sem poluir o contexto.
- [x] **Proteção de Acesso**: Atualizadas as ferramentas `read_file` e `write_file` para impedir acesso a caminhos proibidos.
- [x] **Protocolo de Busca em Camadas**: Atualizados os prompts dos especialistas para forçar o uso de `search_memory` antes de qualquer leitura em disco.
- [x] **Performance (Lazy Loading)**: Implementado carregamento preguiçoso de embeddings, reduzindo a latência de inicialização em 300s.
- [x] **Segurança de Commit (Pre-commit)**: Configurado framework `pre-commit` com scanner de segredos customizado para impedir vazamento de chaves de API.
- [x] **Validação**: Testado bloqueio de `.venv` e proteção de chaves via pre-commit. ✅ Sucesso.

## 🛠️ Fase 5: Harness Agnóstico & API Reativa

### 15. Desacoplamento de Interface (UI-Agnostic)
- [x] **Interface Callback/EventBus**: Criada a classe base `UIInterface` em `ui_interface.py` e integrado o sistema de eventos no `logic.py` (THINKING, TOOL, APPROVAL).
- [x] **Refatorar CLI**: O `cli.py` foi transformado em uma implementação de `UIInterface`, reagindo a eventos para gerenciar o console Rich.
- [x] **Validação**: CLI validado com feedback visual via eventos. ✅ Sucesso.

### 16. API REST v2 (HITL & Streaming)
- [x] **Streaming de Eventos**: Implementado endpoint `/chat` com `StreamingResponse` (SSE) que reporta o progresso do agente em tempo real.
- [x] **Fluxo de Aprovação HTTP**: Criado sistema de `Futures` e endpoint `POST /approve/{id}` para pausar e retomar a execução via web.
- [x] **Gestão de Sessão no Banco**: API integrada ao `SessionLogger` para persistência e recuperação automática de contexto.
- [x] **Validação**: Testado via `curl` com streaming de eventos. ✅ Sucesso.


3. Verifique se as dependências de vetores foram instaladas via `uv`.
