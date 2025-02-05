from config import TICKERS
from utils import get_token
from analysis import analyze_stock
from ml_forecast import predict_stock_price
from chart import send_stock_chart
from trend_classifier import classify_trend
import telebot
import logging
import time
import threading

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

    # Отправляем начальное сообщение о начале процесса
    progress_message = bot.send_message(chat_id, "🔄 Начинаю анализ данных для тикера... Пожалуйста, подождите.")

    # Создаем сообщение для отсчёта времени
    countdown_message = bot.send_message(chat_id, "⏱️ Отсчёт времени начат...")

    # Засекаем время начала работы
    start_time = time.time()

    # Инициализация счётчика шагов
    step_counter = 1

    # Флаг для остановки отсчёта времени
    keep_countdown = True

    def update_countdown():
        # Функция для обновления отсчёта времени
        while keep_countdown:
            elapsed_time = time.time() - start_time
            bot.edit_message_text(f"⏱️ Отсчёт времени: {elapsed_time:.2f} секунд", chat_id, countdown_message.message_id)
            time.sleep(1)

    # Запускаем отдельный поток для обновления отсчёта времени
    countdown_thread = threading.Thread(target=update_countdown)
    countdown_thread.daemon = True
    countdown_thread.start()

    try:
        # Шаг 1: Анализ данных
        step_start_time = time.time()  # Засекаем время начала шага
        bot.edit_message_text(f"🔄 *Шаг {step_counter}/4:* Анализ данных... Это может занять несколько секунд.",
                              chat_id, progress_message.message_id)
        step_counter += 1

        data = analyze_stock(selected_ticker)
        last_price = float(data["Close"].iloc[-1])
        prev_price = float(data["Close"].iloc[-2])  # Цена предыдущего дня для вычисления изменения
        price_change = last_price - prev_price
        change_percent = (price_change / prev_price) * 100

        # Вычисляем прошедшее время для шага 1
        elapsed_time = time.time() - step_start_time
        bot.edit_message_text(f"🔄 *Шаг {step_counter-1}/4:* Анализ данных завершён. Прошло {elapsed_time:.2f} секунд.",
                              chat_id, progress_message.message_id)

        # Шаг 2: Прогноз
        step_start_time = time.time()  # Засекаем время начала шага
        bot.edit_message_text(f"🔮 *Шаг {step_counter}/4:* Прогнозируем цену на завтра...",
                              chat_id, progress_message.message_id)
        step_counter += 1

        predicted_price = predict_stock_price(selected_ticker)

        # Вычисляем прошедшее время для шага 2
        elapsed_time = time.time() - step_start_time
        bot.edit_message_text(f"🔮 *Шаг {step_counter-1}/4:* Прогноз завершён. Прошло {elapsed_time:.2f} секунд.",
                              chat_id, progress_message.message_id)

        # Шаг 3: Классификация тренда
        step_start_time = time.time()  # Засекаем время начала шага
        bot.edit_message_text(f"📊 *Шаг {step_counter}/4:* Классифицируем тренд...",
                              chat_id, progress_message.message_id)
        step_counter += 1

        trend = classify_trend(selected_ticker)

        # Вычисляем прошедшее время для шага 3
        elapsed_time = time.time() - step_start_time
        bot.edit_message_text(f"📊 *Шаг {step_counter-1}/4:* Классификация тренда завершена. Прошло {elapsed_time:.2f} секунд.",
                              chat_id, progress_message.message_id)

        # Шаг 4: Формирование финального сообщения
        signal_text = (
            f"\n📈 *Цена*: *${last_price:.2f}*\n"
            f"🔺 *Изменение за день*: *{price_change:+.2f}* (+{change_percent:+.2f}%)\n"
            f"🔮 *Прогноз на завтра*: *${predicted_price:.2f}*\n"
            f"📊 *Тренд*: {trend}\n"
        )

        # Останавливаем отсчёт времени
        keep_countdown = False
        # Вычисляем общее прошедшее время с начала работы
        total_elapsed_time = time.time() - start_time
        signal_text += f"\n⏱️ Общее время выполнения: {total_elapsed_time:.2f} секунд."
        # Удаляем сообщение отсчёта времени
        bot.delete_message(chat_id, countdown_message.message_id)
        # Обновляем финальное сообщение с результатами
        bot.edit_message_text(f"✅ *Завершено!* Все шаги выполнены.\n{signal_text}",
                              chat_id, progress_message.message_id, parse_mode='Markdown')

        # Отправка графика
        send_stock_chart(selected_ticker, chat_id)

    except Exception as e:
        logging.exception("Ошибка при обработке запроса")
        bot.edit_message_text(f'❌ Ошибка: {str(e)}', chat_id, progress_message.message_id)

        # Останавливаем отсчёт времени в случае ошибки
        keep_countdown = False


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception("Ошибка в основном цикле polling")
