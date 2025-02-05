#!/usr/bin/env python
import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

connection = sqlite3.connect('bannik.db', check_same_thread=False)
cursor = connection.cursor()


def increment_count(chat_id):
    cursor.execute('SELECT * FROM counters WHERE chat_id='+str(chat_id)+';')
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE counters SET count=' + str(row[2]+1) + ' WHERE chat_id='+str(chat_id)+';')
        connection.commit()
    return row[2]+1


def get_count(chat_id):
    cursor.execute('SELECT * FROM counters WHERE chat_id='+str(chat_id)+';')
    row = cursor.fetchone()
    if row:
        return row[2]
    else:
        return 0


bannik_count_messages = [
    "Сколько раз мы были в бане?".lower(),
    "Сколько раз мы ходили в баню?".lower(),
    "Сколько раз мы посещали баню?".lower()
]


bannik_increment_messages = [
    "Мы сходили в баню".lower(),
    "Мы сходили в баню!".lower(),
    "А ниче то что мы сходили в баню?".lower(),
]


def declensions(count, words):
    cases = [2, 0, 1, 1, 1, 2]
    if 4 < count % 100 < 20:
        return words[0]
    if count % 10 < 5:
        return words[cases[count % 10]]
    else:
        return words[2]


async def bannik_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text[8:]
    if message.lower() in bannik_count_messages:
        count = get_count(update.message.chat_id)
        if count == 0:
            await update.message.reply_text("Вы ещё не ходили в баню ни разу")
        else:
            await update.message.reply_text("Вы ходили в баню " + str(count) + " " + declensions(count, ["раз", "раза", "раз"]))
    elif message.lower() in bannik_increment_messages:
        new_count = increment_count(update.message.chat_id)
        await update.message.reply_text("Поздравляю! Это был ваш "+str(new_count)+"-й поход в баню")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["BOT_TOKEN"]).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("bannik", bannik_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()