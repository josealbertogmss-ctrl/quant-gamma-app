import streamlit as st

from engine.analysis import (
    run_analysis
)

from engine.snapshot import (
    get_available_expirations,
    update_snapshot,
    snapshot_exists
)

from charts.plotly_charts import (
    create_gex_chart
)


st.set_page_config(
    page_title="Gamma Dashboard",
    layout="wide"
)

st.title("Gamma Dashboard")

#
# TICKER
#

ticker = st.text_input(
    "Ticker",
    value="SPY"
).upper()

#
# CARGAR EXPIRACIONES
#

expirations = []

if ticker:

    try:

        expirations = (
            get_available_expirations(
                ticker
            )
        )

    except Exception as e:

        st.error(
            f"Error obteniendo expiraciones: {e}"
        )

#
# SELECTOR DE EXPIRACIÓN
#

selected_expiration = None

if len(expirations) > 0:

    selected_expiration = st.selectbox(
        "Expiración máxima",
        expirations
    )

#
# BOTÓN SNAPSHOT
#

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Actualizar datos"
    ):

        try:

            with st.spinner(
                "Descargando cadena completa..."
            ):

                update_snapshot(
                    ticker
                )

            st.success(
                "Snapshot actualizado"
            )

        except Exception as e:

            st.error(str(e))

with col2:

    if snapshot_exists(
        ticker
    ):

        st.success(
            "Snapshot disponible"
        )

    else:

        st.warning(
            "No existe snapshot"
        )

#
# DTE
#

max_dte = 30

if selected_expiration:

    try:

        from datetime import (
            datetime
        )

        exp_date = datetime.strptime(
            selected_expiration,
            "%Y-%m-%d"
        )

        max_dte = (
            exp_date
            - datetime.today()
        ).days

    except Exception:

        max_dte = 30

#
# ANALIZAR
#

results = None

if st.button(
    "Analizar"
):

    try:

        results = run_analysis(
            ticker,
            max_dte
        )

        st.session_state[
            "results"
        ] = results

    except Exception as e:

        st.error(str(e))

#
# RECUPERAR RESULTADOS
#

if "results" in st.session_state:

    results = st.session_state[
        "results"
    ]

    st.subheader(
        "Métricas"
    )

    col1, col2, col3, col4 = st.columns(4)

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
        "Top Net",
        results["top_net_strike"]
    )

    st.plotly_chart(
        create_gex_chart(
            results[
                "net_gex_by_strike"
            ]
        ),
        width="stretch"
    )

    with st.expander(
        "Debug"
    ):

        st.write(results)
