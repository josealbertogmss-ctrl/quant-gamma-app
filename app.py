import streamlit as st

from engine.analysis import run_analysis

from charts.plotly_charts import (
    create_term_structure_chart,
    create_gex_chart,
    create_net_gex_chart,
)

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

    st.metric(
        "Spot",
        round(results["spot"],2)
    )

    st.metric(
        "Gamma Flip",
        round(results["flip_level"],2)
    )

    st.plotly_chart(
        create_term_structure_chart(results),
        use_container_width=True
    )

    st.plotly_chart(
        create_gex_chart(results),
        use_container_width=True
    )
