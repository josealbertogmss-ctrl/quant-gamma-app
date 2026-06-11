import streamlit as st

from charts.plotly_charts import (
    create_gex_chart
)

from engine.analysis import run_analysis


st.title("Gamma Dashboard")

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

if st.button("Analizar"):

    results = run_analysis(
        ticker,
        max_dte
    )

    st.write(results)

    st.plotly_chart(
        create_gex_chart(
            results["net_gex_by_strike"]
        ),
        width="stretch"
    )

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
