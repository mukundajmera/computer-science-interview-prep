from dataclasses import dataclass, field
from typing import List

@dataclass
class CrawlResult:
    url: str
    status_code: int
    content: str = ""
    links: List[str] = field(default_factory=list)
    content_hash: str = ""
    fetched_at: float = 0.0
