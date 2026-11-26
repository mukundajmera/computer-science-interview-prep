import re
from typing import List

class HtmlParser:
    def extract_links(self, html: str) -> List[str]:
        return re.findall(r"href=['\"](.*?)['\"]", html)
