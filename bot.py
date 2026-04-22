
import telebot
from telebot import types
from datetime import datetime

# ============================================================
#  🔧 CONFIG — بدّل هنا فقط
# ============================================================
BOT_TOKEN   = "8745775678:AAFF6aNr9jTMAyorKW1X3pqVpTkTD7AV7uc"          # توكن البوت تاعك
CHANNEL_ID  = "@handover_test"   # اسم القناة تاعك 
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

sessions   = {}   # بيانات الـ session الحالية
done_today = {}   # تتبع من بعث اليوم

# ── الخيارات ────────────────────────────────────────────────
SHIFTS = ["🌞 Day Shift  (07h–19h)", "🌙 Night Shift  (19h–07h)"]

AREAS  = [
    "⚙️ OT1 / Manifold compresseur d'air",
    "⚙️ OT2 / Slug catcher",
    "🏭 AGC's",
    "🏭 BGC's",
    "💧 Dehydration",
    "🔥 IGC's / FG / Ballon de torche",
    "🏭 RGC's / API",
    "🧪 NGL",
    "💧 PWT / RKF / Puits Source",
    "🚀 Export",
]

ETATS = [
    "✅ Normal — No anomaly",
    "⚠️ Minor anomaly",
    "🔴 Major anomaly / Shutdown",
]

# ── helpers ──────────────────────────────────────────────────
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Start Handover")
    bot.send_message(chat_id, "📋 Ready when you are 👇", reply_markup=markup)


def build_report(s):
    return (
        f"📋 *HAND OVER — GROUPEMENT BERKINE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Operator :*  {s['nom']}\n"
        f"📅 *Date / Time :*  {s['date']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *Shift :*  {s['shift']}\n"
        f"📍 *Area :*  {s['area']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏭 *Equipment Status :*\n{s['equipment']}\n\n"
        f"⚠️ *Issues :*\n{s['issues']}\n\n"
        f"🔧 *Maintenance :*\n{s['maintenance']}\n\n"
        f"📝 *Remarks :*\n{s['remarks']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ _Submitted via Hand Over Bot_"
    )


