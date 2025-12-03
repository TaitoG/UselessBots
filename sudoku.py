import os, dotenv
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder,
                          ContextTypes,
                          CommandHandler,
                          ConversationHandler,
                          CallbackQueryHandler)
import random

dotenv.load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user
    await update.message.reply_text(
        "Welcome to Sudoku 4x4 Bot!\n"
        "Use /new_game to start a new Sudoku game."
    )

async def draw_board(board=None):
    keyboard = []
    for i in range(1, 5):
        row_buttons = [InlineKeyboardButton(f"{f'[{board[i-1][j-1]}]' if board and board[i-1][j-1] else '[ ]'}", callback_data=f"{i}x{j}") for j in range(1, 5)]
        keyboard.append(row_buttons)
    number_buttons = [InlineKeyboardButton(str(num), callback_data=f"{num}") for num in range(1, 5)]
    keyboard.append([InlineKeyboardButton("Solve", callback_data="solve")])
    keyboard.append(number_buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def generate_puzzle():
    board = [[None] * 4 for _ in range(4)]
    for _ in range(2):
        i = random.randint(0, 3)
        j = random.randint(0, 3)
        n = random.randint(1, 4)
        board[i][j] = n

    return board

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Starts a new sudoku game 4x4 using InlineKeyboardMarkup to select cells and numbers
    # On selecting cells and numbers update the sudoku board accordingly
    board = generate_puzzle()
    context.user_data['board'] = board
    board_markup = await draw_board(board)
    await update.message.reply_text("New Sudoku Game Started!", reply_markup=board_markup)
    return 0

async def select_cell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle cell selection
    query = update.callback_query
    await query.answer()
    if query.data == "solve":
        return await solve_handler(update, context)
    cell = query.data
    print(f"Cell selected: {cell}")
    context.user_data['selected_cell'] = cell
    return 1

async def select_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle number selection
    query = update.callback_query
    await query.answer()
    number = query.data
    selected_cell = context.user_data.get('selected_cell')
    board = context.user_data.get('board')
    board[int(selected_cell[0])-1][int(selected_cell[2])-1] = int(number)
    context.user_data['board'] = board
    print(f"Number {number} selected for cell {selected_cell}")
    await query.edit_message_reply_markup(await draw_board(board))
    return 0

async def solve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board = context.user_data.get("board")
    errors = validate_board(board)
    if not errors:
        await query.edit_message_text("Board is correct! 🎉")
    else:
        await query.edit_message_text(
            "Errors found:\n" + "\n".join(f"- {e}" for e in errors)
        )

    return ConversationHandler.END

def validate_board(board):
    errors = []
    for i in range(4):
        row = [x for x in board[i] if x]
        if len(row) != len(set(row)):
            errors.append(f"Row {i+1}: duplicates")
    for j in range(4):
        col = [board[i][j] for i in range(4) if board[i][j]]
        if len(col) != len(set(col)):
            errors.append(f"Column {j+1}: duplicates")
    squares = [
        (0, 0), (0, 2),
        (2, 0), (2, 2)
    ]
    for si, sj in squares:
        block = []
        for i in range(si, si+2):
            for j in range(sj, sj+2):
                if board[i][j]:
                    block.append(board[i][j])

        if len(block) != len(set(block)):
            errors.append(f"Square ({si+1},{sj+1}) contains duplicates")
    return errors


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cancel the current game
    await update.message.reply_text("Game cancelled.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
    app.add_handlers = [
        CommandHandler("start", start),
    ]
    app.add_handler(ConversationHandler(
            entry_points=[CommandHandler('new_game', new_game)],
            states={
            0: [CallbackQueryHandler(select_cell)],
            1: [CallbackQueryHandler(select_number)],
            }, 
            fallbacks=[CommandHandler('cancel', cancel)]))
    app.run_polling()
    
if __name__ == '__main__':
    main()