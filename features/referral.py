######## REFERRAL SYSTEM
from config import *
import random, string


def generate_referral_code(user_id):
    """Generate a unique referral code for a user"""
    raw = f"{user_id}{random.randint(1000,9999)}"
    code = "GPTV" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return code


@bot.message_handler(commands=["refer"])
def refer_command(message):
    """/refer — get your unique referral link to invite others"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    epush_user = db.Users.get(user_id)

    if not epush_user:
        bot.reply_to(message, "You need to /register first before you can refer others.")
        return

    if not epush_user.referral_code:
        epush_user.referral_code = generate_referral_code(user_id)
        epush_user.commit()

    code = epush_user.referral_code
    refer_link = f"https://t.me/GlobalPromo_bot?start=ref_{code}"
    whop_link = "https://whop.com/global-promo-tv"

    text = (
        f"<b>Your Referral Link</b>\n\n"
        f"Invite others to join Global Promo TV and earn <b>+50 bonus points</b> per referral!\n\n"
        f"🔗 <code>{refer_link}</code>\n\n"
        f"<b>How it works:</b>\n"
        f"1. Share your link anywhere — IG, email, Discord\n"
        f"2. When they join via your link and /register\n"
        f"3. You get <b>+50 points</b> instantly\n\n"
        f"Also invite them to join our Whop membership:\n"
        f"🛒 {whop_link}\n\n"
        f"Your code: <code>{code}</code>\n"
        f"Total referrals tracked automatically 🚀"
    )

    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, text, parse_mode="html")
    else:
        bot.send_message(user_id, text, parse_mode="html")


@bot.message_handler(commands=["referrals"])
def referrals_command(message):
    """/referrals — see how many people you've referred"""
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)

    if not epush_user:
        bot.reply_to(message, "You need to /register first.")
        return

    count = db.session.query(db.Users).filter(db.Users.referred_by == user_id).count()

    text = (
        f"<b>Your Referrals</b>\n\n"
        f"People you've referred: <b>{count}</b>\n"
        f"Points earned from referrals: <b>{count * 50}</b>\n\n"
        f"Share your link to earn more:\n"
        f"<code>https://t.me/GlobalPromo_bot?start=ref_{epush_user.referral_code}</code>"
    )
    bot.reply_to(message, text, parse_mode="html")
