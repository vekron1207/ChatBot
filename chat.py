import os
import psycopg2
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, Updater

load_dotenv()

# Define PostgreSQL
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# button names and jokes
BUTTONS = {
    'stupid': 'Why did the chicken cross the road?\nTo get to the other side!',
    'fat': 'Why did the tomato turn red?\nBecause it saw the salad dressing!',
    'dumb': 'Why did the bicycle fall over?\nBecause it was two-tired!'
}

keyboard = [
    [
        InlineKeyboardButton("Stupid", callback_data='stupid'),
        InlineKeyboardButton("Fat", callback_data='fat'),
        InlineKeyboardButton("Dumb", callback_data='dumb'),
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi! Press a button to hear a joke.', reply_markup=reply_markup)


def handle_button(update: Update, context):
    """Handle button press."""
    query = update.callback_query
    button_name = query.data
    user_id = query.from_user.id

    # Update the call count
    update_call_count(button_name, user_id)

    # joke based on the button that was pressed
    if button_name in BUTTONS:
        joke = BUTTONS[button_name]
    else:
        joke = 'Sorry, I did not understand that button.'

    query.edit_message_text(text=joke)


def update_call_count(button_name, user_id):
    """Update the call count for a button."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # the row exists for this user and button
    cur.execute(
        'SELECT * FROM button_calls WHERE button_name = %s AND user_id = %s;',
        (button_name, user_id)
    )
    row = cur.fetchone()

    if row:
        # update the call count
        call_count = row[2] + 1
        cur.execute(
            'UPDATE button_calls SET call_count = %s WHERE button_name = %s AND user_id = %s;',
            (call_count, button_name, user_id)
        )
    else:
        # insert a new row with a call count of 1
        cur.execute(
            'INSERT INTO button_calls (button_name, call_count, user_id) VALUES (%s, 1, %s);',
            (button_name, user_id)
        )

    conn.commit()
    cur.close()
    conn.close()


def main():
    """Start the bot."""
    # bot
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # command handlers
    dispatcher.add_handler(CommandHandler('start', start))

    # callback handler
    dispatcher.add_handler(CallbackQueryHandler(handle_button))

    # Startbot
    updater.start_polling()

    # Keep the bot running
    updater.idle()
