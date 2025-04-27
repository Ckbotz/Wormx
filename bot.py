import logging
import os
import time
import urllib.parse
from typing import Final

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN: Final = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

# Check if required environment variables are set
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set.")
    raise ValueError("BOT_TOKEN environment variable is required.")

# API endpoint
API_URL: Final = "https://legendxdata.site/Api/gpt/wormgpt.php?q={}"

async def send_typing_effect(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """Simulate typing effect by sending message in chunks."""
    words = message.split()
    sent_message = None
    
    for i in range(0, len(words), 2):
        partial_message = ' '.join(words[:i+2])
        
        if sent_message:
            await sent_message.edit_text(partial_message)
        else:
            sent_message = await update.message.reply_text(partial_message)
        
        await asyncio.sleep(0.5)  # Adjust typing speed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! Send me a message (e.g., 'Hi how are you'), "
        "and I'll process it with the API."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming user messages."""
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    # Show typing action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        # URL-encode the user message
        encoded_message = urllib.parse.quote(user_message)
        api_url = API_URL.format(encoded_message)
        logger.info(f"Sending request to: {api_url}")

        # Send request to the API
        response = requests.get(api_url)
        response.raise_for_status()

        # Parse JSON response
        try:
            api_response = response.json()
            reply = api_response.get('reply', '')
        except ValueError:
            logger.error("Invalid JSON response from API")
            await update.message.reply_text("Sorry, the API returned an invalid response.")
            return

        if not reply:
            await update.message.reply_text("Sorry, I got an empty reply from the API.")
            return

        # Send response with typing effect
        await send_typing_effect(update, context, reply)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        await update.message.reply_text("Sorry, there was an error connecting to the API.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
