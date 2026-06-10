# 🎬 Transcrição: This "Karpathy System" could 701x your AI Workflows

> **Fonte:** Dream Labs AI — YouTube
> **Data de publicação:** 2026-06-09
> **Duração:** 21:39
> **URL:** https://www.youtube.com/watch?v=4JpwNnw0-jI
> **Data de extração:** 2025-06-10
> **Tema:** Sistema Auto Research de Andre Karpathy

---

## Resumo Executivo

O vídeo descreve o sistema **Auto Research**, open-sourced por Andre Karpathy, que implementa um **loop de auto-otimização** para qualquer "asset" de negócio. O conceito central: o humano define o objetivo e o scoring, e o AI agent roda autonomamente, iterando no asset indefinidamente — inclusive enquanto o humano dorme.

O sistema já acumulou **85.000+ stars no GitHub** e foi usado pelo CEO da Shopify para otimizar código, obtendo **53% mais velocidade**. O vídeo demonstra aplicações práticas em três áreas: velocidade de website, cold email outreach e Facebook ads.

---

## 1. Introdução ao Auto Research

### O que é

**[00:00]** Andre Karpathy, considerado o "godfather" da IA moderna, lançou um sistema simples chamado **Auto Research**, que os maiores labs de IA do mundo gastaram milhões tentando criar. Desde o lançamento, o projeto acumulou mais de **85.000 stars no GitHub**. O CEO da Shopify apontou o sistema para o código da empresa e obteve um speedup de **53%**.

**[00:30]** O sistema não funciona apenas para código. Pode ser apontado para qualquer parte do negócio: emails, ads, landing pages, AI skills, AI agents, ou conteúdo orgânico. Ele força cada parte do negócio a **se auto-aperfeiçoar na velocidade da luz** enquanto você dorme.

**[01:00]** O vídeo promete detalhar o sistema e mostrar como aplicá-lo em três exemplos práticos do mundo real.

---

## 2. Origem e Contexto

### O Tweet de Karpathy

**[01:30]** Karpathy tweetou sobre o projeto, gerando **11 milhões de views**:

> *"I packaged up the auto research project into a new self-contained minimal repo if people would like to play with it over the weekend."*

**[01:30]** Ele explica que o **humano** itera no prompt, dando ao agente um conjunto de instruções sobre o que melhorar. O **AI agent** itera no código de treinamento (ou qualquer asset que se queira melhorar). O sistema literalmente trabalha a noite toda enquanto o humano dorme.

**[01:45]** O objetivo é *"engenhar seus AI agents para fazer o progresso de pesquisa mais rápido indefinidamente, sem qualquer envolvimento humano"* — por isso podemos dormir.

### Resultados Iniciais

**[02:00]** Em seu teste inicial, o LLM rodou em um **loop de 5 minutos**. Após **83 experimentos**, ficou **11% mais rápido** do que quando Karpathy o havia deixado. Ele já vinha trabalhando nesse mesmo agente há muito tempo e concluíra que estava pronto. Mas a ferramenta Auto Research encontrou mais **11% de melhoria** no IQ do agente.

**[02:30]** Karpathy reflete:

> *"I'd been working on this same LLM agent trying to make it smarter for a very long time and thought it was done. But his auto research tool found another 11% improvement in its IQ."*

---

## 3. A Arquitetura de 3 Arquivos

**[03:00]** O sistema é composto por **3 arquivos fundamentais**:

| Arquivo | Função | Quem acessa |
|---------|--------|-------------|
| **Instructions** (`program.md`) | Define O QUE melhorar e os critérios de sucesso | Apenas o humano |
| **Asset** (`train.py`) | O arquivo/asset que será otimizado (código, email, landing page, etc.) | Humano + AI |
| **Scoring** (`prepare.py`) | Métrica objetiva que avalia se a iteração melhorou ou piorou | Apenas o humano (read-only para AI) |

**[03:30]** O sistema é **self-contained** — tudo que o agente precisa saber está nesses 3 arquivos. Não há dependências externas complexas.

---

## 4. O Loop de Auto-Otimização

**[04:00]** O funcionamento do loop:

1. O humano define o objetivo no `instructions.md`
2. O agent AI pega o `asset`, cria uma variação (hipótese)
3. Executa o `scoring` para comparar com o baseline
4. **Se melhorou** → mantém a variação, vira o novo baseline
5. **Se piorou** → descarta, volta ao baseline anterior
6. Repete indefinidamente (ex: loops de 5 minutos, rodando overnight)

