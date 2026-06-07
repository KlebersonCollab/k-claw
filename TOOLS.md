# 🛠️ Agent Tools Manual

Este arquivo é gerado automaticamente a partir de `.agents/tools/`.

### Tool: delegate_to_agent
Description: Delegates a task to a specialist sub-agent.
Usage: delegate_to_agent(agent_id='coder', mission='technical mission')

Detailed Instructions:
Use esta ferramenta para terceirizar tarefas complexas para especialistas.

**REGRAS DE OURO:**
- **MISSÃO:** Forneça um briefing técnico claro (OBJECTIVE, RESOURCES, CONSTRAINTS).
- **ESPECIALISTAS:** Use `coder` para código e `researcher` para análises.

---
### Tool: glob_search

Detailed Instructions:
# Tool: glob_search

Localiza arquivos no projeto usando padrões de busca (wildcards).

### Quando usar:
- Para encontrar arquivos por extensão (ex: todos os `.py`).
- Para listar arquivos em subdiretórios profundos sem usar múltiplos `list_directory`.
- Para verificar a existência de arquivos específicos seguindo um padrão de nome.

### Argumentos:
- `pattern` (string, obrigatório): O padrão glob (ex: "**/*.md", "tests/test_*.py").
- `path` (string, opcional): Diretório base para a busca. Default: ".".

### Retorno:
Lista de caminhos de arquivos que deram match com o padrão, respeitando as regras de ignore do projeto.

---
### Tool: grep_search

Detailed Instructions:
# Tool: grep_search

Busca cirúrgica por padrões de texto ou regex dentro do conteúdo dos arquivos do projeto.

### Quando usar:
- Para encontrar onde uma função ou variável está definida.
- Para localizar mensagens de erro específicas no código.
- Para analisar trechos de código sem ler o arquivo inteiro (economiza tokens).

### Argumentos:
- `pattern` (string, obrigatório): O padrão regex ou texto a buscar.
- `path` (string, opcional): Diretório ou arquivo onde iniciar a busca. Default: ".".
- `include_pattern` (string, opcional): Padrão glob para filtrar arquivos (ex: "*.py", "core/*.md").
- `context` (inteiro, opcional): Número de linhas de contexto antes e depois do match.

### Retorno:
Lista de matches formatada com o nome do arquivo, número da linha e o bloco de contexto.

---
### Tool: list_directory
Description: Lists files and folders, respecting project ignore rules.
Usage: list_directory(path='.')

Detailed Instructions:
Use esta ferramenta para ganhar visão estrutural do projeto.

**REGRAS DE OURO:**
- **VISÃO:** Use sempre antes de ler arquivos específicos se você não tiver certeza dos caminhos.
- **AUTOMÁTICO:** Ignora automaticamente `.venv`, `.git`, e padrões definidos no `.gitignore`.

---
### Tool: read_file
Description: Reads a file from disk with mandatory pagination for existing files.
Usage: read_file(path='path/to/file', start_line=1, end_line=100)

Detailed Instructions:
Use esta ferramenta para ler o conteúdo de arquivos.

**REGRAS DE OURO:**
- **EXISTENTE:** Se o arquivo já existe, você DEVE usar `start_line` e `end_line` para ler apenas o necessário.
- **NOVO/PEQUENO:** Leitura completa permitida apenas se o arquivo tiver menos de 50 linhas.
- **FALLBACK:** Se a leitura falhar, tente listar o diretório para confirmar o caminho.

---
### Tool: replace_string
Description: Surgically replaces a specific exact string block in an EXISTING file.
Usage: replace_string(path='path/to/file', old_string='exact old text', new_string='new text')

Detailed Instructions:
Esta é a ferramenta OBRIGATÓRIA para modificação de código em arquivos existentes.

**REGRAS DE OURO:**
- **EXATIDÃO:** O parâmetro `old_string` deve ser uma cópia EXATA do texto que está no arquivo (incluindo espaços e quebras de linha). Se não for exato, a ferramenta falhará.
- **CONTEXTO ÚNICO:** Se o trecho de código se repetir no arquivo, adicione mais linhas de contexto (antes ou depois) no `old_string` para garantir que o match seja único (ocorrência = 1).
- **SUBSTITUIÇÃO, NÃO CRIAÇÃO:** Se o arquivo não existir, use `write_file` para criá-lo.

---
### Tool: search_memory
Description: Searches past conversation history (FTS5 + Vector).
Usage: search_memory(query='technical topic')

Detailed Instructions:
Use esta ferramenta para recuperar o contexto de sessões passadas.

**REGRAS DE OURO:**
- **LAYER 1:** Retorna IDs e resumos técnicos.
- **ECONOMIA:** Nunca tente ler todas as memórias. Use o ID retornado aqui com `fetch_memory_detail` para ver o conteúdo completo.

---
### Tool: write_file
Description: Creates a NEW file with content. DO NOT use on existing files.
Usage: write_file(path='path/to/new_file', content='content')

Detailed Instructions:
Use esta ferramenta APENAS para criar arquivos novos.

**REGRAS DE OURO:**
- **PROIBIDO:** Nunca use `write_file` para editar arquivos que já existem (isso desperdiça contexto). Use `edit_file` em vez disso.
- **IDENTAÇÃO:** Garanta que o conteúdo siga os padrões do projeto.

---
