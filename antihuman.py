import dotenv, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, 
                          ContextTypes, 
                          ChatMemberHandler, 
                          CommandHandler, 
                          CallbackQueryHandler,
                          MessageHandler,
                          filters)

dotenv.load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user when they start the bot
    # Give them instructions on how to add the bot to a group with button "Add to Group"
    if update.effective_chat.type != "private":
        return
    keyboard = [[
        InlineKeyboardButton("Add to chat", url=f"https://t.me/{(await context.bot.get_me()).username}?startgroup=true")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hello! Add me to your chat to help protect it from filthy humans.", reply_markup=reply_markup)

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle new chat member event
    # For new member you giving a simple captcha to pass using InlineKeyboardMarkup with button "I'm not a bot"
    # If user press the button you kick them from the chat
    for member in update.message.new_chat_members:
        user = member
        keyboard = [[
            InlineKeyboardButton("I'm not a bot", callback_data="captcha")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text=f"Welcome {user.first_name}! Please verify that you are not a bot by clicking the button below.",
            reply_markup=reply_markup,)

async def joined_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle bot being added to a chat
    # Send a welcome message and instructions on how to give admin rights to the bot if needed
    status = update.my_chat_member.new_chat_member.status
    if status == 'member':
        await context.bot.send_message(
            chat_id=update.my_chat_member.chat.id,
            text="Hello! Thanks for adding me to the chat. To help protect your chat from filthy humans, please make sure I have admin rights."
        )
    elif status == 'administrator':
        await context.bot.send_message(
            chat_id=update.my_chat_member.chat.id,
            text="Thanks for making me an admin! I'll make sure to protect your chat from filthy humans."
        )

async def captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle captcha button press
    # Kick the user from the chat if they press the button
    query = update.callback_query
    await query.answer()

    if query.data != "captcha":
        return

    user_who_pressed = query.from_user
    original_message = query.message.reply_to_message
    if not original_message or not original_message.new_chat_members:
        return

    target_user = original_message.new_chat_members[0]
    if user_who_pressed.id != target_user.id:
        return

    chat = query.message.chat

    try:
        await query.edit_message_text(
            f"{user_who_pressed.first_name} pressed the button.\n\nHUMAN DETECTED. BANNED."
        )
        await chat.ban_member(user_who_pressed.id)
    except Exception as e:
        await query.edit_message_text(
            "I tried to ban this human... but I don't have permission to ban users!"
        )

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    
    app.add_handlers([MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member),
                      ChatMemberHandler(joined_chat, ChatMemberHandler.MY_CHAT_MEMBER),
                      CommandHandler("start", start),
                      CallbackQueryHandler(captcha, pattern="^captcha$")])
    
    print('Antihuman bot is running...')
    app.run_polling()
    
if __name__ == '__main__':
    main()