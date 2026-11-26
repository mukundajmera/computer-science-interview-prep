import unittest
from solutions import Trie, WordDictionary, ReplaceWords, MapSum, WordSearchII, AutocompleteSystem

class TestSolutions(unittest.TestCase):
    def test_trie(self):
        trie = Trie()
        trie.insert("apple")
        self.assertTrue(trie.search("apple"))
        self.assertFalse(trie.search("app"))
        self.assertTrue(trie.startsWith("app"))
        trie.insert("app")
        self.assertTrue(trie.search("app"))
        self.assertFalse(trie.search("appl"))
        
        trie2 = Trie()
        trie2.insert("test")
        self.assertTrue(trie2.search("test"))

    def test_word_dictionary(self):
        wd = WordDictionary()
        wd.addWord("bad")
        wd.addWord("dad")
        wd.addWord("mad")
        self.assertFalse(wd.search("pad"))
        self.assertTrue(wd.search("bad"))
        self.assertTrue(wd.search(".ad"))
        self.assertTrue(wd.search("b.."))
        self.assertTrue(wd.search("m.d"))
        self.assertFalse(wd.search("m."))

    def test_replace_words(self):
        rw = ReplaceWords()
        self.assertEqual(rw.replaceWords(["cat", "bat", "rat"], "the cattle was rattled by the battery"), "the cat was rat by the bat")
        self.assertEqual(rw.replaceWords(["a", "b", "c"], "aadsfasf absbs bbab cadsfafs"), "a a b c")
        self.assertEqual(rw.replaceWords(["a", "aa", "aaa", "aaaa"], "a aa a aaaa aaa aaa aaa aaaaaa bbb baba ababa"), "a a a a a a a a bbb baba a")
        self.assertEqual(rw.replaceWords(["catt","cat","bat","rat"], "the cattle was rattled by the battery"), "the cat was rat by the bat")
        self.assertEqual(rw.replaceWords(["ac","ab"], "it is abnormal that this solution is accepted"), "it is ab that this solution is ac")
        self.assertEqual(rw.replaceWords(["abc", "de"], "vwx yz"), "vwx yz")

    def test_map_sum(self):
        ms = MapSum()
        ms.insert("apple", 3)
        self.assertEqual(ms.sum("ap"), 3)
        ms.insert("app", 2)
        self.assertEqual(ms.sum("ap"), 5)
        ms.insert("apple", 2)
        self.assertEqual(ms.sum("ap"), 4)
        self.assertEqual(ms.sum("b"), 0)
        ms.insert("banana", 5)
        self.assertEqual(ms.sum("b"), 5)

    def test_word_search_ii(self):
        ws = WordSearchII()
        board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
        words = ["oath","pea","eat","rain"]
        self.assertEqual(sorted(ws.findWords(board, words)), sorted(["eat","oath"]))
        board2 = [["a","b"],["c","d"]]
        words2 = ["abcb"]
        self.assertEqual(ws.findWords(board2, words2), [])
        board3 = [["a"]]
        words3 = ["a"]
        self.assertEqual(ws.findWords(board3, words3), ["a"])
        board4 = [["a","a"]]
        words4 = ["aaa"]
        self.assertEqual(ws.findWords(board4, words4), [])
        board5 = [["a","b","c"],["a","e","d"],["a","f","g"]]
        words5 = ["eaabcdgfa"]
        self.assertEqual(ws.findWords(board5, words5), ["eaabcdgfa"])
        board6 = [["a"]]
        words6 = ["b"]
        self.assertEqual(ws.findWords(board6, words6), [])

    def test_autocomplete(self):
        ac = AutocompleteSystem(["i love you", "island", "ironman", "i love leetcode"], [5, 3, 2, 2])
        self.assertEqual(ac.input('i'), ["i love you", "island", "i love leetcode"])
        self.assertEqual(ac.input(' '), ["i love you", "i love leetcode"])
        self.assertEqual(ac.input('a'), [])
        self.assertEqual(ac.input('#'), [])
        self.assertEqual(ac.input('i'), ["i love you", "island", "i love leetcode"])
        self.assertEqual(ac.input(' '), ["i love you", "i love leetcode", "i a"])
        self.assertEqual(ac.input('a'), ["i a"])
        self.assertEqual(ac.input('#'), [])

if __name__ == '__main__':
    unittest.main()
