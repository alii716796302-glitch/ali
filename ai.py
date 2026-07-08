from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import is_user_banned, get_remaining_time, is_user_admin
from utils_ai import get_ai_response, clear_context
from keyboards import main_kb

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    clear_context(user_id)
    await update.message.reply_text(
        "🤖 **تم فتح محادثة مع الذكاء الاصطناعي.**\n📌 سأتذكر آخر 200 رسالة.\n📌 لإنهاء المحادثة، اكتب **/end** أو **رجوع**.",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data['ai_mode'] = True

async def handle_ai_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = is_user_admin(user_id)
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_admin))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        context.user_data['ai_mode'] = False
        clear_context(user_id)
        return
    q = update.message.text.strip()
    if q in ["رجوع", "/end", "خروج", "إنهاء", "🔙"]:
        await update.message.reply_text("🔙 تم إنهاء المحادثة.", parse_mode=ParseMode.MARKDOWN, reply_markup=main_kb(user_id, is_admin))
        context.user_data['ai_mode'] = False
        clear_context(user_id)
        return
    if len(q) < 2:
        await update.message.reply_text("❌ السؤال قصير.")
        return
    ans = get_ai_response(q, user_id)
    await update.message.reply_text(
        f"🤖 **الرد:**\n{ans}",
        parse_mode=ParseMode.MARKDOWN
    )
