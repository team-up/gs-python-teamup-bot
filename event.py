class EventFactory:

    @staticmethod
    def create(response_json):
        event_type = response_json['type']
        if event_type == 'chat.message':
            return ChatMessageEvent(response_json['chat'])
        elif event_type == 'chat.initbot':
            return ChatInitEvent(response_json['chat'])
        elif event_type == 'user.drop':
            return UserDropEvent(response_json['user'])
        elif event_type == 'user.password':
            return UserPasswordChangedEvent(response_json['user'])


class ChatMessageEvent:
    def __init__(self, json):
        self.team_index = json.get('team')
        self.room_index = json.get('room')
        self.user_index = json.get('user')
        self.msg_index = json.get('msg')
        self.room_name = json.get('name')


class ChatInitEvent:
    def __init__(self, json):
        self.team_index = json.get('team')
        self.room_index = json.get('room')
        self.user_index = json.get('user')


class UserEvent:
    def __init__(self, json):
        self.user_index = json.get('user')


class UserDropEvent(UserEvent):
    pass


class UserPasswordChangedEvent(UserEvent):
    pass
