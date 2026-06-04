import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 1. Configure Logging to see output inside Render logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Temporary simple dictionary storage for user text (in-memory)
USER_DATA = {}

# Command: /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Welcome to the Text Transformer Bot!**\n\n"
        "Send me any text message, and I will present you with tools to format or convert it instantly."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# Message Handler: Captures incoming text and sends the options menu
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # Store text locally in-memory
    USER_DATA[user_id] = user_text

    # Build the interactive menu buttons
    keyboard = [
        [
            InlineKeyboardButton("🔠 UPPERCASE", callback_data="upper"),
            InlineKeyboardButton("🔡 lowercase", callback_data="lower")
        ],
        [
            InlineKeyboardButton("🔤 Title Case", callback_data="title"),
            InlineKeyboardButton("🔄 Reverse Text", callback_data="reverse")
        ],
        [
            InlineKeyboardButton("🤖 Binary Code", callback_data="binary")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Choose a transformation option for your text:", reply_markup=reply_markup)

# Callback Handler: Processes the selected transformation button
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Acknowledge the callback click immediately

    user_id = update.effective_user.id
    action = query.data

    # Retrieve text from local storage
    original_text = USER_DATA.get(user_id)

    if not original_text:
        await query.edit_message_text("⚠️ Timeout or missing text. Please send a new text message first!")
        return

    # Process transformations strictly using Python core methods
    if action == "upper":
        transformed = original_text.upper()
    elif action == "lower":
        transformed = original_text.lower()
    elif action == "title":
        transformed = original_text.title()
    elif action == "reverse":
        transformed = original_text[::-1]
    elif action == "binary":
        transformed = ' '.join(format(ord(c), '08b') for c in original_text)
    else:
        transformed = "Unknown Option"

    # Send result back to user
    response_text = f"✨ **Result:**\n`{transformed}`"
    await query.edit_message_text(response_text, parse_mode="Markdown")

# Main execution entrypoint
def main():
    import os
    # Render uses Environment Variables to hide tokens securely
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("CRITICAL ERROR: BOT_TOKEN environment variable is missing!")
        sys.exit(1)

    logger.info("Initializing Telegram Bot Application via Polling Worker...")
    
    # Initialize application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Start long polling mode (Perfect for Render Background Worker)
    logger.info("Bot is active and polling for updates.")
    application.run_polling()

if __name__ == '__main__':
    main()
