import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import Filters

from PIL import Image
import pytesseract

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚙️ مقداردهی اولیه Flask
app = Flask(__name__)

# 🧠 تنظیمات ربات
TOKEN = "8173513779:AAGOlPrH4t_X2IMQEbFTJkVfRu6bTf_aE0c"  # ← اینجا توکن خودت رو بذار
bot = Bot(token=TOKEN)

# اتصال Dispatcher به Flask
dispatcher = Dispatcher(bot, None, workers=0)

# ✅ دستور /start
def start(update, context):
    update.message.reply_text("سلام! 👋\nیه تصویر بفرست تا متنتو استخراج کنم 🖼️➡️🔤")

# ✅ هندلر عکس‌ها
def handle_photo(update, context):
    photo_file = update.message.photo[-1].get_file()
    file_path = f"{update.message.chat.id}_image.jpg"
    photo_file.download(file_path)

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='fas')  # برای OCR فارسی

        if text.strip():
            update.message.reply_text(f"✅ متن استخراج‌شده:\n\n{text}")
        else:
            update.message.reply_text("متنی در تصویر پیدا نشد ❌")

    except Exception as e:
        update.message.reply_text("خطایی رخ داد هنگام پردازش تصویر 😢")
        logging.error(f"Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ثبت هندلرها
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

# 🔁 وبهوک برای دریافت آپدیت‌ها
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# 🌐 روت اصلی برای تست
@app.route('/')
def home():
    return "ربات OCR تلگرام با Flask اجرا شده است ✅"

if __name__ == '__main__':
    app.run()
