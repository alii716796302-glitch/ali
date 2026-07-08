from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import DEVELOPER_USERNAME

async def dev_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👤 **المطور:** {DEVELOPER_USERNAME}\n\n📌 للتواصل، اضغط الزر:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 تواصل", url=f"https://t.me/{DEVELOPER_USERNAME.lstrip('@')}")]
        ])
    )
