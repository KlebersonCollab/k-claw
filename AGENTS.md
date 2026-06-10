# 🤖 Agent Catalog

Este repositório utiliza uma arquitetura de Agente Pai (Orquestrador) e Sub-Agentes especialistas.

## Regras de Engajamento
1. O Agente Pai deve delegar tarefas para os especialistas **NUNCA EXECUTAR / SEMPRE DELEGAR**.
2. Cada especialista opera em um contexto isolado para economizar tokens.
3. Use a ferramenta `delegate_to_agent` para iniciar uma subtarefa.
4. Todo codigo que for gerado deve ter teste unitario, de integração, end-to-end e teste de caso de borda antes de ser enviado para o usuario, sempre com cobertura >= 90%.

## Catálogo de Sub-Agentes Especialistas

| Agente | Descrição | Permissão |
|--------|-----------|-----------|
| `coder` | Escrita de código, refatoração e correção de bugs | `write` |
| `researcher` | Busca semântica e análise de documentos | `read` |
| `verifier` | Verificação de código, testes e validação de artefatos | `read` |

### Quando usar cada especialista

- **coder**: Quando precisa criar, modificar ou refatorar código.
- **researcher**: Quando precisa buscar informações, analisar documentos ou entender o codebase.
- **verifier**: Quando precisa validar o trabalho de outro sub-agente — verificar se requisitos foram atendidos, se testes passam, se não há regressões.
