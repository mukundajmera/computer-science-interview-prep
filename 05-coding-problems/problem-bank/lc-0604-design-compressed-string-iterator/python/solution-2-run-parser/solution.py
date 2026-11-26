class StringIterator:
    def __init__(self, compressedString: str):
        self.runs = []
        index = 0
        while index < len(compressedString):
            char = compressedString[index]
            index += 1
            count = 0
            while index < len(compressedString) and compressedString[index].isdigit():
                count = count * 10 + int(compressedString[index])
                index += 1
            self.runs.append([char, count])
        self.index = 0

    def next(self) -> str:
        if not self.hasNext():
            return ' '
        char = self.runs[self.index][0]
        self.runs[self.index][1] -= 1
        if self.runs[self.index][1] == 0:
            self.index += 1
        return char

    def hasNext(self) -> bool:
        return self.index < len(self.runs)
