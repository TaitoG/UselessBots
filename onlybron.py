import os, dotenv
from telegram import Update, LabeledPrice, InputFile
from telegram.ext import (  ApplicationBuilder,
                            PreCheckoutQueryHandler,
                            ContextTypes,
                            CommandHandler,
                            MessageHandler,
                            filters)
from telegram.constants import ParseMode
dotenv.load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user and give instructions on how to get a bron
    await update.message.reply_text(
        "😻 <b>Welcome to OnlyBron!</b> 🏀\n\n"
        "The most exclusive LeBron content on Telegram.\n"
        "One photo of Bron — the king of NBA — costs just <b>1 Star</b>.\n\n"
        "Use /getbron to unlock the divine hooper.",
        parse_mode=ParseMode.HTML
    )

async def getbron(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send an invoice in 1 star for the bron
    await update.message.reply_invoice(
        title="Exclusive Bron Photo",
        description="One (1) high-quality photo of the legendary hooper Bron. "
                    "No refunds. No regrets. Only Bron.",
        payload="bron_photo_1star",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Bron Access", 1)],  # 1 Star
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Checking payment
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Acknowledge successful payment and send the bron to user for folder assets/bron.png
    payment = update.message.successful_payment
    if payment.invoice_payload != "bron_photo_1star":
        return
    photo_path = "assets/bron.png"
    with open(photo_path, "rb") as photo_file:
        await update.message.reply_photo(
            photo=InputFile(photo_file, filename="bron.png"),
            caption="😻 <b>Thank you for supporting Bron!</b>\n"
                    "Here is your exclusive photo.\n"
                    "You are now part of the elite.",
            parse_mode=ParseMode.HTML
        )

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers = [
        CommandHandler('start', start),
        CommandHandler('getbron', getbron),
        PreCheckoutQueryHandler(check),
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment),
    ],
    print('Bron is ready...')
    app.run_polling()

if __name__ == '__main__':
    main()