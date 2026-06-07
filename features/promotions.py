from config import bot, db, telebot
from features.groups import GROUPS, ENGAGEMENT_GROUPS, group_ids
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

WHOP_URL = "https://whop.com/global-promo-tv/"
CLIPFARM_URL = "https://globalpromotv.vercel.app/clipfarm"
GLOBALPROMO_URL = "https://globalpromotv.vercel.app"

DAILY_TARGETS = [
    "@globalpromotv",
    "@rapcap4promo",
    "@bigdrip.network",
    "@vishudoespr",
]


def daily_upsell():
    """Post daily upsell in THE LOUNGE promoting Whop + Global Promo TV"""
    lounge_id = GROUPS.get("lounge")
    if not lounge_id:
        return

    text = (
        "✦ *GLOBAL PROMO TV* ✦\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "*Promotion Packages*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🎬 Billboard & social media campaigns\n"
        "📱 Network distribution across 150+ countries\n"
        "📊 Real engagement metrics\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "*ClipFarm Community*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "✂️ The go-to clipping network for music, fashion & streamers\n"
        "🎵 Clip new music drops weekly\n"
        "👗 Fashion lookbook & runway campaigns\n"
        "🎮 Streamer highlight clips\n"
        "💰 Get paid weekly\n\n"
        f"▶️ Join free: {CLIPFARM_URL}\n\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🛒 Secure promotion: {WHOP_URL}\n"
        f"🌐 Global Promo TV: {GLOBALPROMO_URL}"
    )

    try:
        bot.send_message(
            chat_id=lounge_id,
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"daily_upsell error: {e}")


def engagement_reminder():
    """Send engagement motivation + daily targets to all active engagement groups"""
    targets = "\n".join([f"• {t} — Like + Comment" for t in DAILY_TARGETS])
    for key in ENGAGEMENT_GROUPS:
        gid = GROUPS.get(key)
        if not gid:
            continue

        top_users = _get_top_users(3)
        top_text = ""
        if top_users:
            top_text = "\n".join(
                [f"{i}. @{u.username} — {u.points} pts 🏆"
                 for i, (u,) in enumerate(top_users, 1)]
            )

        text = (
            "🎯 *Daily Engagement Round* 🎯\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "*Today's Engagement Targets:*\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"{targets}\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "*Your Mission:*\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "1️⃣ Post your content link below\n"
            "2️⃣ Like + comment on ALL of today's targets\n"
            "3️⃣ Follow @globalpromotv, @rapcap4promo, @bigdrip.network, @vishudoespr\n"
            "4️⃣ Confirm ✅ Done in DM\n"
            "5️⃣ Earn +10 points 🏆\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "*Leaderboard:*\n"
            "━━━━━━━━━━━━━━━━\n\n"
            + (top_text if top_text else "No points yet. Be the first! 🚀") +
            "\n\n━━━━━━━━━━━━━━━━\n\n"
             f"Want billboard promotion? → {GLOBALPROMO_URL}\n"
            f"✂️ Join the ClipFarm → {CLIPFARM_URL}\n"
            "━━━━━━━━━━━━━━━━\n"
            "Check /points | /top | /spin | /whop"
        )

        try:
            bot.send_message(
                chat_id=gid,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"engagement_reminder error for {key}: {e}")


