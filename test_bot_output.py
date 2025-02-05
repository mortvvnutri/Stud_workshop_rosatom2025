import unittest
from unittest.mock import patch, MagicMock
from bot import select_ticker
import pandas as pd
import tensorflow as tf


class TestBotOutput(unittest.TestCase):

    @patch('telebot.TeleBot.send_message')  # Мокируем send_message
    @patch('telebot.TeleBot.edit_message_text')  # Мокируем edit_message_text
    @patch('telebot.TeleBot.delete_message')  # Мокируем delete_message
    @patch('time.sleep')  # Мокируем time.sleep
    @patch('yfinance.download')  # Мокируем yfinance.download
    @patch('ml_forecast.predict_stock_price')  # Мокируем функцию прогнозирования
    def test_message_format_and_timer(self, mock_predict, mock_yf, mock_sleep, mock_delete_message,
                                      mock_edit_message, mock_send_message):
        # Мокируем данные для yfinance
        mock_yf.return_value = pd.DataFrame({
            'Close': [150.24, 148.39, 149.00, 151.30]
        })

        # Мокируем функцию прогнозирования
        mock_predict.return_value = 152.40  # Предположим, что прогноз на завтра = 152.40

        # Мокируем данные
        chat_id = 12345
        selected_ticker = 'AAPL'
        last_price = 150.24
        price_change = 1.85
        change_percent = 1.25
        predicted_price = 152.40
        trend = "📈 Бычий рынок"

        # Ожидаемое сообщение
        expected_signal_text = (
            f"📊 *Анализ {selected_ticker}*:\n"
            f"📈 *Цена*: *${last_price:.2f}*\n"
            f"🔺 *Изменение за день*: +{change_percent:.2f}% (+{price_change:.2f}$)\n"
            f"🔮 *Прогноз на завтра*: ${predicted_price:.2f}\n"
            f"📊 *Тренд*: {trend}\n"
        )

        # Мокируем объект сообщения
        message = MagicMock()
        message.chat.id = chat_id
        message.text = selected_ticker
        message.message_id = 67890  # Устанавливаем уникальный ID сообщения

        # Отключаем GPU для тестов
        tf.config.set_visible_devices([], 'GPU')

        # Выполняем функцию select_ticker
        select_ticker(message)

        # Проверяем, что send_message был вызван с правильными параметрами
        # Мы ожидаем два вызова: один для начала анализа и один для отсчета времени
        mock_send_message.assert_any_call(chat_id,
                                          '🔄 Начинаю анализ данных для тикера... Пожалуйста, подождите.')
        mock_send_message.assert_any_call(chat_id, '⏱️ Отсчёт времени начат...')

        # Проверяем, что send_message был вызван с итоговым результатом
        mock_send_message.assert_any_call(chat_id, expected_signal_text, parse_mode='Markdown')

        # Проверяем, что edit_message_text был вызван для обновления текста прогресса
        mock_edit_message.assert_any_call(f"🔄 *Шаг 1/4:* Анализ данных... Это может занять несколько секунд.",
                                          chat_id, message.message_id)
        mock_edit_message.assert_any_call(f"🔄 *Шаг 2/4:* Прогнозируем цену на завтра...",
                                          chat_id, message.message_id)
        mock_edit_message.assert_any_call(f"🔄 *Шаг 3/4:* Классифицируем тренд...",
                                          chat_id, message.message_id)
        mock_edit_message.assert_any_call(f"✅ *Завершено!* Все шаги выполнены.\n{expected_signal_text}",
                                          chat_id, message.message_id, parse_mode='Markdown')

        # Проверяем, что delete_message был вызван для удаления сообщения с таймером
        mock_delete_message.assert_called_once_with(chat_id, message.message_id)

        # Проверяем, что таймер был остановлен после выполнения всех шагов
        mock_sleep.assert_called()  # Проверяем, что time.sleep был вызван, что подтверждает работу таймера

if __name__ == '__main__':
    unittest.main()

