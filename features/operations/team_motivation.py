######## OPERATIONS: Team Motivation & Assignment Monitor
from config import *
from features.operations.reports import get_kpi_data
from sqlalchemy import func

STAFF_CHAT_ID = os.getenv("STAFF_CHAT_ID")
CREATOR_CHAT_ID = os.getenv("CREATOR_CHAT_ID")


def morning_motivation():
    """Send team motivation at 8:30 AM (called by scheduler)"""
    kpi = get_kpi_data()
    if not STAFF_CHAT_ID:
        print("No STAFF_CHAT_ID set, skipping motivation.")
        return

    text = (
        "☀️ <b>Rise & Grind — Global Promo TV</b>\n\n"
        "Yesterday's Scoreboard:\n"
        f"✅ Assignments Completed: {kpi['pending_assignments']}\n"
        f"💰 Revenue: ${kpi['today_rev']}\n"
        f"👥 New Creator Recruits: {kpi['new_users_week']}\n\n"
        "Today's Mission:\n"
        "🎯 Reach out to 50+ prospects\n"
        "🎯 Fill open campaign slots\n"
        "🎯 Close 1 new client\n\n"
        "Let's work. 💪"
    )
    try:
        bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
        print("Morning motivation sent.")
    except Exception as e:
        print(f"Morning motivation failed: {e}")


def evening_scoreboard():
    """Send end-of-day scoreboard (called by scheduler)"""
    if not STAFF_CHAT_ID:
        return

    kpi = get_kpi_data()
    top_recruiters = db.session.query(db.Staff).filter_by(active=True, role="recruiter").all()
    top_sales = db.session.query(db.Staff).filter_by(active=True, role="sales").all()

    text = (
        "🌙 <b>Daily Scoreboard</b>\n\n"
        f"💰 Revenue: ${kpi['today_rev']}\n"
        f"📋 New Leads: {kpi['new_leads_week']}\n"
        f"👥 Total Users: {kpi['total_users']}\n"
        f"📢 Open Campaigns: {kpi['open_campaigns']}\n\n"
        "Team:\n"
        f"• Recruiters: {len(top_recruiters)} active\n"
        f"• Sales: {len(top_sales)} active\n\n"
        "Tomorrow's Target:\n"
        f"🎯 ${kpi['total_mrr'] + 500} MRR\n\n"
        "Rest up. Tomorrow we go again. 🔥"
    )
    try:
        bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
    except Exception as e:
        print(f"Evening scoreboard failed: {e}")


def check_assignments():
    """Monitor for approaching deadlines — sends alerts"""
    if not STAFF_CHAT_ID:
        return

    now = datetime.datetime.now()
    soon = now + datetime.timedelta(hours=48)  # 48 hours from now

    urgent = db.session.query(db.Campaign).filter(
        db.Campaign.deadline <= soon,
        db.Campaign.deadline >= now,
        db.Campaign.status.in_(["open", "in_progress"])
    ).all()

    for campaign in urgent:
        remaining = campaign.slots_total - campaign.slots_filled
        deadline_str = campaign.deadline.strftime("%b %d at %H:%M")
        text = (
            f"⚠️ <b>URGENT: Assignment Deadline Approaching</b>\n\n"
            f"Campaign: {campaign.title}\n"
            f"Brand: {campaign.brand or 'N/A'}\n"
            f"Deadline: {deadline_str}\n"
            f"Slots Remaining: {remaining}/{campaign.slots_total}\n"
            f"Payout: ${campaign.payout}/slot\n\n"
            f"Recruiters: Fill these slots NOW!"
        )
        try:
            bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
        except Exception as e:
            print(f"Assignment alert failed: {e}")


def new_opportunity_alert(title, brand, payout, slots, description=""):
    """Send alert when a new Whop/brand opportunity comes in"""
    if not STAFF_CHAT_ID:
        return

    text = (
        f"🎯 <b>New Opportunity Available</b>\n\n"
        f"{title}\n"
        f"Brand: {brand}\n"
        f"Payout: ${payout}\n"
        f"Slots Available: {slots}\n"
        f"{description}\n\n"
        f"Action: Recruit creators ASAP"
    )
    try:
        bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
    except Exception as e:
        print(f"Opportunity alert failed: {e}")


# ─── COMMANDS ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["mission"])
def cmd_mission(message):
    """Show today's mission"""
    kpi = get_kpi_data()
    text = (
        "🎯 <b>Today's Mission</b>\n\n"
        f"Revenue Target: ${kpi['total_mrr'] + 500}\n"
        f"Leads to Close: {kpi['total_leads']}\n"
        f"Assignments to Fill: {kpi['pending_assignments']}\n"
        f"Creators to Recruit: 10\n\n"
        "Let's make it happen. 🚀"
    )
    bot.reply_to(message, text, parse_mode="html")
