import logging
from telegram import Update
from telegram.ext import ContextTypes

from lolibot.config import BotConfig


logger = logging.getLogger(__name__)


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the context for the bot."""
    config: BotConfig = context.application.bot_data.get("config")
    context_name = update.message.text.split("_")[1].strip()
    try:
        config.change_context(context_name)
        context.application.bot_data["config"] = config
        await update.message.reply_text(f"✅ Context changed to {context_name}")
    except Exception as e:
        logger.error(f"Error changing context: {e}")
        await update.message.reply_text(f"❌ Error changing context: {e}")

    # Attempt to update the Telegram bot display name to include the new context.
    try:
        base_name = getattr(config, "bot_name", None) or "Bot"
        new_name = f"{base_name} ({context_name})"
        await context.application.bot.set_my_name(name=new_name)
        # await update.message.reply_text(f"✅ Bot name updated to: {new_name}")
    except Exception as e:  # pragma: no cover - best-effort API call
        logger.warning(f"Could not update bot name: {e}")
        # await update.message.reply_text(f"⚠️ Could not update bot name: {e}")