**[04:30]** O sistema é **stateful** — ele lembra o que já tentou e o que funcionou. Cada experimento é registrado.

---

## 5. O Papel do Humano vs. Agente

**[05:00]** A divisão de responsabilidades:

| Humano | Agente |
|--------|--------|
| Define o objetivo e critérios | Gera variações do asset |
| Itera nas instruções (prompt) | Executa o scoring |
| Define o scoring | Mantém o histórico de experimentos |
| **Não** executa o loop | Roda o loop autonomamente |

**[05:30]** O humano **nunca** executa o loop — apenas o configura. O agente faz o trabalho pesado de experimentação.

---

## 6. Aplicações Além do Código

**[06:00]** O vídeo enfatiza que o Auto Research não é apenas para código. Qualquer "asset" de negócio pode ser otimizado:

- **Cold email**: testar subject lines e corpos para maximizar reply rate
- **Website load speed**: otimizar HTML/assets para minimizar tempo de carregamento
- **Instagram DM outreach**: maximizar call booking rate
- **YouTube titles/thumbnails**: maximizar CTR
- **Sales scripts**: maximizar close rate
- **Prompt engineering**: otimizar prompts para melhores resultados
- **Landing pages**: maximizar conversion rate

---

## 7. Critérios de Aplicabilidade

### Must-Haves

**[08:00]** Três critérios essenciais para que o Auto Research funcione:

**Must-Have #1: Métrica Objetiva**

**[08:30]** Precisa ter um **número claro** que determine se algo melhorou ou piorou:

- ✅ Velocidade de carregamento de website
- ✅ Número de impressões de um conteúdo
- ✅ Click-through rate de uma página

**Must-Have #2: Feedback Loop Rápido**

**[09:00]** Os resultados precisam vir em **minutos ou horas**, não semanas.

- ✅ Velocidade de carregamento (testada em segundos)
- ✅ Abertura de emails (medida na primeira hora)
- ❌ Rankings de SEO (leva ~10 dias para o Google reindexar)

**Must-Have #3: AI Precisa Ter Acesso ao Asset**

**[09:30]** O agente precisa conseguir modificar o asset diretamente.

### Nice-to-Haves

**[10:00]** Critérios desejáveis mas não obrigatórios:

| # | Critério | Descrição |
|---|----------|-----------|
| 4 | **Alto volume de feedback** | Mais dados = mais iterações = mais melhoria |
| 5 | **Barato falhar** | Cada experimento deve ter custo baixo |
| 6 | **Métrica consistente** | O scoring não pode mudar no meio do processo |

---

## 8. Exemplos de Aplicação no Negócio

**[10:30]** O vídeo lista diversas aplicações práticas:

| Área | Asset a Otimizar | Métrica de Scoring |
|------|-----------------|-------------------|
| **Coding efficiency** | Código-fonte | Tempo de execução |
| **Website speed** | HTML/assets | Tempo de carregamento (ms) |
| **Cold email** | Subject line, corpo | Reply rate / Open rate |
| **Instagram DM** | Script de DM | Booking rate |
| **YouTube** | Títulos e thumbnails | CTR / Watch time |
| **Sales scripts** | Roteiro de vendas | Close rate |
| **Prompt engineering** | Prompts | Qualidade do resultado |
| **Landing pages** | Copy e design | Conversion rate |
| **Sales funnels** | Funil completo | Taxa de conversão |
| **App speed** | Código do app | Performance |
| **Cart checkout** | Fluxo de checkout | Taxa de abandono |

**[12:00]** Exemplos detalhados:

- **Website speed**: asset = código-fonte, scoring = runtime em milissegundos
- **Cold email**: instruções = "obter mais replies", scoring = positive reply rate, asset = subject line + opener + CTA
- **Instagram DM**: instruções = "book more calls, stay human, don't spam", scoring = booking rate por template
- **Sales scripts**: análise de quais scripts geram melhor close rate
- **Prompt engineering**: otimizar prompts para melhores resultados

**[13:30]** Sobre feedback loops mais longos: Karpathy recomenda loops de 5 minutos, mas para aplicações de negócio pode-se ser mais flexível. Mesmo com loops de 2-24 horas, ainda é melhor do que fazer todos os testes manualmente.

---

## 9. Master Prompt e Setup

**[14:00]** O apresentador criou um **master prompt** que configura o sistema de 3 arquivos automaticamente. Basta colar no Claude Code e ele:

