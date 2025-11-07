from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
import logging
import traceback
import os
import html
import json
from src.logging import tg_logger

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: CallbackContext):
    """
    Log the error and send a telegram message to notify the developer.
    Credits: https://docs.python-telegram-bot.org/en/stable/examples.errorhandlerbot.html
    """
    try:
        # Safety check: ensure context and error exist
        if not context or not context.error:
            logger.error("Error handler called but context or context.error is None")
            return

        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error("Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) and update else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # Truncate message if it's too long (Telegram has a 4096 character limit)
        if len(message) > 4096:
            message = message[:4000] + "\n\n... (message truncated)"

        # Finally, send the message (only if TELEGRAM_ERROR_CHAT_ID is set and bot is available)
        error_chat_id = os.environ.get("TELEGRAM_ERROR_CHAT_ID")
        if error_chat_id and context.bot:
            try:
                await context.bot.send_message(
                    chat_id=error_chat_id, text=message, parse_mode=ParseMode.HTML
                )
            except Exception as send_error:
                # If sending the error message fails, log it but don't raise
                logger.error(f"Failed to send error message to Telegram: {send_error}", exc_info=send_error)
    except Exception as handler_error:
        # If the error handler itself fails, log it but don't raise to avoid infinite recursion
        logger.critical(f"Error handler itself raised an exception: {handler_error}", exc_info=handler_error)
        # Fallback to simple print if logger also fails
        try:
            print(f"CRITICAL: Error handler failed: {handler_error}")
            print(f"Original error: {context.error if context and context.error else 'Unknown'}")
        except Exception:
            pass  # Last resort - if even print fails, we're in deep trouble