def weekly_leaderboard_highlight():
    """Post leaderboard across all groups — top 5 get featured"""
    top_users = _get_top_users(5)
    if not top_users:
        return

    lines = ["👑 *Weekly Leaderboard* 👑\n"]
    for i, (u,) in enumerate(top_users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        lines.append(f"{medal} @{u.username} — {u.points} pts")

    lines.append("\n━━━━━━━━━━━━━━━━")
    lines.append("🏆 *Top 3 get featured on our billboard!*")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append(f"\nPost your links daily & climb the ranks 🚀")
    lines.append(f"\n{GLOBALPROMO_URL}")

    text = "\n".join(lines)

    for gid in group_ids().values():
        try:
            bot.send_message(
                chat_id=gid,
                text=text,
                parse_mode="Markdown"
            )
        except:
            pass


def network_showcase():
    """Post a full network showcase across all groups every 2 days"""
    showcase = (
        "🌐 *THE GLOBAL PROMO NETWORK* 🌐\n\n"
        "11 circles. One mission. Your success.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎮 *THE STREAM*\n"
        "Streamer engagement pod. Post your Twitch/Kick/YouTube links. "
        "Cross-promote with other streamers. Grow your audience through "
        "consistent engagement. Every view starts with a connection.\n\n"
        "🧵 *THE THREAD*\n"
        "Threads.net engagement. Share your threads, spark conversations, "
        "build your following on the fastest-growing text platform. "
        "Threads rewards activity — we make it consistent.\n\n"
        "👗 *THE RUNWAY*\n"
        "Fashion collective. Post your fits, looks, and style content. "
        "Get real feedback from people who care about fashion. "
        "Your style deserves to be seen.\n\n"
        "🎤 *THE CYPHER*\n"
        "Rapper engagement circle. Drop your tracks, get real criticism "
        "(5+ words required), and level up your sound. "
        "Real feedback beats fake praise every time.\n\n"
        "🎵 *THE SOUNDWAVE*\n"
        "Music engagement pod. All genres welcome. Share your music, "
        "discover new artists, build your fanbase. "
        "Good music finds its audience here.\n\n"
        "📱 *THE AFFILIATES*\n"
        "UGC affiliate network. Share your content, promote your links, "
        "connect with brands. Turn content into income. "
        "Your creativity has value — monetize it.\n\n"
        "🐝 *THE GLOBAL HIVE*\n"
        "Small business side hustle network. Entrepreneurs, freelancers, "
        "grinders. Share your offers, support each other, grow together. "
        "Your side hustle deserves a community.\n\n"
        "⏰ *THE DAILY GRIND*\n"
        "Daily engagement grind. Post content every day, engage daily, "
        "build the habit. Consistency compounds. "
        "Small daily wins create massive results.\n\n"
        "👥 *THE COLLECTIVE*\n"
        "Creative IG exchange. Curated content sharing for creators. "
        "Build real connections that turn into collaborations. "
        "Your network is your net worth.\n\n"
        "🌐 *THE LOUNGE*\n"
        "IG Engagement Max. 4+ word comments on 10 posts per round. "
        "High effort, maximum results. For those serious about growth. "
        "Also your gateway to Global Promo TV packages.\n\n"
        "✦ *THE ENGAGEMENT*\n"
        "Main engagement syndicate. The original pod. "
        "Post, engage, earn points, climb the ranks. "
        "Where it all started.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Follow all accounts:* @globalpromotv  @rapcap4promo  "
        "@bigdrip.network  @vishudoespr\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 *globalpromotv.vercel.app*\n"
        "🛒 *whop.com/global-promo-tv*\n"
        "✂️ *ClipFarm Community* → globalpromotv.vercel.app/clipfarm\n\n"
        "Which circle will you conquer today?"
    )

    for gid in group_ids().values():
        try:
            bot.send_message(
                chat_id=gid,
                text=showcase,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except:
            pass


def registration_reminder():
    """Post registration reminder in all groups asking members to register"""
    total_users = len(db.Users.get_ids())

    register_markup = telebot.types.InlineKeyboardMarkup()
    register_markup.add(telebot.types.InlineKeyboardButton(
        text="✅ Register Now",
        callback_data="register_member"
    ))

    text = (
        "📝 *Not registered yet?*\n\n"
        "You're in the group but your account isn't linked to the bot yet.\n\n"
        f"Currently **{total_users} members** are registered and earning points.\n\n"
        "Tap below to register your IG handle and start:\n"
        "• Earn +10 points per engagement 🏆\n"
        "• Get featured on our billboard\n"
        "• Access ClipFarm clipping community\n"
        "• Climb the /top leaderboard\n\n"
        "Or type: `/register @yourIGhandle`"
    )

    for gid in group_ids().values():
        try:
            bot.send_message(
                chat_id=gid,
                text=text,
                parse_mode="Markdown",
                reply_markup=register_markup,
                disable_web_page_preview=True
            )
        except:
            pass


def _get_top_users(limit=5):
    from database.db import session as db_session
    from sqlalchemy import desc
    return db_session.query(db.Users).filter(
        db.Users.points > 0
    ).order_by(desc(db.Users.points)).limit(limit).all()


# ─── Scheduler ────────────────────────────────────────────────

scheduler = BackgroundScheduler(timezone="UTC")

# Engagement reminders — 10am, 3pm, 7pm daily
scheduler.add_job(
    engagement_reminder,
    CronTrigger.from_crontab("0 10,15,19 * * *"),
    id="engagement_reminder"
)

# Daily upsell — 12pm daily in THE LOUNGE
scheduler.add_job(
    daily_upsell,
    CronTrigger.from_crontab("0 12 * * *"),
    id="daily_upsell"
)

# Weekly leaderboard highlight — Monday 9am
scheduler.add_job(
    weekly_leaderboard_highlight,
    CronTrigger.from_crontab("0 9 * * 1"),
    id="weekly_leaderboard"
)

# Registration reminder — daily at 2pm UTC (nudge unregistered members)
scheduler.add_job(
    registration_reminder,
    CronTrigger.from_crontab("0 14 * * *"),
    id="registration_reminder"
)

# Network showcase — every 2 days at 11am
from apscheduler.triggers.interval import IntervalTrigger
scheduler.add_job(
    network_showcase,
    IntervalTrigger(hours=48),
    id="network_showcase"
)

# ─── OPERATIONS JOBS ─────────────────────────────────────────────────────────

from features.operations.reports import daily_morning_report, daily_evening_report
from features.operations.team_motivation import morning_motivation, evening_scoreboard, check_assignments

# Morning executive report — 8 AM daily
scheduler.add_job(
    daily_morning_report,
    CronTrigger.from_crontab("0 8 * * *"),
    id="morning_report"
)

# Morning motivation — 8:30 AM daily
scheduler.add_job(
    morning_motivation,
    CronTrigger.from_crontab("30 8 * * *"),
    id="morning_motivation"
)

# Evening report — 5 PM daily
scheduler.add_job(
    daily_evening_report,
    CronTrigger.from_crontab("0 17 * * *"),
    id="evening_report"
)

# Evening scoreboard — 6 PM daily
scheduler.add_job(
    evening_scoreboard,
    CronTrigger.from_crontab("0 18 * * *"),
    id="evening_scoreboard"
)

# Assignment deadline check — every 4 hours
scheduler.add_job(
    check_assignments,
    IntervalTrigger(hours=4),
    id="assignment_check"
)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("✅ Promotion scheduler started")
        print(f"   Jobs: {[j.id for j in scheduler.get_jobs()]}")