1. Configura o three-file system
2. Pergunta qual asset otimizar
3. Conecta APIs necessárias
4. Começa o auto research

**[14:30]** O prompt incorpora as regras de Karpathy e o modelo do GitHub.

---

## 10. Exemplo Prático #1: Velocidade de Website

**[15:00]** O apresentador usa um website local mockado pelo Claude Code que não está otimizado.

**[15:15]** Após colar o prompt no Claude Code, o agente responde:

> *"Hi, I'm now your auto research engineer. Here's the deal. In one breath, we pick one thing in your business and turn 'is it good' into a single honest number. Then I sit here all night changing it, scoring it, keeping what wins and trashing what loses."*

**[16:00]** O apresentador confirma: website speed é um **textbook auto research target** — é objetiva, rápida e reachable (HTML e JPEGs em um lugar local).

**[16:30]** O scoring escolhido foi **milissegundos de carregamento**. O agente não pode tocar no arquivo de scoring.

**[17:00]** Resultado: o website foi de **800ms (baseline)** para **90.5ms** — uma melhoria de ~8x. O agente gerou um relatório detalhado com cada rodada e as otimizações aplicadas.

---

## 11. Exemplo Prático #2: Cold Email

**[17:30]** Baseado em exemplo de Nick Serev, que tem uma empresa de cold email outreach.

**[18:00]** O apresentador cola o prompt em uma nova janela do Claude Code:

> *"Consider me your one-person R&D department."*

**[18:15]** Objetivo: melhorar **subject lines de cold emails**. Métrica: **open rate em 24 horas**. Metodologia: enviar 1.000 emails com a nova subject line vs. 1.000 com a anterior, comparar resultados após 24h.

**[18:30]** Ferramentas compatíveis: Smartlead AI para envio, auto dialers para calling agents, Manyhat para DM marketing.

**[19:00]** Como 24h é um feedback loop longo para demonstração, o apresentador pediu ao Claude Code para **simular** como seria o resultado após semanas de execução, com preditores de open rate baseados nas subject lines testadas.

**[19:15]** O ponto-chave: o feedback real (quantas pessoas abriram o email) precisa ser alimentado de volta no sistema para validar cada mudança.

---

## 12. Exemplo Prático #3: Facebook Ads

**[20:00]** O apresentador descreve o que Chamath mencionou: combinar geração de imagens/vídeos com IA + auto research para otimizar ads continuamente.

**[20:15]** Exemplo real mencionado: um criador usou IA para renderizar vídeos curtos no Instagram/TikTok + auto research para aprender com os resultados e iterar. Resultado: *"He's doing really well."*

**[20:30]** Setup para Facebook Ads:
- O agente se conecta diretamente à conta de Facebook Ads
- Cria variações dos ads existentes
- Testa cada variação com **$10**
- Métrica: **cost per click (CPC)**

**[20:45]** Mesmo que leve 2 horas para gastar $10, não importa — o sistema está constantemente testando novos dados em background.

**[21:00]** O apresentador forneceu dados mockados de Facebook Ads. O agente:
- Criou variações dos ads
- Gerou **predicted cost per click** para cada uma
- Montou estrutura de diretórios e arquivos com scoreboard e experiment logs

**[21:15]** Os arquivos de losing experiments ficam registrados para referência.

**[21:30]** O sistema roda autonomamente enquanto o apresentador dorme.

---

## Conclusão

O vídeo demonstra que o Auto Research de Karpathy transcende a otimização de código e pode ser aplicado a praticamente qualquer área de negócio que tenha:

1. Uma **métrica objetiva**
2. Um **feedback loop rápido**
3. Um **asset modificável** pelo agente

A mensagem final: enquanto você dorme, o sistema trabalha — iterando, testando, melhorando — transformando a velocidade de experimentação de **30 experimentos/ano** para potencialmente **36.500/ano**.

---

## Referências Citadas no Vídeo

| Referência | Contexto |
|------------|----------|
| **Auto Research (GitHub)** | Repositório open-source de Andre Karpathy com 85.000+ stars |
| **Shopify** | CEO usou o sistema para otimizar código, obtendo 53% mais velocidade |
| **Nick Serev** | Empresário de cold email outreach, exemplo de aplicação |
| **Chamath** | Investidor que mencionou a aplicação em Facebook Ads |
| **Smartlead AI** | Ferramenta de envio de cold emails compatível |
| **Manyhat** | Ferramenta de DM marketing compatível |
