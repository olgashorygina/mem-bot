import json
import random
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Загружаем базу мемов из очищенного JSON-файла
MEM_DB_PATH = 'mems_database_cleaned.json'


def load_mem_db(path: str = MEM_DB_PATH) -> list:
    """Читает базу мемов из JSON-файла и возвращает список записей."""
    with open(path, encoding='utf-8') as f:
        return json.load(f)

MEM_DB = load_mem_db()


def meme_handler(update: Update, context: CallbackContext) -> None:
    """Обрабатывает текстовые сообщения: ищет мем по описанию, затем по тегам и отправляет результат."""
    query = update.message.text.lower().strip()

    # 1) поиск по описанию
    matches = [m for m in MEM_DB if query in m.get('description', '').lower()]

    # 2) если ничего не найдено — поиск по тегам
    if not matches:
        matches = [m for m in MEM_DB
                   if any(query in tag.lower() for tag in m.get('tags', []))]

    # 3) если всё ещё пусто — ответ с извинениями
    if not matches:
        update.message.reply_text("Мемов по такому запросу не нашлось 😔")
        return

    # 4) случайный выбор одного мемa
    meme = random.choice(matches)
    desc = meme.get('description', '').strip()
    file_name = meme.get('file_name', '').strip()

    # формируем ответ: описание + имя файла
    reply = desc
    if file_name:
        reply += f"\n{file_name}"

    update.message.reply_text(reply)


def main() -> None:
    """Запускает бота с указанным токеном."""
    # Вставьте сюда токен вашего Telegram-бота
    token = '7842347269:AAFsEEL14YCuTTHaU1cgxfxUgeA1qLgWXAM'

    # Инициализация и запуск
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, meme_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
