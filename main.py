from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
import telegram
import redis
import random

env = Env()
env.read_env()
r = redis.StrictRedis(host=env('REDIS_HOST'),
                      port=env('REDIS_PORT'),
                      password=env('REDIS_PASSWORD'),
                      db=0)


def start(bot,update):
    custom_keyboards = [['Новый вопрос', 'Сдаться'],
                        ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboards)
    bot = telegram.Bot(env('TG_TOKEN'))
    bot.send_message(text='Привет! Давай начнем нашу викторину!', chat_id=env('TG_CHAT_ID'), reply_markup=reply_markup)


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    print(update.message.text=='ds')


def send_questions(bot,update):
    if update.message.text == 'Новый вопрос':
        update.message.reply_text('Раздва')


def send_message(bot, update):
    with open('quiz.txt', encoding='KOI8-R') as file:
        quiz = file.read()
    split_quiz = quiz.split('\n\n')
    answer_question = {}
    for phrase in split_quiz:
        if 'Вопрос' in phrase:
            question = phrase.strip()
        if 'Ответ' in phrase:
            answer = phrase.strip()
            answer_question[question] = answer
    custom_keyboards = [['Новый вопрос', 'Сдаться'],
                        ['Мой счет']]
    if update.message.text == custom_keyboards[0][0]:
        update.message.reply_text(random.choice(list(answer_question)))


def main():

    updater = Updater(env('TG_TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, send_message))
    updater.start_polling()


if __name__ == '__main__':
    #send_message()
    main()
