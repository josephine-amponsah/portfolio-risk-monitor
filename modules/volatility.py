import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import yfinance as yf


def implied_vol(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    
    return data

def EWMA():
    pass
    
    
def GARCH():
    pass

def realized_volatility(prices, window=30):
    log_returns = np.log(prices / prices.shift(1)).dropna()
    realized_vol = log_returns.rolling(window=window).std() * np.sqrt(252)  # Annualized volatility
    return realized_vol