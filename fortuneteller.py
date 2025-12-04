import os, dotenv, random
from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          ContextTypes,
                          CommandHandler,
                          MessageHandler,
                          filters)
dotenv.load_dotenv()

locs = {
    'en': {
        'welcome': 'Welcome to the Fortune Teller Bot!\nUse /fortune to receive your fortune for the day or ask "Oh, wise horse, ...?" to get an answer from The Wise Horse.',
        'fortune': '🔮 Your Fortune: {fortune_message}',
        'horse': 'Oh, wise horse',
        'fortunes': {
            'normal': [
                'Stars say today is a good day to rest on bed.',
                'All your important work can wait to tomorrow.',
                'Don\'t worry about your problems, you can just sleep through them.',
                'Are you still up? Go to sleep! Today is great day to procrastinate.',
                'You will have a productive day... tomorrow.',
                'Your future is as bright as your screen at 2 AM.',
                'You will find success in doing nothing today.',
                'Happiness is just a nap away.',
                'You will achieve greatness by avoiding all responsibilities today.',
                'The fortune you seek is in another nap.'
            ],
            'rare': [
                'Well.. Seems like you should finally get up and conquer the world today!',
                'You built up enough energy, now is the time to shine!',
                'Today is the day you make a difference! Go out and seize the moment!',
                'Work hard today, and the universe will reward you generously!',
                'It\'s finally time to do something amazing with your life!'
            ]
        }
    },
    'uk': {
        'weolcome': 'Ласкаво просимо до Бота Ворожки!\nВикористовуйте /fortune, щоб отримати свою вдачу на день або запитайте "О, мудрий кінь, ...?" щоб отримати відповідь від Мудрого Коня.',
        'fortune': '🔮 Ваша вдача: {fortune_message}',
        'horse': 'О, мудрий кінь',
        'fortunes': {
            'normal': [
                'Зірки кажуть, що сьогодні хороший день, щоб полежати в ліжку.',
                'Вся ваша важлива робота може почекати до завтра.',
                'Не хвилюйтеся про свої проблеми, ви можете просто проспати їх.',
                'Ви ще не спите? Ідіть спати! Сьогодні чудовий день для прокрастинації.',
                'У вас буде продуктивний день... завтра.',
                'Ваше майбутнє так само яскраве, як екран о 2 годині ночі.',
                'Ви досягнете успіху, нічого не роблячи сьогодні.',
                'Щастя всього в одному сні.',
                'Ви досягнете величі, уникаючи всіх обов\'язків сьогодні.',
                'Пророцтво, яке ви шукаєте, в іншому сні.'
            ],
            'rare': [
                'Що ж.. Схоже, сьогодні вам нарешті варто встати і підкорити світ!',
                'Ви накопичили достатньо енергії, тепер час сяяти!',
                'Сьогодні той день, коли ви можете змінити все! Вийдіть і скористайтеся моментом!',
                'Працюйте наполегливо сьогодні, і всесвіт щедро вас винагородить!',
                'Пора зробити щось дивовижне у вашому житті!'
            ]
        }
    },
    'ru': {
        'welcome': 'Добро пожаловать в Бот Гадалка!\nИспользуйте /fortune, чтобы получить ваше предсказание на день или спросите "О, мудрый конь, ...?" чтобы получить ответ от Мудрого Коня.',
        'fortune': '🔮 Ваше предсказание: {fortune_message}',
        'horse': 'О, мудрый конь',
        'fortunes': {
            'normal': [
                'Звезды говорят, что сегодня хороший день, чтобы полежать в кровати.',
                'Вся ваша важная работа может подождать до завтра.',
                'Не беспокойтесь о своих проблемах, вы можете просто проспать их.',
                'Вы еще не спите? Идите спать! Сегодня отличный день для прокрастинации.',
                'У вас будет продуктивный день... завтра.',
                'Ваше будущее так же ярко, как экран в 2 часа ночи.',
                'Вы добьетесь успеха, ничего не делая сегодня.',
                'Счастье всего в одном сне.',
                'Вы достигнете величия, избегая всех обязанностей сегодня.',
                'Предсказание, которое вы ищете, в другом сне.'],
            'rare': [
                'Что ж.. Похоже, сегодня вам наконец-то стоит встать и покорить мир!',
                'Вы накопили достаточно энергии, теперь время сиять!',
                'Сегодня тот день, когда вы можете изменить всё! Выйдите и воспользуйтесь моментом!',
                'Работайте усердно сегодня, и вселенная щедро вас вознаградит!',
                'Пора сделать что-то удивительное в вашей жизни!'
            ]
        }
    },
    'it': {
        'welcome': 'Benvenuto nel Bot Indovino!\nUsa /fortune per ricevere la tua fortuna del giorno o chiedi "Oh, saggio cavallo, ...?" per ottenere una risposta dal Saggio Cavallo.',
        'fortune': '🔮 La tua fortuna: {fortune_message}',
        'horse': 'Oh, saggio cavallo',
        'fortunes': {
            'normal': [
                'Le stelle dicono che oggi è un buon giorno per riposare a letto.',
                'Tutto il tuo lavoro importante può aspettare fino a domani.',
                'Non preoccuparti dei tuoi problemi, puoi semplicemente dormire attraverso di essi.',
                'Sei ancora sveglio? Vai a dormire! Oggi è un grande giorno per procrastinare.',
                'Avrai una giornata produttiva... domani.',
                'Il tuo futuro è luminoso come lo schermo alle 2 del mattino.',
                'Raggiungerai il successo non facendo nulla oggi.',
                'La felicità è a un sonnellino di distanza.',
                'Raggiungerai la grandezza evitando tutte le responsabilità oggi.',
                'La fortuna che cerchi è in un altro sonnellino.'
            ],
            'rare': [
                'Beh.. Sembra che oggi dovresti finalmente alzarti e conquistare il mondo!',
                'Hai accumulato abbastanza energia, ora è il momento di brillare!',
                'Oggi è il giorno in cui fai la differenza! Esci e cogli l\'attimo!',
                'Lavora sodo oggi, e l\'universo ti ricompenserà generosamente!',
                'È finalmente il momento di fare qualcosa di straordinario con la tua vita!'
            ]
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user
    lang = update.effective_user.language_code
    if lang not in locs:
        lang = 'en'
    await update.message.reply_text(locs[lang]['welcome'])

async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Provide a random fortune message to the user with 99% chanche of normal fortune
    lang = update.effective_user.language_code
    if lang not in locs:
        lang = 'en'
    fortunes = locs[lang]['fortunes']['normal']
    rare_fortunes = locs[lang]['fortunes']['rare']
    
    if random.random() < 0.01:
        fortune_message = random.choice(rare_fortunes)
    else:
        fortune_message = random.choice(fortunes)
    await update.message.reply_text(locs[lang]['fortune'].format(fortune_message=fortune_message))

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respond to any text message with ? at the end and "Oh, wise horse" at the start of quetion
    lang = update.effective_user.language_code
    if lang not in locs:
        lang = 'en'
    user_message = update.message.text
    if user_message.endswith('?') and user_message.lower().startswith(locs[lang]['horse'].lower()):
        if random.random() > 0.10:
            await update.message.reply_animation(animation='CgACAgQAAxkBAAIXaWkxCb6wuNS1fnDDyL1Rdg_3ab-4AAIICAACfLEEUfTDHiRRNGgPNgQ')
        else:
            await update.message.reply_animation(animation='CgACAgQAAxkBAAIXa2kxCgUStqCdI7wWMyrAfioBGOFwAAITCAACCZBUUN_B4IpNw4nQNgQ')

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers([
        CommandHandler('start', start),
        CommandHandler('fortune', fortune),
        MessageHandler(filters.ALL & ~filters.COMMAND, answer)
    ])
    print('Fortune Teller Bot is running...')
    app.run_polling()
    
if __name__ == '__main__':
    main()