from abc import ABC, abstractmethod
from meeting import Meeting

class NotificationListener(ABC):
    @abstractmethod
    def on_meeting_booked(self, meeting: Meeting):
        pass

    @abstractmethod
    def on_meeting_cancelled(self, meeting: Meeting):
        pass
