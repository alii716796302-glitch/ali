from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import DEVELOPER_ID, DEVELOPER_USERNAME
from db import set_subscription, get_remaining_time

async def sub_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    remaining = get_remaining_time(user_id)
    if remaining and remaining > 0:
        await q.edit_message_text(
            f"✅ اشتراكك نشط.\n⏳ المتبقي: {int(remaining)} ساعة.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])
        )
        return
    await q.edit_message_text(
        "💎 **اختر خطة الاشتراك:**\n\n📅 شهري: 10$ → 30 يوم\n📅 سنوي: 100$ → 365 يوم",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 شهري", callback_data="sub_monthly_user")],
            [InlineKeyboardButton("📅 سنوي", callback_data="sub_yearly_user")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ])
    )

async def handle_user_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    if q.data == "sub_monthly_user":
        await context.bot.send_message(
            DEVELOPER_ID,
            f"🔔 طلب اشتراك شهري من {user.id}\n@{user.username or 'لا يوجد'}"
        )
        await q.edit_message_text(
            f"✅ تم إرسال الطلب للمطور.\n📞 للتواصل: {DEVELOPER_USERNAME}",
            parse_mode=ParseMode.MARKDOWN
        )
    elif q.data == "sub_yearly_user":
        await context.bot.send_message(
            DEVELOPER_ID,
            f"🔔 طلب اشتراك سنوي من {user.id}\n@{user.username or 'لا يوجد'}"
        )
        await q.edit_message_text(
            f"✅ تم إرسال الطلب للمطور.\n📞 للتواصل: {DEVELOPER_USERNAME}",
            parse_mode=ParseMode.MARKDOWN
        )
    elif q.data == "back":
        from .start import start
        await start(update, context)

async def activate_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("activate_monthly_"):
        uid = int(q.data.replace("activate_monthly_", ""))
        end = set_subscription(uid, 30)
        await q.edit_message_text(
            f"✅ تم تفعيل اشتراك شهري للمستخدم {uid} لمدة 30 يوم.\n📅 ينتهي في: {end.strftime('%Y-%m-%d %H:%M')}"
        )
        try:
            await context.bot.send_message(
                uid,
                f"🎉 تم تفعيل اشتراكك الشهري بنجاح! 📅 ينتهي في: {end.strftime('%Y-%m-%d %H:%M')}"
            )
        except:
            pass
    elif q.data.startswith("activate_yearly_"):
        uid = int(q.data.replace("activate_yearly_", ""))
        end = set_subscription(uid, 365)
        await q.edit_message_text(
            f"✅ تم تفعيل اشتراك سنوي للمستخدم {uid} لمدة 365 يوم.\n📅 ينتهي في: {end.strftime('%Y-%m-%d %H:%M')}"
        )
        try:
            await context.bot.send_message(
                uid,
                f"🎉 تم تفعيل اشتراكك السنوي بنجاح! 📅 ينتهي في: {end.strftime('%Y-%m-%d %H:%M')}"
            )
        except:
            pass
