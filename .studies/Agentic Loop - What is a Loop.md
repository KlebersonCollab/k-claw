# Agentic Loop - What is a Loop

> **Fonte:** [YouTube - What is a Loop](https://www.youtube.com/watch?v=7BrxIBkX3mg)
> **Data de extração:** 2025-07-14

---

## Resumo

O vídeo explica o conceito de **Agentic Loop** (Loop Agênico), um padrão que tem ganhado destaque na comunidade de IA. A ideia central: em vez de você promptar o agente a cada passo, você **projeta um loop** que prompta o agente autonomamente até atingir um critério de parada.

---

## Definição de Loop

### Modelo Tradicional (Sequencial)
- Você fornece um prompt → o agente gera output → você avalia → fornece o próximo prompt
- **Você é o gargalo**
- Não funciona para tarefas de longa duração

### Modelo Agentic Loop
- Você define o **objetivo inicial** e o **critério de parada**
- Um **orquestrador** prompta o sistema baseado no estado atual do trabalho
- O loop para quando atinge o critério de parada (testes unitários, máximo de iterações, etc.)
- **Seu trabalho não desapareceu — subiu um nível:** alguém ainda decide o que construir e se é bom

> "Prompting não morreu. Apenas se moveu para o início."

---

## O Loop não é uma ideia nova

| Ano | Conceito |
|-----|----------|
| Clássico | `while loop` com um modelo dentro |
| 2022 | Paper **ReAct** — agente que raciocina, age, lê resultados e repete |
| 2023 | **AutoGPT** — deu um objetivo ao loop e deixou ele se auto-promptar (rodou em círculos, queimou tokens, não entregou nada) |
| Recorrente | **Versão disciplinada** — loop pequeno que alimenta as mesmas instruções, mas reseta o contexto a cada vez para não driftar |

> **"Designar loops" = cron job + tomador de decisão no corpo**

---

## Componentes de um Loop Sério

1. **Work Trees** — cópias isoladas do repositório para agentes não colidirem entre si
2. **Skills** — instruções reutilizáveis nomeadas para o agente não reaprender convenções a cada run
3. **Connectors** — para abrir PRs, atualizar tickets, etc.
4. **Verifier** — **o componente mais importante**: quem escreve o código não deve ser quem o avalia
5. **Memory on disk** — o modelo esquece entre runs; precisa de estado persistente para recuperar de falhas

---

## O Passo de Verificação (O Mais Importante)

> "Um loop que simplesmente escreve código e nunca se verifica é a maneira mais rápida de gerar erros confiantes e queimar tokens."

Um grande loop deve:
- Rodar diferentes testes
- Analisar os resultados
- Ter um **verificador independente** que valide a implementação

Esse mecanismo de feedback é o que faz um loop ser **ótimo**.

---

## Orchestration Tax (Taxa de Orquestração)

- Loops permitem iniciar **centenas de agentes paralelos**
- **Mas o teto real é você** — sua capacidade de revisar, entender e mergear implementações
- O número de loops que você pode rodar é definido pela **sua banda de revisão**, não pela ferramenta
- **Mais agentes ≠ mais de você**

### O Perigo Silencioso
- Se o loop roda sozinho, você só vê o resultado final
- A lacuna entre o que foi entregue e o que você entende **cresce**
- O perigo não é falhar alto — é **sucessar silenciosamente** de uma forma que você parou de acompanhar 300 commits atrás

---

## O Prompt Inicial (A Semente)

- O prompt inicial importa **mais agora, não menos**
- Não é mais um prompt que você corrige enquanto vai — é a **semente para centenas de etapas que você não está assistindo**
- Se vago, o loop não chuta uma vez — chuta com confiança na mesma direção **repetidamente**
- **Specs vagas + critérios de parada vagos + testes vagos = suposições erradas = desastre** (especialmente em loops longos)

---

## Custo

- Todo token gerado pelo loop custa dinheiro
- Precisa ter:
  - Um **check de quando parar de fazer progresso**
  - Um **limite rígido de gastos**
- A versão romântica: "escreva loops e durma" — a versão honesta: sem limites, o custo foge do controle

---

## Quando NÃO usar Loops

- Tarefas simples que um único prompt resolve
- Quando você não tem critérios de parada claros
- Quando não há verificador independente
- Quando o custo de tokens não é gerenciável
- Quando o projeto é grande e a compreensão humana é crítica

---

## Principais Takeaways

1. **Loop = while loop + modelo + critério de parada + verificador**
2. **Seu papel subiu de nível** — de promptar a cada passo para projetar o sistema
3. **O prompt inicial é a semente** — seja preciso, defina critérios claros
4. **Verificação independente é obrigatória** — o agente não deve se auto-avaliar
5. **Orchestration Tax é real** — sua banda de revisão é o limite
6. **Controle de custo é essencial** — limites rígidos de tokens/gastos
7. **Loops não são mágica** — são uma ferramenta com custos e limitações reais
