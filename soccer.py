import os, dotenv, asyncio
from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          ContextTypes,
                          CommandHandler,
                          MessageHandler,
                          ConversationHandler,
                          filters)
dotenv.load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user
    await update.message.reply_text(
        "Welcome to Soccer Penalty Shoot-out Bot!\nUse /play to start a penalty shootout game.\n")
    
async def pen_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Start a new penalty shoot-pout game
    # Rules are simple, user and bot take turns to kick using emoji football ball
    await update.message.reply_text(
        'Get ready for a penalty shootout! Send a ⚽ emoji to take your shot.')
    return 0

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle user kick and bot response with sleep to wait for animation of dice
    await asyncio.sleep(4)
    attempt = context.user_data.get('attempt', 0)
    score, bot_score = context.user_data.get('user_score', 0), context.user_data.get('bot_score', 0)
    shot = update.message.dice.value
    if shot > 2:
        score += 1
        await update.message.reply_text(f"Goal! You scored! Congrats!\nScore now is {score} - {bot_score}\n\nNow its my turn!")
    else:
        await update.message.reply_text(f"Good try! Maybe next time.\nScore stays {score} - {bot_score}\n\nNow its my turn!")
    reply = await update.message.reply_dice(emoji='⚽')
    await asyncio.sleep(4)
    bot_shot = reply.dice.value
    if bot_shot > 2:
        bot_score += 1
        text = f'Looks like I scored!\nScore now is {score} - {bot_score}\n'
        is_winner = check_winner(score, bot_score, attempt)
        if is_winner[0] is not None:
            if is_winner[0]:
                text += 'You win the shootout! Congrats!'
                context.user_data['user_wins'] = context.user_data.get('user_wins', 0) + 1
            else:
                text += 'I win the shootout! Better luck next time!'
                context.user_data['bot_wins'] = context.user_data.get('bot_wins', 0) + 1
            await update.message.reply_text(text)
            clear_data(context)
            return ConversationHandler.END
        else:
            await update.message.reply_text(text+'Your turn!')
    else:
        text = f'Damn it. I missed!\nScore stays {score} - {bot_score}\n'
        is_winner = check_winner(score, bot_score, attempt)
        if is_winner[0] is not None:
            if is_winner[0]:
                text += 'You win the shootout! Congrats!'
                context.user_data['user_wins'] = context.user_data.get('user_wins', 0) + 1
            else:
                text += 'I win the shootout! Better luck next time!'
                context.user_data['bot_wins'] = context.user_data.get('bot_wins', 0) + 1
            await update.message.reply_text(text)
            clear_data(context)
            return ConversationHandler.END
        else:
            await update.message.reply_text(text+'Your turn!')
    attempt += 1
    fill_data(context, score, bot_score, attempt)
    return 0

def clear_data(context):
    context.user_data.pop('user_score', None)
    context.user_data.pop('bot_score', None)
    context.user_data.pop('attempt', None)

def fill_data(context, score, bot_score, attempt):
    context.user_data['user_score'] = score
    context.user_data['bot_score'] = bot_score
    context.user_data['attempt'] = attempt
    
def check_winner(score, bot_score, attempt):
    remaining = 5 - attempt
    if score > bot_score + remaining:
        return True, 'user'
    elif bot_score > score + remaining:
        return False, 'bot'
    else:
        return None, None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cancel the current game
    await update.message.reply_text("Game cancelled. Use /play to start a new game.")
    clear_data(context)
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show user stats
    user_wins = context.user_data.get('user_wins', 0)
    bot_wins = context.user_data.get('bot_wins', 0)
    await update.message.reply_text(f"Your Wins: {user_wins}\nBot Wins: {bot_wins}")

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers([
        CommandHandler("start", start),
        CommandHandler('stats', stats),
        ConversationHandler(
            entry_points=[CommandHandler("play", pen_start)],
            states={
                0: [MessageHandler(filters.Dice.FOOTBALL, kick)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
    ])
    app.run_polling()
    
if __name__ == '__main__':
    main()