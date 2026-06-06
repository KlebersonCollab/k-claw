---
name: "list_directory"
description: "Lists files and folders, respecting project ignore rules."
usage: "list_directory(path='.')"
---
Use esta ferramenta para ganhar visão estrutural do projeto.

**REGRAS DE OURO:**
- **VISÃO:** Use sempre antes de ler arquivos específicos se você não tiver certeza dos caminhos.
- **AUTOMÁTICO:** Ignora automaticamente `.venv`, `.git`, e padrões definidos no `.gitignore`.
