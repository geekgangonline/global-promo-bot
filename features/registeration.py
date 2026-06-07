######## REGISTER
from config import *
import json, urllib.request

WHOP_API_KEY = os.getenv("WHOP_API_KEY")
WHOP_COMPANY_ID = os.getenv("WHOP_COMPANY_ID")


def sync_to_whop(user_id, name, email=None):
    """Mark user for Whop sync — stored locally since Whop leads require existing user_id.
    When the user signs up on Whop with the same email, they can be matched via /match-whop."""
    # Store user data locally for future cross-referencing
    u = db.Users.get(user_id)
    if u and email:
        u.email = email
        u.commit()
    print(f"[WHOP SYNC] Queued user {user_id} ({name}) for Whop cross-reference. Email: {email}")
    return None


def do_register(user_id, name, insta_username, email=None, referred_by=None):
    """Register or update a user's IG handle, return the user object"""
    username = insta_username.strip().strip("@")
    epush_user = db.Users.get(user_id)
    if epush_user:
        epush_user.username = username
        if email:
            epush_user.email = email
        if not epush_user.whop_id:
            whop_id = sync_to_whop(user_id, name, email or epush_user.email)
            if whop_id:
                epush_user.whop_id = whop_id
        epush_user.commit()
        return epush_user, f"✅ IG handle updated to @{username}"
    else:
        epush_user = db.Users(
            user_id=user_id,
            name=name,
            username=username,
            join_date=datetime.datetime.now(),
            email=email,
            referred_by=referred_by,
        )
        epush_user.commit()
        db.UserGroupRegistration.get_or_create(user_id)
        # Sync to Whop
        whop_id = sync_to_whop(user_id, name, email)
        if whop_id:
            epush_user.whop_id = whop_id
            epush_user.commit()
        # Generate referral code for the new user
        if not epush_user.referral_code:
            from features.referral import generate_referral_code
            epush_user.referral_code = generate_referral_code(user_id)
            epush_user.commit()
        return epush_user, f"✅ Welcome, @{username}. You're registered."


@bot.message_handler(commands=["register"])
def register_command(message):
    """/register — register or update your IG handle"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    chat_id = message.chat.id
    is_group = message.chat.type in ["group", "supergroup"]

    # Check if IG handle was provided in the command
    parts = message.text.split(maxsplit=2)
    if len(parts) >= 2:
        handle = parts[1]
        email = parts[2] if len(parts) >= 3 else None
        user, text = do_register(user_id, name, handle, email)
        bot.reply_to(message, text + "\n\nShare your IG link in the group to start earning 🚀\nUse /mytiers to see your active circles.", parse_mode="html")
        return

    # No handle provided — ask for it
    if is_group:
        bot.reply_to(
            message,
            "Send your Instagram username like this:\n"
            "<code>/register yourhandle</code>\n\n"
            "Or include your email for Whop sync:\n"
            "<code>/register yourhandle email@example.com</code>",
            parse_mode="html"
        )
    else:
        msg = bot.send_message(
            user_id,
            "Enter your Instagram username (e.g. @yourhandle):\n"
            "You can also add your email after (e.g. @yourhandle email@example.com)",
            reply_markup=force_reply
        )
        bot.register_for_reply_by_message_id(
            msg.message_id,
            handle_registration_reply_cmd
        )


def handle_registration_reply_cmd(message):
    """Handle reply to /register prompt"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    handle = message.text.strip()

    user, text = do_register(user_id, name, handle)
    bot.send_message(
        user_id,
        text + "\n\nShare your IG link in any Tier 1 group to start earning 🚀\nUse /mytiers to manage your circles.",
        parse_mode="html",
        reply_markup=dashboard_markup
    )


@bot.callback_query_handler(func=lambda call: call.data=="register_member")
def callback_hand(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    name = call.from_user.first_name
    message_id = call.message.json['message_id']
    epush_user = db.Users.get(user_id)
    if epush_user:
        username = epush_user.username
        text = f"""
You're already registered, {name}.
Your IG handle: <b>@{username}</b>

Want to change your username? Tap below.
        """
        bot.edit_message_text(
            text=text,
            chat_id=user_id,
            message_id=message_id,
            parse_mode="html",
            reply_markup=dashview_markup
        )
    else:
        msg = bot.send_message(
            user_id,
            "Enter your Instagram username (e.g. @yourhandle):",
            reply_markup=force_reply
        )
        bot.register_for_reply_by_message_id(
            msg.message_id,
            register_new_user
        )


def register_new_user(message):
    chat_id = message.chat.id
    handle = message.text
    name = message.from_user.first_name
    user_id = message.from_user.id

    user, text = do_register(user_id, name, handle)
    bot.send_message(
        chat_id,
        text=text + "\n\nShare your IG link in the group to start earning 🚀\nUse /mytiers to manage your circles.",
        parse_mode="html",
        reply_markup=dashboard_markup
    )


####### _change user
@bot.callback_query_handler(func=lambda call: call.data=="input_user")
def input_user(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    epush_user = db.Users.get(user_id)
    msg = bot.send_message(
        user_id,
        "Enter your new Instagram username (e.g. @yourhandle):",
        reply_markup=force_reply
    )
    bot.register_for_reply_by_message_id(
        msg.message_id,
        register_new_user
    )
