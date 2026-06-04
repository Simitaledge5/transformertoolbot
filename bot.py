import logging
import sys
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Ensure logs flush instantly on Render's console
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

USER_DATA = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Welcome to the Text Transformer Bot!**\n\n"
        "Send me any text message, and I will present you with tools to format or convert it instantly."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    USER_DATA[user_id] = user_text

    keyboard = [
        [InlineKeyboardButton("🔠 UPPERCASE", callback_data="upper"),
         InlineKeyboardButton("🔡 lowercase", callback_data="lower")],
        [InlineKeyboardButton("🔤 Title Case", callback_data="title"),
         InlineKeyboardButton("🔄 Reverse Text", callback_data="reverse")],
        [InlineKeyboardButton("🤖 Binary Code", callback_data="binary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a transformation option:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    action = query.data
    original_text = USER_DATA.get(user_id)

    if not original_text:
        await query.edit_message_text("⚠️ Missing text. Please send a new message!")
        return

    if action == "upper": transformed = original_text.upper()
    elif action == "lower": transformed = original_text.lower()
    elif action == "title": transformed = original_text.title()
    elif action == "reverse": transformed = original_text[::-1]
    elif action == "binary": transformed = ' '.join(format(ord(c), '08b') for c in original_text)
    else: transformed = "Unknown Option"

    await query.edit_message_text(f"✨ **Result:**\n`{transformed}`", parse_mode="Markdown")

async def run_bot_lifecycle():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("CRITICAL: BOT_TOKEN environment variable is missing!")
        return

    logger.info("Building Telegram application...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Explicitly initialize and start the app inside the running event loop
    logger.info("Initializing application components...")
    await application.initialize()
    await application.updater.start_polling()
    await application.start()

    logger.info("🚀 Bot is successfully running and polling for updates!")

    # Keep the worker alive endlessly while listening for tasks
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Stopping bot service gracefully...")
    finally:
        # Graceful cleanup
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    # Explicitly spawn the event loop structure via asyncio.run()
    # This guarantees an active loop context required by Python 3.14
    asyncio.run(run_bot_lifecycle())

if __name__ == '__main__':
    main()
