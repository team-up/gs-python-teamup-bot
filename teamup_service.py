import requests

event_host = 'https://test-ev.tmup.com'
auth_host = 'https://test-auth.tmup.com'
edge_host = 'https://test-edge.tmup.com'

client_id = 'c'
client_secret = 's'
username = ''
password = ''


class Chat:
    def __init__(self, chat_index, response_json):
        self.index = chat_index
        self.user_index = response_json['user']
        self.chat_type = response_json['type']
        self.content = response_json['content']

    def __str__(self):
        return "Msg Index : {}\nUser Index : {}\nType : {}\nContent : {}\n".format(self.index, self.user_index,
                                                                                   self.chat_type, self.content)


class TeamUpService:
    def __init__(self):
        self.token = None
        self.headers = None
        self.config = {
            'lp_idle_time': 1,
            'lp_wait_timeout': 30
        }

    def login(self):
        response = requests.post(
            url=auth_host + '/oauth2/token',
            data={
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password
            }
        )

        print(response.status_code)
        print(response.json())

        # TODO 실패 처리

        self.token = response.json()['access_token']
        self.headers = {'authorization': 'bearer ' + self.token}

        self.config = self.get_event_config()

    def get_event_config(self):
        response = requests.get(event_host + '/')

        if response.status_code == 200:
            return response.json()

    def get_events(self):
        response = requests.get(event_host + '/v3/events', headers=self.headers)

        print(response.status_code)
        print(response.json())

        events = response.json()['events']
        print(events)

    def get_chat_summary(self, room_index, chat_index):
        response = requests.get(
            edge_host + '/v3/message/summary/{}/{}/1'.format(room_index, chat_index),  # 1 은 confirm
            headers=self.headers
        )

        if response.status_code == 200:
            print(response.json())
            return Chat(chat_index, response.json())

    def post_chat(self, room_index, content):
        chat_header = dict(self.headers)
        chat_header['Content-Type'] = 'application/json; charset=utf-8'
        print(chat_header)
        print(edge_host + '/v3/message/{}/{}'.format(room_index, 1))
        response = requests.post(
            edge_host + '/v3/message/{}/{}'.format(room_index, 1),  # 1 은 타입
            headers=chat_header,
            json={'content': content}  # extras 추가해줘야함
        )

        print(response.status_code)
        print(response.json())


service = TeamUpService()
service.login()
