import plotly.express as px


def create_gex_chart(
    net_gex_by_strike,
    spot,
    call_wall,
    put_wall,
    gamma_flip,
    lower_expected,
    upper_expected
):

    fig = px.bar(
        net_gex_by_strike,
        x="strike",
        y="gex",
        title="Net GEX by Strike"
    )

    fig.add_vline(
        x=spot,
        line_dash="dash"
    )

    if call_wall:

        fig.add_vline(
            x=call_wall,
            line_color="green"
        )

    if put_wall:

        fig.add_vline(
            x=put_wall,
            line_color="red"
        )

    if gamma_flip:

        fig.add_vline(
            x=gamma_flip,
            line_color="white"
        )

    fig.add_vline(
        x=lower_expected,
        line_dash="dot"
    )

    fig.add_vline(
        x=upper_expected,
        line_dash="dot"
    )

    return fig
