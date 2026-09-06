import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template

from modules.risk_monitor import build_var_distribution

load_figure_template("cyborg")

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Risk Monitoring Dashboard"

ALL_TICKERS = [
    "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA", "JPM",
    "V", "XOM", "WMT", "SPY", "QQQ", "IWM", "GLD", "BTC-USD"
]
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META"]

app.layout = html.Div(
    [
        html.H2(
            "Risk Monitoring Dashboard",
            style={"marginBottom": "16px", "color": "#f1f5f9", "fontWeight": "600"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Tickers", style={"color": "#dfe7f3"}),
                        dcc.Dropdown(
                            id="ticker-select",
                            options=[{"label": t, "value": t} for t in ALL_TICKERS],
                            value=DEFAULT_TICKERS,
                            multi=True,
                            clearable=False,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "220px"},
                ),
                html.Div(
                    [
                        html.Label("Portfolio value", style={"color": "#dfe7f3"}),
                        dcc.Input(
                            id="portfolio-value",
                            type="number",
                            value=100000,
                            min=0,
                            step=1000,
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "180px"},
                ),
                html.Div(
                    [
                        html.Label("Date range", style={"color": "#dfe7f3"}),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date="2024-01-01",
                            end_date="2025-01-01",
                            display_format="YYYY-MM-DD",
                            clearable=True,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "260px"},
                ),
                html.Div(
                    [
                        html.Label("Weights", style={"color": "#dfe7f3"}),
                        dcc.Input(
                            id="ticker-weights",
                            type="text",
                            value="AAPL:0.35, MSFT:0.25, GOOG:0.20, AMZN:0.20",
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "260px"},
                ),
                html.Div(
                    [
                        html.Label("VaR horizon (days)", style={"color": "#dfe7f3"}),
                        dcc.Input(
                            id="horizon",
                            type="number",
                            value=10,
                            min=1,
                            step=1,
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "180px"},
                ),
            ],
            style={
                "display": "flex",
                "gap": "16px",
                "flexWrap": "wrap",
                "marginBottom": "20px",
                "padding": "18px",
                "backgroundColor": "#111827",
                "borderRadius": "12px",
                "boxShadow": "0 8px 20px rgba(0,0,0,0.2)",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Summary", style={"color": "#f1f5f9", "marginBottom": "12px"}),
                        html.Div(id="var-summary", style={"lineHeight": "1.8", "color": "#dfe7f3"}),
                    ],
                    style={
                        "background": "#0f172a",
                        "padding": "16px",
                        "borderRadius": "10px",
                        "marginBottom": "20px",
                        "border": "1px solid #263448",
                    },
                ),
                dcc.Graph(
                    id="var-graph",
                    config={"displayModeBar": False},
                    style={"backgroundColor": "#0f172a"},
                ),
            ]
        ),
    ],
    style={
        "maxWidth": "1100px",
        "margin": "auto",
        "padding": "24px",
        "fontFamily": "Arial",
        "backgroundColor": "#020817",
        "minHeight": "100vh",
        "color": "#f8fafc",
    },
)


@app.callback(
    Output("var-summary", "children"),
    Output("var-graph", "figure"),
    Input("ticker-select", "value"),
    Input("portfolio-value", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("ticker-weights", "value"),
    Input("horizon", "value"),
)
def update_dashboard(tickers, portfolio_value, start_date, end_date, weights_value, horizon):
    if not tickers or portfolio_value in (None, "") or not start_date or not end_date or horizon in (None, ""):
        return "Select tickers, dates, portfolio value, and horizon.", go.Figure()

    try:
        horizon = int(horizon)
        portfolio_value = float(portfolio_value)
        daily_mean, daily_vol, var_value, fig = build_var_distribution(
            portfolio_value=portfolio_value,
            tickers=list(tickers),
            start_date=start_date,
            end_date=end_date,
            horizon=horizon,
            weights_value=weights_value,
        )
    except Exception as exc:
        return f"Could not compute VaR: {exc}", go.Figure()

    summary = html.Div(
        [
            html.Div(f"Portfolio value: ${portfolio_value:,.0f}"),
            html.Div(f"Expected daily return: {daily_mean * 100:.4f}%"),
            html.Div(f"Daily volatility: {daily_vol * 100:.4f}%"),
            html.Div(f"VaR at 95% confidence over {horizon} days: ${var_value:,.0f}"),
        ]
    )

    return summary, fig


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8080, use_reloader=False)


