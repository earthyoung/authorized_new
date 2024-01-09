from channels.generic.websocket import WebsocketConsumer
import json


class EchoConsumer(WebsocketConsumer):
    def receive(self, text_data=None, bytes_data=None):
        obj = json.loads(text_data)

        json_string = json.dumps(
            {
                "content": obj["content"],
                "user": obj["user"],
            }
        )
        self.send(json_string)
