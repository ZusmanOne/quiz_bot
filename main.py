from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
import telegram
import redis
import random
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)


env = Env()
env.read_env()
r = redis.StrictRedis(host=env('REDIS_HOST'),
                      port=env('REDIS_PORT'),
                      password=env('REDIS_PASSWORD'),
                      charset="utf-8",
                      decode_responses=True,
                      db=0)

QUESTION, ANSWER, SKIP = range(3)


def start(bot, update):
    reply_keyboard = [['Новый вопрос', 'Завершить'],
                      ['Мой счет']]
    update.message.reply_text(
        'Привет! Я бот, который любит викторины. Сыграем?\n Жми Кнопку "Новый вопрос!"',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return QUESTION


def handle_new_question_request(bot, update):
    user = update.message.from_user
    random_answer = random.choice(list(answer_question))
    r.set(env("TG_ID"), random_answer)
    update.message.reply_text(r.get(env('TG_ID')),reply_markup=ReplyKeyboardRemove())
    return ANSWER


def handle_solution_attempt(bot,update):
    reply_keyboard = [['Новый вопрос', 'Завершить'],
                      ['Мой счет']]
    user = update.message.from_user
    if update.message.text in answer_question[r.get(env('TG_ID'))]:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return QUESTION
    if update.message.text == 'Сдаться':
        return SKIP
    reply_keyboards = [['Новый вопрос', 'Сдаться']]
    update.message.reply_text('Неправильно… Попробуешь ещё раз?\n',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboards, one_time_keyboard=True))
    return ANSWER


def skip_question(bot, update):
    user = update.message.from_user
    update.message.reply_text(answer_question[r.get(env('TG_ID'))])
    new_answer = random.choice(list(answer_question))
    r.set(env("TG_ID"), new_answer)
    update.message.reply_text(r.get(env('TG_ID')))
    return ANSWER


def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Приходи в следующий раз!!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater(env('TG_TOKEN'))
    dp = updater.dispatcher
    updater.start_polling()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [RegexHandler('^(Новый вопрос)$', handle_new_question_request),
                       RegexHandler('Завершить', cancel)],
            ANSWER: [RegexHandler('^(Сдаться)$', skip_question),
                     MessageHandler(Filters.text, handle_solution_attempt),
                     ]
        },
        fallbacks=[CommandHandler('Завершить', cancel)])
    dp.add_handler(conv_handler)
    updater.start_polling()


if __name__ == '__main__':
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
    main()
