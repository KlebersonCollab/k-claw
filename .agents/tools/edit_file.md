---
name: "edit_file"
description: "Surgically replaces a range of lines in an EXISTING file."
usage: "edit_file(path='path/to/file', start_line=10, end_line=15, content='new content')"
---
Esta é a ferramenta OBRIGATÓRIA para arquivos existentes.

**REGRAS DE OURO:**
- **EXISTENTE:** Use SEMPRE que o arquivo já existir no sistema.
- **ZERO WASTE:** Substitua apenas as linhas necessárias para economizar tokens.
- **FALLBACK:** Se o arquivo não existir, use `write_file` para criá-lo.
- Se quiser ADICIONAR código entre as linhas 10 e 11, use `start_line=11, end_line=10`.
