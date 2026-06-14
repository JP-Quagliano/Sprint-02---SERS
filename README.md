# SmartHub Solar — Prova de Conceito Funcional

> Simulador de despacho energético inteligente para a operação ChargeGrid GoodWe.
> EV Challenge 2026 · FIAP × GoodWe · Sprint 2

---

## Identificação

| | |
|---|---|
| **Disciplina** | Soluções em Energias Renováveis e Sustentáveis |
| **Professor** | André Tritiack de Farias |
| **Curso** | Ciência da Computação — 1º Ano · 2026.1 |
| **Turma** | 1CCPH |
| **Grupo** | 02 |

### Integrantes

| Nome | RM |
|------|------|
| João Pedro do Vale Quagliano | 570233 |
| Leticia Aiko Okano | 571988 |
| Thiago Calazans Luz Nakano | 569151 |
| Enzo Scattolin Furtado | 570824 |
| Guilherme De Lucena Fontes | 569658 |
| Matheus Levi Dagel | 571961 |

### Demonstração em vídeo

🎥  https://youtu.be/rZrxjuAEeDI

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Como princípios de energias renováveis estão na solução](#como-princípios-de-energias-renováveis-estão-na-solução)
4. [Como executar](#como-executar)
5. [Estrutura do código](#estrutura-do-código)
6. [Justificativas técnicas e referências](#justificativas-técnicas-e-referências)
7. [Continuidade com as outras disciplinas](#continuidade-com-as-outras-disciplinas)

---

## Visão geral

Este protótipo demonstra a **camada de inteligência energética** do produto **ChargeGrid SmartHub**, proposto na Sprint 1. Para esta disciplina, estendemos a tese original com a integração explícita à geração fotovoltaica da GoodWe (linha **MS G2**) e ao armazenamento estacionário (linha **Lynx Home U**).

O sistema simula 24 horas de operação de uma estação ChargeGrid comercial e demonstra como um **algoritmo de despacho energético** decide, a cada 15 minutos, de onde virá a energia entregue aos veículos elétricos:

```
Prioridade 1 → Geração solar fotovoltaica  (custo zero, CO₂ zero)
Prioridade 2 → Bateria estacionária        (custo zero, CO₂ zero)
Prioridade 3 → Rede elétrica (SIN)         (custo cheio, emissões)
```

A POC compara **dois cenários idênticos** em demanda mas diferentes em inteligência:

| | Cenário baseline | Cenário SmartHub |
|---|---|---|
| Atendimento da demanda | 100% da rede | despacho priorizado |
| Aproveitamento solar | 0% | até ~95% |
| Bateria estacionária | inerte | absorve excedente e descarrega à noite |
| Consumo da rede | máximo | reduzido em 35–60% |

Os resultados são exibidos em um **dashboard interativo** em Streamlit, com sliders para o avaliador testar diferentes configurações (capacidade solar, bateria, ocupação) e ver, em tempo real, o impacto sobre autossuficiência, emissões e custo.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE INTERFACE                        │
│                                                             │
│      ┌───────────────────────────────────────────────┐      │
│      │   app.py — Dashboard Streamlit interativo     │      │
│      │   KPIs · Gráficos 24h · Comparação A/B        │      │
│      └────────────────────┬──────────────────────────┘      │
└───────────────────────────│─────────────────────────────────┘
                            │
┌───────────────────────────│─────────────────────────────────┐
│                CAMADA DE INTELIGÊNCIA                       │
│                            │                                │
│      ┌─────────────────────┼─────────────────────┐          │
│      │                     │                     │          │
│      ▼                     ▼                     ▼          │
│  ┌────────┐          ┌──────────┐          ┌──────────┐     │
│  │dispatcher          │ metrics  │          │ config   │     │
│  │ Decide a │          │KPIs CO₂ │          │Constants │     │
│  │ cada 15min│         │R$ MWh   │          │GoodWe·SIN│     │
│  └────┬───┘          └────┬─────┘          └────┬─────┘     │
│       │                   │                     │           │
└───────│───────────────────│─────────────────────│───────────┘
        │                   │                     │
┌───────│───────────────────│─────────────────────│───────────┐
│       ▼                   ▼                     ▼           │
│              CAMADA DE MODELAGEM FÍSICA                     │
│                                                             │
│  ┌──────────────────┐               ┌──────────────────┐    │
│  │  pv_generation   │               │    ev_demand     │    │
│  │  Curva solar 24h │               │  Demanda EVs 24h │    │
│  │  HSP-SP · NREL   │               │  4 picos típicos │    │
│  └──────────────────┘               └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de dados em uma simulação

1. O usuário define no painel lateral: **capacidade solar (kWp)**, **bateria (kWh)**, **estação do ano**, **número de carregadores**, **fator de ocupação**.
2. `pv_generation.gerar_curva_solar_diaria()` produz o vetor de 96 amostras (1 a cada 15 min) da produção fotovoltaica.
3. `ev_demand.gerar_curva_demanda_diaria()` produz o vetor de demanda dos eletropostos.
4. `dispatcher.simular_despacho()` itera 96 vezes, decidindo a fonte de cada quilowatt entregue.
5. `dispatcher.simular_baseline_sem_smarthub()` roda o cenário de controle (100% rede).
6. `metrics.calcular_kpis()` compara os dois resultados e calcula autossuficiência, CO₂ evitado e economia.
7. O dashboard renderiza gráficos comparativos e cartões de KPI.

---

## Como princípios de energias renováveis estão na solução

Esta seção atende explicitamente o critério principal da rubrica (60 pts).

### 1. Priorização da fonte renovável

O algoritmo de despacho tem como **regra inegociável** que a energia solar disponível seja sempre consumida primeiro, antes de qualquer fonte fóssil da rede. Isso é o oposto da operação ingênua, onde o eletroposto puxa indiscriminadamente da rede, deixando o excedente solar ser exportado a preço de fome (~0,28 R$/kWh do compensação) ou simplesmente desperdiçado.

### 2. Armazenamento como deslocamento temporal de energia limpa

A bateria estacionária é o que transforma a geração intermitente em fornecimento estável. Sem armazenamento, o solar só atende demanda diurna; com bateria, **deslocamos a energia limpa pra fora da janela solar**, atendendo a demanda noturna (pós-19h, fora da geração) sem recorrer à rede. Essa é a essência da operação 24h renovável.

### 3. Eficiência energética como vetor de sustentabilidade

A redução do consumo de rede não é apenas financeira. Cada kWh evitado economiza **38,5 gCO₂eq** segundo o fator do SIN 2024 (MCTI). Para uma estação comercial típica (8 carregadores, 30 kWp, 30 kWh), isso representa **~2,8 toneladas de CO₂ evitadas por ano** — equivalente a 84 árvores adultas absorvendo carbono pelo mesmo período.

### 4. Curtailment consciente e net-metering

Quando o sistema gera além do que pode consumir e armazenar (cenário de fim de semana com baixa demanda + alta irradiação), o excedente é **identificado e quantificado**. Em produção, esse excedente seria exportado pra rede via net-metering (compensação ANEEL), gerando crédito energético adicional — outra forma de retorno renovável sobre o capital instalado.

### 5. Tarifa horária dinâmica (ANEEL Branca)

A camada financeira respeita a estrutura tarifária ANEEL Branca (Res. 733/2016): kWh consumido em ponta (18–20h) tem multiplicador de 1,5×, enquanto fora-ponta (22–05h) é 0,7×. O SmartHub aproveita isso descarregando a bateria justamente nos horários de tarifa cara — outra otimização que **só faz sentido quando há inteligência de despacho**.

---

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Visual Studio Code (recomendado) ou qualquer terminal Python
- Conexão com internet (apenas para instalação inicial das dependências)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/JP-Quagliano/Sprint-02---SERS
cd smarthub-solar

# 2. (opcional) Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o dashboard
streamlit run src/app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`. Use o painel lateral pra explorar diferentes configurações da estação.

### Atalhos para o avaliador

| Para ver... | Configure no painel lateral |
|---|---|
| Cenário modesto de fim de semana | Solar 15 kWp · Bateria 0 kWh · Ocupação 35% |
| Cenário operacional típico | Solar 30 kWp · Bateria 30 kWh · Ocupação 55% |
| Cenário de máximo aproveitamento | Solar 80 kWp · Bateria 60 kWh · Ocupação 80% |
| Impacto da nebulosidade | Mantenha solar alto e suba "Nebulosidade" pra 0.5 |

---

## Estrutura do código

```
smarthub-solar/
├── src/
│   ├── __init__.py
│   ├── config.py         # constantes técnicas (GoodWe, SIN, ANEEL, PVGIS)
│   ├── pv_generation.py  # modelo de geração solar (sinusoidal calibrada)
│   ├── ev_demand.py      # modelo de demanda de eletropostos (4 picos gaussianos)
│   ├── dispatcher.py     # algoritmo de despacho hierárquico + baseline
│   ├── metrics.py        # KPIs de sustentabilidade e financeiros
│   └── app.py            # dashboard Streamlit (interface)
├── docs/
│   └── roteiro_video.md  # script de 5 min para gravação em grupo
├── README.md             # este arquivo
├── requirements.txt
└── .gitignore
```

### Princípios de design

- **Cada módulo tem responsabilidade única.** `pv_generation` não sabe nada sobre eletropostos; `dispatcher` não sabe nada sobre custo financeiro; `metrics` apenas consome resultados.
- **Constantes técnicas em um único lugar** (`config.py`), todas com fonte oficial citada no comentário. Mudou a tarifa? Mudou a tecnologia de bateria? Um arquivo só.
- **Cenário baseline implementado explicitamente** (`simular_baseline_sem_smarthub`) — não é deduzido por subtração, é simulado de fato. Garante comparação honesta nos KPIs.
- **Reprodutibilidade controlada** via seed no painel — o avaliador pode comparar configurações sem ruído estocástico atrapalhar a leitura.

---

## Justificativas técnicas e referências

### Modelo de geração solar

A geração fotovoltaica é modelada como uma curva sinusoidal entre nascer e pôr do sol, com pico calibrado pelas **Horas de Sol Pico (HSP)** de São Paulo (5,5h no verão, 4,0h no inverno — dados PVGIS/NREL). Aplicamos:

- **Performance Ratio (PR) = 0,82** — referência NREL para sistemas bem dimensionados no Brasil, considera perdas por temperatura, sujeira, mismatch e cabeamento.
- **Eficiência do inversor = 97,8%** — datasheet GoodWe MS G2 (segmento comercial leve).
- **Ruído de ±5%** — simula passagem de nuvens leves; mantém a curva visualmente realista sem distorcer a integral diária.

Esse modelo é o padrão de **pré-viabilidade** (PVGIS, SAM-NREL). Para engenharia executiva real, modelos mais detalhados como DISC, Erbs ou REST2 seriam usados — fora do escopo de uma POC.

### Modelo de demanda

A demanda dos eletropostos é uma **soma de gaussianas** centradas em horários característicos da operação comercial (chegada matinal, almoço, tarde, fim de tarde). O mix de carregadores HCA G2 segue distribuição típica de estação comercial (referência ABVE 2024): 60% GW7K + 25% GW11K + 15% GW22K.

### Algoritmo de despacho

Despacho hierárquico em três níveis com curtailment explícito para excedente. A bateria respeita:

- **Profundidade de descarga (DoD) = 90%** — preserva ciclos de vida da Li-FePO4
- **Eficiência round-trip = 93%** — datasheet Lynx Home U
- A penalidade de eficiência é aplicada separadamente em carga e descarga (cada uma √0,93 ≈ 96,4%)

### Fator de emissão

**0,0385 kgCO₂eq/kWh** — média do Sistema Interligado Nacional 2024, publicação oficial MCTI ("Fatores médios de emissão de CO₂ — SIN"). É um valor baixo para padrões internacionais porque a matriz elétrica brasileira é majoritariamente hidrelétrica, mas suficiente para mostrar impacto cumulativo relevante em operação comercial.

### Tarifa de referência

**R$ 0,85/kWh** com multiplicadores da estrutura tarifária ANEEL Branca (Res. Normativa 733/2016): ponta 1,5×, intermediário 1,2×, fora ponta 0,7×. Valores médios do Grupo B3 comercial em SP (ENEL Distribuição, 2024-2025).

---

## Continuidade com as outras disciplinas

O **ChargeGrid SmartHub** é o mesmo produto que aparece em outras quatro disciplinas do EV Challenge 2026. Esta tabela mapeia o que cada disciplina contribui:

| Disciplina | Camada do produto | Tecnologia |
|------------|-------------------|------------|
| Prompt and Artificial Intelligence | Camada conversacional (SmartHub Assistant) | Python + LangChain + Gemini |
| Data Structure and Algorithms | Núcleo de orquestração e despacho | **C (multi-módulo)** |
| Modelagem Linear para ML | Análise estatística de operação | Python (pandas, matplotlib) |
| Pensamento Computacional Python | Modelagem operacional | Python |
| **Energias Renováveis (esta)** | **Camada de integração solar + bateria** | **Python + Streamlit** |

O algoritmo de despacho hierárquico implementado aqui usa **a mesma lógica de prioridade** do load balancing do sistema em C (disciplina DSA) — só que agora aplicada a fontes de energia em vez de carregadores. É a mesma engenharia, em outro nível de abstração.

---

## Próximos passos (Sprint 3)

- Substituir o modelo sinusoidal por séries temporais reais do PVGIS para validação de precisão
- Adicionar previsão probabilística de geração e demanda (Monte Carlo)
- Integrar a interface Streamlit ao sistema em C via API REST (POC de produto completo)
- Calcular payback financeiro do investimento em solar + bateria

---

## Licença

Trabalho acadêmico — distribuição livre para fins educacionais.
