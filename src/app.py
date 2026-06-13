"""
app.py — Dashboard Streamlit do SmartHub Solar
================================================

Aplicação interativa que permite ao usuário configurar parâmetros da
estação ChargeGrid (capacidade solar, bateria, ocupação) e ver, em
tempo real, o desempenho do algoritmo de despacho.

Para rodar:
    pip install -r requirements.txt
    streamlit run src/app.py
"""

from __future__ import annotations
import sys
from pathlib import Path

# Permite rodar tanto via `streamlit run src/app.py` quanto via módulo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src import config, pv_generation, ev_demand, dispatcher, metrics


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="SmartHub Solar — ChargeGrid",
    page_icon="☀️",
    layout="wide",
)


# Paleta de cores consistente em todos os gráficos
COR_SOLAR    = "#F7B32B"
COR_BATERIA  = "#16A085"
COR_REDE     = "#E74C3C"
COR_DEMANDA  = "#2C3E50"


# ============================================================================
# HEADER
# ============================================================================
st.title("☀️ SmartHub Solar — Prova de Conceito")
st.markdown(
    "**Simulador de despacho energético inteligente** para a operação "
    "ChargeGrid GoodWe. Demonstra como a integração de geração solar, "
    "bateria estacionária e algoritmo de despacho reduz consumo de rede, "
    "emissões de CO₂ e custo operacional."
)
st.caption(
    "EV Challenge 2026 · FIAP × GoodWe · Disciplina: Soluções em Energias "
    "Renováveis e Sustentáveis · Sprint 2"
)
st.divider()


# ============================================================================
# SIDEBAR — CONFIGURAÇÃO DO CENÁRIO
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configuração do cenário")

    st.subheader("Geração solar")
    pot_solar = st.slider(
        "Capacidade fotovoltaica instalada (kWp)",
        min_value=5, max_value=100, value=30, step=5,
        help="Soma das potências dos inversores GoodWe MS G2 instalados."
    )
    estacao = st.selectbox(
        "Estação do ano",
        options=["verao", "inverno"],
        format_func=lambda x: "Verão (HSP 5,5h)" if x == "verao" else "Inverno (HSP 4,0h)",
    )
    nebulosidade = st.slider(
        "Nebulosidade média do dia",
        min_value=0.0, max_value=0.7, value=0.1, step=0.05,
        help="0 = céu limpo. Reduz proporcionalmente a geração solar.",
    )

    st.subheader("Armazenamento")
    capac_bateria = st.slider(
        "Capacidade da bateria estacionária (kWh)",
        min_value=0, max_value=100, value=30, step=5,
        help="Linha GoodWe Lynx Home U (Li-FePO4). Eficiência 93% round-trip.",
    )
    soc_inicial = st.slider(
        "Estado de carga inicial da bateria (%)",
        min_value=0, max_value=100, value=20, step=10,
    )

    st.subheader("Demanda dos eletropostos")
    n_carregadores = st.slider(
        "Número de pontos de recarga",
        min_value=2, max_value=20, value=8, step=1,
    )
    ocupacao = st.slider(
        "Fator de ocupação no pico (%)",
        min_value=20, max_value=100, value=55, step=5,
    )

    st.divider()
    st.markdown("**Reproducibilidade**")
    seed = st.number_input("Seed do gerador aleatório", value=42, step=1)
    if st.button("🎲 Novo sorteio (cloud cover + chegadas)"):
        seed = int(np.random.randint(0, 100000))
        st.session_state["seed"] = seed
        st.rerun()


# ============================================================================
# SIMULAÇÃO
# ============================================================================
np.random.seed(seed)

curva_solar = pv_generation.gerar_curva_solar_diaria(
    potencia_instalada_kwp=pot_solar,
    estacao=estacao,
    nebulosidade=nebulosidade,
)
curva_demanda = ev_demand.gerar_curva_demanda_diaria(
    n_carregadores=n_carregadores,
    fator_ocupacao=ocupacao / 100.0,
)
resultado_smart = dispatcher.simular_despacho(
    producao_solar=curva_solar,
    demanda=curva_demanda,
    capacidade_bateria_kwh=capac_bateria,
    soc_inicial_kwh=capac_bateria * (soc_inicial / 100.0),
)
resultado_baseline = dispatcher.simular_baseline_sem_smarthub(curva_demanda)
kpis = metrics.calcular_kpis(resultado_smart, resultado_baseline)
anual = metrics.projetar_anual(kpis)


# ============================================================================
# KPIs PRINCIPAIS (linha superior)
# ============================================================================
st.subheader("📊 Indicadores do dia simulado")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Autossuficiência",
        f"{kpis.autossuficiencia_pct:.1f}%",
        help="Fração da demanda atendida por fontes próprias (solar + bateria)",
    )
