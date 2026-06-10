# 🤝 Guia de Contribuição — Agent Harness

Obrigado por considerar contribuir com o **Agent Harness**! Este documento descreve as diretrizes para contribuições.

## 📋 Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/agent-harness.git`
3. **Crie uma branch**: `git checkout -b feature/minha-feature`
4. **Desenvolva** sua feature ou correção
5. **Teste** (veja abaixo)
6. **Commit**: `git commit -m 'Descrição clara da mudança'`
7. **Push**: `git push origin feature/minha-feature`
8. **Abra um Pull Request**

## ✅ Requisitos de Qualidade

### Testes (Obrigatório)

Todo código deve ter **4 tipos de testes**:

| Tipo | Diretório | Descrição |
|------|-----------|-----------|
| **Unitário** | `tests/unit/` | Testa funções/métodos individuais |
| **Integração** | `tests/integration/` | Testa interação entre módulos |
| **End-to-End** | `tests/e2e/` | Testa fluxos completos do usuário |
| **Edge Cases** | `tests/edge_cases/` | Testa cenários extremos e limites |

**Cobertura mínima: 90%** (verificado via `make test-cov`).

### Comandos de Teste

```bash
# Todos os testes
make test

# Por tipo
make test-unit
make test-integration
make test-e2e
make test-edge

# Com cobertura (>= 90%)
make test-cov

# Tudo com cobertura detalhada
make test-all
```

### Pre-commit Hooks

```bash
# Instalar hooks
make setup-hooks

# Rodar manualmente
uv run pre-commit run --all-files
```

Os hooks verificam:
- Segredos expostos (API keys)
- Formatação de código
- Sintaxe Python
- Trailing whitespace
- Arquivos grandes

## 📝 Padrões de Código

- **Linguagem:** Python 3.13+
- **Estilo:** PEP 8 + Black
- **Tipagens:** Type hints obrigatórios
- **Docstrings:** Google style para funções públicas
- **Commits:** Mensagens claras em português ou inglês

## 🏗️ Arquitetura

O projeto segue a arquitetura **Agente Pai (Orquestrador) + Sub-Agentes Especialistas**:

- **Orquestrador** nunca executa tarefas diretamente — apenas delega via `delegate_to_agent`
- **Sub-agentes** operam em contexto isolado para economizar tokens
- **Verificador** valida todo trabalho antes de entregar ao usuário

Veja `ARCH.md` para detalhes completos da arquitetura.

## 📚 Documentação

Ao adicionar novas funcionalidades:

1. Atualize `README.md` se a funcionalidade afetar o uso
2. Atualize `ARCH.md` se afetar a arquitetura
3. Atualize `TOOLS.md` se adicionar novas ferramentas
4. Atualize `AGENTS.md` se adicionar novos sub-agentes

## 🐛 Reportando Bugs

1. Verifique se o bug já foi reportado nas Issues
2. Crie uma nova Issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Logs relevantes (com segredos mascarados)

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a **MIT License**.
