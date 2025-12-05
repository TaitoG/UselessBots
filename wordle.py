import os, dotenv, random
from threading import Thread
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, Bot
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
from flask import Flask, render_template, request
dotenv.load_dotenv()

secret_words = ['WORDLE', 'ONLYBRON', 'BASED', 'SOCCER', 'SUDOKU', 'ANTIHUMAN', 'FORTUNE']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet user and send him a button to open mini-app
    web_app = WebAppInfo(url=os.getenv("URL"))
    keyboard = [[KeyboardButton(text="🎮 Play Wordle", web_app=web_app)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Welcome to Wordle Bot! To open mini-app please click on the button bellow.', reply_markup=reply_markup)

def bot():
    # Logic for bot
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers([
        CommandHandler("start", start)
    ])
    app.run_polling()

def flask():
    # Logic for Flask server
    app = Flask(__name__, template_folder='assets', static_folder='assets')
    @app.route('/', methods=['GET'])
    def game():
        word = random.choice(secret_words)
        return render_template("wordle.html", secret_word=word, length=len(word))
    app.run(host="0.0.0.0", port=5000, debug=False)
    
if __name__ == '__main__':
    thread = Thread(target=flask)
    thread.daemon = True
    thread.start()
    bot()