with col2:
    st.metric(
        "Solar aproveitado",
        f"{kpis.autoconsumo_solar_pct:.1f}%",
        help="Do que o sistema gerou, quanto foi efetivamente usado",
    )
with col3:
    st.metric(
        "CO₂ evitado",
        f"{kpis.co2_evitado_kg:.1f} kg",
        delta=f"≈ {kpis.arvores_equivalentes:.1f} árvores/ano absorvem isso",
        help="Comparação com cenário 100% rede (fator MCTI)",
    )
with col4:
    st.metric(
        "Economia financeira",
        f"R$ {kpis.economia_vs_baseline_rs:.2f}",
        delta=f"Projeção anual: R$ {anual['economia_rs']:,.0f}",
        help="Custo evitado da rede com tarifa horária dinâmica (ANEEL Branca)",
    )

st.divider()


# ============================================================================
# GRÁFICO PRINCIPAL — Despacho energético ao longo do dia
# ============================================================================
st.subheader("🔌 Despacho energético ao longo das 24h")
st.caption(
    "Cada barra mostra de onde veio a energia entregue aos veículos a cada "
    "intervalo de 15 minutos. A linha amarela indica a geração solar instantânea."
)

# Constrói DataFrame para o gráfico
horas = np.arange(0, 24, config.PASSO_TEMPO_MIN / 60.0)
df_despacho = pd.DataFrame({
    "Hora": horas,
    "Solar direto": resultado_smart.solar_para_carga,
    "Bateria": resultado_smart.bateria_para_carga,
    "Rede": resultado_smart.rede_para_carga,
})

fig, ax = plt.subplots(figsize=(13, 5))

# Áreas empilhadas (de baixo pra cima: solar, bateria, rede)
ax.fill_between(horas, 0,
                resultado_smart.solar_para_carga,
                color=COR_SOLAR, alpha=0.85, label="Solar direto")
ax.fill_between(horas,
                resultado_smart.solar_para_carga,
                resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga,
                color=COR_BATERIA, alpha=0.85, label="Bateria")
ax.fill_between(horas,
                resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga,
                resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga + resultado_smart.rede_para_carga,
                color=COR_REDE, alpha=0.75, label="Rede (SIN)")

# Linha de produção solar (incluindo o que carregou bateria + descarte)
ax.plot(horas, resultado_smart.producao_solar,
        color="#D68910", linewidth=2.0, linestyle="--",
        label="Produção solar total", zorder=5)

ax.set_xlabel("Hora do dia")
ax.set_ylabel("Potência (kW)")
ax.set_title("Atendimento da demanda — composição por fonte")
ax.set_xlim(0, 24)
ax.set_xticks(range(0, 25, 2))
ax.grid(alpha=0.3)
ax.legend(loc="upper left", framealpha=0.95)
plt.tight_layout()
st.pyplot(fig)


# ============================================================================
# COMPARAÇÃO BASELINE vs SMARTHUB
# ============================================================================
st.subheader("⚖️ Comparação: estação sem SmartHub vs estação com SmartHub")
st.caption(
    "Mesma demanda, mesma janela horária. A diferença é apenas o algoritmo "
    "de despacho — comprova o valor da camada de inteligência."
)

col_a, col_b = st.columns(2)

with col_a:
    fig_a, ax_a = plt.subplots(figsize=(7, 4))
    ax_a.fill_between(horas, 0,
                      resultado_baseline.rede_para_carga,
                      color=COR_REDE, alpha=0.85,
                      label="100% rede")
    ax_a.set_title("BASELINE — sem SmartHub", fontweight="bold")
    ax_a.set_xlabel("Hora do dia")
    ax_a.set_ylabel("Potência (kW)")
    ax_a.set_xlim(0, 24)
    ax_a.grid(alpha=0.3)
    ax_a.legend()
    plt.tight_layout()
    st.pyplot(fig_a)
    st.metric("Consumo da rede",
              f"{resultado_baseline.energia_rede:.1f} kWh",
              delta=None)

