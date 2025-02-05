import yfinance as yf
import matplotlib.pyplot as plt
import telebot
import tempfile
from utils import get_token

bot = telebot.TeleBot(get_token())

import yfinance as yf
import matplotlib.pyplot as plt
import tempfile
from utils import get_token

bot = telebot.TeleBot(get_token())


def generate_stock_chart(ticker):
    """Создает график цены акции за последние 24 часа и сохраняет во временный файл."""
    data = yf.download(ticker, period="1d", interval="1h")
    if data.empty:
        raise ValueError(f'Не удалось получить данные для построения графика {ticker}.')

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label=f'{ticker} Price', color='blue')
    plt.title(f'{ticker} - Динамика за 24 часа')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Сохраняем график во временный файл и возвращаем путь к файлу
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.savefig(tmpfile.name)
        plt.close()
        return tmpfile.name  # Возвращаем путь к файлу

