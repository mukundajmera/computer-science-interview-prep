from collections import defaultdict
from typing import List

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True

    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_word

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True


class WordDictionaryNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class WordDictionary:
    def __init__(self):
        self.root = WordDictionaryNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = WordDictionaryNode()
            node = node.children[char]
        node.is_word = True

    def search(self, word: str) -> bool:
        def dfs(index, node):
            if index == len(word):
                return node.is_word
            char = word[index]
            if char != ".":
                if char not in node.children:
                    return False
                return dfs(index + 1, node.children[char])
            for child in node.children.values():
                if dfs(index + 1, child):
                    return True
            return False
        return dfs(0, self.root)


class ReplaceWords:
    def replaceWords(self, dictionary: List[str], sentence: str) -> str:
        root = TrieNode()
        for word in dictionary:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_word = True
            
        res = []
        for word in sentence.split():
            node = root
            prefix = ""
            found = False
            for char in word:
                if char not in node.children:
                    break
                node = node.children[char]
                prefix += char
                if node.is_word:
                    res.append(prefix)
                    found = True
                    break
            if not found:
                res.append(word)
        return " ".join(res)


class MapSumNode:
    def __init__(self):
        self.children = {}
        self.sum = 0

class MapSum:
    def __init__(self):
        self.root = MapSumNode()
        self.map = {}

    def insert(self, key: str, val: int) -> None:
        delta = val - self.map.get(key, 0)
        self.map[key] = val
        node = self.root
        node.sum += delta
        for char in key:
            if char not in node.children:
                node.children[char] = MapSumNode()
            node = node.children[char]
            node.sum += delta

    def sum(self, prefix: str) -> int:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.sum


class WordSearchII:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_word = True
            node.word = word
            
        res = []
        ROWS, COLS = len(board), len(board[0])
        
        def dfs(r, c, node):
            if r < 0 or r >= ROWS or c < 0 or c >= COLS or board[r][c] not in node.children:
                return
            
            tmp = board[r][c]
            board[r][c] = "#"
            next_node = node.children[tmp]
            
            if next_node.is_word:
                res.append(next_node.word)
                next_node.is_word = False
                
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                dfs(r + dr, c + dc, next_node)
            board[r][c] = tmp

        for r in range(ROWS):
            for c in range(COLS):
                dfs(r, c, root)
        return res


class AutocompleteNode:
    def __init__(self):
        self.children = {}
        self.counts = defaultdict(int)

class AutocompleteSystem:
    def __init__(self, sentences: List[str], times: List[int]):
        self.root = AutocompleteNode()
        self.sentence_counts = defaultdict(int)
        self.current_prefix = ""
        self.current_node = self.root
        
        for i in range(len(sentences)):
            self.add_sentence(sentences[i], times[i])

    def add_sentence(self, sentence: str, count: int):
        self.sentence_counts[sentence] += count
        node = self.root
        for char in sentence:
            if char not in node.children:
                node.children[char] = AutocompleteNode()
            node = node.children[char]
            node.counts[sentence] += count

    def input(self, c: str) -> List[str]:
        if c == "#":
            self.add_sentence(self.current_prefix, 1)
            self.current_prefix = ""
            self.current_node = self.root
            return []
        
        self.current_prefix += c
        if self.current_node:
            if c in self.current_node.children:
                self.current_node = self.current_node.children[c]
            else:
                self.current_node = None
                
        if not self.current_node:
            return []
            
        suggestions = sorted(self.current_node.counts.keys(), key=lambda x: (-self.sentence_counts[x], x))
        return suggestions[:3]
