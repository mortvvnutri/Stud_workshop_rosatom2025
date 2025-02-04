from config import TICKERS
from utils import get_token
from analysis import analyze_stock
from ml_forecast import predict_stock_price
from chart import send_stock_chart
from trend_classifier import classify_trend
import telebot
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(get_token())

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [telebot.types.KeyboardButton(ticker) for ticker in TICKERS]
    keyboard.add(*buttons)
    bot.send_message(chat_id, 'Выберите тикер:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in TICKERS)
def select_ticker(message):
    chat_id = message.chat.id
    selected_ticker = message.text
    bot.send_message(chat_id, f'📊 Тикер {selected_ticker} выбран. Ожидайте анализ...')

    try:
        # Анализ данных
        data = analyze_stock(selected_ticker)
        last_price = float(data["Close"].iloc[-1])
        signal_text = f'📌 Анализ {selected_ticker}:\nПоследняя цена: {last_price:.2f}\n'
        bot.send_message(chat_id, signal_text)

        # Прогноз
        predicted_price = predict_stock_price(selected_ticker)
        bot.send_message(chat_id, f'🔮 Прогноз цены на завтра: ${predicted_price:.2f}')

        # Классификация тренда
        trend = classify_trend(selected_ticker)
        bot.send_message(chat_id, f'📊 {trend}')

        # Отправка графика
        send_stock_chart(selected_ticker, chat_id)
    except Exception as e:
        logging.exception("Ошибка при обработке запроса")
        bot.send_message(chat_id, f'Ошибка: {str(e)}')

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception("Ошибка в основном цикле polling")
