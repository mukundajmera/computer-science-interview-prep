import time
from typing import Dict
import urllib.parse

class PolitenessPolicy:
    def __init__(self, delay_ms: int = 100) -> None:
        self.delay_ms = delay_ms
        self.last_access: Dict[str, float] = {}

    def wait_for_host(self, url: str) -> None:
        host = urllib.parse.urlparse(url).netloc
        now = time.time()
        if host in self.last_access:
            elapsed = (now - self.last_access[host]) * 1000
            if elapsed < self.delay_ms:
                time.sleep((self.delay_ms - elapsed) / 1000.0)
        self.last_access[host] = time.time()
