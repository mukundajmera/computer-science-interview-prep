from typing import Dict, List
import urllib.parse

class RobotsPolicy:
    def __init__(self) -> None:
        self.disallowed: Dict[str, List[str]] = {}

    def add_rule(self, host: str, path: str) -> None:
        if host not in self.disallowed:
            self.disallowed[host] = []
        self.disallowed[host].append(path)

    def is_allowed(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()
        if host in self.disallowed:
            for path in self.disallowed[host]:
                if parsed.path.startswith(path):
                    return False
        return True
