import streamlit as st

# ============================================================
# IMPORTS
# ============================================================

# Gráfico principal
from charts.plotly_charts import (
    create_gex_chart
)

# Motor de análisis
from engine.analysis import run_analysis


# ============================================================
# CABECERA
# ============================================================

st.title("Gamma Dashboard")


# ============================================================
# INPUTS DEL USUARIO
# ============================================================

# Ticker a analizar
ticker = st.text_input(
    "Ticker",
    value="SPY"
)

# Máximo DTE a considerar
max_dte = st.slider(
    "DTE máximo",
    1,
    365,
    30
)


# ============================================================
# BOTÓN DE EJECUCIÓN
# ============================================================

if st.button("Analizar"):

    # Ejecuta el motor principal
    results = run_analysis(
        ticker,
        max_dte
    )

    # ========================================================
    # MÉTRICAS PRINCIPALES
    # ========================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Spot",
        round(results["spot"], 2)
    )

    col2.metric(
        "Top Call",
        results["top_call_strike"]
    )

    col3.metric(
        "Top Net",
        results["top_net_strike"]
    )

    # ========================================================
    # RESULTADOS CRUDOS (TEMPORAL)
    # ========================================================

    st.write(results)

    # ========================================================
    # GRÁFICO GEX
    # ========================================================

    st.plotly_chart(
        create_gex_chart(
            results["net_gex_by_strike"]
        ),
        width="stretch"
    )
