from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
import telegram

env = Env()
env.read_env()


def start(bot,update):
    update.message.reply_text('Привет!!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def send_message():
    custom_keyboards = [['Новый вопрос', 'Сдаться'],
                        ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboards)
    bot = telegram.Bot(env('TG_TOKEN'))
    bot.send_message(text='test answer', chat_id=env('TG_CHAT_ID'),reply_markup=reply_markup)


def main():
    updater = Updater(env('TG_TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text,echo))
    updater.start_polling()



if __name__ == '__main__':
    with open('quiz.txt',encoding='KOI8-R') as file:
        quiz = file.read()
    split_quiz = quiz.split('\n\n')
    answer_question = {}
    for phrase in split_quiz:
        if 'Вопрос' in phrase:
            question = phrase.split(':')[1].strip()
        if 'Ответ' in phrase:
            answer = phrase.split(':')[1].strip()
            answer_question[question]=answer
    send_message()
    main()
