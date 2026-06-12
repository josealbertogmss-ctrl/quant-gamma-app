import streamlit as st

from engine.data import (
    get_expirations
)

from engine.analysis import (
    run_analysis
)

from charts.plotly_charts import (
    create_gex_chart
)

st.set_page_config(
    page_title="Quant Gamma",
    layout="wide"
)

st.title("Quant Gamma Dashboard")

ticker = st.text_input(
    "Ticker",
    value="SPY"
).upper()

#
# CARGAR EXPIRACIONES
#

if st.button("Cargar expiraciones"):

    try:

        expirations = get_expirations(
            ticker
        )

        st.session_state[
            "expirations"
        ] = expirations

    except Exception as e:

        st.error(
            f"Error cargando expiraciones: {e}"
        )

#
# SELECTOR DE EXPIRACIÓN
#

selected_expiration = None

if "expirations" in st.session_state:

    selected_expiration = st.selectbox(
        "Selecciona expiración",
        st.session_state["expirations"]
    )

#
# ANALIZAR
#

if (
    selected_expiration
    and
    st.button("Analizar")
):

    with st.spinner(
        "Calculando Gamma..."
    ):

        results = run_analysis(
            ticker,
            selected_expiration
        )

    st.session_state[
        "results"
    ] = results

#
# MOSTRAR RESULTADOS
#

if "results" in st.session_state:

    results = st.session_state[
        "results"
    ]

    col1, col2, col3, col4, col5 = st.columns(5)

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

    col4.metric(
        "Gamma Flip",
        results["gamma_flip"]
    )

    col5.metric(
        "Expected Move",
        round(
            results["expected_move"],
            2
        )
    )

    st.plotly_chart(
        create_gex_chart(
            results["net_gex_by_strike"]
        ),
        width="stretch"
    )

    with st.expander(
        "Debug"
    ):
        st.write(results)
