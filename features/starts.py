from config import *
import time


@bot.message_handler(commands=["start", "Start"])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    # Check for referral code
    ref_code = None
    parts = message.text.split()
    if len(parts) >= 2:
        payload = parts[1]
        if payload.startswith("ref_"):
            ref_code = payload[4:]

    existing = db.Users.get(user_id)
    if existing:
        bot.send_message(
            user_id,
            f"Welcome back, {name}. You're registered as @{existing.username}.\n\n"
            f"Use /register @newhandle to change your IG handle.\n"
            f"Use /mytiers to manage your circles.\n"
            f"Use /dashboard for your stats.",
            parse_mode="html",
            reply_markup=dashboard_markup
        )
        return

    # Store referral code persistently for when user registers
    if ref_code:
        referrer = db.session.query(db.Users).filter(db.Users.referral_code == ref_code).first()
        if referrer:
            ref = db.PendingReferral(user_id=user_id, referrer_user_id=referrer.user_id)
            ref.commit()

    intro = f"""
✦ <b>THE ENGAGEMENT — GLOBAL PROMO NETWORK</b> ✦

Welcome to the syndicate, {name}.

<b>3-Tier Engagement System:</b>

🏆 <b>Tier 1</b> (Core — always active):
   THE ENGAGEMENT | THE LOUNGE | THE COLLECTIVE

🌟 <b>Tier 2</b> (Specialty — opt-in via /join-tier2):
   THE STREAM | THE THREAD | THE RUNWAY
   THE CYPHER | THE DAILY GRIND

🔒 <b>Tier 3</b> (Verified — /join-tier3):
   THE SOUNDWAVE | THE AFFILIATES | THE GLOBAL HIVE

<b>How it works:</b>
1️⃣ Share your IG link in any group
2️⃣ Bot creates a task 🆔 pushed to the network
3️⃣ Members tap 🚀 Start Earning to repost + comment
4️⃣ Confirm ✅ Done → +10 points 🏆

<b>Rules:</b>
• Drop real comments (4+ words in Lounge, 5+ in Cypher)
• Like every post you engage with 💙
• 3 warnings = permanent exile

"Your network is your net worth." 👑
    """

    bot.send_message(user_id, text=intro, parse_mode="html")
    time.sleep(1)

    # Immediately ask for IG handle
    msg = bot.send_message(
        user_id,
        "Send me your Instagram username to register:\n\n"
        "(e.g. @yourhandle or just yourhandle)",
        reply_markup=force_reply
    )
    bot.register_for_reply_by_message_id(
        msg.message_id,
        handle_start_registration
    )


def handle_start_registration(message):
    """Register user after /start flow"""
    chat_id = message.chat.id
    insta_username = message.text.strip().strip("@")
    name = message.from_user.first_name
    user_id = message.from_user.id

    # Apply pending referral if exists
    referred_by = db.PendingReferral.consume(user_id)

    from features.registeration import do_register
    user, text = do_register(user_id, name, insta_username, referred_by=referred_by)

    msg = text + "\n\nShare your IG link in any Tier 1 group to start earning 🚀\n"
    msg += "Use /join-tier2 to unlock more circles.\n"
    msg += "Use /mytiers to see your active groups."

    if referred_by:
        referrer = db.Users.get(referred_by)
        if referrer:
            msg += f"\n\n⭐ You were referred by @{referrer.username}!"
            referrer.points = (referrer.points or 0) + 50
            referrer.commit()

    bot.send_message(
        chat_id,
        text=msg,
        parse_mode="html",
        reply_markup=dashboard_markup
    )


@bot.message_handler(commands=['lang', 'Lang', "LANG"])
def lang(message):
    user_id = message.from_user.id
    bot.send_message(user_id, text="This bot operates in English only.", parse_mode="html")
