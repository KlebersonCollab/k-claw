---
name: "replace_string"
description: "Surgically replaces a specific exact string block in an EXISTING file."
usage: "replace_string(path='path/to/file', old_string='exact old text', new_string='new text')"
---
Esta é a ferramenta OBRIGATÓRIA para modificação de código em arquivos existentes.

**REGRAS DE OURO:**
- **EXATIDÃO:** O parâmetro `old_string` deve ser uma cópia EXATA do texto que está no arquivo (incluindo espaços e quebras de linha). Se não for exato, a ferramenta falhará.
- **CONTEXTO ÚNICO:** Se o trecho de código se repetir no arquivo, adicione mais linhas de contexto (antes ou depois) no `old_string` para garantir que o match seja único (ocorrência = 1).
- **SUBSTITUIÇÃO, NÃO CRIAÇÃO:** Se o arquivo não existir, use `write_file` para criá-lo.
