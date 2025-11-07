from telegram import Update
from telegram.ext import CallbackContext

from src.logging import tg_logger


def error_handler(update: Update, context: CallbackContext):
    try:
        tg_logger.warning(f'Update "{update}" caused error', exc_info=context.error)
    except Exception:
        print(f"Error in error handler: {context.error}")
