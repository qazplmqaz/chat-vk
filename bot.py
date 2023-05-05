import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import re
import pickle
import os
import poe
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from io import BytesIO
import io
from pydub import AudioSegment
import speech_recognition as sr
import requests
from gtts import gTTS

class UserContext:
    def __init__(self):
        self.context = ""

    def add_text(self, text):
        self.context += text

    def clear_context(self):
        self.context = ""

    def get_context(self):
        return self.context

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

def process_audio_message(event):
            message = event.text
            user_id = event.user_id
            link_ogg = event.obj.message['attachments'][0]['audio_message']['link_ogg']
            file_name = str(user_id) + '.pkl'
            if os.path.isfile(file_name):
                with open(file_name, 'rb') as f:
                    user_context = UserContext.deserialize(f.read())
            else:
                user_context = UserContext()
            if event.obj.message.get('attachments'):
                    send_message(user_id, 'Обработка гс')
                    response = requests.get(link_ogg)
                    audio = AudioSegment.from_file(io.BytesIO(response.content), format="ogg")
                    audio.export("voice.wav", format="wav")
                    r = sr.Recognizer()
                    with sr.AudioFile("voice.wav") as source:
                        audio_data = r.record(source)
                        text = r.recognize_google(audio_data, language='ru-RU')

                        if "Включено" in user_context.get_context().lower():
                                send_message(user_id, "Сообщение в обработке! Ожидайте...")
                                response = generate_openai_response(user_context.get_context(), message)
                                user_context.add_text(message)
                        else:
                                send_message(user_id, "Сообщение в обработке! Ожидайте...")
                                response = generate_openai_response("", message)
                                user_context.clear_context()
                                user_context.add_text(response)
                        with open(file_name, 'wb') as f:
                            f.write(user_context.serialize())

                    text = response.choices[0].text
                    tts = gTTS(text=text, lang='ru')
                    voice = BytesIO()
                    tts.write_to_fp(voice)
                    voice.seek(0)
                    upload_url = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=user_id)['upload_url']
                    response = requests.post(upload_url, files={'file': ('voice.ogg', voice)})
                    doc = vk.docs.save(file=response.json()['file'], title='voice message')['audio_message']
                    attachment = 'doc{}_{}'.format(doc['owner_id'], doc['id'])
                    send_message(user_id,'', attachment)

def generate_openai_response(context, prompt):
    client = poe.Client("OUm8jQ_OMP8CE9np4gr23g%3D%3D")
    if client.get_remaining_messages == None:
       client = poe.Client("nefE3Yrn5YKi3AuZ7SoZjg%3D%3D")
    message = context + prompt
    for chunk in client.send_message("capybara", message):
        pass
    client.send_chat_break("capybara")
    response = chunk["text"]
    return response


def send_message(user_id, message, keyboard=None):
    random_id = random.getrandbits(31) * random.choice([-1, 1])
    vk.messages.send(user_id=user_id, message=message, random_id=random_id, keyboard=keyboard)


def process_message(event):
    message = event.text
    user_id = event.user_id

    file_name = str(user_id) + '.pkl'
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as f:
            user_context = UserContext.deserialize(f.read())
    else:
        user_context = UserContext()

    # создаем клавиатуру
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Включить", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Выключить", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Очистить контекст", color=VkKeyboardColor.SECONDARY)
    keyboard = keyboard.get_keyboard()

    if message == "Включить":
        user_context.add_text("Включено.\n")
        with open(file_name, 'wb') as f:
            f.write(user_context.serialize())
        send_message(user_id, "Контекст включён!", keyboard=keyboard)
        return

    if message == "Выключить":
        user_context.add_text("Выключено.\n")
        with open(file_name, 'wb') as f:
            f.write(user_context.serialize())
        send_message(user_id, "Контекст выключен!", keyboard=keyboard)
        return

    if message == "Очистить контекст":
        user_context.clear_context()
        with open(file_name, 'wb') as f:
            f.write(user_context.serialize())
        send_message(user_id, "Контекст очищен!", keyboard=keyboard)
        return

    if message[0] != "Очистить контекст" or message[0] != "Выключить" or message[0] != "Включить":
        if "Включено" in user_context.get_context().lower():
            send_message(user_id, "Сообщение в обработке! Ожидайте...")
            response = generate_openai_response(user_context.get_context(), message)
            user_context.add_text(message)
        else:
            send_message(user_id, "Сообщение в обработке! Ожидайте...")
            response = generate_openai_response("", message)
            user_context.clear_context()
            user_context.add_text(response)

        with open(file_name, 'wb') as f:
            f.write(user_context.serialize())

        response_parts = re.findall('.{1,4000}', response)

        for part in response_parts:
            send_message(user_id, part, keyboard=keyboard)


if __name__ == '__main__':
    vk_session = vk_api.VkApi(token='vk1.a.QeBBHtozKFg4YlPmayk4mDm0hnNZBgKj4Q6s1P4XC8iXjbprUGaSvkLyB_J9YY7e58vbZ27shbiGBSGszbU5XHO_1SuKru8ZzlWFfK4Hw9bYIbdFpgcEWH99znB6SzxKesQkld-2LQSfLmC1HRQfFbtlWYKFpgKObn563tDhMKDlHxAyKZPFJElMiWSi8tZCM24mPef_f458V0_9vt2TSA')
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        process_message(event)
