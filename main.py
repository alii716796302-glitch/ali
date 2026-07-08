# main.py - مع إضافة مسح ai_mode عند الضغط على أي زر (عدا زر الذكاء الاصطناعي)

import asyncio
import io
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode
from config import BOT_TOKEN, CHANNEL_USERNAME, DEVELOPER_ID
from db import init_db, add_admin, is_user_admin, get_remaining_time, get_setting, get_all_users, add_user, is_user_banned
from start import start, check_sub_cb
from ai import ask_ai, handle_ai_msg, clear_context
from image import gen_img_cmd, edit_img_cmd, handle_photo, img_edit_cb, handle_edit_input, handle_gen_img
from admin import admin_panel, admin_cb, handle_admin_text
from subscription import sub_cmd, handle_user_sub, activate_sub
from developer import dev_cmd
from tts import tts_cmd, handle_voice_select, handle_tts_text
from keyboards import main_kb, admin_kb, image_edit_kb, voice_options_kb

async def monitor(application):
    while True:
        try:
            users = get_all_users()
            warn_hours = int(get_setting('warning_hours') or 2)
            for uid, _, _, sub_end, _, _, _ in users:
                if sub_end:
                    from db import get_remaining_time
                    rem = get_remaining_time(uid)
                    if rem is not None and 0 < rem <= warn_hours:
                        try:
                            await asyncio.wait_for(
                                application.bot.send_message(
                                    uid,
                                    f"⚠️ تحذير! مدة اشتراكك على وشك الانتهاء.\n⏳ المتبقي: {int(rem)} ساعة.",
                                    parse_mode=ParseMode.MARKDOWN
                                ),
                                timeout=10
                            )
                        except:
                            pass
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Monitor error: {e}")
            await asyncio.sleep(3600)

