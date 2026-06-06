---
name: "write_file"
description: "Creates a NEW file with content. DO NOT use on existing files."
usage: "write_file(path='path/to/new_file', content='content')"
---
Use esta ferramenta APENAS para criar arquivos novos.

**REGRAS DE OURO:**
- **PROIBIDO:** Nunca use `write_file` para editar arquivos que já existem (isso desperdiça contexto). Use `edit_file` em vez disso.
- **IDENTAÇÃO:** Garanta que o conteúdo siga os padrões do projeto.
