from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import add_user, is_user_banned, is_user_admin, add_admin, get_setting, set_subscription, is_user_restricted, get_remaining_time, get_required_channels
from keyboards import main_kb
from config import DEVELOPER_ID
import asyncio

async def check_channels_fast(user_id, context):
    channels = get_required_channels()
    if not channels:
        return True
    tasks = [context.bot.get_chat_member(chat_id=f"@{ch}", user_id=user_id) for ch in channels]
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception) or r.status in ['left', 'kicked']:
                return False
        return True
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    add_user(user_id, user.username, user.first_name)
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 أنت محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    if user_id == DEVELOPER_ID:
        add_admin(user_id)
    channels = get_required_channels()
    if channels and not await check_channels_fast(user_id, context):
        kb = [[InlineKeyboardButton(f"📢 اشترك في @{ch}", url=f"https://t.me/{ch}")] for ch in channels]
        kb.append([InlineKeyboardButton("✅ تحقق", callback_data="check_sub")])
        await update.message.reply_text("⚠️ يرجى الاشتراك في القنوات:", reply_markup=InlineKeyboardMarkup(kb))
        return
    if is_user_restricted(user_id):
        free_hours = int(get_setting('free_trial_hours') or 24)
        set_subscription(user_id, free_hours/24)
        await update.message.reply_text(
            f"🎉 مرحباً! تم تفعيل التجربة المجانية لمدة {free_hours} ساعة.",
            reply_markup=main_kb(user_id, is_user_admin(user_id))
        )
        return
    remaining = get_remaining_time(user_id)
    if remaining is None or remaining <= 0:
        await update.message.reply_text(
            "⏰ انتهت التجربة.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 تفعيل الاشتراك", callback_data="subscribe")]])
        )
        return
    await update.message.reply_text(
        f"👋 مرحباً {user.first_name}! اشتراكك نشط.",
        reply_markup=main_kb(user_id, is_user_admin(user_id))
    )

async def check_sub_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    channels = get_required_channels()
    if channels and await check_channels_fast(user_id, context):
        await q.edit_message_text("✅ تم التحقق!")
    else:
        kb = [[InlineKeyboardButton(f"📢 اشترك في @{ch}", url=f"https://t.me/{ch}")] for ch in channels]
        kb.append([InlineKeyboardButton("🔄 حاول مجدداً", callback_data="check_sub")])
        await q.edit_message_text("❌ لا تزال غير مشترك.", reply_markup=InlineKeyboardMarkup(kb))
        return
    await start(update, context)