async def main_handler(update: Update, context):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, False))
        return

    text = update.message.text
    is_admin = is_user_admin(user_id) or (user_id == DEVELOPER_ID)

    # ========== الأزرار الرئيسية ==========
    if text == "🤖 اسأل الذكاء الاصطناعي":
        # مسح أي وضع آخر وتفعيل الذكاء الاصطناعي
        context.user_data.pop('gen_img', None)
        context.user_data.pop('edit_img', None)
        context.user_data.pop('edit_action', None)
        context.user_data.pop('img_data', None)
        context.user_data.pop('tts_mode', None)
        context.user_data.pop('tts_voice', None)
        context.user_data.pop('voice_select', None)
        await ask_ai(update, context)
        return

    # جميع الأزرار الأخرى: نمسح ai_mode أولاً ثم ننفذ الأمر
    if text == "🎨 توليد صورة":
        context.user_data.pop('ai_mode', None)
        context.user_data.pop('tts_mode', None)
        await gen_img_cmd(update, context)
        return

    if text == "📷 تعديل صورة":
        context.user_data.pop('ai_mode', None)
        context.user_data.pop('tts_mode', None)
        await edit_img_cmd(update, context)
        return

    if text == "🎙️ تحويل صوت":
        context.user_data.pop('ai_mode', None)
        context.user_data.pop('gen_img', None)
        context.user_data.pop('edit_img', None)
        await tts_cmd(update, context)
        return

    if text == "📅 حالة الاشتراك":
        context.user_data.pop('ai_mode', None)   # ← إيقاف الذكاء الاصطناعي
        rem = get_remaining_time(user_id)
        if rem and rem > 0:
            await update.message.reply_text(
                f"✅ اشتراكك نشط.\n⏳ المتبقي: {int(rem)} ساعة.",
                reply_markup=main_kb(user_id, is_admin)
            )
        else:
            await update.message.reply_text(
                "⏰ انتهى اشتراكك.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 تفعيل الاشتراك", callback_data="subscribe")]])
            )
        return

    if text == "📢 قناة البوت":
        context.user_data.pop('ai_mode', None)   # ← إيقاف الذكاء الاصطناعي
        await update.message.reply_text(
            f"📢 قناة البوت: {CHANNEL_USERNAME}",
            reply_markup=main_kb(user_id, is_admin)
        )
        return

    if text == "💎 تفعيل الاشتراك":
        context.user_data.pop('ai_mode', None)   # ← إيقاف الذكاء الاصطناعي
        rem = get_remaining_time(user_id)
        if rem and rem > 0:
            await update.message.reply_text(
                f"✅ اشتراكك نشط.\n⏳ المتبقي: {int(rem)} ساعة.",
                reply_markup=main_kb(user_id, is_admin)
            )
            return
        await update.message.reply_text(
            "💎 اختر خطة:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 شهري (10$)", callback_data="sub_monthly_user")],
                [InlineKeyboardButton("📅 سنوي (100$)", callback_data="sub_yearly_user")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        return

    if text == "👤 المطور":
        context.user_data.pop('ai_mode', None)   # ← إيقاف الذكاء الاصطناعي
        await dev_cmd(update, context)
        return

    if text == "👑 لوحة التحكم":
        context.user_data.pop('ai_mode', None)   # ← إيقاف الذكاء الاصطناعي
        if is_admin:
            await admin_panel(update, context)
        else:
            await update.message.reply_text(
                "🚫 غير مصرح.",
                reply_markup=main_kb(user_id, is_admin)
            )
        return

    # ========== الأوامر الإدارية (إذا كان المشرف في وضع إداري) ==========
    if is_admin:
        admin_modes = [
            'broadcast_mode', 'add_ch_mode', 'add_admin_mode', 'ban_mode',
            'unban_mode', 'activate_sub_mode', 'set_trial_mode',
            'set_price_monthly_mode', 'set_price_yearly_mode',
            'set_days_mode', 'set_warning_mode'
        ]
        if any(k in context.user_data for k in admin_modes):
            # سيتم مسح ai_mode داخل handle_admin_text نفسه (لأننا أضفناه هناك أيضاً)
            await handle_admin_text(update, context)
            return

    # ========== أوضاع خاصة (توليد، تعديل، صوت) ==========
    if context.user_data.get('gen_img'):
        await handle_gen_img(update, context)
        return
    if context.user_data.get('edit_action'):
        await handle_edit_input(update, context)
        return
    if context.user_data.get('tts_mode'):
        await handle_tts_text(update, context)
        return

    # ========== وضع الذكاء الاصطناعي ==========
    if context.user_data.get('ai_mode'):
        # أوامر إنهاء المحادثة
        if text in ["رجوع", "/end", "خروج", "إنهاء", "🔙"]:
            await update.message.reply_text(
                "🔙 تم إنهاء المحادثة.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_kb(user_id, is_admin)
            )
            context.user_data['ai_mode'] = False
            clear_context(user_id)
            return
        await handle_ai_msg(update, context)
        return

    # ========== أي رسالة أخرى ==========
    if len(text) > 2 and not text.startswith('/'):
        await update.message.reply_text(
            "👋 اضغط **أسأل الذكاء الاصطناعي** لبدء محادثة، أو استخدم الأزرار الأخرى.",
            reply_markup=main_kb(user_id, is_admin)
        )

def main():
    print("="*60)
    print("🤖 بوت الذكاء الاصطناعي المتكامل (لوحة ثابتة)")
    print("👤 المطور: @xxhhjl")
    print("="*60)
    
    init_db()
    add_user(DEVELOPER_ID, "developer", "Developer")
    add_admin(DEVELOPER_ID)
    
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_cb, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(sub_cmd, pattern="^subscribe$"))
    app.add_handler(CallbackQueryHandler(handle_user_sub, pattern="^(sub_monthly_user|sub_yearly_user|back)$"))
    app.add_handler(CallbackQueryHandler(admin_cb, pattern="^(admin_|activate_monthly_|activate_yearly_)"))
    app.add_handler(CallbackQueryHandler(img_edit_cb, pattern="^edit_"))
    app.add_handler(CallbackQueryHandler(handle_voice_select, pattern="^(voice_|back_main)"))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, lambda u, c: u.message.reply_text("📂 تم استلام الملف")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handler))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(monitor(app))

    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
