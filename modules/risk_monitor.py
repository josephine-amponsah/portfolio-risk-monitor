import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


def get_portfolio_prices(tickers, start_date, end_date):
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )

    if data.empty:
        raise ValueError("No data found for the selected tickers and date range.")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(1):
            prices = data.xs("Close", level=1, axis=1)
        elif "Adj Close" in data.columns.get_level_values(1):
            prices = data.xs("Adj Close", level=1, axis=1)
        else:
            prices = data.iloc[:, 0]
    else:
        if "Close" in data.columns:
            prices = data["Close"]
        elif "Adj Close" in data.columns:
            prices = data["Adj Close"]
        elif len(data.columns) == 1:
            prices = data.iloc[:, 0]
        else:
            prices = data

    if isinstance(prices, pd.DataFrame):
        prices = prices[[c for c in prices.columns if c in tickers] if set(tickers).issubset(set(prices.columns)) else prices.columns]

    return prices.dropna()


def parse_weights(tickers, weights_value):
    if weights_value in (None, ""):
        weights = np.ones(len(tickers)) / len(tickers)
        return weights

    if isinstance(weights_value, dict):
        values = weights_value
    else:
        values = {}
        cleaned = str(weights_value).replace(" ", "")
        for part in [p for p in cleaned.split(",") if p]:
            if ":" in part:
                key, val = part.split(":", 1)
                values[key.upper()] = float(val)

    weights = [values.get(str(t).upper(), 0) for t in tickers]
    weights = np.array(weights, dtype=float)

    if weights.size == 0 or np.sum(weights) == 0:
        weights = np.ones(len(tickers)) / len(tickers)
    else:
        weights = weights / weights.sum()

    return weights


def build_var_distribution(portfolio_value, tickers, start_date, end_date, horizon, weights_value=None, confidence=0.95, simulations=3000):
    prices = get_portfolio_prices(tickers, start_date, end_date)
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    returns = np.log(prices / prices.shift(1)).dropna()
    weights = parse_weights(list(prices.columns), weights_value)

    if isinstance(returns, pd.DataFrame):
        mean_vec = returns.mean()
        cov = returns.cov()
        daily_mean = float(mean_vec.dot(weights))
        daily_vol = float(np.sqrt(weights @ cov.to_numpy() @ weights))
    else:
        daily_mean = float(returns.mean() * weights[0])
        daily_vol = float(np.std(returns) * np.sqrt(weights[0] ** 2))

    z = np.random.normal(0, 1, size=simulations)
    pnl = portfolio_value * (daily_mean * horizon + daily_vol * np.sqrt(horizon) * z)
    losses = np.maximum(-pnl, 0)
    var_value = float(np.quantile(losses, confidence))

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=losses, nbinsx=40, name="Loss distribution", marker_color="#4bc0c0", opacity=0.8))
    fig.add_vline(x=var_value, line_color="#ff6b6b", line_dash="dash", annotation_text=f"VaR {confidence:.0%}")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101826",
        plot_bgcolor="#101826",
        font={"color": "#e5edf8"},
        title={"text": "Portfolio loss distribution", "x": 0.05},
        xaxis_title="Loss amount",
        yaxis_title="Frequency",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return daily_mean, daily_vol, var_value, fig
