# 🛠️ Agent Tools Manual

> **Versão:** 0.1.0 · **Última Atualização:** 2026-01-17
> Este arquivo documenta todas as ferramentas disponíveis no Agent Harness.
> Gerado a partir de `tools/` e `tools/registry.py`.

---

## 📋 Índice

1. [Ferramentas de Arquivo](#ferramentas-de-arquivo)
2. [Ferramentas de Busca](#ferramentas-de-busca)
3. [Ferramentas de Shell](#ferramentas-de-shell)
4. [Ferramentas de Memória](#ferramentas-de-memória)
5. [Ferramentas de Delegação](#ferramentas-de-delegação)

---

## Ferramentas de Arquivo

### `list_directory`

**Permissão:** `read` · **Requer Aprovação:** Não

Lista arquivos e diretórios em um caminho, respeitando regras de ignore do projeto (`.gitignore`, `.venv`, `.git`, etc.).

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `path` | `string` | Não | `"."` | Diretório base para listagem |

**Quando usar:**
- Para ganhar visão estrutural do projeto antes de ler arquivos específicos.
- Para navegar diretórios desconhecidos.

**Regras de Ouro:**
- Use sempre antes de ler arquivos se não tiver certeza dos caminhos.
- Ignora automaticamente `.venv`, `.git`, `__pycache__`, `node_modules`.

---

### `read_file`

**Permissão:** `read` · **Requer Aprovação:** Não

Lê conteúdo de arquivo com paginação obrigatória para arquivos existentes.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `path` | `string` | Sim | — | Caminho do arquivo |
| `start_line` | `int` | Não | `1` | Linha inicial (1-based) |
| `end_line` | `int` | Não | `null` | Linha final |

**Quando usar:**
- Para ler conteúdo de arquivos específicos.
- Para analisar código ou documentação.

**Regras de Ouro:**
- **EXISTENTE:** Se o arquivo já existe, DEVE usar `start_line` e `end_line`.
- **NOVO/PEQUENO:** Leitura completa permitida apenas se < 50 linhas.
- **FALLBACK:** Se falhar, liste o diretório para confirmar o caminho.

---

### `replace_string`

**Permissão:** `write` · **Requer Aprovação:** ✅ Sim

Substitui cirurgicamente um bloco de texto exato em um arquivo existente.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `path` | `string` | Sim | — | Caminho do arquivo |
| `old_string` | `string` | Sim | — | Texto exato a substituir |
| `new_string` | `string` | Sim | — | Novo texto |

**Quando usar:**
- Para modificar código em arquivos existentes.
- Para correções pontuais sem reescrever o arquivo inteiro.

**Regras de Ouro:**
- **EXATIDÃO:** `old_string` deve ser cópia EXATA do texto no arquivo.
- **CONTEXTO ÚNICO:** Se o trecho se repetir, adicione mais linhas de contexto.
- **SUBSTITUIÇÃO, NÃO CRIAÇÃO:** Se o arquivo não existir, use `write_file`.

---

### `write_file`

**Permissão:** `write` · **Requer Aprovação:** ✅ Sim

Escreve conteúdo em um arquivo (cria novo ou sobrescreve).

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `path` | `string` | Sim | — | Caminho do arquivo |
| `content` | `string` | Sim | — | Conteúdo a escrever |

**Quando usar:**
- Para criar arquivos novos.
- Para escrever conteúdo que não existe ainda.

**Regras de Ouro:**
- **PROIBIDO** usar em arquivos existentes (use `replace_string`).
- Para arquivos novos, forneça o conteúdo completo.

---

## Ferramentas de Busca

### `grep_search`

**Permissão:** `read` · **Requer Aprovação:** Não

Busca cirúrgica por padrões de texto ou regex dentro do conteúdo dos arquivos.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `pattern` | `string` | Sim | — | Padrão regex ou texto |
| `path` | `string` | Não | `"."` | Diretório ou arquivo base |
| `include_pattern` | `string` | Não | — | Filtro de arquivos (ex: `"*.py"`) |
| `context` | `int` | Não | `0` | Linhas de contexto ao redor do match |

**Quando usar:**
- Para encontrar onde uma função ou variável está definida.
- Para localizar mensagens de erro específicas.
- Para analisar trechos sem ler o arquivo inteiro (economiza tokens).

---

### `glob_search`

**Permissão:** `read` · **Requer Aprovação:** Não

Localiza arquivos no projeto usando padrões de busca (wildcards).

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `pattern` | `string` | Sim | — | Padrão glob (ex: `"**/*.md"`) |
| `path` | `string` | Não | `"."` | Diretório base |

**Quando usar:**
- Para encontrar arquivos por extensão (ex: todos os `.py`).
- Para listar arquivos em subdiretórios profundos.
- Para verificar existência de arquivos seguindo um padrão.

---

## Ferramentas de Shell

### `run_shell`

**Permissão:** `execute` · **Requer Aprovação:** ✅ Sim

Executa um comando bash no sistema.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `command` | `string` | Sim | — | Comando bash a executar |

**Quando usar:**
- Para executar comandos de sistema, build, teste, etc.
- Para operações que requerem acesso ao shell.

**Regras de Ouro:**
- Comandos são classificados por risco (`read`/`write`/`full`) via `tools/classification.py`.
- Comandos de risco `full` (ex: `rm`, `sudo`, `chmod`) requerem aprovação explícita.
- Pre-tool hooks podem bloquear comandos (ex: `sudo`).

---

## Ferramentas de Memória

### `search_memory`

**Permissão:** `read` · **Requer Aprovação:** Não

Busca em camadas no histórico de conversas (L1: IDs + summaries, L2: FTS5 + vetorial).

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `query` | `string` | Sim | — | Termo de busca |
| `layer` | `string` | Não | `"L1"` | Camada: `L1`, `L2`, ou `L3` |
| `target_id` | `int` | Não | — | ID específico para L3 |

**Quando usar:**
- Para recuperar contexto de sessões passadas.
- Para buscar informações em memória de longo prazo.

**Regras de Ouro:**
- **L1 (padrão):** Retorna IDs e resumos técnicos (economiza tokens).
- **L2:** Busca híbrida FTS5 + vetorial.
- **L3:** Conteúdo completo via `fetch_memory_detail(id)`.

---

### `fetch_memory_detail`

**Permissão:** `read` · **Requer Aprovação:** Não

Recupera conteúdo completo de uma memória específica por ID.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `memory_id` | `int` | Sim | — | ID da memória (de `search_memory`) |

**Quando usar:**
- Para obter o conteúdo completo após identificar a memória via `search_memory`.

---

### `forget_session`

**Permissão:** `execute` · **Requer Aprovação:** ✅ Sim

Deleta todos os dados associados a uma sessão (mensagens, eventos, memórias).

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `session_id_to_forget` | `string` | Sim | — | ID da sessão a deletar |

**Quando usar:**
- Para limpar dados de sessões antigas ou sensíveis.
- Para liberar espaço no banco de dados.

**Regras de Ouro:**
- **IRREVERSÍVEL:** Todos os dados da sessão serão permanentemente deletados.
- Requer aprovação explícita do usuário.

---

## Ferramentas de Delegação

### `delegate_to_agent`

**Permissão:** `read` · **Requer Aprovação:** Não

Delega uma tarefa para um sub-agente especialista.

**Argumentos:**
| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `agent_id` | `string` | Sim | — | ID do agente: `coder`, `researcher`, `verifier` |
| `mission` | `string` | Sim | — | Briefing técnico da tarefa |
| `parent_yolo` | `bool` | Não | `false` | Se true, pula aprovações no sub-agente |

**Quando usar:**
- Para terceirizar tarefas complexas para especialistas.
- Para executar código (`coder`), pesquisar (`researcher`) ou validar (`verifier`).

**Regras de Ouro:**
- **MISSÃO:** Forneça briefing claro (OBJETIVO, RECURSOS, RESTRIÇÕES).
- **ESPECIALISTAS:**
  - `coder` → escrita de código, refatoração, correção de bugs.
  - `researcher` → busca semântica, análise de documentos.
  - `verifier` → validação independente de artefatos e testes.

---

## 📊 Resumo de Permissões

| Ferramenta | Permissão | Aprovação |
|---|---|---|
| `list_directory` | `read` | Não |
| `read_file` | `read` | Não |
| `grep_search` | `read` | Não |
| `glob_search` | `read` | Não |
| `search_memory` | `read` | Não |
| `fetch_memory_detail` | `read` | Não |
| `delegate_to_agent` | `read` | Não |
| `replace_string` | `write` | ✅ Sim |
| `write_file` | `write` | ✅ Sim |
| `run_shell` | `execute` | ✅ Sim |
| `forget_session` | `execute` | ✅ Sim |

---

## 🔧 Como Adicionar Novas Ferramentas

1. Crie a função da ferramenta em `tools/` (ex: `tools/my_tool.py`).
2. Registre no `tools/__init__.py`:
   ```python
   registry.register(
       "my_tool",
       "Descrição da ferramenta.",
       "read",  # ou "write" / "execute"
       my_tool_function,
       requires_approval=False,  # True se for destrutiva
   )
   ```
3. A ferramenta estará disponível automaticamente para o agente.

---

*Documento mantido pela equipe do Agent Harness. Para atualizações, edite `tools/` e regenere com `make generate-tools`.*
