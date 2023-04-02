import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai

openai.api_key = "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"

def get_response(message):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def main():
    vk_session = vk_api.VkApi(token='vk1.a.QeBBHtozKFg4YlPmayk4mDm0hnNZBgKj4Q6s1P4XC8iXjbprUGaSvkLyB_J9YY7e58vbZ27shbiGBSGszbU5XHO_1SuKru8ZzlWFfK4Hw9bYIbdFpgcEWH99znB6SzxKesQkld-2LQSfLmC1HRQfFbtlWYKFpgKObn563tDhMKDlHxAyKZPFJElMiWSi8tZCM24mPef_f458V0_9vt2TSA')
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            user_id = event.user_id
            message = event.text

            response = get_response(message)
            vk.messages.send(user_id=user_id, message=response, random_id=0)

if __name__ == '__main__':
    main()