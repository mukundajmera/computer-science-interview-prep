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
    def __init__(self, capacity: int = 10000, batch_size: int = 100):
        self._queue: queue.Queue = queue.Queue(maxsize=capacity)
        self._is_running = True
        self._batch_size = batch_size
        self._worker = threading.Thread(target=self._process_logs, name="AsyncLogWorker", daemon=False)
        self._worker.start()

    def submit(self, event: LogEvent, appenders: List[Appender]) -> None:
        if self._is_running:
            try:
                self._queue.put(LogTask(event, appenders), block=True, timeout=1.0)
            except queue.Full:
                pass

    def _process_logs(self) -> None:
        while self._is_running or not self._queue.empty():
            tasks = []
            try:
                task = self._queue.get(timeout=0.1)
                tasks.append(task)
                
                # Try to batch
                while len(tasks) < self._batch_size and not self._queue.empty():
                    try:
                        t = self._queue.get_nowait()
                        tasks.append(t)
                    except queue.Empty:
                        break
                        
                for t in tasks:
                    for appender in t.appenders:
                        try:
                            appender.append(t.event)
                        except Exception as e:
                            print(f"Appender failed: {e}")
                    self._queue.task_done()
                    
            except queue.Empty:
                pass

    def stop(self) -> None:
        self._is_running = False
        self._worker.join(timeout=5.0)
