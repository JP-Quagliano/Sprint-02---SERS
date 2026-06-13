"""
metrics.py — Cálculo de KPIs de sustentabilidade e financeiro
==============================================================

Pega o resultado de uma simulação (ResultadoDespacho) e calcula:

    1. Indicadores de eficiência energética
       - taxa de autossuficiência (% da demanda atendida por fontes próprias)
       - taxa de autoconsumo solar (% do solar gerado que foi efetivamente usado)
       - taxa de aproveitamento da bateria

    2. Indicadores de sustentabilidade
       - emissões evitadas (kgCO2eq) usando fator do SIN
       - equivalência em árvores plantadas (1 árvore absorve ~22 kgCO2/ano)
       - equivalência em km não rodados de veículo a combustão

    3. Indicadores financeiros
       - custo da energia consumida (usando tarifa horária dinâmica)
       - economia vs cenário baseline
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from . import config
from .dispatcher import ResultadoDespacho


@dataclass
class KPIs:
    """Conjunto de indicadores resumidos para exibição no dashboard."""
    # Sustentabilidade
    autossuficiencia_pct:  float       # 0–100
    autoconsumo_solar_pct: float       # 0–100
    co2_evitado_kg:        float
    arvores_equivalentes:  float       # 1 árvore ≈ 22 kgCO2/ano
    km_evitados_combustao: float       # 1 L gasolina ≈ 2.31 kg CO2; 1 L ≈ 10 km

    # Financeiro
    custo_rede_rs:         float       # quanto pagou de rede
    economia_vs_baseline_rs: float     # quanto economizou vs cenário sem SmartHub
    custo_unitario_medio_rs_kwh: float

    # Energético
    energia_total_demandada_kwh: float
    energia_solar_gerada_kwh:    float
    energia_rede_kwh:            float


def _tarifa_horaria(hora: int) -> float:
    """Retorna a tarifa em R$/kWh para uma hora específica (0-23)."""
    base = config.TARIFA_REDE_BASE_RS_POR_KWH
    if 18 <= hora <= 20:
        return base * config.MULT_TARIFA_PONTA
    if hora == 17 or hora == 21:
        return base * config.MULT_TARIFA_INTERMEDIARIA
    if hora >= 22 or hora <= 5:
        return base * config.MULT_TARIFA_FORA_PONTA
    return base


def calcular_custo_rede(resultado: ResultadoDespacho) -> float:
    """Calcula o custo total em R$ aplicando tarifa horária dinâmica."""
    dt_h = config.PASSO_TEMPO_MIN / 60.0
    custo = 0.0
    for i, kw in enumerate(resultado.rede_para_carga):
        hora_do_dia = int((i * config.PASSO_TEMPO_MIN) / 60) % 24
        energia_kwh = kw * dt_h
        custo += energia_kwh * _tarifa_horaria(hora_do_dia)
    return custo


def calcular_kpis(
    smart: ResultadoDespacho,
    baseline: ResultadoDespacho,
) -> KPIs:
    """
    Compara o cenário com SmartHub vs baseline e produz os KPIs.
    """
    # ---------- AUTOSSUFICIENCIA E AUTOCONSUMO ----------
    energia_de_fontes_proprias = (
        smart.energia_solar_usada + smart.energia_bateria_usada
    )

    autossuficiencia = (
        100.0 * energia_de_fontes_proprias / smart.energia_demandada
        if smart.energia_demandada > 0 else 0.0
    )
    autoconsumo = (
        100.0 * smart.energia_solar_usada / smart.energia_solar_total
        if smart.energia_solar_total > 0 else 0.0
    )

    # ---------- EMISSÕES EVITADAS ----------
    # Energia da rede que NÃO foi consumida graças ao SmartHub
    energia_evitada_kwh = baseline.energia_rede - smart.energia_rede
    co2_evitado_kg = energia_evitada_kwh * config.FATOR_EMISSAO_SIN_KG_POR_KWH

    arvores = co2_evitado_kg / 22.0          # 1 árvore ≈ 22 kgCO2/ano
    # Gasolina: 1 L emite ~2.31 kgCO2; rendimento típico ~10 km/L → 4.33 km/kgCO2
    km_evitados = co2_evitado_kg * 4.33

    # ---------- CUSTOS ----------
    custo_smart    = calcular_custo_rede(smart)
    custo_baseline = calcular_custo_rede(baseline)
    economia       = custo_baseline - custo_smart

    custo_unit = (
        custo_smart / smart.energia_demandada
        if smart.energia_demandada > 0 else 0.0
    )

    return KPIs(
        autossuficiencia_pct=autossuficiencia,
        autoconsumo_solar_pct=autoconsumo,
        co2_evitado_kg=co2_evitado_kg,
        arvores_equivalentes=arvores,
        km_evitados_combustao=km_evitados,
        custo_rede_rs=custo_smart,
        economia_vs_baseline_rs=economia,
        custo_unitario_medio_rs_kwh=custo_unit,
        energia_total_demandada_kwh=smart.energia_demandada,
        energia_solar_gerada_kwh=smart.energia_solar_total,
        energia_rede_kwh=smart.energia_rede,
    )


def projetar_anual(kpis_diarios: KPIs) -> dict:
    """
    Projeta os KPIs diários para uma operação anual (365 dias).
    Usado para mostrar impacto cumulativo no dashboard.
    """
    return {
        "co2_evitado_t":   kpis_diarios.co2_evitado_kg * 365 / 1000.0,
        "arvores":         kpis_diarios.arvores_equivalentes * 365,
        "km_evitados":     kpis_diarios.km_evitados_combustao * 365,
        "economia_rs":     kpis_diarios.economia_vs_baseline_rs * 365,
    }


if __name__ == "__main__":
    from . import pv_generation, ev_demand, dispatcher
    np.random.seed(42)
    solar = pv_generation.gerar_curva_solar_diaria(30.0, "verao")
    demanda = ev_demand.gerar_curva_demanda_diaria(8)
    smart = dispatcher.simular_despacho(solar, demanda, 30.0)
    base = dispatcher.simular_baseline_sem_smarthub(demanda)
    kpis = calcular_kpis(smart, base)
    print(f"Autossuficiência:    {kpis.autossuficiencia_pct:.1f}%")
    print(f"CO2 evitado/dia:     {kpis.co2_evitado_kg:.2f} kg")
    print(f"Economia/dia:        R$ {kpis.economia_vs_baseline_rs:.2f}")
    anual = projetar_anual(kpis)
    print(f"\nProjeção anual:")
    print(f"  CO2 evitado:     {anual['co2_evitado_t']:.2f} t")
    print(f"  Árvores equiv.:  {anual['arvores']:.0f}")
    print(f"  Economia:        R$ {anual['economia_rs']:,.2f}")
