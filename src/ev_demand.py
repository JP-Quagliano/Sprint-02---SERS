"""
ev_demand.py — Modelagem da demanda de recarga elétrica
========================================================

Gera curvas realistas de demanda de eletropostos comerciais (linha HCA G2)
ao longo de 24 horas. A demanda agregada é uma soma de gaussianas
posicionadas nos horários típicos de uso, conforme estudos de adoção
brasileira de veículos elétricos (ABVE 2024).

Cada sessão simulada é representada pelo carregador que a atende:
    - GW7K-HCA-20   (7 kW)  — vagas de longa permanência
    - GW11K-HCA-20  (11 kW) — vagas mistas
    - GW22K-HCA-20  (22 kW) — vagas de fluxo rápido

A escolha do modelo segue uma distribuição típica de estação comercial:
60% GW7K + 25% GW11K + 15% GW22K (consultoria ABVE para shoppings).
"""

from __future__ import annotations
import numpy as np
from . import config


def _gaussiana(horas: np.ndarray, centro: float, largura: float) -> np.ndarray:
    """Curva gaussiana centrada em `centro` com desvio `largura`."""
    return np.exp(-0.5 * ((horas - centro) / largura) ** 2)


def gerar_curva_demanda_diaria(
    n_carregadores: int = 8,
    fator_ocupacao: float = 0.55,
) -> np.ndarray:
    """
    Gera o vetor de demanda agregada (kW) dos eletropostos ao longo de 24h.

    Parâmetros:
        n_carregadores: quantidade total de pontos de recarga na estação
        fator_ocupacao: 0.0 a 1.0 — quão lotada a estação fica no pico

    Retorna:
        np.ndarray de tamanho PASSOS_POR_DIA com potência total em kW
    """
    horas = np.arange(0, 24, config.PASSO_TEMPO_MIN / 60.0)
    demanda = np.zeros_like(horas)

    # Soma das gaussianas de cada pico característico
    for centro, intensidade, largura in config.PERFIL_DEMANDA_COMERCIAL:
        demanda += intensidade * _gaussiana(horas, centro, largura)

    # Aplica janela operacional do estabelecimento (sem demanda fora dela)
    fechado = (horas < config.HORA_ABERTURA) | (horas > config.HORA_FECHAMENTO)
    demanda[fechado] *= 0.05  # 5% residual (carga noturna ocasional de frota)

    # Normaliza o pico para representar a capacidade máxima utilizada
    if demanda.max() > 0:
        demanda = demanda / demanda.max()

    # Estimativa de potência simultânea no pico:
    # mix típico: 60% GW7K + 25% GW11K + 15% GW22K → ~9.6 kW médio
    potencia_media_carregador_kw = (
        0.60 * config.POTENCIA_GW7K_KW
        + 0.25 * config.POTENCIA_GW11K_KW
        + 0.15 * config.POTENCIA_GW22K_KW
    )
    capacidade_total_kw = n_carregadores * potencia_media_carregador_kw
    pico_real_kw = capacidade_total_kw * fator_ocupacao

    demanda = demanda * pico_real_kw

    # Adiciona ruído estocástico de +/- 8% (chegadas aleatórias)
    ruido = np.random.normal(loc=1.0, scale=0.08, size=demanda.shape)
    demanda = demanda * np.clip(ruido, 0.85, 1.15)
    demanda = np.maximum(demanda, 0)

    return demanda


def energia_diaria_demandada_kwh(curva_demanda: np.ndarray) -> float:
    """Energia total demandada num dia (kWh) — integral simples da curva."""
    return float(curva_demanda.sum() * (config.PASSO_TEMPO_MIN / 60.0))


if __name__ == "__main__":
    curva = gerar_curva_demanda_diaria(n_carregadores=8, fator_ocupacao=0.55)
    print(f"Pico de demanda: {curva.max():.2f} kW")
    print(f"Demanda media:   {curva.mean():.2f} kW")
    print(f"Energia diaria:  {energia_diaria_demandada_kwh(curva):.2f} kWh")
