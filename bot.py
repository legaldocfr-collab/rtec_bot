import random
import json
import time
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8769689539
ADMIN_USERNAME = "@oficiul3"

FREE_LIMIT = 5
DATA_FILE = "users_data.json"


# ================= LOAD / SAVE =================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


users_data = load_data()


# ================= GENERARE TICKET =================

def generate_ticket():
    return "000" + str(random.randint(100000, 999999))


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Scrie doar numarul de bord.\nExemplu:\n3957"
    )


# ================= HANDLE MESSAGE =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Introdu doar numarul de bord.")
        return

    user_id = str(update.effective_user.id)
    current_time = int(time.time())

    if user_id not in users_data:
        users_data[user_id] = {
            "used": 0,
            "credits": 0,
            "subscription": 0
        }

    user = users_data[user_id]

    # ===== VERIFICARE ACCES =====

    if int(user_id) == ADMIN_ID:
        pass

    elif user["subscription"] > current_time:
        pass

    elif user["credits"] > 0:
        user["credits"] -= 1
        save_data(users_data)

    elif user["used"] < FREE_LIMIT:
        user["used"] += 1
        save_data(users_data)

    else:
        await update.message.reply_text(
            "Pentru a continua utilizarea serviciului este necesara activarea contului.\n\n"
            "Tarife:\n"
            "• 3 lei / bon\n"
            "• 100 lei / luna\n\n"
            f"Contact: {ADMIN_USERNAME}"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"User a atins limita gratuita:\nID: {user_id}"
        )
        return

    # ===== GENERARE BON =====

    bord = text
    now = datetime.now()
    data_ora = now.strftime("%d.%m.%Y %H:%M")
    ticket_number = generate_ticket()

    bon_text = f"""IM RTEC

Bilet Nr MCT-{ticket_number}

{data_ora}

Pret 6 MDL

Bord {bord}"""

    await update.message.reply_text(bon_text)


# ================= ADMIN COMENZI =================

async def addcredit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Folosire: /addcredit user_id suma")
        return

    user_id = context.args[0]
    amount = int(context.args[1])

    if user_id not in users_data:
        users_data[user_id] = {"used": 0, "credits": 0, "subscription": 0}

    users_data[user_id]["credits"] += amount
    save_data(users_data)

    await update.message.reply_text("Credit adaugat.")


async def addsub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Folosire: /addsub user_id zile")
        return

    user_id = context.args[0]
    days = int(context.args[1])

    expiry = int(time.time()) + days * 86400

    if user_id not in users_data:
        users_data[user_id] = {"used": 0, "credits": 0, "subscription": 0}

    users_data[user_id]["subscription"] = expiry
    save_data(users_data)

    await update.message.reply_text("Abonament activat.")


# ================= MAIN =================
if __name__ == "__main__":
    if not TOKEN:
        print("EROARE: TOKEN nu este setat!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addcredit", addcredit))
    app.add_handler(CommandHandler("addsub", addsub))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()


