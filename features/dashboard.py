from config import (
    bot, 
    dashboard_markup, 
    dashview_markup, 
    db,
    )


@bot.callback_query_handler(func=lambda call: call.data=="warns")
def warns(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    message_id = call.message.json['message_id']
    epush_user = db.Users.get(user_id)
    warns = epush_user.warns
    
    text = f"""
⚠️ <b>Warnings</b>

You have <b>{warns}/3</b> warnings.

3 warnings = permanent exile.
For help: /support YOUR_MESSAGE
    """
    bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=message_id,
        parse_mode="html",
        reply_markup=dashview_markup
    )

@bot.callback_query_handler(func=lambda call: call.data=="engagement")
def engagement(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    message_id = call.message.json["message_id"]
    epush_user = db.Users.get(user_id)
    engagements = epush_user.pool_count

    text = f"""
📊 <b>Engagements</b>

Successful engagements: <b>{engagements}</b>

🏆 Points: <b>{epush_user.points}</b>

Share an IG link in the group to start a new round!
    """
    bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=message_id,
        parse_mode="html",
        reply_markup=dashview_markup
    )

@bot.callback_query_handler(func=lambda call: call.data=="dashboard")
def dashboard(call):
    bot.answer_callback_query(call.id, text="dashboard")
    user_id = call.from_user.id
    message_id = call.message.json['message_id'] 
    epush_user = db.Users.get(user_id)
    
    dashboard_text = f"""
✦ <b>THE ENGAGEMENT</b>

👤 @{epush_user.username}
🏆 Points: {epush_user.points}
📊 Engagements: {epush_user.pool_count}
⚠️ Warnings: {epush_user.warns}/3

Share your IG link in the group to start a round. 📢
    """
    bot.send_message(
        chat_id=user_id,
        text=dashboard_text,
        parse_mode="html",
        reply_markup=dashview_markup
    )


@bot.message_handler(commands=["dashboard", "menu"])
def menu(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)

    dashboard_text = f"""
✦ <b>THE ENGAGEMENT</b>

👤 @{epush_user.username}
🏆 Points: {epush_user.points}
📊 Engagements: {epush_user.pool_count}
⚠️ Warnings: {epush_user.warns}/3

Share your IG link in the group to start a round. 📢
    """

    bot.send_message(
        user_id,
        text=dashboard_text,
        parse_mode="html",
        reply_markup=dashview_markup
    )


@bot.message_handler(commands=["points"])
def show_points(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user:
        bot.reply_to(message, "You're not registered. Send /start")
        return
    
    text = f"""
🏆 <b>Your Points</b>

<b>{epush_user.points}</b> points total
<b>{epush_user.pool_count}</b> engagements confirmed

+10 points per confirmed engagement!

Share a link in the group to earn more. 🚀
    """
    bot.reply_to(message, text, parse_mode="html")


@bot.message_handler(commands=["top"])
def leaderboard(message):
    from database.db import session as db_session
    from sqlalchemy import desc
    top_users = db_session.query(db.Users).filter(
        db.Users.points > 0
    ).order_by(desc(db.Users.points)).limit(10).all()

    if not top_users:
        bot.reply_to(message, "No points awarded yet. Be the first! 🏆")
        return

    lines = ["🏆 <b>Leaderboard</b> 🏆\n"]
    for i, u in enumerate(top_users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        lines.append(f"{medal} @{u.username} — {u.points} pts")
    lines.append("\n+10 points per engagement! Share your link 🚀")

    bot.reply_to(message, "\n".join(lines), parse_mode="html")
