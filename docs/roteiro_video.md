# Roteiro do Vídeo — Sprint 2 GoodWe Challenge
## SmartHub Solar — Prova de Conceito Funcional

**Duração total prevista:** ~4min50s (com 10s de buffer entre handoffs)
**Tempo por integrante:** ~48 segundos · ~115 a 130 palavras
**Ritmo de fala recomendado:** ~145 palavras por minuto (natural, sem pressa)
**Formato:** todos os integrantes aparecem em câmera (rubrica veda narração por IA)

A tela é compartilhada com o **dashboard Streamlit** rodando em paralelo. A pessoa que está falando opera o dashboard quando o momento pedir. Outras pessoas podem reagir em pequenas miniaturas se for chamada com várias câmeras, mas o foco é o conteúdo + a tela.

---

## Pessoa 1 — Abertura e Recap da Sprint 1
**Tempo:** 00:00 – 00:48
**Tela:** câmera + slide simples com logo ChargeGrid SmartHub
**Critério coberto:** organização da apresentação (parte dos 20 pts) + ponte com Sprint 1

### Fala
> "Na Sprint 1 apresentamos o ChargeGrid SmartHub: a camada de inteligência que transforma carregadores GoodWe em operação comercial. Definimos quatro pilares — controle de demanda, protocolos abertos, tarifação e IA aplicada. Mas para esta disciplina, Energias Renováveis e Sustentáveis, faltava conectar o produto à parte mais nobre do portfólio GoodWe: os inversores solares. É exatamente isso que provamos hoje. Construímos um simulador funcional que demonstra como o SmartHub integra geração fotovoltaica e bateria estacionária a uma estação ChargeGrid real — reduzindo consumo de rede, custo e emissão de CO₂ ao mesmo tempo."

### Pontos-chave para gravação
- Recapitula Sprint 1 sem alongar — em 2 frases
- "Mais nobre do portfólio GoodWe" — entonação valorizando o ecossistema solar
- "É exatamente isso que provamos hoje" — pausa marcada, vira a tese da apresentação

---

## Pessoa 2 — Arquitetura e Tese Técnica
**Tempo:** 00:48 – 01:38
**Tela:** diagrama de arquitetura do README (3 camadas: interface, inteligência, modelagem física)
**Critério coberto:** justificativa técnica dos componentes (parte dos 60 pts)

### Fala
> "O protótipo tem três camadas. Na base, modelagem física — uma curva sinusoidal de geração solar calibrada pelas horas de sol pico de São Paulo, dados do PVGIS, e uma curva de demanda com quatro picos típicos de estação comercial. No meio, a inteligência: o despachante decide a cada 15 minutos de onde vem a energia, seguindo uma hierarquia inegociável — solar primeiro, bateria segundo, rede só em último caso. No topo, a interface em Streamlit, onde o operador configura capacidade e vê o resultado em tempo real. Toda parametrização é baseada em fonte oficial — GoodWe datasheets, fator do SIN do MCTI, tarifa branca da ANEEL."

### Pontos-chave para gravação
- "Hierarquia inegociável" — entonação firme, conceito-chave
- Os três níveis (modelagem, inteligência, interface) precisam aparecer nítidos
- "Fonte oficial" — credibilidade, slide pode até mostrar os logos MCTI / ANEEL / PVGIS

---

## Pessoa 3 — Demonstração ao Vivo Parte 1 (Geração e Demanda)
**Tempo:** 01:38 – 02:28
**Tela:** dashboard Streamlit aberto, ajustando sliders no painel lateral
**Critério coberto:** funcionalidade operacional do sistema (parte central dos 60 pts)

### Fala
> "Vamos ver o sistema rodando. Configuro a estação com 30 kWp de inversores GoodWe MS G2 — uma instalação comercial padrão. Adiciono 30 kWh de bateria Lynx Home U, oito pontos de recarga HCA G2 e cinquenta e cinco por cento de ocupação no pico. A simulação roda imediatamente. Olhem o gráfico de despacho: cada barra mostra a composição da energia entregue a cada quinze minutos. De manhã, quase tudo é solar — a curva amarela acompanha a geração. À noite, a barra ganha vermelho — é a rede entrando. Entre eles, a faixa verde da bateria suaviza a transição."

### Pontos-chave para gravação
- Pessoa 3 opera o dashboard fisicamente — mostrar os cliques é parte do conteúdo
- "A simulação roda imediatamente" — destaca a interatividade
- Apontar pra tela quando descrever as três cores (amarelo, verde, vermelho)

---

## Pessoa 4 — Demonstração ao Vivo Parte 2 (Comparação A/B)
**Tempo:** 02:28 – 03:18
**Tela:** Streamlit rolado até a seção "Comparação baseline vs SmartHub"
**Critério coberto:** evidência dos conceitos de energias renováveis (parte central dos 60 pts)

### Fala
> "Aqui está o ponto. Mesma demanda, mesma janela horária — o que muda é só a presença do SmartHub. Sem SmartHub, à esquerda, o gráfico é vermelho do começo ao fim: tudo da rede, sem aproveitar a geração solar mesmo que houvesse painéis instalados. Com SmartHub, à direita, a maior parte da energia vira amarela e verde. O consumo da rede caiu de quase quatrocentos kWh para menos de duzentos — uma redução de cinquenta por cento em um único dia. Isso é o que estamos chamando de inteligência energética: não basta ter solar, é preciso saber despachar."

### Pontos-chave para gravação
- "Aqui está o ponto" — abre com peso, este trecho carrega muito da rubrica
- Apontar visualmente para os dois gráficos lado a lado
- "Não basta ter solar, é preciso saber despachar" — frase de impacto, pausa antes e depois

---

