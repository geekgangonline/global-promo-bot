from config import *
from features.groups import GROUPS, TIERS, tier_chat_ids

def listToString(s):
    str1 = """"""
    for ele in s:
        str1 += (ele+"""
""")
    return str1

def warn_status(stype=None):
    all_epush_users = db.Users.get_users()
    list_insta = ["@"+i.username+" - "+"⚠️ "+str(i.warns)+" | 🏆 "+str(i.points) for i in all_epush_users]
    if stype=='ids':
        list_insta = ["@"+i.username+" - ID "+str(i.user_id)+" | 🏆 "+str(i.points) for i in all_epush_users]
    list_string = listToString(list_insta)
    list_text = f"""
👥 Member Status — /warn @user to warn

{list_string}
"""
    return list_text


@bot.message_handler(commands=["warn"])
def admin_view(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if epush_user.user_id in ADMIN:
        findall = re.findall('@[\w\.]+', message.text)
        if findall:
            for item in findall:
                itemi=item.strip("@")
                warn_user=db.Users.get_username(itemi)
                if warn_user:
                    warn_user.warning()
                    warn_user.commit()
                    text = f"""
<b>🔻WARNING {warn_user.warns}/3🔻</b>
You failed to confirm the last engagement.
                    """
                    if warn_user.warns>=3:
                        text = f"""
<b>🔻WARNING {warn_user.warns}/3 — EXILED🔻</b>
You have been removed for 3 warnings.
Contact /support for help.
                        """
                    bot.send_message(
                        warn_user.user_id,
                        text=text,
                        parse_mode="html"
                    )
                else:
                    bot.send_message(
                        user_id,
                        text=f"🔴 {item} not found",
                        parse_mode="html"
                    )
    
        list_text = warn_status()
        bot.send_message(
            user_id,
            text=list_text,
            parse_mode="html"
        )
    else:
        bot.send_message(user_id, text="Access denied.")

        
@bot.message_handler(commands=["free"])
def free(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if epush_user.user_id in ADMIN:
        findall = re.findall('@[\w\.]+', message.text)
        if findall:
            for item in findall:
                itemi=item.strip("@")
                warn_user=db.Users.get_username(itemi)
                if warn_user:
                    warn_user.warns = 0
                    warn_user.blocked = False
                    warn_user.commit()
                    bot.send_message(
                        warn_user.user_id,
                        text="✅ You've been reinstated. Engage with purpose.",
                        parse_mode="html"
                    )
                else:
                    bot.send_message(
                        user_id,
                        text=f"🔴 {item} not found",
                        parse_mode="html"
                    )
    
        list_text = warn_status()
        bot.send_message(
            user_id,
            text=list_text,
            parse_mode="html"
        )
    else:
        bot.send_message(user_id, text="Access denied.")


@bot.message_handler(commands=["delete"])
def delete_user(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if epush_user.user_id in ADMIN:
        findall = re.findall('@[\w\.]+', message.text)
        if findall:
            for item in findall:
                itemi=item.strip("@")
                del_user=db.Users.get_username(itemi)
                if del_user:
                    del_user.delete()
                    bot.send_message(
                        del_user.user_id,
                        text="You've been removed. /start to re-register.",
                        parse_mode="html"
                    )
                else:
                    bot.send_message(
                        user_id,
                        text=f"🔴 {item} not found",
                        parse_mode="html"
                    )
    
        list_text = warn_status()
        bot.send_message(
            user_id,
            text=list_text,
            parse_mode="html"
        )
    else:
        bot.send_message(user_id, text="Access denied.")


WELCOME_BROADCAST = (
    "🌐 *WELCOME TO THE GLOBAL PROMO NETWORK* 🌐\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "We run on a *3-Tier engagement system* — the most structured "
    "growth network on Telegram. Here's how it works.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🏆 *TIER 1 — CORE CIRCLES (Always Active)*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Post a link → it's pushed to ALL Tier 1 groups + your selected Tier 2 groups.\n\n"
    "✦ *THE ENGAGEMENT* — Main syndicate. Post, engage, earn.\n"
    "✦ *THE LOUNGE* — IG Engagement Max. 4+ word comments, link proof.\n"
    "✦ *THE COLLECTIVE* — Creative exchange. Build real connections.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🌟 *TIER 2 — SPECIALTY CIRCLES (Opt-In)*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Use `/join-tier2` to activate any of these:\n\n"
    "🎮 THE STREAM — Streamer cross-promotion pod\n"
    "🧵 THE THREAD — Threads.net engagement circle\n"
    "👗 THE RUNWAY — Fashion collective\n"
    "🎤 THE CYPHER — Rapper feedback (5+ word criticism)\n"
    "⏰ THE DAILY GRIND — Daily engagement habit\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔒 *TIER 3 — VERIFIED CIRCLES*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Exclusive access. Contact admin to verify.\n\n"
    "🎵 THE SOUNDWAVE — Music engagement pod\n"
    "📱 THE AFFILIATES — UGC affiliate network\n"
    "🐝 THE GLOBAL HIVE — Small business network\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "*HOW TO USE THE NETWORK*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "1️⃣ Post your IG/TikTok/Twitter link in any Tier 1 group\n"
    "2️⃣ The bot creates an *Instagram Task* with Task ID 🆔\n"
    "3️⃣ Task is pushed to all Tier 1 groups + your active Tier 2 groups\n"
    "4️⃣ Members tap *🚀 Start Earning* to begin\n"
    "5️⃣ Members repost your content + drop a real comment\n"
    "6️⃣ They confirm with *✅ Done* — you both earn +10 pts 🏆\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "*DAILY ENGAGEMENT REMINDERS*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Daily targets posted at 10am / 3pm / 7pm UTC.\n"
    "Follow + engage on all target accounts.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "*POINTS & REWARDS*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "• +10 pts per confirmed engagement\n"
    "• /points — Check your balance\n"
    "• /top — Leaderboard\n"
    "• /spin — Try your luck\n"
    "• /mytiers — Your active groups\n"
    "• Top 3 weekly → featured on Global Promo TV billboard 🏆\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌐 globalpromotv.vercel.app\n"
    "🛒 whop.com/global-promo-tv\n\n"
    "Follow our network:\n"
    "@globalpromotv  @rapcap4promo  @bigdrip.network  @vishudoespr\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "Ready. Set. Rise. 👑"
)


@bot.message_handler(commands=["welcome", "broadcast"])
def broadcast_welcome(message):
    """Admin-only: send updated welcome to all 11 groups"""
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user or epush_user.user_id not in ADMIN:
        bot.reply_to(message, "Access denied.")
        return

    sent = 0
    failed = 0
    for gid in GROUPS.values():
        if not gid:
            continue
        try:
            bot.send_message(
                chat_id=gid,
                text=WELCOME_BROADCAST,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            sent += 1
        except Exception as e:
            print(f"broadcast_welcome failed for {gid}: {e}")
            failed += 1

    bot.reply_to(
        message,
        f"✅ Welcome broadcast sent to {sent} groups. "
        f"Failed: {failed}."
    )


@bot.message_handler(regexp='allusers')
def allusers(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if epush_user.user_id in ADMIN:
        list_text = warn_status(stype='ids')
        bot.send_message(
            user_id,
            text=list_text,
            parse_mode="html"
        )


@bot.message_handler(regexp='test_round\s\d+')
def test_round(message):
    user_id = message.from_user.id
    round_started = db.Rounds.get_lastRound()
    test_num = int(message.text.split(" ")[-1])
    if not round_started:
        bot.send_message(user_id, text="No rounds exist yet. Start one first.", parse_mode="html")
        return
    if round_started.drop_duration():
        for i in range(test_num):
            test_user = db.Users(
                user_id=90909000+i,
                name=f"test_user {i}",
                username=f"test_user{i}",
                join_date=datetime.datetime.now()
            )
            round_started.join(test_user)
        bot.send_message(
            user_id,
            text=f"✅ {test_num} test users registered",
            parse_mode="html"
        )
    else:
        bot.send_message(
            user_id,
            text="⏳ Drop session for last round has ended",
            parse_mode="html"
        )


@bot.message_handler(commands=["geninvites"])
def admin_geninvites(message):
    """Generate permanent invite links for all groups (admin only)"""
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user or epush_user.user_id not in ADMIN:
        return

    bot.reply_to(message, "Generating invite links for all groups...")

    for name, chat_id in GROUPS.items():
        try:
            invite = bot.create_chat_invite_link(chat_id, member_limit=0)
            print(f"[INVITE] {name}: {invite.invite_link}")
            bot.send_message(
                user_id,
                f"🔗 <b>{name.upper()}</b>\n{invite.invite_link}",
                parse_mode="html"
            )
        except Exception as e:
            bot.send_message(
                user_id,
                f"❌ <b>{name.upper()}</b> — {e}",
                parse_mode="html"
            )


@bot.message_handler(commands=["sync-whop"])
def admin_sync_whop(message):
    """List all registered users ready for Whop cross-reference (admin only)"""
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user or epush_user.user_id not in ADMIN:
        return

    users = db.session.query(db.Users).filter(db.Users.email.isnot(None)).all()
    if not users:
        bot.reply_to(message, "No users with emails to cross-reference.")
        return

    lines = []
    for u in users:
        whop_status = "✅ Synced" if u.whop_id else "⏳ Pending"
        lines.append(f"• @{u.username} — {u.email} — {whop_status}")

    text = (
        f"📋 <b>Users ready for Whop cross-reference:</b>\n\n"
        + "\n".join(lines) +
        f"\n\nTotal: {len(users)} users with emails"
    )
    bot.send_message(user_id, text, parse_mode="html")


@bot.message_handler(commands=["whop-members"])
def admin_whop_members(message):
    """Fetch Whop members and cross-reference with Telegram users (admin only)"""
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    if not epush_user or epush_user.user_id not in ADMIN:
        return

    bot.reply_to(message, "Fetching Whop members...")

    import urllib.request, json
    from features.registeration import WHOP_API_KEY, WHOP_COMPANY_ID
    try:
        req = urllib.request.Request(
            f"https://api.whop.com/api/v1/members?company_id={WHOP_COMPANY_ID}&limit=50",
            headers={"Authorization": f"Bearer {WHOP_API_KEY}"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        members = data.get("data", [])

        if not members:
            bot.send_message(user_id, "No Whop members found.")
            return

        lines = []
        matched = 0
        for m in members:
            mu = m.get("user", {})
            mem_email = mu.get("email", "")
            mem_name = mu.get("name", "").strip()
            mem_username = mu.get("username", "")

            # Check if this email matches any Telegram user
            tg_user = db.session.query(db.Users).filter(db.Users.email == mem_email).first()
            if tg_user:
                icon = "🔄"
                matched += 1
                match_info = f" → @{tg_user.username} (TG)"
            else:
                icon = "🔵"
                match_info = ""

            lines.append(f"{icon} {mem_name} ({mem_email}){match_info}")

        text = (
            f"📊 <b>Whop Members ({len(members)} total)</b>\n"
            f"Matched with Telegram: {matched}\n\n"
            + "\n".join(lines[:30])
        )
        if len(members) > 30:
            text += f"\n... and {len(members)-30} more"

        bot.send_message(user_id, text, parse_mode="html")

    except Exception as e:
        bot.send_message(user_id, f"❌ Error fetching Whop members: {e}")
