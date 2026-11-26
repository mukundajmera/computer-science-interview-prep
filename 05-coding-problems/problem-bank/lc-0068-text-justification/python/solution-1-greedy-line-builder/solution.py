from typing import List


class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        lines: List[str] = []
        index = 0
        while index < len(words):
            start = index
            letters = len(words[index])
            index += 1
            while index < len(words) and letters + len(words[index]) + (index - start) <= maxWidth:
                letters += len(words[index])
                index += 1
            lines.append(self._format_line(words, start, index, letters, maxWidth, index == len(words)))
        return lines

    def _format_line(self, words: List[str], start: int, end: int, letters: int, width: int, last_line: bool) -> str:
        gaps = end - start - 1
        if last_line or gaps == 0:
            line = ' '.join(words[start:end])
            return line + ' ' * (width - len(line))
        total_spaces = width - letters
        even_spaces, extra_spaces = divmod(total_spaces, gaps)
        parts: List[str] = []
        for i in range(start, end):
            if i > start:
                spaces = even_spaces + (1 if i - start <= extra_spaces else 0)
                parts.append(' ' * spaces)
            parts.append(words[i])
        return ''.join(parts)
