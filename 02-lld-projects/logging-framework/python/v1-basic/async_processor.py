import queue
import threading
from typing import List, Optional
from log_event import LogEvent
from appenders import Appender

class LogTask:
    def __init__(self, event: LogEvent, appenders: List[Appender]):
        self.event = event
        self.appenders = appenders

class AsyncLogProcessor:
    def __init__(self, capacity: int = 10000):
        self._queue: queue.Queue = queue.Queue(maxsize=capacity)
        self._is_running = True
        self._worker = threading.Thread(target=self._process_logs, name="AsyncLogWorker", daemon=False)
        self._worker.start()

    def submit(self, event: LogEvent, appenders: List[Appender]) -> None:
        if self._is_running:
            try:
                # Block if full to prevent dropping (for basic implementation)
                self._queue.put(LogTask(event, appenders), block=True, timeout=1.0)
            except queue.Full:
                pass # Queue full, log dropped in this simple impl

    def _process_logs(self) -> None:
        while self._is_running or not self._queue.empty():
            try:
                task = self._queue.get(timeout=0.1)
                for appender in task.appenders:
                    try:
                        appender.append(task.event)
                    except Exception as e:
                        # Don't let appender crash the processor
                        print(f"Appender failed: {e}")
                self._queue.task_done()
            except queue.Empty:
                pass

    def stop(self) -> None:
        self._is_running = False
        # Queue.get with timeout doesn't block indefinitely so no need to artificially interrupt.
        # Just join the thread so it finishes remaining items.
        self._worker.join(timeout=5.0)

