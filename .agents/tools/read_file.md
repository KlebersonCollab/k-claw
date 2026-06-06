---
name: "read_file"
description: "Reads a file from disk with mandatory pagination for existing files."
usage: "read_file(path='path/to/file', start_line=1, end_line=100)"
---
Use esta ferramenta para ler o conteúdo de arquivos.

**REGRAS DE OURO:**
- **EXISTENTE:** Se o arquivo já existe, você DEVE usar `start_line` e `end_line` para ler apenas o necessário.
- **NOVO/PEQUENO:** Leitura completa permitida apenas se o arquivo tiver menos de 50 linhas.
- **FALLBACK:** Se a leitura falhar, tente listar o diretório para confirmar o caminho.
