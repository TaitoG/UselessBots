import os, dotenv, datetime, hashlib
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQuery, InputTextMessageContent, InlineQueryResultArticle)
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler,
                          InlineQueryHandler)
dotenv.load_dotenv()

locs = {
    'en': {
        'start': "To see how based you are, type @{bot_name} in any chat or press the button below.",
        'start_button': "Check how based you are!",
        'inline_title': "Your Based Score",
        'inline_description': 'Click to see how based you are today!',
        'inline_message': 'You are based on {based_score}%!',
        'share_button': "Share your based score!"
    },
    'uk': {
        'start': "Щоб дізнатися свій рівень потужності, наберіть @{bot_name} у будь-якому чаті або натисніть кнопку нижче.",
        'start_button': "Перевірте свій рівень потужності!",
        'inline_title': "Ваш рівень потужності",
        'inline_description': 'Натисніть, щоб дізнатися свій рівень потужності сьогодні!',
        'inline_message': 'Ваш рівень потужності становить {based_score}%!',
        'share_button': "Поділитися своїм рівнем потужності!"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user
    bot_name = (await context.bot.get_me()).username
    lang = 'uk' if update.effective_user.language_code == 'uk' else 'en'
    button = [
        [InlineKeyboardButton(locs[lang]['start_button'], switch_inline_query="")]
    ]
    reply_markup = InlineKeyboardMarkup(button)
    await update.message.reply_text(locs[lang]['start'].format(bot_name=bot_name), reply_markup=reply_markup)

async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle inline query to return a based score from 0 to 100% using hash of user id with datetime
    # for unique but consistent daily score
    query: InlineQuery = update.inline_query
    user_id = query.from_user.id
    lang = 'uk' if query.from_user.language_code == 'uk' else 'en'
    today = datetime.datetime.now().date()
    based_score = int(hashlib.sha256(f"{user_id}{today}".encode()).hexdigest(), 16) % 101
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(locs[lang]['share_button'], switch_inline_query="")]])
    results = [
        InlineQueryResultArticle(
            id=str(user_id),
            title=locs[lang]['inline_title'],
            input_message_content=InputTextMessageContent(locs[lang]['inline_message'].format(based_score=based_score)),
            description=locs[lang]['inline_description'],
            reply_markup=reply_markup
        )
    ]
    await query.answer(results=results, cache_time=0)

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers([
        CommandHandler("start", start),
        InlineQueryHandler(inline_handler)
    ])
    app.run_polling()
    
if __name__ == '__main__':
    main()