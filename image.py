 # image.py - تعديل لإبقاء اللوحة الرئيسية ثابتة

import io
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import is_user_banned, get_remaining_time, is_user_admin
from utils_image import generate_image, resize_img, crop_img, rotate_img, grayscale_img, sepia_img, blur_img, sharpen_img, watermark_img, compress_img
from keyboards import main_kb, image_edit_kb, remove_kb
from config import DEVELOPER_ID

async def gen_img_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    await update.message.reply_text("🎨 أرسل وصفاً للصورة.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
    context.user_data['gen_img'] = True

async def edit_img_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    # ✅ إبقاء اللوحة الرئيسية ظاهرة
    await update.message.reply_text("📷 أرسل الصورة التي تريد تعديلها.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
    context.user_data['edit_img'] = True

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        await update.message.reply_text("🚫 محظور.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await update.message.reply_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    if context.user_data.get('edit_img') or context.user_data.get('edit_action'):
        photo = update.message.photo[-1]
        f = await context.bot.get_file(photo.file_id)
        data = await f.download_as_bytearray()
        context.user_data['img_data'] = data
        context.user_data['edit_img'] = True
        # ✅ عرض أزرار التعديل مع إبقاء اللوحة الرئيسية
        await update.message.reply_text("✅ تم استلام الصورة! اختر التعديل:", reply_markup=image_edit_kb())
    else:
        await update.message.reply_text("📷 لإرسال صورة للتعديل، اضغط أولاً على **📷 تعديل صورة**.", reply_markup=main_kb(user_id, is_user_admin(user_id)))

async def img_edit_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    is_admin = is_user_admin(user_id)
    if is_user_banned(user_id):
        await q.edit_message_text("🚫 محظور.", reply_markup=main_kb(user_id, is_admin))
        return
    remaining = get_remaining_time(user_id)
    if not remaining or remaining <= 0:
        await q.edit_message_text("⏰ انتهى اشتراكك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 اشترك", callback_data="subscribe")]]))
        return
    data = q.data
    img_data = context.user_data.get('img_data')
    if not img_data:
        await q.edit_message_text("❌ لا توجد صورة. أرسل صورة أولاً.", reply_markup=main_kb(user_id, is_admin))
        return
    if data == "back_main":
        await q.edit_message_text("🔙 تم العودة.", reply_markup=main_kb(user_id, is_admin))
        context.user_data.pop('img_data', None)
        context.user_data.pop('edit_img', None)
        return
    if data in ["edit_resize", "edit_crop", "edit_rotate", "edit_watermark", "edit_compress"]:
        msgs = {
            "edit_resize": "📐 أرسل العرض والارتفاع مثال: 800 600",
            "edit_crop": "🎯 أرسل x y w h مثال: 10 20 300 200",
            "edit_rotate": "🔄 أرسل الدرجات مثال: 90",
            "edit_watermark": "📌 أرسل النص",
            "edit_compress": "📦 أرسل الجودة (1-100) مثال: 50"
        }
        # ✅ إبقاء اللوحة الرئيسية ظاهرة
        await q.edit_message_text(msgs[data], reply_markup=main_kb(user_id, is_admin))
        context.user_data['edit_action'] = data.replace("edit_", "")
        return
    await q.edit_message_text("⏳ جاري التعديل...")
    try:
        funcs = {
            "edit_grayscale": grayscale_img,
            "edit_sepia": sepia_img,
            "edit_blur": blur_img,
            "edit_sharpen": sharpen_img
        }
        if data in funcs:
            res = funcs[data](img_data)
            await context.bot.send_photo(chat_id=q.message.chat_id, photo=InputFile(io.BytesIO(res), "edited.png"), caption="✅ تم التعديل!")
            await q.delete_message()
            # ✅ إبقاء اللوحة الرئيسية مع أزرار التعديل
            await context.bot.send_message(chat_id=q.message.chat_id, text="📷 اختر تعديلاً آخر:", reply_markup=image_edit_kb())
        else:
            await q.edit_message_text("❌ تعديل غير معروف.", reply_markup=image_edit_kb())
    except Exception as e:
        await q.edit_message_text(f"❌ خطأ: {e}", reply_markup=image_edit_kb())

async def handle_edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    action = context.user_data.get('edit_action')
    img_data = context.user_data.get('img_data')
    if not action or not img_data:
        return
    text = update.message.text
    try:
        funcs = {
            "resize": resize_img,
            "crop": crop_img,
            "rotate": rotate_img,
            "watermark": watermark_img,
            "compress": compress_img
        }
        if action == "compress":
            quality = int(text.strip())
            if quality < 1 or quality > 100:
                await update.message.reply_text("❌ الجودة بين 1 و 100.", reply_markup=image_edit_kb())
                return
            res = funcs[action](img_data, quality)
        elif action == "resize":
            w, h = map(int, text.split()[:2])
            res = funcs[action](img_data, w, h)
        elif action == "crop":
            x, y, w, h = map(int, text.split()[:4])
            res = funcs[action](img_data, x, y, w, h)
        elif action == "rotate":
            deg = int(text.strip())
            res = funcs[action](img_data, deg)
        elif action == "watermark":
            res = funcs[action](img_data, text)
        else:
            await update.message.reply_text("❌ إجراء غير معروف.", reply_markup=image_edit_kb())
            return
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=InputFile(io.BytesIO(res), "edited.png"), caption="✅ تم التعديل!")
        # ✅ إبقاء اللوحة الرئيسية مع أزرار التعديل
        await context.bot.send_message(chat_id=update.message.chat_id, text="📷 اختر تعديلاً آخر:", reply_markup=image_edit_kb())
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}", reply_markup=image_edit_kb())
    context.user_data.pop('edit_action', None)

async def handle_gen_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get('gen_img'):
        text = update.message.text
        if len(text) < 3:
            await update.message.reply_text("❌ الوصف قصير.", reply_markup=main_kb(user_id, is_user_admin(user_id)))
            return
        msg = await update.message.reply_text("🎨 جاري توليد الصورة...")
        img_data = generate_image(text)
        if img_data:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=InputFile(io.BytesIO(img_data), "generated.png"), caption=f"🖼️ تم توليد الصورة بناءً على:\n📝 {text}")
        else:
            await context.bot.edit_message_text("❌ فشل توليد الصورة.", chat_id=update.message.chat_id, message_id=msg.message_id)
        context.user_data.pop('gen_img', None)
        # ✅ إبقاء اللوحة الرئيسية ظاهرة
        await context.bot.send_message(chat_id=update.message.chat_id, text="📋 القائمة الرئيسية:", reply_markup=main_kb(user_id, is_user_admin(user_id)))
        return True
    return False
