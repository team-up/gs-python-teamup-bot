import threading
import time


class BaseBot:
    def __init__(self, service):
        self.service = service

    # thread-safe 하다고 나와있긴 하지만 보장이 되는지 고민해 봐야함
    # callback 패턴으로 바꾸는 것 고려
    def handle_event(self, events):
        for event in events:
            if event.chat_event:
                chat = self.service.get_chat_summary(event.chat_event.room_index,
                                                     event.chat_event.msg_index)

                self.handle_chat(event.chat_event.room_index, chat)

    def run(self):
        while True:
            events = self.service.get_events()
            if events:
                threading.Thread(target=self.handle_event, args=(events,)).start()
            time.sleep(self.service.config['lp_idle_time'])

    def handle_chat(self, room_index, chat):
        raise NotImplementedError()


class TextBot(BaseBot):

    def handle_chat(self, room_index, chat):
        if chat and chat.content == "ㅎㅇ":
            self.service.post_chat(room_index, "ㅎㅇㅎㅇ")


class ButtonBot(BaseBot):

    def __init__(self, service):
        super(ButtonBot, self).__init__(service)
        self.test_extras = [
            {
                'version': 1,
                'type': 'answer',
                'msg_buttons': [
                    {"type": "text", "text": "텍스트 버튼"},
                    {"type": "url", "text": "구글", "url": "https://www.google.com"}
                ]
            }
        ]

    def handle_chat(self, room_index, chat):
        if chat and chat.content == "ㅎㅇ":
            self.service.post_chat(room_index, "ㅎㅇㅎㅇ", self.test_extras)
