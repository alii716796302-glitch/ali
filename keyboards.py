from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def main_kb(user_id, is_admin=False):
    keyboard = [
        [KeyboardButton("🤖 اسأل الذكاء الاصطناعي")],
        [KeyboardButton("🎨 توليد صورة"), KeyboardButton("📷 تعديل صورة")],
        [KeyboardButton("🎙️ تحويل صوت"), KeyboardButton("📅 حالة الاشتراك")],
        [KeyboardButton("📢 قناة البوت"), KeyboardButton("💎 تفعيل الاشتراك")],
        [KeyboardButton("👤 المطور")],
    ]
    if is_admin:
        keyboard.append([KeyboardButton("👑 لوحة التحكم")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast")],
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="admin_add_ch")],
        [InlineKeyboardButton("➖ حذف قناة", callback_data="admin_rm_ch")],
        [InlineKeyboardButton("📜 القنوات", callback_data="admin_list_ch")],
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("💰 الاشتراكات", callback_data="admin_subs")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings")],
    ])

def image_edit_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📐 تغيير الحجم", callback_data="edit_resize")],
        [InlineKeyboardButton("🎯 اقتصاص", callback_data="edit_crop")],
        [InlineKeyboardButton("🔄 تدوير", callback_data="edit_rotate")],
        [InlineKeyboardButton("⚫ تدرج رمادي", callback_data="edit_grayscale")],
        [InlineKeyboardButton("🟤 سيبيا", callback_data="edit_sepia")],
        [InlineKeyboardButton("💨 ضبابية", callback_data="edit_blur")],
        [InlineKeyboardButton("🔍 وضوح", callback_data="edit_sharpen")],
        [InlineKeyboardButton("📌 علامة مائية", callback_data="edit_watermark")],
        [InlineKeyboardButton("📦 ضغط", callback_data="edit_compress")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def remove_kb():
    return ReplyKeyboardRemove()

def voice_options_kb():
    voices = {
        "👨 رجل": "alloy",
        "👩 امرأة": "shimmer",
        "🧒 طفل": "fable",
        "👴 خشن": "onyx",
        "👩 ناعم": "nova",
        "🎵 صدى": "echo"
    }
    kb = [[InlineKeyboardButton(name, callback_data=f"voice_{key}")] for name, key in voices.items()]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(kb)

def user_management_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 إضافة مشرف", callback_data="admin_add_admin")],
        [InlineKeyboardButton("👤 حذف مشرف", callback_data="admin_rm_admin")],
        [InlineKeyboardButton("🚫 حظر", callback_data="admin_ban")],
        [InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unban")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
    ])

def subscription_management_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 شهري (10$)", callback_data="sub_monthly")],
        [InlineKeyboardButton("📅 سنوي (100$)", callback_data="sub_yearly")],
        [InlineKeyboardButton("➕ تفعيل لمستخدم", callback_data="admin_activate_sub")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
    ])

def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ تعديل مدة التجربة", callback_data="admin_set_trial")],
        [InlineKeyboardButton("💰 تعديل سعر شهري", callback_data="admin_set_price_monthly")],
        [InlineKeyboardButton("💰 تعديل سعر سنوي", callback_data="admin_set_price_yearly")],
        [InlineKeyboardButton("📅 تعديل مدة الاشتراك", callback_data="admin_set_days")],
        [InlineKeyboardButton("⚠️ تعديل وقت التحذير", callback_data="admin_set_warning")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
    ])

def channels_list_kb(channels):
    kb = [[InlineKeyboardButton(f"❌ حذف @{ch}", callback_data=f"admin_del_ch_{ch}")] for ch in channels]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(kb)

def admins_list_kb(admins):
    kb = [[InlineKeyboardButton(f"❌ حذف {uid}", callback_data=f"admin_del_admin_{uid}")] for uid in admins if uid != 7958260008]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(kb)
