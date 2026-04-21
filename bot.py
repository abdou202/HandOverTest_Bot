
import telebot
from telebot import types
from datetime import datetime

# 🔑 Replace with your bot token from BotFather
TOKEN = "8745775678:AAFF6aNr9jTMAyorKW1X3pqVpTkTD7AV7uc"
    
    # هنا تحط ID تاع القناة
CHANNEL_ID = "@handover_test"

AREAS = [
    "OT1 / Manifold compresseur d’air",
    "OT2 / Slug catcher",
    "AGC’s",
    "BGC’s",
    "Dehydration",
    "IGC’s / FG / Ballon de torche",
    "RGC’s / API",
    "NGL",
    "PWT / RKF / Puits Source",
    "Export"
]

bot = telebot.TeleBot(TOKEN)

user_data = {}
done_today = {}

# -------- MENU --------
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Start Handover")
    bot.send_message(chat_id, "📋 اختر:", reply_markup=markup)

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):
    text = """
👋 مرحبا بك في نظام Hand Over

📌 الخطوات:
1- تختار Shift
2- تجاوب على الأسئلة
3- البوت ينشر التقرير في القناة

اضغط على الزر للبدء 👇
"""
    bot.send_message(message.chat.id, text)
    main_menu(message.chat.id)

# -------- CANCEL --------
@bot.message_handler(func=lambda m: m.text == "❌ Annuler")
def cancel(message):
    user_data.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "❌ تم إلغاء العملية")
    main_menu(message.chat.id)

