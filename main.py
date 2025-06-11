from flask import Flask, render_template
import requests
import logging
from time import sleep

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Список резервных API для цитат
QUOTE_APIS = [
    "https://api.quotable.io/random",
    "https://zenquotes.io/api/random",
    "https://quotes.rest/qod.json"
]


# Функция для получения случайной цитаты с резервными API
def get_random_quote(max_retries=3):
    for attempt in range(max_retries):
        for api_url in QUOTE_APIS:
            try:
                logger.info(f"Попытка {attempt + 1}: запрос к {api_url}")
                response = requests.get(api_url, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    # Обработка разных форматов ответов от API
                    if "quotable.io" in api_url:
                        return {
                            'content': data['content'],
                            'author': data['author'],
                            'source': 'Quotable.io'
                        }
                    elif "zenquotes.io" in api_url:
                        return {
                            'content': data[0]['q'],
                            'author': data[0]['a'],
                            'source': 'ZenQuotes.io'
                        }
                    elif "quotes.rest" in api_url:
                        return {
                            'content': data['contents']['quotes'][0]['quote'],
                            'author': data['contents']['quotes'][0]['author'],
                            'source': 'They Said So'
                        }

            except (requests.exceptions.RequestException, KeyError) as e:
                logger.error(f"Ошибка при запросе к {api_url}: {str(e)}")
                continue

        if attempt < max_retries - 1:
            sleep(1)  # Задержка перед повторной попыткой

    # Если все попытки исчерпаны
    return {
        'content': "Не удалось получить цитату. Пожалуйста, попробуйте позже.",
        'author': "Система",
        'source': 'Локальное сообщение'
    }


@app.route('/')
def index():
    quote = get_random_quote()
    return render_template('quote.html', quote=quote)


if __name__ == '__main__':
    app.run(debug=True)