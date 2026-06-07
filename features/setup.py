import requests
from config import bot, ADMIN, TOKEN

API = f"https://api.telegram.org/bot{TOKEN}"

def is_admin(user_id):
    return user_id in ADMIN

STORY = (
    "🍒 *IG ENGAGEMENT PROCESS* 🍒\n\n"
    "Das Engagement-Pod für Instagram — nur Emoji-Kommentare 😍🔥💯\n\n"
    "---\n"
    "*Was du bekommst:*\n"
    "✅ Echte Likes & Emoji-Kommentare auf jeden Post\n"
    "✅ Cross-Promotion in der Gruppe\n"
    "✅ Algorithmus-Boost durch Engagement-Signale\n"
    "✅ Punkte sammeln 🏆 für jede Teilnahme\n\n"
    "---\n"
    "*So einfach geht's:*\n"
    "1. Poste deinen IG-Link in der Gruppe\n"
    "2. Alle werden benachrichtigt\n"
    "3. Hinterlasse 😍🔥💯 auf den Posts der anderen\n"
    "4. Bestätige mit ✅ Done\n"
    "5. Sammle Punkte und wachse 📈\n\n"
    "---\n"
    "Los geht's mit `/start` — registriere deinen Handle und leg los! 🚀"
)

@bot.message_handler(commands=['story'])
def post_story(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Only admins can use /story")
        return
    bot.send_message(
        message.chat.id,
        STORY,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['setup'])
def setup_group(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "Only admins can run /setup")
        return

    if message.chat.type != 'private':
        bot.reply_to(message, "Run /setup in a private chat with the bot (not in a group)")
        return

    msg = bot.reply_to(message, "Creating engagement group...")

    r = requests.post(f"{API}/createNewGroupChat", json={
        "user_ids": [user_id],
        "title": "IG Engagement Process"
    })
    data = r.json()
    if not data.get("ok"):
        bot.edit_message_text(
            f"Failed to create group: {data.get('description', 'unknown error')}",
            message.chat.id, msg.message_id
        )
        return

    group_id = data["result"]["id"]

    # Set title & description
    requests.post(f"{API}/setChatDescription", json={
        "chat_id": group_id,
        "description": (
            "IG Engagement Process — Emoji-Kommentare 😍🔥💯 | "
            "Poste deinen IG-Link, like & kommentiere bei anderen, sammle Punkte 🏆"
        )
    })

    # Create invite link
    link_r = requests.post(f"{API}/createChatInviteLink", json={
        "chat_id": group_id,
        "member_limit": 0
    })
    link_data = link_r.json()
    invite_link = link_data.get("result", {}).get("invite_link", "N/A")

    welcome = (
        "🍒 *WILLKOMMEN BEIM IG ENGAGEMENT PROCESS* 🍒\n\n"
        "Instagram Engagement nur mit Emojis 😍🔥💯\n\n"
        "---\n"
        "*So funktioniert's:*\n"
        "1️⃣ Schick `/start` um dich zu registrieren\n"
        "2️⃣ Gib deinen IG-Handle ein (z.B. `@yourhandle`)\n"
        "3️⃣ Poste deinen IG-Link in der Gruppe\n"
        "4️⃣ Like 💙 + Emoji-Kommentar 😍🔥 bei anderen\n"
        "5️⃣ Bestätige mit ✅ Done im DM\n"
        "6️⃣ Sammle +10 Punkte pro Engagement 🏆\n\n"
        "---\n"
        "*Regeln:*\n"
        "• NUR Emoji-Kommentare 😍🔥💯👏 (kein Text nötig)\n"
        "• Like jeden Post in der Runde 💙\n"
        "• 3 Verwarnungen = Rauswurf\n\n"
        "---\n"
        "*Bereit zu wachsen?* Schick `/start`.\n\n"
        f"🔗 Einladungslink: {invite_link}"
    )

    send = requests.post(f"{API}/sendMessage", json={
        "chat_id": group_id,
        "text": welcome,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
    send_data = send.json()
    welcome_msg_id = send_data.get("result", {}).get("message_id")

    # Pin the welcome message
    if welcome_msg_id:
        requests.post(f"{API}/pinChatMessage", json={
            "chat_id": group_id,
            "message_id": welcome_msg_id
        })

    bot.edit_message_text(
        f"✅ *Gruppe erstellt!*\n\n"
        f"**Titel:** IG Engagement Process\n"
        f"**Einladungslink:** {invite_link}\n\n"
        f"Füge @GlobalPromo_bot als **Admin** in der Gruppe hinzu.\n\n"
        f"Mitglieder: `/start` → IG registrieren → loslegen!",
        message.chat.id, msg.message_id,
        parse_mode="Markdown"
    )