# -------- START HANDOVER --------
@bot.message_handler(func=lambda m: m.text == "🚀 Start Handover")
def handover_start(message):
    today = datetime.now().strftime("%Y-%m-%d")

    if message.chat.id in done_today and done_today[message.chat.id] == today:
        bot.send_message(message.chat.id, "❌ راك درت Hand Over اليوم")
        main_menu(message.chat.id)
        return

    user_data[message.chat.id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for area in AREAS:
        markup.add(area)

    markup.add("❌ Annuler")

    bot.send_message(message.chat.id, "📍 اختر Area:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in AREAS)
def get_area(message):
    user_data[message.chat.id]['area'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌞 Day", "🌙 Night", "❌ Annuler")

    bot.send_message(message.chat.id, "🔄 اختر Shift:", reply_markup=markup)

# -------- SHIFT --------
@bot.message_handler(func=lambda m: m.text in ["🌞 Day", "🌙 Night"])
def get_shift(message):
    user_data[message.chat.id]['shift'] = message.text
    ask_equipment(message)

# -------- EQUIPMENT --------
def ask_equipment(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Annuler")

    bot.send_message(message.chat.id, "⚙️ حالة المعدات ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_equipment)

def get_equipment(message):
    if message.text == "❌ Annuler":
        cancel(message)
        return

    user_data[message.chat.id]['equipment'] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    ask_issues(message)

# -------- ISSUES --------
def ask_issues(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Annuler")

    bot.send_message(message.chat.id, "⚠️ المشاكل (Issues) ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_issues)

def get_issues(message):
    if message.text == "❌ Annuler":
        cancel(message)
        return

    user_data[message.chat.id]['issues'] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    ask_maintenance(message)

# -------- MAINTENANCE --------
def ask_maintenance(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Annuler")

    bot.send_message(message.chat.id, "🛠️ الصيانة (Maintenance) ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_maintenance)

def get_maintenance(message):
    if message.text == "❌ Annuler":
        cancel(message)
        return

    user_data[message.chat.id]['maintenance'] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    ask_remarks(message)

# -------- REMARKS --------
def ask_remarks(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Annuler")

    bot.send_message(message.chat.id, "📊 ملاحظات إضافية ؟", reply_markup=markup)
    bot.register_next_step_handler(message, finish)

# -------- FINISH --------
def finish(message):
    if message.text == "❌ Annuler":
        cancel(message)
        return

    user_data[message.chat.id]['remarks'] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    today_full = datetime.now().strftime("%Y-%m-%d %H:%M")
    username = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}"

    data = user_data.get(message.chat.id)
    if not data:
        bot.send_message(message.chat.id, "❌ لا توجد بيانات")
        main_menu(message.chat.id)
        return

    report = f"""
📢 *HANDOVER REPORT*

👤 Operator: {username}
📅 Date: {today_full}
📍 Area: {data['area']}
🔄 Shift: {data['shift']}

━━━━━━━━━━━━━━━

⚙️ *Equipment Status:*
{data['equipment']}

⚠️ *Issues:*
{data['issues']}

🛠️ *Maintenance:*
{data['maintenance']}

📊 *Remarks:*
{data['remarks']}

━━━━━━━━━━━━━━━
"""

    user_data[message.chat.id]['report'] = report

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Confirm", "✏️ Edit", "❌ Cancel")

    bot.send_message(message.chat.id, report, parse_mode="Markdown")
    bot.send_message(message.chat.id, "❓ هل تريد الإرسال أو التعديل؟", reply_markup=markup)

# -------- CONFIRM --------
@bot.message_handler(func=lambda m: m.text == "✅ Confirm")
def confirm(message):
    data = user_data.get(message.chat.id)
    if not data or 'report' not in data:
        bot.send_message(message.chat.id, "❌ لا يوجد تقرير")
        return

    try:
        bot.send_message(CHANNEL_ID, data['report'], parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ تم إرسال الـ Hand Over", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطأ: {e}")

    done_today[message.chat.id] = datetime.now().strftime("%Y-%m-%d")
    user_data.pop(message.chat.id, None)

    main_menu(message.chat.id)

# -------- CANCEL CONFIRM --------
@bot.message_handler(func=lambda m: m.text == "❌ Cancel")
def cancel_confirm(message):
    user_data.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "❌ تم إلغاء العملية")
    main_menu(message.chat.id)

# -------- EDIT MENU --------
@bot.message_handler(func=lambda m: m.text == "✏️ Edit")
def edit_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        "⚙️ Equipment",
        "⚠️ Issues",
        "🛠️ Maintenance",
        "📊 Remarks",
        "🔙 Back"
    )

    bot.send_message(message.chat.id, "✏️ ماذا تريد تعديله؟", reply_markup=markup)

# -------- BACK --------
@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back(message):
    back_to_confirm(message)

# -------- EDIT FIELDS --------
@bot.message_handler(func=lambda m: m.text == "⚙️ Equipment")
def edit_equipment(message):
    bot.send_message(message.chat.id, "✏️ اكتب Equipment الجديد:")
    bot.register_next_step_handler(message, save_equipment)

def save_equipment(message):
    user_data[message.chat.id]['equipment'] = message.text
    back_to_confirm(message)

@bot.message_handler(func=lambda m: m.text == "⚠️ Issues")
def edit_issues(message):
    bot.send_message(message.chat.id, "✏️ اكتب Issues الجديد:")
    bot.register_next_step_handler(message, save_issues)

def save_issues(message):
    user_data[message.chat.id]['issues'] = message.text
    back_to_confirm(message)

@bot.message_handler(func=lambda m: m.text == "🛠️ Maintenance")
def edit_maintenance(message):
    bot.send_message(message.chat.id, "✏️ اكتب Maintenance الجديد:")
    bot.register_next_step_handler(message, save_maintenance)

def save_maintenance(message):
    user_data[message.chat.id]['maintenance'] = message.text
    back_to_confirm(message)

@bot.message_handler(func=lambda m: m.text == "📊 Remarks")
def edit_remarks(message):
    bot.send_message(message.chat.id, "✏️ اكتب Remarks الجديد:")
    bot.register_next_step_handler(message, save_remarks)

def save_remarks(message):
    user_data[message.chat.id]['remarks'] = message.text
    back_to_confirm(message)

# -------- BACK TO CONFIRM --------
def back_to_confirm(message):
    data = user_data.get(message.chat.id)
    if not data:
        bot.send_message(message.chat.id, "❌ لا توجد بيانات")
        main_menu(message.chat.id)
        return

    today_full = datetime.now().strftime("%Y-%m-%d %H:%M")
    username = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}"

    report = f"""
📢 *HANDOVER REPORT*

👤 Operator: {username}
📅 Date: {today_full}
📍 Area: {data['area']}
🔄 Shift: {data['shift']}

━━━━━━━━━━━━━━━

⚙️ *Equipment Status:*
{data['equipment']}

⚠️ *Issues:*
{data['issues']}

🛠️ *Maintenance:*
{data['maintenance']}

📊 *Remarks:*
{data['remarks']}

━━━━━━━━━━━━━━━
"""

    user_data[message.chat.id]['report'] = report

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Confirm", "✏️ Edit", "❌ Cancel")

    bot.send_message(message.chat.id, report, parse_mode="Markdown")
    bot.send_message(message.chat.id, "🔁 تم التحديث، تأكد:", reply_markup=markup)

# -------- RUN --------
bot.infinity_polling()
