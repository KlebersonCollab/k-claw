# 🔍 Análise: Karpathy Auto Research vs K-Claw Harness

> **Fonte:** Vídeo "This 'Karpathy System' could 701x your AI Workflows" (Dream Labs AI, 2026-06-09)
> **Transcrição:** [`transcricao.md`](./transcricao.md)
> **Data da análise:** 2025-06-10

---

## 1. Resumo do Sistema "Auto Research" de Karpathy

O vídeo descreve o **Auto Research**, um sistema open-sourced por Andre Karpathy que implementa um **loop de auto-otimização** para qualquer "asset" de negócio. O conceito central é simples mas poderoso: o humano define o objetivo e o scoring, e o AI agent roda autonomamente, iterando no asset indefinidamente.

### Arquitetura de 3 Arquivos

| Arquivo | Função | Quem acessa |
|---------|--------|-------------|
| **Instructions** (`program.md`) | Define O QUE melhorar e os critérios de sucesso | Apenas o humano |
| **Asset** (`train.py`) | O arquivo/asset que será otimizado (código, email, landing page, etc.) | Humano + AI |
| **Scoring** (`prepare.py`) | Métrica objetiva que avalia se a iteração melhorou ou piorou | Apenas o humano (read-only para AI) |

### O Loop

1. O humano define o objetivo no `instructions.md`
2. O agent AI pega o `asset`, cria uma variação (hipótese)
3. Executa o `scoring` para comparar com o baseline
4. **Se melhorou** → mantém a variação, vira o novo baseline
5. **Se piorou** → descarta, volta ao baseline anterior
6. Repete indefinidamente (ex: loops de 5 minutos, rodando overnight)

### Critérios de Aplicabilidade

**Must-Haves:**
1. **Métrica objetiva** — precisa ter um número claro (load time, CTR, reply rate)
2. **Feedback loop rápido** — resultados em minutos/horas, não semanas
3. **AI precisa ter acesso** ao asset para modificá-lo

**Nice-to-Have:**
4. **Alto volume de feedback** — mais dados = mais iterações = mais melhoria
5. **Barato falhar** — cada experimento deve ter custo baixo
6. **Métrica consistente** — o scoring não pode mudar no meio do processo

### Exemplos de Aplicação Citados no Vídeo

- **Coding efficiency**: otimizar tempo de execução de código (Shopify: 53% mais rápido)
- **Cold email**: testar subject lines e corpos para maximizar reply rate
- **Website load speed**: otimizar HTML/assets para minimizar tempo de carregamento
- **Instagram DM outreach**: maximizar call booking rate
- **YouTube titles/thumbnails**: maximizar CTR
- **Sales scripts**: maximizar close rate
- **Prompt engineering**: otimizar prompts para melhores resultados
- **Landing pages**: maximizar conversion rate

---

## 2. Mapeamento: Auto Research vs K-Claw

### 2.1 O que o K-Claw já tem (e é compatível)

| Conceito Auto Research | Equivalente K-Claw | Status |
|------------------------|-------------------|--------|
| **Loop de iteração** | `harness.py` StateGraph com ciclo `agent → tools → agent` | ✅ Já existe |
| **Human-in-the-loop** | Humano define objetivo, revisa resultados, pode interromper | ✅ Já existe |
| **Max iterations** | `max_iterations` no harness | ✅ Já existe |
| **Sub-agentes especializados** | `coder`, `researcher`, `verifier` | ✅ Já existe |
| **Verificação independente** | Agente `verifier` separado do `coder` | ✅ Já existe |
| **Orquestração** | Agente Pai coordena sub-agentes | ✅ Já existe |
| **Tools/ferramentas** | `write_file`, `run_shell`, `grep_search`, etc. | ✅ Já existe |

### 2.2 O que o K-Claw NÃO tem (gaps)

| Conceito Auto Research | Gap no K-Claw |
|------------------------|---------------|
| **Scoring Plugin** | ❌ Não existe mecanismo objetivo de avaliação (número) que o agente não possa manipular |
| **Loop Autônomo (Overnight Mode)** | ❌ Não existe modo de execução contínua/background — tudo é REPL interativo |
| **Experiment Tracking** | ❌ Não existe logging estruturado de iterações (hipótese → resultado → decisão) |
| **Baseline Management** | ❌ Não existe conceito de "baseline" com auto-revert |
| **Scoring Lock** | ❌ Não existe mecanismo de read-only para arquivos de scoring |

---

## 3. Recomendações Acionáveis

### 3.1 Alta Prioridade — Fundacional

#### 🔴 **A) Scoring Plugin System**

O componente mais importante do Auto Research é o **scoring mechanism** — uma forma objetiva e imutável de avaliar se uma iteração melhorou ou piorou o asset.

**Proposta:**
- Criar uma ferramenta `run_scoring(asset_path) -> float` no ToolRegistry
- O scoring script é definido pelo humano e marcado como read-only para o agente
- O agente chama a ferramenta, recebe um número, e decide se mantém ou descarta a iteração

