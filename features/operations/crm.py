######## OPERATIONS: CRM — Leads, Clients, Creators
from config import *
from sqlalchemy import func
from features.operations.permissions import has_permission, get_role


def log_action(action, entity_type, entity_id, description, performed_by):
    db.ActivityLog.log(action, entity_type, entity_id, description, performed_by)


# ─── LEADS ──────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["newlead"])
def cmd_new_lead(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "sales"):
        bot.reply_to(message, "⛔ Only sales team can add leads.")
        return

    text = message.text.replace("/newlead", "", 1).strip()
    if not text:
        bot.reply_to(message, "Usage: /newlead Name | Company | Email | Phone | Source\nExample: /newlead John Doe | XYZ Corp | john@email.com | 555-0100 | ig_outreach")
        return

    parts = [p.strip() for p in text.split("|")]
    name = parts[0] if len(parts) > 0 else "Unknown"
    company = parts[1] if len(parts) > 1 else None
    email = parts[2] if len(parts) > 2 else None
    phone = parts[3] if len(parts) > 3 else None
    source = parts[4] if len(parts) > 4 else "manual"

    lead = db.Lead(name=name, email=email, phone=phone, company=company, source=source, assigned_to=user_id)
    lead.commit()
    log_action("lead_created", "lead", lead.id, f"New lead: {name} from {company or source}", user_id)
    bot.reply_to(message, f"✅ Lead created: {name}\nID: #{lead.id}\nSource: {source}")


