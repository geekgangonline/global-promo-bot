from config import *
from config import ADMIN,bot

WHOP_URL = "https://whop.com/global-promo-tv/"
CLIPFARM_URL = "https://globalpromotv.vercel.app/clipfarm"

@bot.message_handler(commands=["whop", "clipfarm"])
def whop_cmd(message):
    """Send user to the ClipFarm Whop community"""
    user_id = message.from_user.id
    text = (
        "✂️ *ClipFarm — Music, Fashion & Streamer Network*\n\n"
        "The go-to clipping community for creators.\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "*What you get:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🎵 Clip new music drops weekly\n"
        "👗 Fashion lookbook & runway campaigns\n"
        "🎮 Streamer & gamer highlight clips\n"
        "💰 Get paid weekly via Stripe\n"
        "📈 Your clips distributed across our network\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "Whether you're a beginner or a pro,\n"
        "this is where creators turn clips into income.\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"▶️ [Join Free on Whop]({WHOP_URL})\n"
        f"🌐 [Learn More]({CLIPFARM_URL})"
    )
    bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

def support_response(message, sender_id, message_id):
    response = message.text
    response_text = f"""
<b>📨 SUPPORT RESPONSE</b>

<pre>🗣️{response}</pre>"""
    bot.send_message(
        sender_id,
        text=response_text,
        parse_mode="html",
        reply_to_message_id=message_id
    )

@bot.message_handler(commands=["support"])
def support(message):
    sender_id = message.from_user.id
    message_id = message.message_id
    sender = db.Users.get(sender_id)
    complaint = message.text.replace("/support", "")
    if complaint:
        refer = f"""
<b>📨 NEW SUPPORT REQUEST FROM </b><a href="tg://user?id={sender_id}">@{sender.username}</a>

<pre>🗣️ <i>{complaint}</i></pre>

<pre><em>Reply to this message to respond to @{sender.username}</em></pre>
        """
        for i in ADMIN:    
            outgoing = bot.send_message(
                i,
                text=refer,
                parse_mode="html"
            )
            outgoing_id = outgoing.message_id
            bot.register_for_reply_by_message_id(outgoing_id, support_response, sender_id, message_id)
    else:
        bot.send_message(
            sender_id,
            text="❌ /support must be followed by your message\n<pre>e.g. /support Please reinstate my account</pre>",
            parse_mode="html",
            reply_to_message_id=message_id
        )
