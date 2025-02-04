import yfinance as yf
import matplotlib.pyplot as plt
import telebot
import tempfile
from utils import get_token

bot = telebot.TeleBot(get_token())

def send_stock_chart(ticker, chat_id):
    """Создает и отправляет график цены акции за последние 24 часа."""
    data = yf.download(ticker, period="1d", interval="1h")
    if data.empty:
        bot.send_message(chat_id, f'Не удалось получить данные для построения графика {ticker}.')
        return

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label=f'{ticker} Price', color='blue')
    plt.title(f'{ticker} - Динамика за 24 часа')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Сохраняем график во временный файл
    with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
        plt.savefig(tmpfile.name)
        plt.close()
        tmpfile.seek(0)
        bot.send_photo(chat_id, tmpfile)
