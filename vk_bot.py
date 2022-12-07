import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env
import redis
import logging
from handler_log import TelegramLogsHandler
from generate_quiz import create_quiz

logger = logging.getLogger(__name__)


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Завершить', color=VkKeyboardColor.NEGATIVE)
    logger.info('Бот запущен')
    vk_api.messages.send(
        user_id=event.user_id,
        message="Привет! Я бот, который любит викторины. Сыграем?\n Жми Кнопку Новый вопрос!",
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def cancel_quiz(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать', color=VkKeyboardColor.POSITIVE)
    vk_api.messages.send(
        user_id=event.user_id,
        message="Приходи в следующий раз!!",
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def send_question(event, vk_api,answer_question):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)
    random_answer = random.choice(list(answer_question))
    r.set(event.user_id, random_answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=r.get(event.user_id),
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def send_answer(event, vk_api,answer_question):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Завершить', color=VkKeyboardColor.NEGATIVE)
    vk_api.messages.send(
        user_id=event.user_id,
        message=answer_question[r.get(event.user_id)],
        random_id=random.randint(1, 1000),
    )
    random_answer = random.choice(list(answer_question))
    r.set(event.user_id, random_answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=r.get(event.user_id),
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_answer_request(event, vk_api,answer_question):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    if event.text in answer_question[r.get(event.user_id)]:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Завершить', color=VkKeyboardColor.NEGATIVE)
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard(),
        )
    else:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Завершить', color=VkKeyboardColor.POSITIVE)
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно попробуй еще раз',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard(),
        )


def main():
    vk_session = vk.VkApi(token=env('VK_ID'))
    vk_api = vk_session.get_api()
    tg_token = env('TG_TOKEN')
    chat_id = env('TG_ID')
    answer_question = create_quiz()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_token, chat_id))
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == 'Начать':
                    start(event,vk_api)
                elif event.text == 'Завершить':
                    cancel_quiz(event, vk_api)
                elif event.text == 'Новый вопрос':
                    send_question(event, vk_api,answer_question)
                elif event.text == 'Сдаться':
                    send_answer(event, vk_api,answer_question)
                else:
                    handle_answer_request(event, vk_api,answer_question)
        except ConnectionError:
            logger.error('Connection terminated')
        except Exception:
            logger.error('Что пошло не так')


if __name__ == "__main__":
    env = Env()
    env.read_env()
    r = redis.StrictRedis(host=env('REDIS_HOST'),
                          port=env('REDIS_PORT'),
                          password=env('REDIS_PASSWORD'),
                          charset="utf-8",
                          decode_responses=True,
                          db=0)
    main()
