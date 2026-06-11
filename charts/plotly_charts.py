import plotly.express as px


def create_gex_chart(
    net_gex_by_strike
):

    fig = px.bar(
        net_gex_by_strike,
        x="strike",
        y="gex",
        title="Net GEX by Strike"
    )

    return fig