# ══════════════════════════════════════════════════════════════
#  /start & /aide
# ══════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start', 'aide'])
def start(message):
    name = message.from_user.first_name or "Operator"
    text = (
        f"👋 *Welcome {name}!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 I'm the *Hand Over Bot* — Groupement Berkine.\n\n"
        f"📋 *How it works:*\n"
        f"  1️⃣  Press *Start Handover*\n"
        f"  2️⃣  Select your *Shift* then *Area*\n"
        f"  3️⃣  Fill in Equipment, Issues, Maintenance & Remarks\n"
        f"  4️⃣  Review the report → *Confirm* to publish\n\n"
        f"📌 *Commands:*\n"
        f"  /start — Show this message\n"
        f"  /annuler — Cancel current session\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Press the button below to begin!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    main_menu(message.chat.id)


# ══════════════════════════════════════════════════════════════
#  Cancel
# ══════════════════════════════════════════════════════════════
def do_cancel(chat_id, user_id):
    sessions.pop(user_id, None)
    bot.send_message(chat_id, "❌ *Session cancelled.*", parse_mode="Markdown")
    main_menu(chat_id)

@bot.message_handler(commands=['annuler'])
def annuler_cmd(message):
    do_cancel(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda m: m.text == "❌ Cancel")
def annuler_btn(message):
    do_cancel(message.chat.id, message.from_user.id)


# ══════════════════════════════════════════════════════════════
#  STEP 0 — Start Handover
# ══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🚀 Start Handover")
def handover_start(message):
    uid   = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")

    if done_today.get(uid) == today:
        bot.send_message(message.chat.id,
                         "⚠️ *You already submitted a Hand Over today.*\n"
                         "Contact your supervisor if you need to resubmit.",
                         parse_mode="Markdown")
        main_menu(message.chat.id)
        return

    sessions[uid] = {
        "nom":         message.from_user.full_name,
        "date":        datetime.now().strftime("%d/%m/%Y  %H:%M"),
        "shift":       "", "area":        "",
        "equipment":   "", "issues":      "",
        "maintenance": "", "remarks":     "",
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for s in SHIFTS:
        markup.add(s)
    markup.add("❌ Cancel")

    bot.send_message(message.chat.id,
                     "🔄 *Step 1 / 6* — Select your *Shift:*",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_area)


# ══════════════════════════════════════════════════════════════
#  STEP 1 — Area
# ══════════════════════════════════════════════════════════════
def step_area(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["shift"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for a in AREAS:
        markup.add(a)
    markup.add("❌ Cancel")

    bot.send_message(message.chat.id,
                     "📍 *Step 2 / 6* — Select your *Area:*",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_equipment)


# ══════════════════════════════════════════════════════════════
#  STEP 2 — Equipment status
# ══════════════════════════════════════════════════════════════
def step_equipment(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["area"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for e in ETATS:
        markup.add(e)
    markup.add("❌ Cancel")

    bot.send_message(message.chat.id,
                     "🏭 *Step 3 / 6* — *Equipment Status:*",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_issues)


# ══════════════════════════════════════════════════════════════
#  STEP 3 — Issues
# ══════════════════════════════════════════════════════════════
def step_issues(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["equipment"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Cancel")

    bot.send_message(message.chat.id,
                     "⚠️ *Step 4 / 6* — *Issues / Anomalies:*\n_(Type freely or press the button)_",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_maintenance)


# ══════════════════════════════════════════════════════════════
#  STEP 4 — Maintenance
# ══════════════════════════════════════════════════════════════
def step_maintenance(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["issues"] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Cancel")

    bot.send_message(message.chat.id,
                     "🔧 *Step 5 / 6* — *Maintenance done:*\n_(Type freely or press the button)_",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_remarks)


# ══════════════════════════════════════════════════════════════
#  STEP 5 — Remarks
# ══════════════════════════════════════════════════════════════
def step_remarks(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["maintenance"] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Cancel")

    bot.send_message(message.chat.id,
                     "📝 *Step 6 / 6* — *Additional Remarks:*\n_(Type freely or press the button)_",
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, step_preview)


# ══════════════════════════════════════════════════════════════
#  PREVIEW
# ══════════════════════════════════════════════════════════════
def step_preview(message):
    if message.text == "❌ Cancel":
        do_cancel(message.chat.id, message.from_user.id); return
    uid = message.from_user.id
    sessions[uid]["remarks"] = (
        "Nothing to report" if message.text == "🚫 Nothing to report" else message.text
    )
    _show_preview(message)


def _show_preview(message):
    uid  = message.from_user.id
    data = sessions.get(uid)
    if not data:
        bot.send_message(message.chat.id, "❌ Session expired.")
        main_menu(message.chat.id); return

    rapport = build_report(data)
    sessions[uid]["report"] = rapport

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Confirm & Publish", "✏️ Edit", "❌ Cancel")

    bot.send_message(message.chat.id, rapport, parse_mode="Markdown")
    bot.send_message(message.chat.id,
                     "👆 *Review your report.*\nConfirm to publish or Edit to modify.",
                     reply_markup=markup, parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
#  CONFIRM
# ══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "✅ Confirm & Publish")
def confirm(message):
    uid  = message.from_user.id
    data = sessions.get(uid)

    if not data or "report" not in data:
        bot.send_message(message.chat.id, "❌ No report found. Start again.")
        main_menu(message.chat.id); return

    try:
        bot.send_message(CHANNEL_ID, data["report"], parse_mode="Markdown")
        bot.send_message(message.chat.id,
                         "✅ *Hand Over published successfully!* 🎉",
                         reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id,
                         f"❌ *Publish error:*\n`{e}`\n\nMake sure the bot is *admin* in the channel.",
                         parse_mode="Markdown")

    done_today[uid] = datetime.now().strftime("%Y-%m-%d")
    sessions.pop(uid, None)
    main_menu(message.chat.id)


# ══════════════════════════════════════════════════════════════
#  EDIT MENU
# ══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "✏️ Edit")
def edit_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚙️ Equipment", "⚠️ Issues")
    markup.add("🔧 Maintenance", "📝 Remarks")
    markup.add("🔙 Back to preview", "❌ Cancel")
    bot.send_message(message.chat.id, "✏️ *What do you want to edit?*",
                     reply_markup=markup, parse_mode="Markdown")


def _ask_edit(message, label, key):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚫 Nothing to report", "❌ Cancel")
    bot.send_message(message.chat.id,
                     f"✏️ *Edit {label}:*\n_(Type the new value)_",
                     reply_markup=markup, parse_mode="Markdown")

    def save(msg):
        if msg.text == "❌ Cancel":
            do_cancel(msg.chat.id, msg.from_user.id); return
        sessions[msg.from_user.id][key] = (
            "Nothing to report" if msg.text == "🚫 Nothing to report" else msg.text
        )
        _show_preview(msg)

    bot.register_next_step_handler(message, save)


@bot.message_handler(func=lambda m: m.text == "⚙️ Equipment")
def edit_eq(m): _ask_edit(m, "Equipment Status", "equipment")

@bot.message_handler(func=lambda m: m.text == "⚠️ Issues")
def edit_is(m): _ask_edit(m, "Issues", "issues")

@bot.message_handler(func=lambda m: m.text == "🔧 Maintenance")
def edit_mn(m): _ask_edit(m, "Maintenance", "maintenance")

@bot.message_handler(func=lambda m: m.text == "📝 Remarks")
def edit_rm(m): _ask_edit(m, "Remarks", "remarks")

@bot.message_handler(func=lambda m: m.text == "🔙 Back to preview")
def back_btn(m): _show_preview(m)


# ══════════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════════
print("🤖 Hand Over Bot is running...")
bot.infinity_polling()
