from config import *
from config import (
    bot,
    db,
    datetime,
    telebot,
)
from apscheduler.schedulers.background import BackgroundScheduler
from features.groups import get_group_tier, tier_chat_ids, TIERS, GROUPS
import re
import time


PUSH_WARN_DELAY_HOURS = 2
POINTS_PER_ENGAGEMENT = 10
COMMENTS_NEEDED = 5


def extract_ig_handle(url):
    match = re.search(r'instagram\.com/([A-Za-z0-9_.]+)', url)
    return match.group(1) if match else None


def auto_warn(round_id):
    """auto-warn all participants who didn't confirm engagement for a push"""
    round_obj = db.Rounds.get_round(round_id)
    if not round_obj:
        return
    for entry in round_obj.memberlist:
        if entry.engaged:
            continue
        user = db.Users.get(entry.user_id)
        if not user:
            continue
        warns = user.warning()
        text = f"""
⚠️ <b>Engagement Not Confirmed</b>

You didn't confirm the last engagement round.
Warnings: {warns}/3

Engage on the next round to avoid exile.
        """
        try:
            bot.send_message(
                chat_id=user.user_id,
                text=text,
                parse_mode="html"
            )
        except:
            pass


def build_target_groups(group_id, poster_user_id):
    """Determine which groups to push the task to based on tier"""
    orig_tier = get_group_tier(group_id)
    targets = set()

    # Tier 1 groups always receive all tasks
    for gid in tier_chat_ids("tier1"):
        targets.add(gid)

    if orig_tier == "tier1":
        # Also push to any Tier 2 groups the poster has registered for
        reg = db.UserGroupRegistration.get(poster_user_id)
        if reg and reg.tier2_groups:
            for key in reg.tier2_groups.split(","):
                gid = GROUPS.get(key.strip())
                if gid:
                    targets.add(gid)
    elif orig_tier == "tier2":
        # Push to the originating Tier 2 group + poster's other registered Tier 2s
        targets.add(group_id)
        reg = db.UserGroupRegistration.get(poster_user_id)
        if reg and reg.tier2_groups:
            for key in reg.tier2_groups.split(","):
                gid = GROUPS.get(key.strip())
                if gid:
                    targets.add(gid)
    else:
        # Tier 3 — push to Tier 1 only (already added above)
        pass

    return list(targets)


