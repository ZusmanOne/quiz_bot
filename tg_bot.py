from environs import Env
import logging
import redis
import random
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from handler_log import TelegramLogsHandler


logger = logging.getLogger(__name__)

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
    logger.info('Бот запущен')
    update.message.reply_text(
        'Привет! Я бот, который любит викторины. Сыграем?\n Жми Кнопку "Новый вопрос!"',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return QUESTION


def handle_new_question_request(bot, update):
    random_answer = random.choice(list(answer_question))
    r.set(env("TG_ID"), random_answer)
    update.message.reply_text(r.get(env('TG_ID')), reply_markup=ReplyKeyboardRemove())
    return ANSWER


def handle_solution_attempt(bot, update):
    reply_keyboard = [['Новый вопрос', 'Завершить'],
                      ['Мой счет']]
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
    update.message.reply_text(answer_question[r.get(env('TG_ID'))])
    new_answer = random.choice(list(answer_question))
    r.set(env("TG_ID"), new_answer)
    update.message.reply_text(r.get(env('TG_ID')))
    return ANSWER


def cancel(bot, update):
    update.message.reply_text('Приходи в следующий раз!!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning(f"Возникла ошибка- {error} в {update}")


def main():
    tg_token = env('TG_TOKEN')
    chat_id = env('TG_ID')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_token, chat_id))
    updater = Updater(tg_token)
    dp = updater.dispatcher

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
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    with open('quiz.txt', encoding='KOI8-R') as file:
        quiz = file.read()
    split_quiz = quiz.split('\n\n')
    answer_question = {}
    for phrase in split_quiz:
        try:
            if 'Вопрос' in phrase:
                question = phrase.strip()
            if 'Ответ' in phrase:
                answer = phrase.strip()
                answer_question[question] = answer
        except Exception:
            logger.exception('Что то пошло не так')
    main()
