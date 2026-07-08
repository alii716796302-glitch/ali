import io
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import is_user_banned, get_remaining_time, is_user_admin
from services_tts import text_to_speech
from keyboards import main_kb, voice_options_kb

async def tts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    await update.message.reply_text("🎙️ **اختر نوع الصوت:**", parse_mode=ParseMode.MARKDOWN, reply_markup=voice_options_kb())
    context.user_data['voice_select'] = True

async def handle_voice_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back_main":
        user_id = q.from_user.id
        await q.edit_message_text("🔙 تم العودة.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        context.user_data.pop('voice_select', None)
        return
    voice = q.data.replace("voice_", "")
    context.user_data['tts_voice'] = voice
    await q.edit_message_text(
        f"✅ تم اختيار الصوت.\n\n🎙️ أرسل النص (حد أقصى 500 حرف).",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data['tts_mode'] = True
    context.user_data['voice_select'] = False

async def handle_tts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get('tts_mode'):
        text = update.message.text
        if len(text) < 2:
            await update.message.reply_text("❌ النص قصير.")
            return
        if len(text) > 500:
            await update.message.reply_text("❌ النص طويل (الحد 500 حرف).")
            return
        voice = context.user_data.get('tts_voice', 'alloy')
        msg = await update.message.reply_text("🎙️ جاري تحويل النص...")
        audio = text_to_speech(text, voice)
        if audio:
            await context.bot.send_audio(
                chat_id=update.message.chat_id,
                audio=InputFile(io.BytesIO(audio), "speech.mp3"),
                caption="🎙️ تم التحويل!"
            )
        else:
            await context.bot.edit_message_text(
                "❌ فشل التحويل.",
                chat_id=update.message.chat_id,
                message_id=msg.message_id
            )
        context.user_data.pop('tts_mode', None)
        context.user_data.pop('tts_voice', None)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="📋 القائمة الرئيسية:",
            reply_markup=main_kb(user_id, is_user_admin(user_id))
        )
        return True
    return False
