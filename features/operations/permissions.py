######## OPERATIONS: Role-Based Permissions
from config import *

TEAM_ROLES = {
    "owner": 100,
    "manager": 80,
    "recruiter": 50,
    "sales": 50,
    "creator": 10,
}

def get_role(user_id):
    staff = db.Staff.get(user_id)
    if staff and staff.active:
        return staff.role
    return "creator"

def has_permission(user_id, min_role="creator"):
    role = get_role(user_id)
    return TEAM_ROLES.get(role, 0) >= TEAM_ROLES.get(min_role, 0)

def require_role(min_role="creator"):
    """Decorator that checks role before executing command"""
    from functools import wraps
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            if not has_permission(user_id, min_role):
                bot.reply_to(message, "⛔ You don't have permission to use this command.")
                return
            return func(message, *args, **kwargs)
        return wrapper
    return decorator


# ─── STAFF MANAGEMENT ─────────────────────────────────────────────────────────

@bot.message_handler(commands=["addstaff"])
def add_staff(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "owner"):
        bot.reply_to(message, "⛔ Only the owner can manage staff.")
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /addstaff @telegram_handle role\nRoles: manager, recruiter, sales, creator")
        return

    handle = parts[1].strip("@")
    role = parts[2].lower()
    if role not in TEAM_ROLES:
        bot.reply_to(message, f"Invalid role. Choose: {', '.join(TEAM_ROLES.keys())}")
        return

    name = parts[3] if len(parts) >= 4 else handle
    staff_user = db.Users.get_username(handle)
    if not staff_user:
        bot.reply_to(message, f"User @{handle} hasn't registered in the bot yet.")
        return

    existing = db.Staff.get(staff_user.user_id)
    if existing:
        existing.role = role
        existing.name = name
        existing.active = True
        existing.commit()
        bot.reply_to(message, f"✅ @{handle} updated to role: {role}")
    else:
        staff = db.Staff(staff_user.user_id, name, role, handle)
        staff.commit()
        bot.reply_to(message, f"✅ @{handle} added as {role}")

    db.ActivityLog.log("staff_added", "staff", staff_user.user_id, f"@{handle} added as {role}", user_id)


@bot.message_handler(commands=["staff"])
def list_staff(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "manager"):
        bot.reply_to(message, "⛔ Permission denied.")
        return

    staff_list = db.session.query(db.Staff).filter_by(active=True).all()
    if not staff_list:
        bot.reply_to(message, "No staff members.")
        return

    lines = []
    for s in staff_list:
        handle = s.telegram_handle or str(s.user_id)
        lines.append(f"• @{handle} — {s.role}")
    bot.reply_to(message, "👥 <b>Team</b>\n\n" + "\n".join(lines), parse_mode="html")
