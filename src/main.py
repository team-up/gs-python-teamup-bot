import json
import threading

import os

from teamup_service import TeamUpService

import time

service = TeamUpService()

file_name = os.path.join(os.path.dirname(__file__), 'authentication.json')
with open(file_name) as data_file:
    authentication = json.load(data_file)

service.login(authentication)

# thread-safe 하다고 나와있긴 하지만 보장이 되는지 고민해 봐야함
# callback 패턴으로 바꾸는 것 고려
def handle_event(events):
    for event in events:
        if event.chat_event:
            chat = service.get_chat_summary(event.chat_event.room_index,
                                            event.chat_event.msg_index)

            if chat and chat.content == "ㅎㅇ":
                service.post_chat(event.chat_event.room_index, "ㅎㅇㅎㅇ")

while True:
    events = service.get_events()
    if events:
        threading.Thread(target=handle_event, args=(events,)).start()
    time.sleep(service.config['lp_idle_time'])
