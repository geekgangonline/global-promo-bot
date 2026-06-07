from config import *
from config import (
    bot,
    db,
    telebot,
)
from features.groups import TIERS, GROUPS


TIER2_NAMES = {
    "cypher": "🎤 THE CYPHER — Rapper feedback circle",
    "stream": "🎮 THE STREAM — Streamer engagement pod",
    "thread": "🧵 THE THREAD — Threads.net engagement",
    "runway": "👗 THE RUNWAY — Fashion collective",
    "dailygrind": "⏰ THE DAILY GRIND — Daily engagement grind",
}

TIER3_NAMES = {
    "soundwave": "🎵 THE SOUNDWAVE — Music engagement pod",
    "affiliates": "📱 THE AFFILIATES — UGC affiliate network",
    "hive": "🐝 THE GLOBAL HIVE — Small business network",
}


@bot.message_handler(commands=["join_tier2", "join-tier2"])
def join_tier2(message):
    """Show available Tier 2 groups to join"""
    user_id = message.from_user.id
    user = db.Users.get(user_id)
    if not user:
        bot.reply_to(message, "You're not registered. Send /start first.")
        return

    reg = db.UserGroupRegistration.get_or_create(user_id)
    current = set(reg.tier2_groups.split(",")) if reg.tier2_groups else set()

    text = "🌟 <b>Available Tier 2 Circles</b>\n\n"
    text += "Choose which groups you want to receive tasks in:\n\n"

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for key, label in TIER2_NAMES.items():
        status = "✅" if key in current else "⬜"
        markup.add(telebot.types.InlineKeyboardButton(
            text=f"{status} {label}",
            callback_data=f"t2_toggle_{key}"
        ))

    text += "\nTap any circle to toggle it on/off.\n"
    text += "Tasks will be pushed to circles you've joined."

    bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode="html",
        reply_markup=markup
    )


@bot.message_handler(commands=["join_tier3", "join-tier3"])
def join_tier3(message):
    """Request Tier 3 access (verified members only)"""
    user_id = message.from_user.id
    user = db.Users.get(user_id)
    if not user:
        bot.reply_to(message, "You're not registered. Send /start first.")
        return

    reg = db.UserGroupRegistration.get_or_create(user_id)
    if reg.tier3_verified:
        text = "✅ You're already verified for Tier 3 circles.\n\n"
        text += "<b>Available Tier 3 Circles:</b>\n"
        for key, label in TIER3_NAMES.items():
            text += f"• {label}\n"
        text += "\nPost your content in these groups to reach exclusive members."
        bot.send_message(chat_id=user_id, text=text, parse_mode="html")
        return

    text = (
        "🔒 <b>Tier 3 — Verified Members Only</b>\n\n"
        "Tier 3 circles are exclusive to verified members:\n"
        "• 🎵 THE SOUNDWAVE — Music pod\n"
        "• 📱 THE AFFILIATES — UGC affiliate network\n"
        "• 🐝 THE GLOBAL HIVE — Small business network\n\n"
        "To request verification, contact an admin.\n"
        "Send a message to the group admins to apply."
    )
    bot.send_message(chat_id=user_id, text=text, parse_mode="html")


@bot.message_handler(commands=["mytiers", "my_tiers"])
def my_tiers(message):
    """Show user's current tier registrations"""
    user_id = message.from_user.id
    user = db.Users.get(user_id)
    if not user:
        bot.reply_to(message, "You're not registered. Send /start first.")
        return

    reg = db.UserGroupRegistration.get(user_id)
    text = "👤 <b>Your Tier Registrations</b>\n\n"

    # Tier 1 — always active
    text += "🏆 <b>Tier 1 (Always Active):</b>\n"
    for key in TIERS["tier1"]:
        name = key.capitalize()
        text += f"   • THE {name.upper()}\n"

    # Tier 2
    text += "\n🌟 <b>Tier 2 (Your Selection):</b>\n"
    if reg and reg.tier2_groups:
        for key in reg.tier2_groups.split(","):
            label = TIER2_NAMES.get(key.strip(), key)
            text += f"   ✅ {label}\n"
    else:
        text += "   ⬜ None — use /join-tier2 to select\n"

    # Tier 3
    text += "\n🔒 <b>Tier 3 (Verified Only):</b>\n"
    if reg and reg.tier3_verified:
        for key in TIERS["tier3"]:
            label = TIER3_NAMES.get(key, key)
            text += f"   ✅ {label}\n"
    else:
        text += "   🔐 Not verified — use /join-tier3\n"

    text += "\nUse /join-tier2 to manage your selections."

    bot.send_message(chat_id=user_id, text=text, parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("t2_toggle_"))
def toggle_tier2(call):
    """Toggle a Tier 2 group registration"""
    user_id = call.from_user.id
    group_key = call.data.replace("t2_toggle_", "")

    reg = db.UserGroupRegistration.get_or_create(user_id)
    current = set(reg.tier2_groups.split(",")) if reg.tier2_groups else set()

    if group_key in current:
        reg.remove_tier2(group_key)
        status = "⬜ Removed from"
    else:
        reg.add_tier2(group_key)
        status = "✅ Added to"

    label = TIER2_NAMES.get(group_key, group_key)
    bot.answer_callback_query(call.id, f"{status} {label}")

    # Refresh the message
    current = set(reg.tier2_groups.split(",")) if reg.tier2_groups else set()
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for key, lbl in TIER2_NAMES.items():
        mark = "✅" if key in current else "⬜"
        markup.add(telebot.types.InlineKeyboardButton(
            text=f"{mark} {lbl}",
            callback_data=f"t2_toggle_{key}"
        ))

    bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
