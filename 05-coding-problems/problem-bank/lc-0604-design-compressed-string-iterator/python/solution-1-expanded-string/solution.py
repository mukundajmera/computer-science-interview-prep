class StringIterator:
    def __init__(self, compressedString: str):
        pieces = []
        index = 0
        while index < len(compressedString):
            char = compressedString[index]
            index += 1
            count = 0
            while index < len(compressedString) and compressedString[index].isdigit():
                count = count * 10 + int(compressedString[index])
                index += 1
            pieces.append(char * count)
        self.expanded = ''.join(pieces)
        self.index = 0

    def next(self) -> str:
        if not self.hasNext():
            return ' '
        char = self.expanded[self.index]
        self.index += 1
        return char

    def hasNext(self) -> bool:
        return self.index < len(self.expanded)
