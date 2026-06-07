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
