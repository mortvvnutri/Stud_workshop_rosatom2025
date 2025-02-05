import numpy as np
import yfinance as yf

def classify_trend(ticker):
    """Классифицирует тренд (бычий/медвежий) на основе последних 60 дней или доступных данных."""
    data = yf.download(ticker, period="6mo")['Close']
    if data.empty:
        return "Нет данных для классификации тренда."
    
    # Если данных меньше 60, используем весь доступный диапазон
    recent_data = data if len(data) < 60 else data[-60:]
    
    X = np.arange(len(recent_data)).reshape(-1, 1)
    y = recent_data.values.reshape(-1, 1)

    # Вычисляем наклон тренда
    slope = np.polyfit(X.flatten(), y.flatten(), 1)[0]

    # Порог для нейтрального тренда (можно настроить)
    if abs(slope) < 1e-6:
        return "Нейтральный тренд"
    elif slope > 0:
        return "📈 Бычий рынок (восходящий тренд)"
    else:
        return "📉 Медвежий рынок (нисходящий тренд)"
