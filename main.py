import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from fpdf import FPDF

BOT_TOKEN = "7693918135:AAGO-4A2lCRMaDnpmItkOY94w1f16_D0iSw"

USER_IMAGES = {}
PREMIUM_USERS = set()
IMAGE_LIMIT = 7

def create_pdf(images, filename):
    pdf = FPDF()
    for img in images:
        pdf.add_page()
        pdf.image(img, x=10, y=10, w=190)
    pdf.output(filename)

def is_premium(user_id):
    return user_id in PREMIUM_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_IMAGES.setdefault(user_id, [])
    await update.message.reply_text(
        "👋 Welcome! Use /convert to create a PDF from images.\nJust send me the images first!"
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USER_IMAGES.setdefault(user_id, [])

    if not is_premium(user_id) and len(USER_IMAGES[user_id]) >= IMAGE_LIMIT:
        await update.message.reply_text("🚫 Free image limit reached. Upgrade for more!")
        return

    file = await update.message.photo[-1].get_file()
    path = f"{user_id}_{len(USER_IMAGES[user_id])}.jpg"
    await file.download_to_drive(path)
    USER_IMAGES[user_id].append(path)
    await update.message.reply_text("🖼️ Image saved!")

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    images = USER_IMAGES.get(user_id, [])
    if not images:
        await update.message.reply_text("⚠️ No images found.")
        return

    filename = f"{user_id}_output.pdf"
    create_pdf(images, filename)

    with open(filename, 'rb') as f:
        await context.bot.send_document(chat_id=user_id, document=f, filename="output.pdf")

    for img in images:
        os.remove(img)
    USER_IMAGES[user_id] = []
    os.remove(filename)

    await update.message.reply_text("✅ PDF created!")

async def error_handler(update, context):
    print(f"⚠️ Error: {context.error}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_error_handler(error_handler)

    print("🤖 Bot is running...")
    app.run_polling()
