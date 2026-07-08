from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import *
from keyboards import admin_kb, user_management_kb, subscription_management_kb, settings_kb, channels_list_kb, admins_list_kb
from config import DEVELOPER_ID

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إيقاف الذكاء الاصطناعي فور الدخول إلى لوحة التحكم
    context.user_data.pop('ai_mode', None)
    
    user_id = update.effective_user.id
    if not is_user_admin(user_id):
        await update.message.reply_text("🚫 غير مصرح.")
        return
    await update.message.reply_text("👑 لوحة التحكم:", reply_markup=admin_kb())

async def admin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إيقاف الذكاء الاصطناعي عند الضغط على أي زر داخل لوحة التحكم
    context.user_data.pop('ai_mode', None)
    
    q = update.callback_query
    await q.answer()
    if not is_user_admin(q.from_user.id):
        await q.edit_message_text("🚫 غير مصرح.")
        return
    data = q.data
    if data == "admin_stats":
        stats = get_stats()
        users = get_all_users()
        user_list = "\n".join([f"👤 {u[2]} (@{u[1] or 'لا يوجد'})" for u in users[:20]])
        if len(users) > 20:
            user_list += f"\n... و {len(users)-20} مستخدمين آخرين"
        await q.edit_message_text(
            f"📊 الإحصائيات:\n👥 المستخدمين: {stats['total']}\n✅ النشطين: {stats['active']}\n🚫 المحظورين: {stats['banned']}\n🔒 المقيدين: {stats['restricted']}\n👑 المشرفين: {stats['admins']}\n\n📋 آخر المستخدمين:\n{user_list}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_kb()
        )
    elif data == "admin_broadcast":
        context.user_data['broadcast_mode'] = True
        await q.edit_message_text("📢 أرسل الرسالة:", reply_markup=admin_kb())
    elif data == "admin_add_ch":
        context.user_data['add_ch_mode'] = True
        await q.edit_message_text("➕ أرسل معرف القناة:", reply_markup=admin_kb())
    elif data == "admin_rm_ch":
        ch = get_required_channels()
        if not ch:
            await q.edit_message_text("❌ لا توجد قنوات.", reply_markup=admin_kb())
            return
        await q.edit_message_text("اختر قناة لحذفها:", reply_markup=channels_list_kb(ch))
    elif data.startswith("admin_del_ch_"):
        ch = data[13:]
        remove_required_channel(ch)
        await q.edit_message_text(f"✅ تم حذف @{ch}.", reply_markup=admin_kb())
    elif data == "admin_list_ch":
        ch = get_required_channels()
        await q.edit_message_text("📜 القنوات:\n" + "\n".join([f"- @{ch}" for ch in ch]) if ch else "❌ لا توجد قنوات.", reply_markup=admin_kb())
    elif data == "admin_users":
        await q.edit_message_text("👥 إدارة المستخدمين:", reply_markup=user_management_kb())
    elif data == "admin_add_admin":
        context.user_data['add_admin_mode'] = True
        await q.edit_message_text("➕ أرسل ID المستخدم:", reply_markup=admin_kb())
    elif data == "admin_rm_admin":
        admins = get_all_admins()
        if len(admins) <= 1:
            await q.edit_message_text("❌ لا يمكن حذف المشرف الوحيد.", reply_markup=admin_kb())
            return
        await q.edit_message_text("اختر مشرفاً لحذفه:", reply_markup=admins_list_kb(admins))
    elif data.startswith("admin_del_admin_"):
        uid = int(data[16:])
        if uid == DEVELOPER_ID:
            await q.edit_message_text("❌ لا يمكن حذف المطور.", reply_markup=admin_kb())
            return
        remove_admin(uid)
        await q.edit_message_text(f"✅ تم حذف المشرف {uid}.", reply_markup=admin_kb())
    elif data == "admin_ban":
        context.user_data['ban_mode'] = True
        await q.edit_message_text("🚫 أرسل ID المستخدم:", reply_markup=admin_kb())
    elif data == "admin_unban":
        context.user_data['unban_mode'] = True
        await q.edit_message_text("✅ أرسل ID المستخدم:", reply_markup=admin_kb())
    elif data == "admin_subs":
        await q.edit_message_text("💰 إدارة الاشتراكات:", reply_markup=subscription_management_kb())
    elif data == "admin_activate_sub":
        context.user_data['activate_sub_mode'] = True
        await q.edit_message_text("➕ أرسل ID المستخدم:", reply_markup=admin_kb())
    elif data == "admin_settings":
        fh = get_setting('free_trial_hours') or 24
        pm = get_setting('subscription_price_monthly') or 10
        py = get_setting('subscription_price_yearly') or 100
        days = get_setting('subscription_days') or 30
        warn = get_setting('warning_hours') or 2
        await q.edit_message_text(
            f"⚙️ الإعدادات:\n⏳ التجربة: {fh} ساعة\n💰 السعر الشهري: {pm}$\n💰 السعر السنوي: {py}$\n📅 المدة: {days} يوم\n⚠️ التحذير: {warn} ساعة",
            reply_markup=settings_kb()
        )
    elif data == "admin_set_trial":
        context.user_data['set_trial_mode'] = True
        await q.edit_message_text("⏳ أرسل عدد ساعات التجربة:", reply_markup=admin_kb())
    elif data == "admin_set_price_monthly":
        context.user_data['set_price_monthly_mode'] = True
        await q.edit_message_text("💰 أرسل السعر الشهري:", reply_markup=admin_kb())
    elif data == "admin_set_price_yearly":
        context.user_data['set_price_yearly_mode'] = True
        await q.edit_message_text("💰 أرسل السعر السنوي:", reply_markup=admin_kb())
    elif data == "admin_set_days":
        context.user_data['set_days_mode'] = True
        await q.edit_message_text("📅 أرسل عدد أيام الاشتراك:", reply_markup=admin_kb())
    elif data == "admin_set_warning":
        context.user_data['set_warning_mode'] = True
        await q.edit_message_text("⚠️ أرسل عدد ساعات التحذير:", reply_markup=admin_kb())
    elif data == "admin_back":
        await q.edit_message_text("👑 لوحة التحكم:", reply_markup=admin_kb())

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إيقاف الذكاء الاصطناعي عند استقبال أي نص في الوضع الإداري
    context.user_data.pop('ai_mode', None)
    
    user_id = update.effective_user.id
    if not is_user_admin(user_id):
        return
    text = update.message.text
    if context.user_data.get('broadcast_mode'):
        users = get_all_users()
        sent = 0
        for uid, _, _, _, _, _, _ in users:
            try:
                if update.message.photo:
                    await context.bot.send_photo(uid, photo=update.message.photo[-1].file_id, caption=text)
                elif update.message.document:
                    await context.bot.send_document(uid, document=update.message.document.file_id, caption=text)
                elif update.message.video:
                    await context.bot.send_video(uid, video=update.message.video.file_id, caption=text)
                else:
                    await context.bot.send_message(uid, text)
                sent += 1
            except:
                pass
        await update.message.reply_text(f"✅ تم الإذاعة لـ {sent} مستخدم.")
        context.user_data.pop('broadcast_mode', None)
    elif context.user_data.get('add_ch_mode'):
        ch = text.strip().lstrip('@')
        if ch:
            add_required_channel(ch)
            await update.message.reply_text(f"✅ تمت إضافة @{ch}.")
        else:
            await update.message.reply_text("❌ معرف غير صحيح.")
        context.user_data.pop('add_ch_mode', None)
    elif context.user_data.get('add_admin_mode'):
        try:
            uid = int(text.strip())
            add_admin(uid)
            await update.message.reply_text(f"✅ تمت إضافة {uid} كمشرف.")
        except:
            await update.message.reply_text("❌ معرف غير صحيح.")
        context.user_data.pop('add_admin_mode', None)
    elif context.user_data.get('ban_mode'):
        try:
            uid = int(text.strip())
            ban_user(uid)
            await update.message.reply_text(f"✅ تم حظر {uid}.")
        except:
            await update.message.reply_text("❌ معرف غير صحيح.")
        context.user_data.pop('ban_mode', None)
    elif context.user_data.get('unban_mode'):
        try:
            uid = int(text.strip())
            unban_user(uid)
            await update.message.reply_text(f"✅ تم إلغاء حظر {uid}.")
        except:
            await update.message.reply_text("❌ معرف غير صحيح.")
        context.user_data.pop('unban_mode', None)
    elif context.user_data.get('activate_sub_mode'):
        try:
            uid = int(text.strip())
        except:
            await update.message.reply_text("❌ معرف غير صحيح.")
            context.user_data.pop('activate_sub_mode', None)
            return
        await update.message.reply_text(
            f"💎 اختر خطة للمستخدم {uid}:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 شهري", callback_data=f"activate_monthly_{uid}")],
                [InlineKeyboardButton("📅 سنوي", callback_data=f"activate_yearly_{uid}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
            ])
        )
        context.user_data.pop('activate_sub_mode', None)
    elif context.user_data.get('set_trial_mode'):
        try:
            val = int(text.strip())
            set_setting('free_trial_hours', str(val))
            await update.message.reply_text(f"✅ مدة التجربة {val} ساعة.")
        except:
            await update.message.reply_text("❌ رقم غير صحيح.")
        context.user_data.pop('set_trial_mode', None)
    elif context.user_data.get('set_price_monthly_mode'):
        try:
            val = int(text.strip())
            set_setting('subscription_price_monthly', str(val))
            await update.message.reply_text(f"✅ السعر الشهري {val}$.")
        except:
            await update.message.reply_text("❌ رقم غير صحيح.")
        context.user_data.pop('set_price_monthly_mode', None)
    elif context.user_data.get('set_price_yearly_mode'):
        try:
            val = int(text.strip())
            set_setting('subscription_price_yearly', str(val))
            await update.message.reply_text(f"✅ السعر السنوي {val}$.")
        except:
            await update.message.reply_text("❌ رقم غير صحيح.")
        context.user_data.pop('set_price_yearly_mode', None)
    elif context.user_data.get('set_days_mode'):
        try:
            val = int(text.strip())
            set_setting('subscription_days', str(val))
            await update.message.reply_text(f"✅ مدة الاشتراك {val} يوم.")
        except:
            await update.message.reply_text("❌ رقم غير صحيح.")
        context.user_data.pop('set_days_mode', None)
    elif context.user_data.get('set_warning_mode'):
        try:
            val = int(text.strip())
            set_setting('warning_hours', str(val))
            await update.message.reply_text(f"✅ وقت التحذير {val} ساعة.")
        except:
            await update.message.reply_text("❌ رقم غير صحيح.")
        context.user_data.pop('set_warning_mode', None)
