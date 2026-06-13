"""
config.py — Constantes técnicas do simulador SmartHub Solar

Todos os parâmetros aqui são fundamentados em dados públicos brasileiros
(MCTI, ANEEL, NREL/PVGIS, GoodWe technical specs) para garantir que a
simulação seja tecnicamente defensável.
"""

# ============================================================================
# LOCALIZAÇÃO E CLIMA — São Paulo, SP (centro do mercado-alvo GoodWe Brasil)
# ============================================================================
LATITUDE = -23.55                          # graus (São Paulo capital)
HORAS_SOL_PICO_VERAO   = 5.5               # HSP típica jan-mar (NREL/PVGIS)
HORAS_SOL_PICO_INVERNO = 4.0               # HSP típica jun-ago (NREL/PVGIS)
NASCER_SOL_VERAO,  POR_SOL_VERAO   = 6.0,  19.0   # janelas solares (h)
NASCER_SOL_INVERNO, POR_SOL_INVERNO = 6.5, 17.5

# ============================================================================
# FATORES DE EMISSÃO E TARIFAS — fontes oficiais brasileiras
# ============================================================================
# Fator médio de emissão do SIN (Sistema Interligado Nacional), 2024.
# Fonte: MCTI — Ministério da Ciência, Tecnologia e Inovação,
# "Fatores médios de emissão de CO2 — Sistema Interligado Nacional".
FATOR_EMISSAO_SIN_KG_POR_KWH = 0.0385      # kgCO2eq/kWh (média 2024)

# Tarifa-base de energia comercial em SP (referência ENEL Distribuição,
# Grupo B3 - convencional, sem ICMS, valor médio 2024-2025).
TARIFA_REDE_BASE_RS_POR_KWH = 0.85         # R$/kWh

# Multiplicadores de tarifa branca (Res. ANEEL 733/2016)
MULT_TARIFA_PONTA          = 1.50          # 18h–20h
MULT_TARIFA_INTERMEDIARIA  = 1.20          # 17h e 21h
MULT_TARIFA_FORA_PONTA     = 0.70          # 22h–05h

# ============================================================================
# COMPONENTES DA INFRAESTRUTURA — linhas reais GoodWe
# ============================================================================
# Inversores fotovoltaicos (linha MS G2 trifásico — segmento comercial leve)
EFICIENCIA_INVERSOR        = 0.978         # 97.8% (GoodWe MS G2 datasheet)

# Perdas adicionais do sistema (cabos, sujeira, mismatch, temperatura)
# Performance Ratio típico para sistemas bem dimensionados no Brasil.
PERFORMANCE_RATIO          = 0.82          # 82% (NREL guideline para BR)

# Eficiência round-trip de baterias estacionárias (linha Lynx Home U)
EFICIENCIA_BATERIA         = 0.93          # 93% carga + descarga (Li-FePO4)
PROFUNDIDADE_DESCARGA_MAX  = 0.90          # DoD máxima para preservar ciclos

# Eletropostos da linha HCA G2 (mesma utilizada nas outras disciplinas)
POTENCIA_GW7K_KW   = 7.0
POTENCIA_GW11K_KW  = 11.0
POTENCIA_GW22K_KW  = 22.0

# ============================================================================
# PARÂMETROS DE SIMULAÇÃO
# ============================================================================
PASSO_TEMPO_MIN    = 15                    # granularidade da simulação (min)
PASSOS_POR_DIA     = 24 * 60 // PASSO_TEMPO_MIN  # 96 amostras/dia

# Janela operacional do estabelecimento comercial
HORA_ABERTURA      = 7
HORA_FECHAMENTO    = 22

# ============================================================================
# PERFIS DE DEMANDA — picos típicos de estação comercial
# ============================================================================
# Cada pico é uma gaussiana: (hora_centro, intensidade_relativa, largura_h)
PERFIL_DEMANDA_COMERCIAL = [
    (8.5,  0.7, 1.2),    # chegada matinal — visitantes/funcionários
    (12.5, 0.5, 1.0),    # horário de almoço — fluxo médio
    (15.0, 0.6, 1.5),    # tarde — uso constante
    (18.5, 1.0, 1.5),    # pico fim de tarde — frota retornando + saída
]
