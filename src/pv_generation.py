"""
pv_generation.py — Modelagem da geração fotovoltaica
======================================================

Implementa um modelo simplificado de geração solar para uma instalação
GoodWe (linha MS G2) em São Paulo.

A função `gerar_curva_solar_diaria()` produz um perfil de 24 horas com
amostragem definida em config.PASSO_TEMPO_MIN. O modelo é baseado em:

    P(t) = P_kWp × PR × η_inv × sin(π × (t − t_nasc) / (t_pôr − t_nasc))

para t ∈ [t_nasc, t_pôr], e zero fora desse intervalo. PR é o
Performance Ratio (NREL: typically 0.75–0.85 para BR), η_inv é a
eficiência do inversor GoodWe.

Esse modelo sinusoidal é a aproximação padrão de primeira ordem usada em
estudos preliminares de pré-viabilidade (PVGIS, SAM-NREL). Para POC, é
suficiente — modelos detalhados (DISC, Erbs, REST2) seriam usados na
fase de engenharia executiva.
"""

from __future__ import annotations
import numpy as np
from . import config


def gerar_curva_solar_diaria(
    potencia_instalada_kwp: float,
    estacao: str = "verao",
    nebulosidade: float = 0.0,
) -> np.ndarray:
    """
    Gera o vetor de produção solar instantânea (kW) ao longo de 24h.

    Parâmetros:
        potencia_instalada_kwp: capacidade total dos inversores (kWp)
        estacao: 'verao' ou 'inverno' (afeta horas de sol pico)
        nebulosidade: 0 (céu limpo) a 1 (totalmente coberto) — reduz produção

    Retorna:
        np.ndarray de tamanho PASSOS_POR_DIA com potência em kW por intervalo
    """
    if estacao == "verao":
        nascer = config.NASCER_SOL_VERAO
        por    = config.POR_SOL_VERAO
        hsp    = config.HORAS_SOL_PICO_VERAO
    else:
        nascer = config.NASCER_SOL_INVERNO
        por    = config.POR_SOL_INVERNO
        hsp    = config.HORAS_SOL_PICO_INVERNO

    # Eficiência composta do sistema
    perdas_totais = config.PERFORMANCE_RATIO * config.EFICIENCIA_INVERSOR

    # Pico solar instantâneo derivado das HSP. Integral da senoide ao longo
    # do dia deve igualar energia diária esperada = kWp × HSP × η.
    # ∫ P_max·sin(π·t/L) dt de 0 a L = 2·P_max·L/π = E_dia
    # → P_max = E_dia · π / (2·L)
    duracao_dia = por - nascer
    energia_dia_kwh = potencia_instalada_kwp * hsp * perdas_totais
    pico_kw = (energia_dia_kwh * np.pi) / (2.0 * duracao_dia)

    # Aplica nebulosidade (perda direta)
    pico_kw *= (1.0 - nebulosidade)

    # Vetor de tempo amostrado a cada PASSO_TEMPO_MIN
    horas = np.arange(0, 24, config.PASSO_TEMPO_MIN / 60.0)

    producao = np.zeros_like(horas)
    janela_solar = (horas >= nascer) & (horas <= por)
    producao[janela_solar] = pico_kw * np.sin(
        np.pi * (horas[janela_solar] - nascer) / duracao_dia
    )

    # Variação realista: ruído de ±5% para simular passagem de nuvens leves
    ruido = np.random.normal(loc=1.0, scale=0.05, size=producao.shape)
    producao = producao * np.clip(ruido, 0.85, 1.15)
    producao = np.maximum(producao, 0)  # nunca negativo

    return producao


def energia_diaria_estimada_kwh(
    potencia_instalada_kwp: float,
    estacao: str = "verao",
) -> float:
    """Energia esperada num dia típico (kWh), sem perdas por nebulosidade."""
    hsp = (config.HORAS_SOL_PICO_VERAO if estacao == "verao"
           else config.HORAS_SOL_PICO_INVERNO)
    pr  = config.PERFORMANCE_RATIO * config.EFICIENCIA_INVERSOR
    return potencia_instalada_kwp * hsp * pr


if __name__ == "__main__":
    # Smoke test
    for est in ["verao", "inverno"]:
        curva = gerar_curva_solar_diaria(30.0, estacao=est)
        energia = curva.sum() * (config.PASSO_TEMPO_MIN / 60.0)
        print(f"[{est:8s}] pico={curva.max():.2f} kW | "
              f"energia diaria={energia:.2f} kWh")
