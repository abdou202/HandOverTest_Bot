import telebot
from telebot import types

# 🔑 Replace with your bot token from BotFather
TOKEN = "8745775678:AAFF6aNr9jTMAyorKW1X3pqVpTkTD7AV7uc"

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔄 Shift ? (Day/Night)")
    bot.register_next_step_handler(message, get_shift)

def get_shift(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]['shift'] = message.text
    
    bot.send_message(message.chat.id, "⚙️ Equipment status ?")
    bot.register_next_step_handler(message, get_equipment)

def get_equipment(message):
    user_data[message.chat.id]['equipment'] = message.text
    
    bot.send_message(message.chat.id, "⚠️ Issues ?")
    bot.register_next_step_handler(message, get_issues)

def get_issues(message):
    user_data[message.chat.id]['issues'] = message.text
    
    bot.send_message(message.chat.id, "🛠️ Maintenance ?")
    bot.register_next_step_handler(message, get_maintenance)

def get_maintenance(message):
    user_data[message.chat.id]['maintenance'] = message.text
    
    bot.send_message(message.chat.id, "📊 Remarks ?")
    bot.register_next_step_handler(message, finish)

def finish(message):
    user_data[message.chat.id]['remarks'] = message.text
    
    data = user_data[message.chat.id]
    
    report = f"""
🔄 SHIFT: {data['shift']}

⚙️ Equipment:
{data['equipment']}

⚠️ Issues:
{data['issues']}

🛠️ Maintenance:
{data['maintenance']}

📊 Remarks:
{data['remarks']}
"""
    
    bot.send_message(message.chat.id, "✅ Handover saved!")
    
    # هنا تحط ID تاع القناة
    CHANNEL_ID = "@handover_test"
    bot.send_message(CHANNEL_ID, report)

bot.infinity_polling()
