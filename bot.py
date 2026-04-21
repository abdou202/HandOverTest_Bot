
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

# ---- تخزين مؤقت للبيانات (RAM) ----
sessions = {}

WARDIYAS = ["🌅 Day Shift  (07h–19h)", "🌙 Night Shift  (19h–07h)"]
ZONES    = [
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
ETATS    = ["✅ Normal — Aucune anomalie", "⚠️ Anomalie mineure", "🔴 Anomalie majeure / Arrêt"]
INTERVENTIONS = ["✅ Aucune intervention", "🔧 Maintenance préventive", "🚨 Intervention d'urgence", "🔩 Remplacement équipement"]

# ══════════════════════════════════════════════════════════════
#  /start  —  رسالة الترحيب
# ══════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "Operator"
    text = (
        f"👋 *Bienvenue {name} !*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 Je suis le *Bot Hand Over* du Groupement Berkine.\n\n"
        f"📋 *Comment ça marche ?*\n"
        f"  1️⃣  Tape /handover pour démarrer\n"
        f"  2️⃣  Réponds aux questions via les boutons\n"
        f"  3️⃣  Le rapport est publié automatiquement dans la chaîne\n\n"
        f"📌 *Commandes disponibles :*\n"
        f"  /handover — Créer un Hand Over\n"
        f"  /annuler  — Annuler en cours de route\n"
        f"  /aide     — Afficher ce message\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Prêt ? Lance */handover* !"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['aide'])
def aide(message):
    start(message)


# ══════════════════════════════════════════════════════════════
#  /annuler
# ══════════════════════════════════════════════════════════════
@bot.message_handler(commands=['annuler'])
def annuler(message):
    uid = message.from_user.id
    if uid in sessions:
        del sessions[uid]
    bot.send_message(message.chat.id, "❌ Hand Over *annulé*.\nTape /handover pour recommencer.", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
#  ÉTAPE 1 — /handover  →  choix de la wardiya
# ══════════════════════════════════════════════════════════════
@bot.message_handler(commands=['handover'])
def handover_start(message):
    uid = message.from_user.id
    sessions[uid] = {
        "nom": message.from_user.full_name,
        "date": datetime.now().strftime("%d/%m/%Y  %H:%M"),
        "wardiya": "", "zone": "", "etat": "",
        "intervention": "", "remarque": ""
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for w in WARDIYAS:
        markup.add(types.KeyboardButton(w))

    bot.send_message(
        message.chat.id,
        "🕐 *Étape 1 / 5* — Quelle est ta *wardiya* ?",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, step_zone)


# ══════════════════════════════════════════════════════════════
#  ÉTAPE 2 — Zone
# ══════════════════════════════════════════════════════════════
def step_zone(message):
    uid = message.from_user.id
    sessions[uid]["wardiya"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for z in ZONES:
        markup.add(types.KeyboardButton(z))

    bot.send_message(
        message.chat.id,
        "📍 *Étape 2 / 5* — What is your *Area* ?",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, step_etat)


# ══════════════════════════════════════════════════════════════
#  ÉTAPE 3 — État des installations
# ══════════════════════════════════════════════════════════════
def step_etat(message):
    uid = message.from_user.id
    sessions[uid]["zone"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for e in ETATS:
        markup.add(types.KeyboardButton(e))

    bot.send_message(
        message.chat.id,
        "🏭 *Étape 3 / 5* — *État des installations* ?",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, step_intervention)


# ══════════════════════════════════════════════════════════════
#  ÉTAPE 4 — Interventions
# ══════════════════════════════════════════════════════════════
def step_intervention(message):
    uid = message.from_user.id
    sessions[uid]["etat"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in INTERVENTIONS:
        markup.add(types.KeyboardButton(i))

    bot.send_message(
        message.chat.id,
        "🔧 *Étape 4 / 5* — *Interventions effectuées* ?",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, step_remarque)


# ══════════════════════════════════════════════════════════════
#  ÉTAPE 5 — Remarques libres
# ══════════════════════════════════════════════════════════════
def step_remarque(message):
    uid = message.from_user.id
    sessions[uid]["intervention"] = message.text

    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "📝 *Étape 5 / 5* — *Remarques supplémentaires ?*\n_(Écris librement ou tape `—` si aucune)_",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, step_publish)


# ══════════════════════════════════════════════════════════════
#  PUBLICATION dans la chaîne
# ══════════════════════════════════════════════════════════════
def step_publish(message):
    uid = message.from_user.id
    s = sessions[uid]
    s["remarque"] = message.text

    rapport = (
        f"📋 *HAND OVER — GROUPEMENT BERKINE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Operator :*  {s['nom']}\n"
        f"📅 *Date / Heure :*  {s['date']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *Shift :*  {s['wardiya']}\n"
        f"📍 *Area :*  {s['zone']}\n"
        f"🏭 *État installations :*  {s['etat']}\n"
        f"🔧 *Interventions :*  {s['intervention']}\n"
        f"📝 *Remarques :*  {s['remarque']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ _Rapport soumis via Bot Hand Over_"
    )

    try:
        bot.send_message(CHANNEL_ID, rapport, parse_mode="Markdown")
        bot.send_message(
            message.chat.id,
            "✅ *Hand Over publié avec succès dans la chaîne !* 🎉\n\nTape /handover pour un nouveau rapport.",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ *Erreur lors de la publication :*\n`{e}`\n\nVérifie que le bot est admin dans la chaîne.",
            parse_mode="Markdown"
        )

    del sessions[uid]


# ══════════════════════════════════════════════════════════════
#  LANCEMENT
# ══════════════════════════════════════════════════════════════
print("🤖 Bot Hand Over démarré...")
bot.infinity_polling()
