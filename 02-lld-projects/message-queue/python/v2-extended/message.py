class Message:
    def __init__(self, message_id: str, payload: str):
        self.id = message_id
        self.payload = payload

    def __str__(self):
        return f"Message(id={self.id}, payload={self.payload})"
