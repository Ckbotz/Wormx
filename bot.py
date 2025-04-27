import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import filters  # Updated import for Filters
import requests
import json
import urllib.parse
import time
import logging
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Check if required environment variables are set
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set.")
    raise ValueError("BOT_TOKEN environment variable is required.")

# Note: API_ID and API_HASH are loaded but not used in this script
# They can be used if integrating with Telethon or Pyrogram for additional functionality

# API endpoint
API_URL = "https://legendxdata.site/Api/gpt/wormgpt.php?q={}"

# Simulate typing effect
def send_typing_effect(update, context, message):
    words = message.split()
    for i in range(0, len(words), 2):
        partial_message = ' '.join(words[:i+2])
        update.message.reply_text(partial_message)
        time.sleep(0.5)  # Adjust typing speed (seconds per chunk)
        # Delete the partial message to update it
        if i < len(words) - 2:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id + 1)

# Handle /start command
def start(update, context):
    update.message.reply_text("Hello! Send me a message (e.g., 'Hai how are you'), and I'll process it with the API.")

# Handle user messages
def handle_message(update, context):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    # Show typing action
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        # URL-encode the user message
        encoded_message = urllib.parse.quote(user_message)
        # Construct the API URL with encoded message
        api_url = API_URL.format(encoded_message)
        logger.info(f"Sending request to: {api_url}")

        # Send request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse JSON response
        try:
            api_response = response.json()
            reply = api_response.get('reply', '')
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from API")
            update.message.reply_text("Sorry, the API returned an invalid response.")
            return

        if not reply:
            update.message.reply_text("Sorry, I got an empty reply from the API.")
            return

        # Send response with typing effect
        send_typing_effect(update, context, reply)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        update.message.reply_text("Sorry, there was an error connecting to the API.")

# Error handler
def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Initialize the bot with the bot token
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Updated filters usage
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()

if __name__ == '__main__':
    main()
