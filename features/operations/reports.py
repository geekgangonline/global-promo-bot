######## OPERATIONS: Daily & Weekly KPI Reports
from config import *
from features.operations.permissions import has_permission
from sqlalchemy import func
import os, json, urllib.request

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STAFF_CHAT_ID = os.getenv("STAFF_CHAT_ID")


def get_kpi_data():
    today = datetime.datetime.now().date()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)

    # Users
    total_users = db.session.query(db.Users).count()
    new_users_week = db.session.query(db.Users).filter(
        db.func.date(db.Users.join_date) >= week_ago
    ).count()

    # Revenue
    today_rev = db.session.query(func.sum(db.RevenueRecord.amount)).filter(
        db.func.date(db.RevenueRecord.recorded_at) == today
    ).scalar() or 0
    week_rev = db.session.query(func.sum(db.RevenueRecord.amount)).filter(
        db.RevenueRecord.recorded_at >= week_ago
    ).scalar() or 0
    month_rev = db.session.query(func.sum(db.RevenueRecord.amount)).filter(
        db.RevenueRecord.recorded_at >= month_ago
    ).scalar() or 0

    # Leads & Clients
    new_leads_week = db.session.query(db.Lead).filter(
        db.func.date(db.Lead.created_at) >= week_ago
    ).count()
    total_leads = db.session.query(db.Lead).count()
    active_clients = db.session.query(db.Client).filter_by(status="active").count()
    total_mrr = db.session.query(func.sum(db.Client.monthly_value)).filter_by(status="active").scalar() or 0

    # Creators
    total_creators = db.session.query(db.Creator).count()

    # Campaigns
    open_campaigns = db.session.query(db.Campaign).filter(
        db.Campaign.status.in_(["open", "in_progress"])
    ).count()
    pending_assignments = db.session.query(db.Assignment).filter(
        db.Assignment.status.in_(["assigned", "submitted"])
    ).count()

    # Engagement
    total_points = db.session.query(func.sum(db.Users.points)).scalar() or 0
    total_rounds = db.session.query(db.Rounds).count()

    return {
        "total_users": total_users,
        "new_users_week": new_users_week,
        "today_rev": today_rev,
        "week_rev": week_rev,
        "month_rev": month_rev,
        "new_leads_week": new_leads_week,
        "total_leads": total_leads,
        "active_clients": active_clients,
        "total_mrr": total_mrr,
        "total_creators": total_creators,
        "open_campaigns": open_campaigns,
        "pending_assignments": pending_assignments,
        "total_points": total_points,
        "total_rounds": total_rounds,
    }


def generate_ai_report(kpi):
    if not OPENAI_API_KEY:
        return None
    try:
        prompt = f"""You are the operations analyst for Global Promo TV. Generate a brief executive summary from these KPIs:

- Total Users: {kpi['total_users']} (New this week: {kpi['new_users_week']})
- Revenue Today: ${kpi['today_rev']}, This Week: ${kpi['week_rev']}, This Month: ${kpi['month_rev']}
- Leads: {kpi['total_leads']} total ({kpi['new_leads_week']} new this week)
- Active Clients: {kpi['active_clients']} (MRR: ${kpi['total_mrr']})
- Creators: {kpi['total_creators']}
- Open Campaigns: {kpi['open_campaigns']} (Pending assignments: {kpi['pending_assignments']})
- Points Awarded: {kpi['total_points']}

Write 2-3 sentences: what's the status, what needs attention, and one actionable recommendation."""
        data = json.dumps({"model": "gpt-4", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=data,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            method="POST"
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI report failed: {e}")
        return None


@bot.message_handler(commands=["report"])
def cmd_report(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    kpi = get_kpi_data()
    ai_summary = generate_ai_report(kpi)

    text = (
        "📊 <b>Executive Dashboard</b>\n\n"
        f"👥 Users: {kpi['total_users']} (+{kpi['new_users_week']} this week)\n"
        f"💰 Revenue Today: ${kpi['today_rev']} | Week: ${kpi['week_rev']} | Month: ${kpi['month_rev']}\n"
        f"📋 Leads: {kpi['total_leads']} (+{kpi['new_leads_week']} this week)\n"
        f"🏢 Active Clients: {kpi['active_clients']} (MRR: ${kpi['total_mrr']})\n"
        f"🎭 Creators: {kpi['total_creators']}\n"
        f"📢 Open Campaigns: {kpi['open_campaigns']} | Pending: {kpi['pending_assignments']}\n"
        f"🏆 Points: {kpi['total_points']}\n"
    )

    if ai_summary:
        text += f"\n🧠 <b>AI Analysis:</b>\n{ai_summary}"

    bot.reply_to(message, text, parse_mode="html")


def daily_morning_report():
    """Called by scheduler at 8 AM — sends to staff channel"""
    kpi = get_kpi_data()
    ai_summary = generate_ai_report(kpi)

    text = (
        "☀️ <b>Good Morning Team</b>\n\n"
        f"<b>Yesterday:</b>\n"
        f"💰 Revenue: ${kpi['today_rev']}\n"
        f"📋 New Leads: {kpi['new_leads_week']}\n"
        f"👥 New Users: {kpi['new_users_week']}\n\n"
        f"<b>Today's Focus:</b>\n"
        f"• Fill {kpi['pending_assignments']} pending assignment(s)\n"
        f"• Close {kpi['total_leads']} lead(s) in pipeline\n"
        f"• MRR Target: ${kpi['total_mrr']}\n"
    )
    if ai_summary:
        text += f"\n🧠 {ai_summary}"

    if STAFF_CHAT_ID:
        try:
            bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
        except Exception as e:
            print(f"Morning report send failed: {e}")
    print("Morning report sent.")


def daily_evening_report():
    """Called by scheduler at 5 PM"""
    kpi = get_kpi_data()
    ai_summary = generate_ai_report(kpi)

    # Top performers
    top_users = db.session.query(db.Users).order_by(db.Users.points.desc()).limit(3).all()
    top_text = ""
    if top_users:
        top_list = [f"• @{u.username} — {u.points} pts" for u in top_users if u.username]
        top_text = "Top Engagers:\n" + "\n".join(top_list) + "\n\n"

    text = (
        "🌙 <b>Evening Scoreboard</b>\n\n"
        f"💰 Revenue Closed Today: ${kpi['today_rev']}\n"
        f"📋 Leads Generated: {kpi['new_leads_week']}\n"
        f"👥 New Members: {kpi['new_users_week']}\n"
        f"🏢 Active Clients: {kpi['active_clients']} (MRR: ${kpi['total_mrr']})\n\n"
        f"{top_text}"
    )
    if ai_summary:
        text += f"🧠 {ai_summary}"

    if STAFF_CHAT_ID:
        try:
            bot.send_message(int(STAFF_CHAT_ID), text, parse_mode="html")
        except Exception as e:
            print(f"Evening report send failed: {e}")
    print("Evening report sent.")
