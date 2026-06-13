"""
dispatcher.py — Algoritmo de despacho energético inteligente
=============================================================

Este é o módulo central do SmartHub Solar. Em cada intervalo de tempo
(15 min por padrão), o despachante decide DE ONDE virá a energia para
atender a demanda dos eletropostos, respeitando a hierarquia:

    Prioridade 1 — Geração solar instantânea (custo zero, CO2 zero)
    Prioridade 2 — Bateria estacionária    (custo zero, CO2 zero, finita)
    Prioridade 3 — Rede elétrica (SIN)     (custo cheio, CO2 emite)

O excedente solar (quando produção > demanda) carrega a bateria, até o
limite de capacidade. Se a bateria estiver cheia E houver excedente,
esse excedente é DESCARTADO (curtailed) — em produção real iria pra rede
via net-metering, mas modelamos como perda por simplicidade.

A bateria respeita a profundidade de descarga máxima (DoD) para preservar
ciclos de vida, e considera eficiência round-trip de 93% (Li-FePO4).

Comparação `baseline` (sem despacho): a mesma demanda é atendida 100%
pela rede, sem aproveitar solar nem bateria — é o cenário "estação
ingênua sem inteligência".
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from . import config


@dataclass
class ResultadoDespacho:
    """Resultado de uma simulação de 24h com o algoritmo de despacho."""
    # Curvas instantâneas (kW por passo de tempo)
    producao_solar:   np.ndarray
    demanda_total:    np.ndarray
    solar_para_carga: np.ndarray   # solar consumido diretamente pelos EVs
    solar_para_bat:   np.ndarray   # solar excedente que carregou bateria
    solar_descartado: np.ndarray   # solar excedente perdido (bateria cheia)
    bateria_para_carga: np.ndarray # descarga da bateria para os EVs
    rede_para_carga:    np.ndarray # consumo da rede para suprir o déficit
    estado_bateria_kwh: np.ndarray # state of charge ao longo do tempo

    # Energia totalizada (kWh ao final do dia)
    energia_demandada:    float = 0.0
    energia_solar_total:  float = 0.0  # gerada (incluindo descarte)
    energia_solar_usada:  float = 0.0  # diretamente em carga
    energia_bateria_usada: float = 0.0
    energia_rede:         float = 0.0
    energia_descartada:   float = 0.0


def simular_despacho(
    producao_solar: np.ndarray,
    demanda: np.ndarray,
    capacidade_bateria_kwh: float = 30.0,
    soc_inicial_kwh: float = 0.0,
) -> ResultadoDespacho:
    """
    Roda a simulação de despacho ao longo de 24h.

    Parâmetros:
        producao_solar: vetor de produção solar (kW) por passo
        demanda: vetor de demanda dos eletropostos (kW) por passo
        capacidade_bateria_kwh: capacidade nominal da bateria
        soc_inicial_kwh: estado de carga inicial (default 0 = bateria vazia)

    Retorna:
        ResultadoDespacho com todas as curvas e totais.
    """
    n = len(producao_solar)
    dt_h = config.PASSO_TEMPO_MIN / 60.0      # fração de hora por passo

    # Capacidade útil = capacidade nominal × DoD máxima
    capacidade_util = capacidade_bateria_kwh * config.PROFUNDIDADE_DESCARGA_MAX
    soc = min(soc_inicial_kwh, capacidade_util)  # estado de carga (kWh)

    # Vetores de resultado
    solar_carga    = np.zeros(n)
    solar_bat      = np.zeros(n)
    solar_desc     = np.zeros(n)
    bat_carga      = np.zeros(n)
    rede_carga     = np.zeros(n)
    estado_bateria = np.zeros(n)

    # Loop principal de despacho
    for i in range(n):
        gen_kw = producao_solar[i]
        load_kw = demanda[i]

        # Energia (kWh) disponível e demandada neste intervalo
        energia_gen  = gen_kw * dt_h
        energia_load = load_kw * dt_h

        # ---------- PASSO 1: solar direto para carga ----------
        usado_direto = min(energia_gen, energia_load)
        deficit = energia_load - usado_direto      # quanto ainda falta
        excedente = energia_gen - usado_direto     # quanto sobrou de solar

        solar_carga[i] = usado_direto / dt_h       # converte de volta para kW

        # ---------- PASSO 2: excedente solar carrega bateria ----------
        if excedente > 0 and soc < capacidade_util:
            espaco_disponivel = capacidade_util - soc
            # eficiência de carga ≈ sqrt(round-trip), aproximação justa
            eficiencia_carga = config.EFICIENCIA_BATERIA ** 0.5
            energia_para_bat = min(excedente * eficiencia_carga,
                                   espaco_disponivel)
            soc += energia_para_bat
            solar_bat[i] = (energia_para_bat / eficiencia_carga) / dt_h
            excedente -= energia_para_bat / eficiencia_carga

        # Se ainda sobra solar e a bateria está cheia, descartamos
        if excedente > 0:
            solar_desc[i] = excedente / dt_h

        # ---------- PASSO 3: descarrega bateria para suprir déficit ----------
        if deficit > 0 and soc > 0:
            eficiencia_descarga = config.EFICIENCIA_BATERIA ** 0.5
            # energia útil entregue = energia tirada × eficiência
            energia_que_falta = deficit
            energia_a_retirar = min(energia_que_falta / eficiencia_descarga,
                                    soc)
            energia_entregue = energia_a_retirar * eficiencia_descarga
            soc -= energia_a_retirar
            bat_carga[i] = energia_entregue / dt_h
            deficit -= energia_entregue

        # ---------- PASSO 4: o que ainda faltar vem da rede ----------
        if deficit > 0:
            rede_carga[i] = deficit / dt_h

        estado_bateria[i] = soc

    # Totaliza energias em kWh
    energia_demandada    = demanda.sum() * dt_h
    energia_solar_total  = producao_solar.sum() * dt_h
    energia_solar_usada  = solar_carga.sum() * dt_h
    energia_bateria_usada = bat_carga.sum() * dt_h
    energia_rede         = rede_carga.sum() * dt_h
    energia_descartada   = solar_desc.sum() * dt_h

    return ResultadoDespacho(
        producao_solar=producao_solar,
        demanda_total=demanda,
        solar_para_carga=solar_carga,
        solar_para_bat=solar_bat,
        solar_descartado=solar_desc,
        bateria_para_carga=bat_carga,
        rede_para_carga=rede_carga,
        estado_bateria_kwh=estado_bateria,
        energia_demandada=energia_demandada,
        energia_solar_total=energia_solar_total,
        energia_solar_usada=energia_solar_usada,
        energia_bateria_usada=energia_bateria_usada,
        energia_rede=energia_rede,
        energia_descartada=energia_descartada,
    )


def simular_baseline_sem_smarthub(demanda: np.ndarray) -> ResultadoDespacho:
    """
    Cenário de comparação: estação ingênua, sem SmartHub.
    Toda a demanda é atendida pela rede. Nenhuma fonte renovável usada
    (mesmo se houvesse painéis solares, sem despacho inteligente eles
    apenas exportariam para o grid sem aproveitamento direto).
    """
    n = len(demanda)
    dt_h = config.PASSO_TEMPO_MIN / 60.0
    zeros = np.zeros(n)
    return ResultadoDespacho(
        producao_solar=zeros.copy(),
        demanda_total=demanda.copy(),
        solar_para_carga=zeros.copy(),
        solar_para_bat=zeros.copy(),
        solar_descartado=zeros.copy(),
        bateria_para_carga=zeros.copy(),
        rede_para_carga=demanda.copy(),
        estado_bateria_kwh=zeros.copy(),
        energia_demandada=demanda.sum() * dt_h,
        energia_solar_total=0.0,
        energia_solar_usada=0.0,
        energia_bateria_usada=0.0,
        energia_rede=demanda.sum() * dt_h,
        energia_descartada=0.0,
    )


if __name__ == "__main__":
    from . import pv_generation, ev_demand
    np.random.seed(42)
    solar = pv_generation.gerar_curva_solar_diaria(30.0, estacao="verao")
    demanda = ev_demand.gerar_curva_demanda_diaria(n_carregadores=8)
    r = simular_despacho(solar, demanda, capacidade_bateria_kwh=30.0)
    print(f"Demanda total:    {r.energia_demandada:.1f} kWh")
    print(f"Solar gerada:     {r.energia_solar_total:.1f} kWh")
    print(f"Solar usada:      {r.energia_solar_usada:.1f} kWh")
    print(f"Bateria usada:    {r.energia_bateria_usada:.1f} kWh")
    print(f"Rede consumida:   {r.energia_rede:.1f} kWh")
    print(f"Solar descartada: {r.energia_descartada:.1f} kWh")
