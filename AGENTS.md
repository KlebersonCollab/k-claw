# 🤖 Agent Catalog

Este repositório utiliza uma arquitetura de Agente Pai (Orquestrador) e Sub-Agentes especialistas.

## Regras de Engajamento

1. O Agente Pai deve delegar tarefas para os especialistas **NUNCA EXECUTAR / SEMPRE DELEGAR**.
2. Cada especialista opera em um contexto isolado para economizar tokens.
3. Use a ferramenta `delegate_to_agent` para iniciar uma subtarefa.
4. Todo código que for gerado deve ter teste unitário, de integração, end-to-end e teste de caso de borda antes de ser enviado para o usuário, sempre com cobertura >= 90%.

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

## Fluxo de Delegação

```
Orquestrador → coder → verifier → decisão (DELIVER / ESCALATE / LOOP)
```

1. O Orquestrador recebe a tarefa e delega ao **coder**.
2. O **coder** executa a tarefa e produz um relatório técnico.
3. O Orquestrador delega ao **verifier** com o relatório do coder.
4. O **verifier** valida o trabalho e retorna status: `PASS`, `FAIL` ou `NEEDS_REVIEW`.
5. Se `FAIL` ou `NEEDS_REVIEW`: o Orquestrador re-delega ao **coder** com feedback (até `max_correction_retries`).
6. Se exceder o limite de retries: decisão é `ESCALATE` (intervenção humana).

## Qualidade e Testes

Todo código gerado pelos sub-agentes deve seguir o padrão de qualidade definido em `AGENTS.md`:

- **Testes unitários**: Cobertura de funções e métodos individuais.
- **Testes de integração**: Validação da interação entre módulos.
- **Testes end-to-end (e2e)**: Fluxos completos do usuário.
- **Testes de caso de borda (edge_cases)**: Cenários extremos e limites.
- **Cobertura mínima**: >= 90% (verificado via `pytest --cov=.`).