def push_post(post_link, poster_user_id, group_id):
    """trigger an engagement push for a shared post with new IG task format"""
    print(f"pushing post: {post_link} from user {poster_user_id}")

    poster = db.Users.get(poster_user_id)
    poster_name = poster.username if poster else "someone"
    ig_handle = extract_ig_handle(post_link) or poster_name

    # Build target groups based on tier
    target_groups = build_target_groups(group_id, poster_user_id)

    # Create a round representing this push
    push_round = db.Rounds.create_now(post_link=post_link, poster_user_id=poster_user_id)
    task_id = f"#{push_round.id}"

    # Formatted Instagram Task message
    task_msg = (
        f"🆕 New 📸 Instagram Task Available!\n\n"
        f"🆔 Task ID: {task_id}\n"
        f"👤 Created by: @{poster_name}\n"
        f"👤 Telegram User: @{poster_name}\n"
        f"📸 Post by: @{ig_handle}\n"
        f"💬 Comments needed: {COMMENTS_NEEDED}\n\n"
        f"👇 <b>Repost to your story + drop a real comment on the post.</b>\n\n"
        f"Click below to start earning!"
    )

    # Inline button
    engage_markup = telebot.types.InlineKeyboardMarkup()
    engage_btn = telebot.types.InlineKeyboardButton(
        text="🚀 Start Earning",
        callback_data=f"engage_task_{push_round.id}"
    )
    engage_markup.add(engage_btn)

    # Post task message to all target groups
    for gid in target_groups:
        try:
            bot.send_message(
                chat_id=gid,
                text=task_msg,
                parse_mode="html",
                disable_web_page_preview=True,
                reply_markup=engage_markup
            )
        except Exception as e:
            print(f"Could not send task to group {gid}: {e}")

    # Auto-enroll everyone except the poster
    all_users = db.Users.get_ids()
    for uid in all_users:
        user = db.Users.get(uid)
        if user and not user.blocked and user.user_id != poster_user_id:
            push_round.join(user)

    print(f"task {task_id} pushed to {len(target_groups)} groups, {len(push_round.memberlist)} members enrolled")

    # schedule auto-warn
    scheduler = BackgroundScheduler()
    warn_time = datetime.datetime.now() + datetime.timedelta(hours=PUSH_WARN_DELAY_HOURS)
    scheduler.add_job(auto_warn, "date", run_date=warn_time, args=[push_round.id])
    scheduler.start()

    print(f"auto-warn scheduled at {warn_time}")


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("engage_task_"))
def handle_engage_start(call):
    """When a user clicks 'Start Earning', DM them with engagement instructions"""
    user_id = call.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user:
        bot.answer_callback_query(call.id, "You're not registered. Send /start to me first.")
        return

    # Extract round ID from callback data
    round_id = int(call.data.split("_")[-1])
    push_round = db.Rounds.get_round(round_id)
    if not push_round:
        bot.answer_callback_query(call.id, "This task has expired.")
        return

    poster = db.Users.get(push_round.poster_user_id)
    poster_name = poster.username if poster else "someone"

    bot.answer_callback_query(call.id, "📩 Check your DMs!")

    done_markup = telebot.types.InlineKeyboardMarkup()
    done_btn = telebot.types.InlineKeyboardButton(
        text="✅ Done — Engaged ✅",
        callback_data="confirm_done"
    )
    done_markup.add(done_btn)

    text = (
        f"🚀 <b>Task {push_round.id} — Engage Now</b>\n\n"
        f"👤 Created by: @{poster_name}\n"
        f"📸 Post: <a href=\"{push_round.post_link}\">View on Instagram</a>\n\n"
        f"<b>Your mission:</b>\n"
        f"1️⃣ Open the post & <b>repost</b> to your story 📲\n"
        f"2️⃣ Drop a real comment ({COMMENTS_NEEDED}+ words) 💬\n"
        f"3️⃣ Like the post 💙\n"
        f"4️⃣ Tap <b>✅ Done</b> below\n\n"
        f"+{POINTS_PER_ENGAGEMENT} points for confirming! 🏆"
    )

    try:
        bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="html",
            reply_markup=done_markup
        )
    except Exception as e:
        print(f"Could not DM user {user_id}: {e}")


@bot.callback_query_handler(func=lambda call: call.data=="confirm_done")
def confirm_done(call):
    user_id = call.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user:
        bot.answer_callback_query(call.id, "You're not registered.")
        return

    all_rounds = db.Rounds.get_all()
    if not all_rounds:
        bot.answer_callback_query(call.id, "No active task.")
        return

    latest = all_rounds[-1]
    for entry in latest.memberlist:
        if entry.user_id == user_id:
            if entry.engaged:
                bot.answer_callback_query(call.id, "✅ Already confirmed! (+0 pts)")
                return
            entry.mark_engaged()
            points = epush_user.add_points(POINTS_PER_ENGAGEMENT)
            epush_user.engaged()
            bot.answer_callback_query(call.id, f"✅ Confirmed! +{POINTS_PER_ENGAGEMENT} pts 🏆")
            bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ <b>Confirmed.</b> You have {points} points total. Keep rising. 🔥\n\n"
                    f"Check /dashboard for your stats."
                ),
                parse_mode="html"
            )
            return

    bot.answer_callback_query(call.id, "You're not in this task.")


@bot.message_handler(commands=["round"])
def triggerround(message):
    """manual trigger for testing — pushes a fake post"""
    user_id = message.from_user.id
    user = db.Users.get(user_id)
    if not user:
        bot.reply_to(message, "You're not registered.")
        return
    test_link = f"https://www.instagram.com/{user.username}/"
    push_post(test_link, user_id, message.chat.id)
    bot.reply_to(message, f"Test push sent using your IG link: {test_link}")
