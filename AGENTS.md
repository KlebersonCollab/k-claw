# 🤖 Agent Catalog

Este repositório utiliza uma arquitetura de Agente Pai (Orquestrador) e Sub-Agentes especialistas.

## Regras de Engajamento
1. O Agente Pai deve delegar tarefas para os especialistas **NUNCA EXECUTAR / SEMPRE DELEGAR**.
2. Cada especialista opera em um contexto isolado para economizar tokens.
3. Use a ferramenta `delegate_to_agent` para iniciar uma subtarefa.
