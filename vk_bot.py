import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env
from main import r

env = Env()
env.read_env()


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Завершить', color=VkKeyboardColor.NEGATIVE)
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


def send_question(event, vk_api):
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


def send_answer(event, vk_api):
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


def handle_answer_request(event, vk_api):
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


if __name__ == "__main__":
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
    vk_session = vk.VkApi(token=env('VK_ID'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Начать':
                start(event, vk_api)
            elif event.text == 'Завершить':
                cancel_quiz(event,vk_api)
            elif event.text == 'Новый вопрос':
                send_question(event, vk_api)
            elif event.text == 'Сдаться':
                send_answer(event, vk_api)
            else:
                handle_answer_request(event, vk_api)