```python
# Exemplo de scoring plugin
def run_scoring(asset_path: str) -> dict:
    """Executa o scoring script definido pelo humano. Read-only para o agente."""
    # 1. Lê o scoring script (imutável, definido pelo humano)
    # 2. Executa o asset contra o scoring
    # 3. Retorna {"score": float, "baseline": float, "improved": bool}
    ...
```

**Onde encaixaria:** Nova ferramenta no `ToolRegistry` + convenção de arquivo `scoring.py` na raiz do projeto.

#### 🔴 **B) Auto-Research Loop Mode**

Um novo modo no harness que executa o loop de otimização autonomamente:

```
1. Humano define: asset + instructions + scoring
2. Harness entra em modo "auto-research":
   a. Agent modifica o asset (hipótese)
   b. Scoring é executado
   c. Se melhorou → mantém, volta para (a)
   d. Se piorou → descarta, volta para (a)
   e. Repete até max_iterations ou convergência
3. Harness reporta resultados ao humano
```

**Onde encaixaria:** Novo estado no `harness.py` StateGraph ou novo modo `auto_research` no CLI.

### 3.2 Média Prioridade — Valor Adicionado

#### 🔧 **C) Experiment Tracking**

Registrar cada iteração com: hipótese, mudança feita, score anterior, score novo, decisão (keep/revert).

**Onde encaixaria:** Nova tabela no SQLite + ferramenta `log_experiment()` no ToolRegistry.

#### 🔧 **D) Verifier como Scoring Function**

O agente `verifier` já existe e poderia ser estendido para atuar como **scoring automatizado** — recebendo o asset e retornando uma avaliação quantitativa baseada em critérios objetivos (testes, benchmarks, lint, etc.).

**Vantagem:** Reutiliza infraestrutura existente, sem criar novo componente.

#### 🔧 **E) Template de "Auto Research Mission"**

Um template de prompt/missão pré-definido para quando o usuário quer rodar um ciclo de auto-otimização:

```
"Quero otimizar [ASSET] para melhorar [MÉTRICA].
O scoring será feito por [SCRIPT/CRITÉRIO].
Execute até [MAX_ITERATIONS] iterações ou convergência."
```

**Onde encaixaria:** Como uma skill em `.agents/skills/auto-research.md`.

### 3.3 Baixa Prioridade — Nice to Have

#### 🔧 **F) Overnight Execution / Agendamento**

Permitir que o harness seja executado como um processo background (systemd, cron, ou similar) para rodar loops longos sem sessão interativa ativa.

**Complexidade:** Alta — requer gerenciamento de processos, recovery de falhas, notificação de conclusão.

#### 🔧 **G) Multi-Asset Parallel Research**

O vídeo menciona que o sistema poderia ser apontado para múltiplos assets simultaneamente. O K-Claw poderia delegar múltiplos `coder` agents para otimizar diferentes assets em paralelo.

**Onde encaixaria:** Extensão do `delegate_to_agent` para suportar múltiplas delegações concorrentes.

---

## 4. Análise Crítica — O que NÃO Devemos Copiar

### ⚠️ **Scoring puramente quantitativo tem limites**

O vídeo foca muito em métricas objetivas, mas muitos problemas de negócio têm componentes qualitativos. O K-Claw já tem a vantagem de ter **human-in-the-loop** e **verificação independente**, que capturam nuances que um score numérico não captura.

### ⚠️ **Loops infinitos sem supervisão são perigosos**

O Auto Research roda "indefinidamente" — isso pode gerar custos inesperados e resultados indesejados. O K-Claw já tem `max_iterations` e aprovação interativa, que são **proteções importantes** que não devem ser removidas.

### ⚠️ **Overfitting**

O próprio CEO do Shopify mencionou que os resultados estavam "somewhat overfit". Um loop de otimização sem validação em dados reais pode otimizar para a métrica mas piorar o resultado real. O K-Claw já mitiga isso com o `verifier` independente.

---

## 5. Conclusão

O sistema Auto Research de Karpathy é essencialmente um **padrão de uso** de componentes que o K-Claw já possui. A principal diferença é que o Auto Research propõe um **modo de operação** (loop autônomo com scoring) que o K-Claw ainda não implementa nativamente.

### O que já temos (fundação sólida):
- Orquestração de sub-agentes ✅
- Human-in-the-loop ✅
- Verificação independente ✅
- Max iterations ✅
- Tool system ✅

### O que falta (2 features de alto impacto):
1. **Scoring Plugin System** — mecanismo objetivo de avaliação
2. **Auto-Research Loop Mode** — modo de execução autônoma

### Recomendação Final

Implementar as 2 features de alta prioridade (A e B) daria ao K-Claw a capacidade de rodar loops de auto-otimização equivalentes ao Auto Research, mas com as vantagens adicionais que o K-Claw já possui (human-in-the-loop, verifier independente, max iterations).

O esforço estimado é moderado — a arquitetura do K-Claw já suporta essas features, falta apenas implementar o scoring plugin e o modo de loop autônomo.
