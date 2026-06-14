# 📊 Relatório de Análise Técnica — Agent Harness (Atualizado)

> **Data:** 2026-06-14
> **Última Atualização:** 2026-06-14
> **Versão Analisada:** 0.1.0
> **Avaliador:** K-Claw — Engenheiro de Software Sênior
> **Escopo:** Relatório de estado atual do projeto Agent Harness (k-claw), incluindo estrutura, dependências e funcionalidades.

---

## 📋 Resumo Executivo (Executive Summary)

O **Agent Harness** é um framework de orquestração multi-agente de ponta construído em Python (>=3.13). Sua principal inovação reside na implementação rigorosa do padrão **Agente Pai (Orquestrador) + Sub-Agentes Especialistas**, garantindo que o Orquestrador funcione puramente como delegador (`delegate_to_agent`), mantendo a separação de responsabilidades e aumentando a robustez.

O sistema foi desenhado para ser não apenas funcional, mas altamente observável, seguro e extensível, suportando múltiplas fontes LLM (OpenAI, Anthropic, etc.) através de uma arquitetura modular. A memória é um pilar central, utilizando um sistema em três camadas que garante tanto a velocidade contextual quanto o recall semântico profundo.

### 🎯 Pontos Chave da Arquitetura
*   **Orquestração Delegativa:** Elimina chamadas diretas de função no orquestrador principal.
*   **Memória Multi-Camadas:** Cache (L1) → Híbrido (L2: FTS5 + Vetorial) → Detalhe Completo (L3).
*   **Segurança Robusta:** Implementação de Human-in-the-Loop (HITL), Redação de Segredos e Modos operacionais restritos.

---

## 🏛️ Decisões Arquiteturais Core (Core Architectural Decisions)

Esta seção detalha os padrões implementados que definem a integridade do sistema, indo além de uma simples lista de tecnologias.

### 2.1. Padrão Orquestração e Fluxo de Trabalho
**Decisão:** Implementação estrita do padrão Agente Pai → Especialista.
**Impacto:** O `Orchestrator` não executa lógica de negócio ou I/O; ele apenas avalia o estado global (Blackboard), determina a ferramenta necessária, formata os argumentos e delega via mecanismo controlado (`delegate_to_agent`). Isso isola falhas e garante auditabilidade.
**Mecanismo:** Uso de LangGraph para definir estados transitórios e transições baseadas em resultados de ferramentas/agentes.

### 2.2. Sistema de Memória Contextual Avançada (3-Layer Memory)
A memória não é um repositório único, mas um sistema hierárquico otimizado para diferentes necessidades:

1.  **Camada L1 (Cache):** Para contexto imediato da sessão atual; alta velocidade de leitura e escrita de fatos recentes.
2.  **Camada L2 (Hybrid Search):** O motor principal de recuperação de conhecimento. Combina duas abordagens em um único índice SQLite:
    *   **FTS5:** Para busca por palavra-chave exata e rápida.
    *   **sqlite-vec:** Para busca vetorial por similaridade semântica (cosseno, 384 dimensões).
3.  **Camada L3 (Detalhe Completo):** Armazenamento do conteúdo completo das memórias, acessado somente quando necessário para minimizar o uso de tokens.

---

## 📁 Estrutura do Projeto

```
D:\Projetos\k-claw
├── .coverage
├── .env.template
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── AGENTS.md
├── ARCH.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── REPORT.md
├── TOOLS.md
├── benchmark_results_baseline.txt
├── pyproject.toml
├── pytest.ini
├── uv.lock
├── core/
├── entrypoints/
├── infra/
├── scripts/
├── tests/
├── tools/
├── webui/
```

**Descrição dos diretórios principais:**
*   `core/` - Lógica central do framework (orquestração, memória, ferramentas).
*   `entrypoints/` - Pontos de entrada (CLI, API, Telegram bot).
*   `infra/` - Infraestrutura (configuração de bancos, serviços externos).
*   `tests/` - Suite de testes (unitários, de integração, end-to-end, edge cases).
*   `tools/` - Ferramentas auxiliares e scripts.
*   `webui/` - Interface web (frontend e backend).

---

## 🛠️ Tecnologias e Dependências

**Linguagem:** Python >=3.13

**Dependências Principais (via pyproject.toml):**
*   **Framework:** LangGraph, LangChain
*   **API:** FastAPI, Uvicorn
*   **LLM:** Integrações com OpenAI, Anthropic, Ollama, HuggingFace, OpenRouter
*   **Memória e Busca:** SQLite (WAL, FTS5), sqlite-vec
*   **Validação:** Pydantic
*   **Variáveis de Ambiente:** Python-Dotenv
*   **Interface:** Rich
*   **Testes:** Pytest, Pytest-Asyncio, Pytest-Cov
*   **Qualidade:** Pre-commit
*   **Comunicação:** Python-Telegram-Bot
*   **YAML:** PyYAML
*   **Embeddings:** Sentence-Transformers
*   **ORM:** SQLAlchemy

**Scripts de Entrada (definidos em pyproject.toml):**
*   `agent-harness-cli` - Interface de linha de comando
*   `agent-harness-api` - Servidor API FastAPI
*   `agent-harness-bot` - Bot do Telegram

**Grupos de Dependências de Desenvolvimento:**
*   `dev`: Pytest, Pytest-Asyncio, Pre-commit

---

## 🧪 Qualidade e Testes

O projeto segue um rigoroso padrão de qualidade:
*   **Cobertura mínima de testes:** >= 90% (verificado via `pytest --cov=.`).
*   **Tipos de testes:**
    *   Unitários: Cobertura de funções e métodos individuais.
    *   Integração: Validação da interação entre módulos.
    *   End-to-end (e2e): Fluxos completos do usuário.
    *   Edge cases: Cenários extremos e limites.
*   **Ferramentas:** Pytest com plugins de asyncio e coverage.
*   **Configuração:** `pytest.ini` e seções `[tool.coverage.*]` no `pyproject.toml`.

---

## 🚀 Como Começar

Consulte o `README.md` para instruções detalhadas de instalação e uso. Comandos úteis do `Makefile`:
*   `make install` - Instala dependências usando uv
*   `make setup` - Configuração inicial (copia .env, instala dependências)
*   `make run` - Executa a API em primeiro plano (desenvolvimento)
*   `make test` - Executa todos os testes
*   `make test-cov` - Executa testes com relatório de cobertura (>= 90%)
*   `make clear-memory` - Limpa todas as sessões e memória de longo prazo (Banco de Dados SQLite)

---

## 📈 Próximos Passos (Roadmap Sugerido)

Com base no estado atual do projeto, os próximos passos poderiam incluir:
1.  **Estabilidade e Bug Fixes:** Addressar issues identificadas nos testes e no uso real.
2.  **Expansão de Integrações LLM:** Adicionar suporte a novos provedores e modelos.
3.  **Melhorias na UI/WebUI:** Aprimorar a interface web para monitoramento e interação com agentes.
4.  **Documentação Avançada:** Tutoriais, exemplos de uso e guias de contribuição.
5.  **Benchmarks de Desempenho:** Otimização da memória e busca híbrida para cargas maiores.
6.  **Segurança:** Auditorias de segurança e expansão dos modos de operação restrita.
7.  **Integração Contínua (CI):** Fortalecer pipelines de CI/CD com testes em múltiplos ambientes.

---

> *Este relatório foi gerado automaticamente como parte do processo de manutenção do projeto. Para questões ou sugestões, consulte o `CONTRIBUTING.md` ou abra uma issue no repositório.*