@bot.message_handler(commands=["leads"])
def cmd_list_leads(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    status_filter = None
    parts = message.text.split()
    if len(parts) >= 2:
        status_filter = parts[1]

    query = db.session.query(db.Lead)
    if status_filter:
        query = query.filter_by(status=status_filter)
    leads = query.order_by(db.Lead.created_at.desc()).limit(20).all()

    if not leads:
        bot.reply_to(message, "No leads found.")
        return

    lines = [f"📋 <b>Leads ({status_filter or 'all'})</b>\n"]
    for l in leads:
        assignee = f" (→ {l.assigned_to})" if l.assigned_to else ""
        lines.append(f"#{l.id} {l.name} — {l.status} — ${l.estimated_value}{assignee}")
    bot.reply_to(message, "\n".join(lines[:25]), parse_mode="html")


# ─── CLIENTS ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["newclient"])
def cmd_new_client(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "sales"):
        bot.reply_to(message, "⛔ Only sales team can add clients.")
        return

    text = message.text.replace("/newclient", "", 1).strip()
    if not text:
        bot.reply_to(message, "Usage: /newclient Name | Company | Service | Monthly $\nServices: " + ", ".join(f"${v['price']} {k}" for k, v in db.SERVICE_CATALOG.items()))
        return

    parts = [p.strip() for p in text.split("|")]
    name = parts[0] if len(parts) > 0 else "Unknown"
    company = parts[1] if len(parts) > 1 else None
    service = parts[2] if len(parts) > 2 else None
    monthly = int(parts[3].replace("$", "").replace(",", "")) if len(parts) > 3 else 0

    client = db.Client(name=name, email=None, company=company, service=service, monthly_value=monthly, assigned_to=user_id)
    client.commit()
    log_action("client_created", "client", client.id, f"New client: {name} — ${monthly}/mo ({service})", user_id)
    bot.reply_to(message, f"✅ Client added: {name}\nService: {service}\nMonthly: ${monthly}")


@bot.message_handler(commands=["clients"])
def cmd_list_clients(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    clients = db.session.query(db.Client).filter_by(status="active").all()
    if not clients:
        bot.reply_to(message, "No active clients.")
        return

    total_mrr = sum(c.monthly_value or 0 for c in clients)
    lines = [f"🏢 <b>Active Clients ({len(clients)})</b>\nMRR: ${total_mrr}\n"]
    for c in clients:
        lines.append(f"• {c.name} — ${c.monthly_value}/mo — {c.service or 'N/A'}")
    bot.reply_to(message, "\n".join(lines), parse_mode="html")


# ─── CREATORS ──────────────────────────────────────────────────────────────

@bot.message_handler(commands=["newcreator"])
def cmd_new_creator(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "recruiter"):
        bot.reply_to(message, "⛔ Only recruiters can add creators.")
        return

    text = message.text.replace("/newcreator", "", 1).strip()
    if not text:
        bot.reply_to(message, "Usage: /newcreator Name | @telegram | @instagram | niches\nExample: /newcreator Jane Doe | @janedoe | @jane_ig | music,fashion")
        return

    parts = [p.strip() for p in text.split("|")]
    name = parts[0] if len(parts) > 0 else "Unknown"
    tg_handle = parts[1].strip("@") if len(parts) > 1 else None
    ig = parts[2].strip("@") if len(parts) > 2 else None
    niches = parts[3] if len(parts) > 3 else None

    creator = db.Creator(name=name, telegram_handle=tg_handle, instagram=ig, niches=niches)
    creator.commit()
    log_action("creator_added", "creator", creator.id, f"New creator: {name} ({ig}) — {niches}", user_id)
    bot.reply_to(message, f"✅ Creator added: {name}\nIG: @{ig}\nNiches: {niches}")


@bot.message_handler(commands=["creators"])
def cmd_list_creators(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    query = db.session.query(db.Creator)
    niche_filter = None
    parts = message.text.split()
    if len(parts) >= 2:
        niche_filter = parts[1]
        query = query.filter(db.Creator.niches.contains(niche_filter))

    creators = query.order_by(db.Creator.audience_size.desc()).limit(20).all()
    if not creators:
        bot.reply_to(message, "No creators found.")
        return

    total = len(creators)
    total_audience = sum(c.audience_size or 0 for c in creators)
    lines = [f"🎭 <b>Creators ({total})</b>\nTotal audience: {total_audience:,}\n"]
    for c in creators:
        lines.append(f"• {c.name} — @{c.instagram or 'N/A'} — {c.audience_size or 0} followers — {c.niches or 'N/A'}")
    bot.reply_to(message, "\n".join(lines[:25]), parse_mode="html")


# ─── REVENUE ───────────────────────────────────────────────────────────────

@bot.message_handler(commands=["revenue"])
def cmd_revenue(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    text = message.text.replace("/revenue", "", 1).strip()
    if text:
        # Record revenue
        parts = [p.strip() for p in text.split("|")]
        try:
            amount = int(parts[0].replace("$", "").replace(",", ""))
        except ValueError:
            bot.reply_to(message, "Usage: /revenue $amount | Source | Description\nExample: /revenue 500 | client_payment | Med Bros campaign")
            return
        source = parts[1] if len(parts) > 1 else "manual"
        desc = parts[2] if len(parts) > 2 else None
        rev = db.RevenueRecord(amount=amount, source=source, description=desc, recorded_by=user_id)
        rev.commit()
        log_action("revenue_recorded", "revenue", rev.id, f"${amount} from {source}", user_id)
        bot.reply_to(message, f"💰 Revenue recorded: ${amount} from {source}")
        return

    # Show revenue summary
    today = datetime.datetime.now().date()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)

    today_rev = db.session.query(db.func.sum(db.RevenueRecord.amount)).filter(
        db.func.date(db.RevenueRecord.recorded_at) == today
    ).scalar() or 0

    week_rev = db.session.query(db.func.sum(db.RevenueRecord.amount)).filter(
        db.RevenueRecord.recorded_at >= week_ago
    ).scalar() or 0

    month_rev = db.session.query(db.func.sum(db.RevenueRecord.amount)).filter(
        db.RevenueRecord.recorded_at >= month_ago
    ).scalar() or 0

    total_rev = db.session.query(db.func.sum(db.RevenueRecord.amount)).scalar() or 0

    text = (
        "💰 <b>Revenue Dashboard</b>\n\n"
        f"Today: <b>${today_rev}</b>\n"
        f"This Week: <b>${week_rev}</b>\n"
        f"This Month: <b>${month_rev}</b>\n"
        f"All Time: <b>${total_rev}</b>\n\n"
        "Record new: /revenue $amount | source | description"
    )
    bot.reply_to(message, text, parse_mode="html")


# ─── ACTIVITY LOG ──────────────────────────────────────────────────────────

@bot.message_handler(commands=["log"])
def cmd_activity_log(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "owner"):
        return

    entries = db.session.query(db.ActivityLog).order_by(db.ActivityLog.created_at.desc()).limit(15).all()
    if not entries:
        bot.reply_to(message, "No activity logged yet.")
        return

    lines = ["📜 <b>Recent Activity</b>\n"]
    for e in entries:
        time = e.created_at.strftime("%m/%d %H:%M")
        lines.append(f"• {time} — {e.action}: {e.description or e.entity_type or 'N/A'}")
    bot.reply_to(message, "\n".join(lines), parse_mode="html")
