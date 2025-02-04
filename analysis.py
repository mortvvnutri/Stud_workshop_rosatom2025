import yfinance as yf
import pandas as pd
import numpy as np

def analyze_stock(ticker):
    """Загружает данные и рассчитывает индикаторы для тикера."""
    data = yf.download(ticker, period="1y")
    if data.empty:
        raise ValueError(f"Не удалось загрузить данные для тикера {ticker}.")

    # Скользящие средние
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

    # RSI (14)
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    # Защита от деления на ноль:
    rs = gain / loss.replace(0, np.nan)
    data['RSI_14'] = 100 - (100 / (1 + rs))
    data['RSI_14'] = data['RSI_14'].fillna(100)  # если loss==0, RSI считается равным 100

    # Полосы Боллинджера на основе 20-дневного SMA
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    std = data['Close'].rolling(window=20).std().squeeze()
    data['BB_Upper'] = data['SMA_20'] + (std * 2)
    data['BB_Lower'] = data['SMA_20'] - (std * 2)

    return data
