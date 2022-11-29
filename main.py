from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env

env = Env()
env.read_env()


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(env('TG_TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()





if __name__ == '__main__':
    with open('quiz.txt',encoding='KOI8-R') as file:
        quiz = file.read()
    split_quiz = quiz.split('\n\n')
    answer_question = {}
    for i in split_quiz:
        if 'Вопрос' in i:
            question = i.split(':')[1].strip()
        if 'Ответ' in i:
            answer = i.split(':')[1].strip()
            answer_question[question]=answer
    print(answer_question)


    main()