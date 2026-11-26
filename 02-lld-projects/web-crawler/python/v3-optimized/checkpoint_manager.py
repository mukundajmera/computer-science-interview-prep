import json
from typing import List
import threading

class CheckpointManager:
    def __init__(self) -> None:
        self.saved_state: List[str] = []
        self.lock = threading.Lock()

    def save_checkpoint(self, queue_state: List[str]) -> None:
        with self.lock:
            self.saved_state = queue_state.copy()

    def load_checkpoint(self) -> List[str]:
        with self.lock:
            return self.saved_state.copy()
