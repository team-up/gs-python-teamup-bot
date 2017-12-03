class EventFactory:

    @staticmethod
    def create(response_json):
        event_type = response_json['type']
        if event_type.startswith('chat'):
            return ChatEvent(response_json['chat'])


class ChatEvent:
    def __init__(self, json):
        self.team_index = json.get('team')
        self.room_index = json.get('room')
        self.user_index = json.get('user')
        self.msg_index = json.get('msg')
        self.room_name = json.get('name')
