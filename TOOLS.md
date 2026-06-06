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
### Tool: edit_file
Description: Surgically replaces a range of lines in an EXISTING file.
Usage: edit_file(path='path/to/file', start_line=10, end_line=15, content='new content')

Detailed Instructions:
Esta é a ferramenta OBRIGATÓRIA para arquivos existentes.

**REGRAS DE OURO:**
- **EXISTENTE:** Use SEMPRE que o arquivo já existir no sistema.
- **ZERO WASTE:** Substitua apenas as linhas necessárias para economizar tokens.
- **FALLBACK:** Se o arquivo não existir, use `write_file` para criá-lo.
- Se quiser ADICIONAR código entre as linhas 10 e 11, use `start_line=11, end_line=10`.

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
