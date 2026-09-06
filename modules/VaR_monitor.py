import pandas as pd
import numpy as np
import scipy.stats as stats
import yfinance as yf
import matplotlib.pyplot as plt


def portfolio_data(tickers,start_date, end_date):
    """
    Calculate the portfolio returns based on the given tickers.

    Parameters:
    tickers (list): List of stock tickers.
    start_date (str): Start date for historical data in 'YYYY-MM-DD' format.
    end_date (str): End date for historical data in 'YYYY-MM-DD' format.

    Returns:
    pd.Series: Portfolio returns as a pandas Series.
    """
    # Fetch historical data for the given tickers
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    # using log returns instead of percentage change due additivity property of log returns
    log_returns = np.log(data / data.shift(1)).dropna()

    return log_returns

def portfolio_norms(log_returns, weights):
    cov = np.cov(log_returns, rowvar=False)
    variance  = weights.T @ cov @ weights
    std_dev = np.sqrt(variance)
    expected_return = np.sum(log_returns.mean() * weights)
    return cov, std_dev, expected_return

def scenarios(portfolio_value, expected_return, std_dev, horizon):
    z_score = np.random.normal(0,1)
    gains = portfolio_value * (expected_return * horizon + std_dev * np.sqrt(horizon) * z_score)
    return gains

def monte_carlo_simulation(log_returns, weights, num_simulations):
    sims = []
    for i in range(num_simulations):
        cov, std_dev, expected_return = portfolio_norms(log_returns, weights)
        simulated_gains = scenarios(1, expected_return, std_dev, 1)
        sims.append(simulated_gains)
    return sims

def var_cov(portfolio_value, log_returns, weights, confidence_level):
    cov, std_dev, expected_return = portfolio_norms(log_returns, weights)
    z_score = stats.norm.ppf(1 - confidence_level)
    var = portfolio_value * (expected_return + z_score * std_dev)
    return var

def historical_simulation(portfolio_value, log_returns, weights, confidence_level):
    portfolio_returns = log_returns @ weights
    var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    return portfolio_value * var