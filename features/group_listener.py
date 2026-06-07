from config import *
from config import (
    bot,
    db,
    datetime,
    telebot,
    force_reply,
    dashboard_markup
)
from features.groups import get_group_tier, TIERS
import re

SOCIAL_PATTERNS = [
    r'(?:https?://)?(?:www\.)?instagram\.com/\w+[/]?',
    r'(?:https?://)?(?:www\.)?tiktok\.com/@\w+[/]?\S*',
    r'(?:https?://)?(?:www\.)?twitter\.com/\w+[/]?\S*',
    r'(?:https?://)?(?:www\.)?x\.com/\w+[/]?\S*',
    r'(?:https?://)?(?:www\.)?facebook\.com/\w+[/]?\S*',
    r'(?:https?://)?(?:www\.)?youtube\.com/\w+[/]?\S*',
    r'(?:https?://)?(?:www\.)?youtu\.be/\S+',
    r'(?:https?://)?(?:www\.)?threads\.net/@\w+[/]?\S*',
]

ENGAGEMENT_POINTS = 10

def find_social_link(text):
    for pattern in SOCIAL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.is_bot and member.id == bot.get_me().id:
            chat = message.chat
            existing = db.GroupChat.get(chat.id)
            if not existing:
                gc = db.GroupChat(
                    chat_id=chat.id,
                    title=chat.title,
                    invite_link=None
                )
                gc.commit()
                print(f"Bot added to group: {chat.title} ({chat.id})")
            return
        if member.is_bot:
            continue

        chat = message.chat
        existing = db.GroupChat.get(chat.id)
        if not existing:
            gc = db.GroupChat(chat_id=chat.id, title=chat.title)
            gc.commit()

        existing_user = db.Users.get(member.id)
        if existing_user:
            try:
                bot.send_message(
                    chat.id,
                    f"Welcome back, {member.first_name}. You're already registered as @{existing_user.username}."
                )
            except:
                pass
            continue

        # Group welcome with register button
        group_markup = telebot.types.InlineKeyboardMarkup()
        group_markup.add(telebot.types.InlineKeyboardButton(
            text="✅ Register Now",
            callback_data="register_member"
        ))
        bot.send_message(
            chat.id,
            f"👋 <b>Welcome, {member.first_name}!</b>\n\n"
            f"Drop your IG links → earn points 🏆 → get featured.\n\n"
            f"Tap <b>Register Now</b> below or send <code>/register @yourhandle</code> to begin.",
            parse_mode="html",
            reply_markup=group_markup
        )

        # Try DM — if it fails, registration is handled by the group button or /register
        try:
            msg = bot.send_message(
                member.id,
                f"Welcome to <b>{chat.title}</b>, {member.first_name}.\n\n"
                f"<b>How it works:</b>\n"
                f"1. Share your IG/TikTok link in the group\n"
                f"2. An <b>Instagram Task</b> is created 🆔\n"
                f"3. Task pushed to all <b>Tier 1</b> + your <b>Tier 2</b> groups\n"
                f"4. Members tap <b>🚀 Start Earning</b> to begin\n"
                f"5. Members repost + comment on your content\n"
                f"6. Confirm with <b>✅ Done</b> to earn <b>+{ENGAGEMENT_POINTS} points</b> 🏆\n\n"
                f"<b>Want more reach?</b> Use /join-tier2 to unlock specialty circles.\n"
                f"<b>Check your tiers:</b> /mytiers\n\n"
                f"Send me your Instagram username to register:\n\n"
                f"(e.g. @yourhandle)",
                reply_markup=force_reply
            )
            bot.register_for_reply_by_message_id(
                msg.message_id,
                handle_registration_reply,
                group_id=chat.id
            )
        except:
            # DM failed — user can register via group button or /register command
            pass


def handle_registration_reply(message, group_id=None):
    chat_id = message.chat.id
    insta_username = message.text.strip().strip("@")
    name = message.from_user.first_name
    user_id = message.from_user.id

    from features.registeration import do_register
    user, text = do_register(user_id, name, insta_username)

    bot.send_message(
        chat_id,
        text=text + "\n\n<b>Want access to Tier 2 groups?</b>\n"
                     f"Send <code>/join-tier2</code> to see available circles.\n\n"
                     f"Share your IG link in the group to start an engagement task.",
        parse_mode="html",
        reply_markup=dashboard_markup
    )

    if group_id:
        try:
            bot.send_message(
                group_id,
                f"🎉 {name} (@{insta_username}) is registered and ready to engage.\n\n"
                f"Welcome {name} to the circle."
            )
        except:
            pass


@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'], content_types=['text'])
def handle_group_link(message):
    if message.from_user.is_bot:
        return

    link = find_social_link(message.text)
    if not link:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    user = db.Users.get(user_id)
    if not user:
        register_markup = telebot.types.InlineKeyboardMarkup()
        register_markup.add(telebot.types.InlineKeyboardButton(
            text="✅ Register Now",
            callback_data="register_member"
        ))
        bot.reply_to(
            message,
            "⚠️ You need to register first.\n\n"
            "Send <code>/register @yourIGhandle</code> here or tap below.",
            parse_mode="html",
            reply_markup=register_markup
        )
        return

    tier = get_group_tier(chat_id)
    tier_label = tier.replace("tier", "Tier ") if tier else "Group"

    from features.round import push_post
    push_post(link, user_id, chat_id)

    bot.reply_to(
        message,
        f"📢 <b>Instagram Task Created!</b>\n\n"
        f"Your post has been pushed to all {tier_label} groups "
        f"across the network.\n"
        f"Members will repost, comment, and engage. 💪🔥\n\n"
        f"Track your points with /points",
        parse_mode="html"
    )
