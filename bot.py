import telebot
from telebot import types

# 🔑 Replace with your bot token from BotFather
TOKEN = "8745775678:AAFF6aNr9jTMAyorKW1X3pqVpTkTD7AV7uc"

bot = telebot.TeleBot(TOKEN)

# 🚀 START COMMAND
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! 👋\nUse /menu to see options.")

# ❓ HELP COMMAND
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "I am a simple bot 🤖\nCommands:\n/start\n/help\n/menu")

# 🔘 MENU WITH BUTTONS
@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Say Hello 👋")
    btn2 = types.KeyboardButton("About ℹ️")
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

# 📩 HANDLE BUTTON CLICKS & TEXT
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if text == "say hello 👋":
        bot.reply_to(message, "Hello there 😄")

    elif text == "about ℹ️":
        bot.reply_to(message, "I'm a TeleBot example built with Python!")

    elif "hi" in text:
        bot.reply_to(message, "Hey! How are you? 😊")

    else:
        bot.reply_to(message, "I don't understand 🤔\nTry /menu")

# ▶️ RUN BOT
print("Bot is running...")
bot.infinity_polling()