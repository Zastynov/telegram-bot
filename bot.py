import pandas as pd
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 токен берём из Render
TOKEN = os.getenv("TOKEN")

GROUP_NAME = "1МРОА 05-25"
USER_FILE = "user.txt"


# 📂 найти Excel файл
def find_latest_file():
    files = [f for f in os.listdir() if f.endswith(".xlsx")]
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]


# 👤 сохранить имя
def save_name(user_id, name):
    data = {}

    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                uid, uname = line.strip().split("|")
                data[uid] = uname

    data[str(user_id)] = name

    with open(USER_FILE, "w", encoding="utf-8") as f:
        for uid, uname in data.items():
            f.write(f"{uid}|{uname}\n")


# 👤 загрузить имя
def load_name(user_id):
    if not os.path.exists(USER_FILE):
        return None

    with open(USER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            uid, uname = line.strip().split("|")
            if uid == str(user_id):
                return uname

    return None


# 📅 получить расписание
def get_schedule(day_offset=1):
    file = find_latest_file()

    if not file:
        return "❌ Файл расписания не найден"

    try:
        df = pd.read_excel(file)
    except:
        return "❌ Ошибка чтения файла"

    target_day = (datetime.now() + timedelta(days=day_offset)).strftime("%d.%m")

    # ищем колонку с датой
    date_column = None
    for col in df.columns:
        if "дата" in str(col).lower():
            date_column = col
            break

    if not date_column:
        return "❌ Не найдена колонка с датой"

    df = df[df[date_column].astype(str).str.contains(target_day, na=False)]

    # фильтр по группе
    df = df[df.apply(lambda row: row.astype(str).str.contains(GROUP_NAME).any(), axis=1)]

    if df.empty:
        return "🎉 Пар нет!"

    text = ""
    for i, row in enumerate(df.values, 1):
        text += f"{i}️⃣ {' | '.join(map(str, row))}\n"

    return text


# 🚀 команды

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = load_name(user_id)

    if name:
        await update.message.reply_text(f"С возвращением, {name} 👋\n\nКоманды:\n/today\n/tomorrow")
    else:
        await update.message.reply_text("Привет! 👋\nНапиши своё имя:")


# 👤 ввод имени
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = load_name(user_id)

    if not name:
        user_name = update.message.text.strip()
        save_name(user_id, user_name)
        await update.message.reply_text(f"Окей, {user_name} 😎\nТеперь используй /today или /tomorrow")


# 📅 сегодня
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = load_name(user_id) or "друг"

    schedule = get_schedule(0)

    await update.message.reply_text(f"Привет, {name} 👋\n\n📅 Сегодня:\n{schedule}")


# 📅 завтра
async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = load_name(user_id) or "друг"

    schedule = get_schedule(1)

    await update.message.reply_text(f"Привет, {name} 👋\n\n📅 Завтра:\n{schedule}")


# ▶️ запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("tomorrow", tomorrow))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))

app.run_polling()
