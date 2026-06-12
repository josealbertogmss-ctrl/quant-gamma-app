import streamlit as st
import pandas as pd

from engine.analysis import run_analysis

from charts.plotly_charts import (
    create_gex_chart
)

st.title(
    "Gamma Dashboard"
)

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

    st.session_state["results"] = results

if "results" in st.session_state:

    results = st.session_state["results"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Spot",
        round(
            results["spot"],
            2
        )
    )

    col2.metric(
        "Call Wall",
        results["call_wall"]
    )

    col3.metric(
        "Put Wall",
        results["put_wall"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gamma Flip",
        (
            round(
                results["gamma_flip"],
                2
            )
            if results["gamma_flip"]
            else "N/A"
        )
    )

    col2.metric(
        "Expected Move",
        round(
            results["expected_move"],
            2
        )
    )

    col3.metric(
        "IV ATM",
        round(
            results["selected_iv_atm"]
            * 100,
            2
        )
    )

    st.plotly_chart(
        create_gex_chart(
            results["net_gex_by_strike"],
            results["spot"],
            results["call_wall"],
            results["put_wall"],
            results["gamma_flip"],
            results["lower_expected"],
            results["upper_expected"]
        ),
        width="stretch"
    )

    st.subheader(
        "Top Call Walls"
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Strike":
                results["call_walls"]
            }
        ),
        width="stretch"
    )

    st.subheader(
        "Top Put Walls"
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Strike":
                results["put_walls"]
            }
        ),
        width="stretch"
    )

    with st.expander(
        "Debug"
    ):
        st.write(results)
