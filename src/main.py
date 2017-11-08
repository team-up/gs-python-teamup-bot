import json

import os

from teamup_service import TeamUpService

import time

service = TeamUpService()

file_name = os.path.join(os.path.dirname(__file__), 'authentication.json')
with open(file_name) as data_file:
    authentication = json.load(data_file)

service.login(authentication)

while True:
    events = service.get_events()
    if events:
        for event in events:
            if event.chat_event:
                chat = service.get_chat_summary(event.chat_event.room_index,
                                                event.chat_event.msg_index)

                if chat:
                    print("채팅 옴 : {}".format(chat.content))

                    if chat.content == "ㅎㅇ":
                        service.post_chat(event.chat_event.room_index,
                                          "ㅎㅇㅎㅇ")
    time.sleep(service.config['lp_idle_time'])
