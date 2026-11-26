import threading
from typing import List
import time

try:
    from .shard_queue import ShardQueue
    from .backpressure_controller import BackpressureController
except ImportError:
    from shard_queue import ShardQueue
    from backpressure_controller import BackpressureController

class CrawlCoordinator:
    def __init__(self, queue: ShardQueue, backpressure: BackpressureController) -> None:
        self.queue = queue
        self.backpressure = backpressure
        self.completed: List[str] = []
        self.lock = threading.Lock()
        self.running = True
        
    def cancel(self) -> None:
        self.running = False

    def worker_loop(self, host: str, num_tasks: int) -> None:
        tasks_done = 0
        while tasks_done < num_tasks and self.running:
            if self.backpressure.acquire():
                try:
                    req = self.queue.dequeue(host)
                    if req:
                        with self.lock:
                            self.completed.append(req.url)
                        tasks_done += 1
                    else:
                        time.sleep(0.01)
                finally:
                    self.backpressure.release()
            else:
                time.sleep(0.01)

    def run_concurrently(self, host: str, num_tasks: int, num_threads: int) -> None:
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self.worker_loop, args=(host, num_tasks // num_threads))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
