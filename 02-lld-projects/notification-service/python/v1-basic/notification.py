
class Notification:
    def __init__(self, user_id, message, channel_type):
        self.user_id = user_id
        self.message = message
        self.channel_type = channel_type

class Channel:
    def send(self, notification):
        pass

class EmailChannel(Channel):
    def send(self, notification):
        # Simulate sending email
        return True

class SMSChannel(Channel):
    def send(self, notification):
        # Simulate sending SMS
        return True

class Dispatcher:
    def __init__(self):
        self.channels = {
            "EMAIL": EmailChannel(),
            "SMS": SMSChannel()
        }

    def dispatch(self, notification):
        channel = self.channels.get(notification.channel_type)
        if channel:
            return channel.send(notification)
        return False
