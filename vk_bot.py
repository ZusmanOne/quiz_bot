import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from environs import Env


env = Env()
env.read_env()




def echo(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белая кнопка', color=VkKeyboardColor.POSITIVE)
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )




if __name__ == "__main__":
    vk_session = vk.VkApi(token=env('VK_ID'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)
            print(event.user_id)
