from dataclasses import dataclass

@dataclass
class CrawlRequest:
    url: str
    depth: int = 0