## Pessoa 5 — KPIs e Resultados Quantificados
**Tempo:** 03:18 – 04:08
**Tela:** Streamlit rolado até os KPI cards e o painel de "Impacto anual projetado"
**Critério coberto:** apresentação de dados gerados pelo sistema (parte dos 60 pts) + clareza (20 pts)

### Fala
> "Os números falam. Cinquenta por cento de autossuficiência energética em um único dia de operação. Noventa por cento do solar gerado é efetivamente consumido — quase nada é descartado. Cada dia opera com sete kgs de CO₂ a menos no ar. Projetando isso para o ano, temos quase três toneladas de carbono evitadas — equivalente a oitenta árvores adultas absorvendo durante doze meses, ou sessenta mil quilômetros que um carro a combustão deixou de rodar. Financeiramente: economia anual de sessenta e três mil reais sobre o cenário sem SmartHub. Um payback técnico para a instalação solar + bateria que se paga sozinho."

### Pontos-chave para gravação
- Os números precisam ser ditos com clareza — pausa entre cada um
- "Os números falam" — abertura forte, com olhar firme na câmera
- "Se paga sozinho" — fechamento confiante, sem inflexão dramática

---

## Pessoa 6 — Continuidade e Conclusão
**Tempo:** 04:08 – 04:55
**Tela:** câmera + slide simples ou screenshot do README seção "Continuidade com outras disciplinas"
**Critério coberto:** clareza didática (20 pts) + coerência geral

### Fala
> "Esta camada solar fecha o ecossistema. Em outras disciplinas o grupo construiu o núcleo do SmartHub em C, a camada conversacional em Python com LangChain, e a análise estatística da operação. O que entregamos aqui não é um exercício isolado — é a camada que conecta o produto à parte renovável do portfólio GoodWe. Para a Sprint 3 substituiremos a curva sinusoidal por séries temporais reais do PVGIS, e integraremos esta interface ao núcleo em C via API. Em resumo: o ChargeGrid SmartHub não controla só recarga — orquestra energia. E energia limpa, com inteligência, vira o vetor mais poderoso de sustentabilidade que a operação de transporte elétrico tem a oferecer. Obrigado."

### Pontos-chave para gravação
- "Esta camada solar fecha o ecossistema" — abertura conectiva, vincula tudo
- Os três próximos passos (PVGIS real, integração com C, Sprint 3) dão tom de continuidade
- "Energia limpa, com inteligência, vira o vetor mais poderoso de sustentabilidade" — pausa antes, olhar firme, pausa depois
- "Obrigado" curto e seco

---

## Distribuição de Pontos da Rubrica por Pessoa

| Pessoa | Trecho | Pontos da rubrica cobertos |
|---|---|---|
| 1 | Abertura + recap Sprint 1 | Parte dos 20 pts (organização) + ponte com Sprint 1 |
| 2 | Arquitetura técnica | Parte dos 60 pts (justificativa técnica + conceitos) |
| 3 | Demo geração e demanda | Parte central dos 60 pts (funcionalidade operacional) |
| 4 | Comparação A/B baseline vs SmartHub | Parte central dos 60 pts (evidência de renováveis) |
| 5 | KPIs e impacto quantificado | Parte dos 60 pts (dados gerados) + 20 pts (clareza) |
| 6 | Continuidade e conclusão | 20 pts (clareza didática + coerência geral) |

**Cobertura total prevista: 100/100** — desde que cada pessoa cumpra o tempo, mostre a tela quando indicado e mantenha o olhar e a entonação firmes.

---

## Checklist Técnico Pré-Gravação

### Antes de começar a gravar

- [ ] Computador conectado em rede estável (de preferência cabo, não Wi-Fi)
- [ ] Dashboard rodando em `streamlit run src/app.py` numa janela limpa do navegador
- [ ] Resolução de tela ajustada para 1920x1080 (full HD)
- [ ] Aba do navegador sem notificações abertas
- [ ] Áudio testado em cada integrante (sem ruído de fundo)
- [ ] Iluminação de rosto adequada em todos
- [ ] Mensagens do celular silenciadas

### Configurações sugeridas pra Pessoa 3 mostrar

```
Capacidade solar: 30 kWp
Estação: Verão
Nebulosidade: 0.10
Bateria: 30 kWh
SOC inicial: 20%
Carregadores: 8
Ocupação: 55%
Seed: 42
```

Esses números reproduzem aproximadamente os KPIs citados pela Pessoa 5 — **importante manter consistência entre fala e tela**.

### Recomendações finais

- **Ensaiem cronometrando.** Quem estourar 55s na primeira tentativa, corte uma frase do bloco.
- **Pessoa 3 e 4 precisam decorar onde clicar.** As demos ao vivo são o coração da apresentação — fluência com a interface vale ponto.
- **Pessoa 5 carrega os números.** Não improvise valores diferentes do que vai aparecer na tela. Se o seed der números levemente diferentes na hora, ajuste a fala para o que efetivamente aparecer no dashboard.
- **Pessoa 6 fecha o vídeo.** A frase final precisa cair com convicção — se for o último ensaio antes de dormir, dorma com ela na cabeça, grava melhor de manhã.

### Configurações do YouTube

- Visibilidade: **Não listado** (não Privado — Privado bloqueia o avaliador)
- Título sugerido: `ChargeGrid SmartHub — Sprint 2 Energias Renováveis | FIAP × GoodWe`
- Descrição: copie a seção "Visão geral" do README
- Tags opcionais: `goodwe`, `chargegrid`, `fiap`, `energias renováveis`, `streamlit`

---

*Roteiro alinhado à mesma estrutura disciplinada da Sprint 1 — mesma cadência, mesmos 6 blocos cobrindo a rubrica completa.*
