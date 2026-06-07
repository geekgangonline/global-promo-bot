######## OPERATIONS: Campaign & Assignment Tracking
from config import *
from features.operations.permissions import has_permission
from sqlalchemy import func


@bot.message_handler(commands=["newcampaign"])
def cmd_new_campaign(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    text = message.text.replace("/newcampaign", "", 1).strip()
    if not text:
        bot.reply_to(message, "Usage: /newcampaign Title | Brand | Payout | Slots | Deadline(YYYY-MM-DD) | Type\nTypes: ugc, engagement, promotion, pr")
        return

    parts = [p.strip() for p in text.split("|")]
    title = parts[0]
    brand = parts[1] if len(parts) > 1 else None
    payout = int(parts[2].replace("$", "")) if len(parts) > 2 else 0
    slots = int(parts[3]) if len(parts) > 3 else 1
    deadline = datetime.datetime.strptime(parts[4], "%Y-%m-%d") if len(parts) > 4 and parts[4] else None
    ctype = parts[5] if len(parts) > 5 else "ugc"

    camp = db.Campaign(title=title, brand=brand, payout=payout, slots_total=slots, deadline=deadline, type=ctype)
    camp.commit()
    bot.reply_to(message, f"📢 Campaign created: {title}\nBrand: {brand}\nPayout: ${payout}/slot\nSlots: {slots}\nDeadline: {deadline or 'N/A'}")

    # Post to staff channel
    staff_chat_id = os.getenv("STAFF_CHAT_ID")
    if staff_chat_id:
        try:
            bot.send_message(int(staff_chat_id),
                f"📢 <b>New Campaign</b>\n\n{title}\nBrand: {brand}\nPayout: ${payout}\nSlots: {slots}\nDeadline: {deadline or 'N/A'}\n\nUse /assign to fill slots.",
                parse_mode="html")
        except:
            pass


@bot.message_handler(commands=["campaigns"])
def cmd_list_campaigns(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "recruiter"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    campaigns = db.session.query(db.Campaign).filter(db.Campaign.status.in_(["open", "in_progress"])).all()
    if not campaigns:
        bot.reply_to(message, "No open campaigns.")
        return

    lines = ["📢 <b>Open Campaigns</b>\n"]
    for c in campaigns:
        remaining = c.slots_total - c.slots_filled
        deadline = c.deadline.strftime("%b %d") if c.deadline else "No deadline"
        lines.append(f"• <b>{c.title}</b> — ${c.payout}/slot — {remaining} slots left — Due {deadline}")
    bot.reply_to(message, "\n".join(lines), parse_mode="html")


@bot.message_handler(commands=["assign"])
def cmd_assign_creator(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "recruiter"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    text = message.text.replace("/assign", "", 1).strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /assign campaign_id | @creator_handle\nFind campaign IDs with /campaigns")
        return

    try:
        campaign_id = int(parts[0])
    except ValueError:
        bot.reply_to(message, "Campaign ID must be a number.")
        return

    handle = parts[1].strip("@")
    creator = db.session.query(db.Creator).filter(
        (db.Creator.telegram_handle == handle) | (db.Creator.instagram == handle)
    ).first()

    if not creator:
        bot.reply_to(message, f"Creator @{handle} not found. Add them with /newcreator first.")
        return

    campaign = db.Campaign.get(db.Campaign, campaign_id)
    if not campaign:
        bot.reply_to(message, f"Campaign #{campaign_id} not found.")
        return

    if campaign.slots_filled >= campaign.slots_total:
        bot.reply_to(message, "This campaign is fully booked.")
        return

    assignment = db.Assignment(campaign_id=campaign_id, creator_id=creator.id)
    assignment.commit()
    campaign.slots_filled += 1
    campaign.commit()

    bot.reply_to(message, f"✅ {creator.name} assigned to {campaign.title}\nSlots remaining: {campaign.slots_total - campaign.slots_filled}")


@bot.message_handler(commands=["assignments"])
def cmd_list_assignments(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    assignments = db.session.query(db.Assignment).join(db.Campaign).filter(
        db.Assignment.status.in_(["assigned", "submitted"])
    ).limit(20).all()

    if not assignments:
        bot.reply_to(message, "No pending assignments.")
        return

    lines = ["📋 <b>Pending Assignments</b>\n"]
    for a in assignments:
        creator = db.session.query(db.Creator).filter_by(id=a.creator_id).first()
        campaign = db.session.query(db.Campaign).filter_by(id=a.campaign_id).first()
        cname = creator.name if creator else "Unknown"
        ctitle = campaign.title if campaign else "Unknown"
        deadline = campaign.deadline.strftime("%b %d") if campaign and campaign.deadline else "N/A"
        lines.append(f"• {cname} → {ctitle} — {a.status} — Due {deadline}")
    bot.reply_to(message, "\n".join(lines), parse_mode="html")