with col_b:
    fig_b, ax_b = plt.subplots(figsize=(7, 4))
    ax_b.fill_between(horas, 0,
                      resultado_smart.solar_para_carga,
                      color=COR_SOLAR, alpha=0.85, label="Solar")
    ax_b.fill_between(horas,
                      resultado_smart.solar_para_carga,
                      resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga,
                      color=COR_BATERIA, alpha=0.85, label="Bateria")
    ax_b.fill_between(horas,
                      resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga,
                      resultado_smart.solar_para_carga + resultado_smart.bateria_para_carga + resultado_smart.rede_para_carga,
                      color=COR_REDE, alpha=0.75, label="Rede")
    ax_b.set_title("COM SMARTHUB — despacho inteligente", fontweight="bold")
    ax_b.set_xlabel("Hora do dia")
    ax_b.set_ylabel("Potência (kW)")
    ax_b.set_xlim(0, 24)
    ax_b.grid(alpha=0.3)
    ax_b.legend()
    plt.tight_layout()
    st.pyplot(fig_b)
    st.metric("Consumo da rede",
              f"{resultado_smart.energia_rede:.1f} kWh",
              delta=f"-{resultado_baseline.energia_rede - resultado_smart.energia_rede:.1f} kWh vs baseline",
              delta_color="inverse")

st.divider()


# ============================================================================
# ESTADO DA BATERIA
# ============================================================================
st.subheader("🔋 Estado de carga da bateria estacionária")
st.caption(
    "A bateria absorve excedente solar durante o dia e devolve à noite, "
    "deslocando energia limpa pra fora do pico de geração."
)

if capac_bateria > 0:
    fig_bat, ax_bat = plt.subplots(figsize=(13, 3))
    ax_bat.fill_between(horas, 0, resultado_smart.estado_bateria_kwh,
                        color=COR_BATERIA, alpha=0.7)
    ax_bat.axhline(
        capac_bateria * config.PROFUNDIDADE_DESCARGA_MAX,
        color="black", linestyle="--", linewidth=1,
        label=f"Capacidade útil ({config.PROFUNDIDADE_DESCARGA_MAX*100:.0f}% DoD)"
    )
    ax_bat.set_xlabel("Hora do dia")
    ax_bat.set_ylabel("Carga (kWh)")
    ax_bat.set_xlim(0, 24)
    ax_bat.set_ylim(0, capac_bateria * 1.05)
    ax_bat.legend()
    ax_bat.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_bat)
else:
    st.info("Defina capacidade > 0 no painel lateral para visualizar.")

st.divider()


# ============================================================================
# IMPACTO ANUAL PROJETADO
# ============================================================================
st.subheader("🌍 Impacto anual projetado")
st.caption(
    "Extrapolando o resultado do dia simulado para 365 dias de operação "
    "(condições médias). Útil para argumento de payback e narrativa ESG."
)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("CO₂ evitado", f"{anual['co2_evitado_t']:.2f} t/ano")
with c2:
    st.metric("Árvores equivalentes", f"{anual['arvores']:,.0f}")
with c3:
    st.metric("Km não rodados", f"{anual['km_evitados']:,.0f} km")
with c4:
    st.metric("Economia projetada", f"R$ {anual['economia_rs']:,.0f}")


# ============================================================================
# RODAPÉ — METODOLOGIA E REFERÊNCIAS
# ============================================================================
with st.expander("📖 Metodologia e referências técnicas"):
    st.markdown(f"""
**Modelo solar:** curva sinusoidal calibrada por Horas de Sol Pico de São Paulo
(NREL/PVGIS) — verão {config.HORAS_SOL_PICO_VERAO}h, inverno {config.HORAS_SOL_PICO_INVERNO}h.
Performance Ratio de {config.PERFORMANCE_RATIO*100:.0f}% e eficiência de inversor
GoodWe MS G2 de {config.EFICIENCIA_INVERSOR*100:.1f}%.

**Modelo de bateria:** Lynx Home U (Li-FePO4) com eficiência round-trip de
{config.EFICIENCIA_BATERIA*100:.0f}% e DoD máxima de {config.PROFUNDIDADE_DESCARGA_MAX*100:.0f}%.

**Fator de emissão:** {config.FATOR_EMISSAO_SIN_KG_POR_KWH*1000:.1f} gCO₂eq/kWh
(média do SIN 2024 — MCTI).

**Tarifa de referência:** R$ {config.TARIFA_REDE_BASE_RS_POR_KWH:.2f}/kWh com
multiplicadores ANEEL Branca (Res. 733/2016) — ponta {config.MULT_TARIFA_PONTA}×,
intermediário {config.MULT_TARIFA_INTERMEDIARIA}×, fora ponta {config.MULT_TARIFA_FORA_PONTA}×.

**Frota HCA G2:** mix típico 60% GW7K + 25% GW11K + 15% GW22K
(referência ABVE para estações comerciais 2024).

**Algoritmo de despacho:** prioridade hierárquica (solar → bateria → rede)
com curtailment em excedente solar. Mesma lógica do sistema em C entregue
na disciplina Data Structure and Algorithms (sprint paralela).
""")
