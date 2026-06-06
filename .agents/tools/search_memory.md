---
name: "search_memory"
description: "Searches past conversation history (FTS5 + Vector)."
usage: "search_memory(query='technical topic')"
---
Use esta ferramenta para recuperar o contexto de sessões passadas.

**REGRAS DE OURO:**
- **LAYER 1:** Retorna IDs e resumos técnicos.
- **ECONOMIA:** Nunca tente ler todas as memórias. Use o ID retornado aqui com `fetch_memory_detail` para ver o conteúdo completo.
