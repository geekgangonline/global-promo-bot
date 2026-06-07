from config import bot

GAME_URL = "https://globalpromotv.vercel.app"

@bot.message_handler(commands=['game'])
def game_command(message):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Visit Global Promo TV", url=GAME_URL))

    bot.reply_to(
        message,
        "🚀 *Global Promo TV*\n\n"
        "Premium Artist Promotion:\n"
        "• Billboard-style Music Video Display 📺\n"
        "• Social Media Campaigns 📱\n"
        "• Industry-Grade Exposure 🌐\n\n"
        "Discover more:",
        parse_mode="Markdown",
        reply_markup=markup
    )
