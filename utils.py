def get_token():
    """Читает Telegram API токен из файла."""
    try:
        with open("token.txt", "r") as file:
            token = file.read().strip()
            if not token:
                raise ValueError("Токен пустой.")
            return token
    except FileNotFoundError:
        raise FileNotFoundError("Файл token.txt не найден. Проверьте путь к файлу с токеном.")
