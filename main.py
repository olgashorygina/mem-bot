import os
import json
import random
import logging
import speech_recognition as sr
from pydub import AudioSegment

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

# === Настройка логирования ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === Загрузка базы мемов ===
MEM_DB_PATH = 'mems_database_cleaned.json'

def load_mem_db(path: str = MEM_DB_PATH) -> list:
    with open(path, encoding='utf-8') as f:
        return json.load(f)

MEM_DB = load_mem_db()
REPEAT_KEYWORDS = ["ещё", "ещё один", "следующий", "дальше", "другой"]

# === Обработка текстовых сообщений ===
def meme_handler(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    print(f"👤 {user.username} ({user.first_name} {user.last_name}) — ID: {user.id}")

    query = update.message.text.strip().lower()

    if query in REPEAT_KEYWORDS:
        last_query = context.user_data.get("last_query")
        if not last_query:
            update.message.reply_text("Сначала отправь ключевое слово 🔑")
            return
        query = last_query
    else:
        context.user_data["last_query"] = query

    matches = [m for m in MEM_DB if query in m.get('description', '').lower()]
    if not matches:
        matches = [m for m in MEM_DB if any(query in tag.lower() for tag in m.get('tags', []))]

    if not matches:
        update.message.reply_text("Мемов по такому запросу не нашлось 😔")
        return

    chosen = random.choice(matches)
    file_name = chosen.get('file_name')
    photo_path = os.path.join('all_memes', file_name)

    try:
        with open(photo_path, 'rb') as photo:
            update.message.reply_photo(photo, caption=chosen.get('description', ''))
    except FileNotFoundError:
        update.message.reply_text(f"Не удалось найти файл {photo_path}")

# === Обработка голосовых сообщений ===
def voice_handler(update: Update, context: CallbackContext) -> None:
    file = update.message.voice.get_file()
    file.download("voice.ogg")
    sound = AudioSegment.from_ogg("voice.ogg")
    sound.export("voice.wav", format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("voice.wav") as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        update.message.text = text
        meme_handler(update, context)
    except Exception as e:
        update.message.reply_text("Не удалось распознать голос 😞")

# === Стартовое сообщение ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    print(f"🆕 Старт от {user.username} ({user.first_name} {user.last_name}) — ID: {user.id}")
    update.message.reply_text("Привет! Отправь ключевое слово или голосовое сообщение — и я подберу мем 🎯")

# === Основной запуск ===
def main():
    token = '7842347269:AAFsEEL14YCuTTHaU1cgxfxUgeA1qLgWXAM'
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, meme_handler))
    dp.add_handler(MessageHandler(Filters.voice, voice_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
