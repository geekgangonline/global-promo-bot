import datetime
import random
from config import bot
from database import db

PRIZES = [
    {"name": "🎤 Track Promotion 24h", "weight": 15, "desc": "Your track on Global Promo TV for 24 hours"},
    {"name": "⭐ Group Shoutout", "weight": 20, "desc": "Pinned shoutout in all three circles"},
    {"name": "💰 50 Bonus Points", "weight": 25, "desc": "+50 points credited to your account"},
    {"name": "🔁 Free Pass", "weight": 25, "desc": "One auto-confirmed engagement — zero effort"},
    {"name": "🎵 Producer Introduction", "weight": 10, "desc": "Connected with an industry producer"},
    {"name": "👑 The Grand Prize", "weight": 5, "desc": "Full promo package + 500 bonus points"},
]

def weighted_choice():
    total = sum(p["weight"] for p in PRIZES)
    r = random.uniform(0, total)
    upto = 0
    for p in PRIZES:
        upto += p["weight"]
        if r <= upto:
            return p
    return PRIZES[0]

def cooldown_remaining(user_id):
    last = db.SpinHistory.last_spin(user_id)
    if not last:
        return 0
    elapsed = (datetime.datetime.now() - last.spun_at).total_seconds()
    remaining = 86400 - elapsed  # 24 hours
    if remaining <= 0:
        return 0
    return int(remaining)

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"

@bot.message_handler(commands=['spin'])
def spin_wheel(message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    remaining = cooldown_remaining(user_id)
    if remaining > 0:
        bot.reply_to(
            message,
            f"⏳ You can spin again in {format_time(remaining)}.\n\n"
            f"Return later for another chance to win. 🎁"
        )
        return

    prize = weighted_choice()
    spin = db.SpinHistory(user_id, name, prize["name"])
    spin.commit()

    total = db.SpinHistory.total_spins(user_id)

    # Spinning animation
    msg = bot.reply_to(message, "🎰 *Spinning the wheel...*", parse_mode="Markdown")
    bot.edit_message_text(
        "🎰 *Spinning...* 🌀\n\n🔘🔘🔘🔘🔘🔘",
        message.chat.id, msg.message_id,
        parse_mode="Markdown"
    )
    import time
    time.sleep(0.5)
    bot.edit_message_text(
        f"🎰 *Result!*\n\n"
        f"🏆 *{prize['name']}*\n"
        f"📝 {prize['desc']}\n\n"
        f"Your spins: {total}\n\n"
        f"*More?* https://globalpromotv.vercel.app 🚀",
        message.chat.id, msg.message_id,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['spins'])
def my_spins(message):
    user_id = message.from_user.id
    total = db.SpinHistory.total_spins(user_id)
    last = db.SpinHistory.last_spin(user_id)
    last_prize = last.prize if last else "None yet"
    remaining = cooldown_remaining(user_id)

    text = (
        f"🎰 *Your Spin Stats*\n\n"
        f"Total spins: {total}\n"
        f"Last prize: {last_prize}\n"
        f"Next spin in: {format_time(remaining) if remaining > 0 else 'Ready now!'}\n\n"
        f"Spin again with /spin"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['leaderboard'])
def spin_leaderboard(message):
    from database.db import session as db_session
    from sqlalchemy import func
    results = db_session.query(
        db.SpinHistory.name,
        db.SpinHistory.prize,
        func.count(db.SpinHistory.id).label('count')
    ).group_by(db.SpinHistory.name).order_by(func.count(db.SpinHistory.id).desc()).limit(10).all()

    if not results:
        bot.reply_to(message, "No spins yet! Be the first with /spin")
        return

    lines = ["🏆 *Spin Leaderboard* 🏆\n"]
    for i, (name, prize, count) in enumerate(results, 1):
        lines.append(f"{i}. {name} — {count} spins")
    lines.append("\nSpin to win! /spin")

    bot.reply_to(message, "\n".join(lines), parse_mode="Markdown")
