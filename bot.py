import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

# Пример функции (потом заменим на твою логику с Mail.ru)
def get_schedule():
    return "📚 Завтра:\n1) Математика\n2) Физика\n3) Информатика"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /schedule")

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_schedule()
    await update.message.reply_text(text)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("schedule", schedule))

print("Бот запущен...")
app.run_polling() 
