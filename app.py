import streamlit as st

from charts.plotly_charts import (
    create_gex_chart
)

from engine.analysis import run_analysis


# ============================================================
# CABECERA
# ============================================================

st.title("Gamma Dashboard")


# ============================================================
# INPUTS
# ============================================================

ticker = st.text_input(
    "Ticker",
    value="SPY"
)

max_dte = st.slider(
    "DTE máximo",
    1,
    365,
    30
)


# ============================================================
# EJECUCIÓN
# ============================================================

if st.button("Analizar"):

    results = run_analysis(
        ticker,
        max_dte
    )

    # ========================================================
    # MÉTRICAS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Spot",
        round(results["spot"], 2)
    )

    col2.metric(
        "Call Wall",
        results["call_wall"]
    )

    col3.metric(
        "Put Wall",
        results["put_wall"]
    )

    col4.metric(
        "Top Net",
        results["top_net_strike"]
    )

    # ========================================================
    # DEBUG
    # ========================================================

    with st.expander("Debug"):

        st.write(results)

    # ========================================================
    # GRÁFICO
    # ========================================================

    st.plotly_chart(
        create_gex_chart(
            results["net_gex_by_strike"]
        ),
        width="stretch"
    )
