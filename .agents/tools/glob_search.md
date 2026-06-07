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
