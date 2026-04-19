
import telebot
from telebot import types
from datetime import datetime

# 🔑 Replace with your bot token from BotFather
TOKEN = "8745775678:AAFF6aNr9jTMAyorKW1X3pqVpTkTD7AV7uc"
    
    # هنا تحط ID تاع القناة
CHANNEL_ID = "@handover_test"

bot = telebot.TeleBot(TOKEN)

user_data = {}
done_today = {}

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):
    text = """
👋 مرحبا بك في نظام Hand Over

📌 الخطوات:
1- تختار Shift
2- تجاوب على الأسئلة
3- البوت ينشر التقرير في القناة

⚠️ ملاحظة:
مرة واحدة فقط في اليوم

اضغط للبدء 👇
"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Start Handover")

    bot.send_message(message.chat.id, text, reply_markup=markup)

# -------- START HANDOVER --------
@bot.message_handler(func=lambda m: m.text == "🚀 Start Handover")
def handover_start(message):
    today = datetime.now().strftime("%Y-%m-%d")

    if message.chat.id in done_today and done_today[message.chat.id] == today:
        bot.send_message(message.chat.id, "❌ راك درت Hand Over اليوم")
        return

    user_data[message.chat.id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌞 Day", "🌙 Night")

    bot.send_message(message.chat.id, "🔄 اختر Shift:", reply_markup=markup)

# -------- SHIFT --------
@bot.message_handler(func=lambda m: m.text in ["🌞 Day", "🌙 Night"])
def get_shift(message):
    user_data[message.chat.id]['shift'] = message.text

    ask_equipment(message)

# -------- EQUIPMENT --------
def ask_equipment(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report")

    bot.send_message(message.chat.id, "⚙️ حالة المعدات ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_equipment)

def get_equipment(message):
    if message.text == "🚫 Nothing to report":
        user_data[message.chat.id]['equipment'] = "Nothing to report"
    else:
        user_data[message.chat.id]['equipment'] = message.text

    ask_issues(message)

# -------- ISSUES --------
def ask_issues(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report")

    bot.send_message(message.chat.id, "⚠️ المشاكل (Issues) ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_issues)

def get_issues(message):
    if message.text == "🚫 Nothing to report":
        user_data[message.chat.id]['issues'] = "Nothing to report"
    else:
        user_data[message.chat.id]['issues'] = message.text

    ask_maintenance(message)

# -------- MAINTENANCE --------
def ask_maintenance(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report")

    bot.send_message(message.chat.id, "🛠️ الصيانة (Maintenance) ؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_maintenance)

def get_maintenance(message):
    if message.text == "🚫 Nothing to report":
        user_data[message.chat.id]['maintenance'] = "Nothing to report"
    else:
        user_data[message.chat.id]['maintenance'] = message.text

    ask_remarks(message)

# -------- REMARKS --------
def ask_remarks(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚫 Nothing to report")

    bot.send_message(message.chat.id, "📊 ملاحظات إضافية ؟", reply_markup=markup)
    bot.register_next_step_handler(message, finish)

# -------- FINISH --------
def finish(message):
    if message.text == "🚫 Nothing to report":
        user_data[message.chat.id]['remarks'] = "Nothing to report"
    else:
        user_data[message.chat.id]['remarks'] = message.text

    today_full = datetime.now().strftime("%Y-%m-%d %H:%M")
    username = message.from_user.first_name

    data = user_data[message.chat.id]

    report = f"""
📢 *HANDOVER REPORT*

👤 Operator: {username}
📅 Date: {today_full}
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

    bot.send_message(message.chat.id, "✅ تم تسجيل الـ Hand Over", reply_markup=types.ReplyKeyboardRemove())

    bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")

    # منع التكرار
    done_today[message.chat.id] = datetime.now().strftime("%Y-%m-%d")

# -------- RUN --------
bot.infinity_polling()




