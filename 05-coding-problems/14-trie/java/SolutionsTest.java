import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        testTrie();
        testWordDictionary();
        testReplaceWords();
        testMapSum();
        testWordSearchII();
        testAutocompleteSystem();
        System.out.println("All Java tests passed!");
    }

    private static void assertEqual(Object actual, Object expected) {
        if (!actual.equals(expected)) {
            throw new AssertionError("Expected: " + expected + " but got: " + actual);
        }
    }

    private static void assertTrue(boolean val) {
        if (!val) throw new AssertionError("Expected true but got false");
    }

    private static void assertFalse(boolean val) {
        if (val) throw new AssertionError("Expected false but got true");
    }

    private static void testTrie() {
        Solutions.Trie trie = new Solutions.Trie();
        trie.insert("apple");
        assertTrue(trie.search("apple"));
        assertFalse(trie.search("app"));
        assertTrue(trie.startsWith("app"));
        trie.insert("app");
        assertTrue(trie.search("app"));
        assertFalse(trie.search("appl"));
        
        Solutions.Trie trie2 = new Solutions.Trie();
        trie2.insert("test");
        assertTrue(trie2.search("test"));
    }

    private static void testWordDictionary() {
        Solutions.WordDictionary wd = new Solutions.WordDictionary();
        wd.addWord("bad");
        wd.addWord("dad");
        wd.addWord("mad");
        assertFalse(wd.search("pad"));
        assertTrue(wd.search("bad"));
        assertTrue(wd.search(".ad"));
        assertTrue(wd.search("b.."));
        assertTrue(wd.search("m.d"));
        assertFalse(wd.search("m."));
    }

    private static void testReplaceWords() {
        Solutions.ReplaceWords rw = new Solutions.ReplaceWords();
        assertEqual(rw.replaceWords(Arrays.asList("cat", "bat", "rat"), "the cattle was rattled by the battery"), "the cat was rat by the bat");
        assertEqual(rw.replaceWords(Arrays.asList("a", "b", "c"), "aadsfasf absbs bbab cadsfafs"), "a a b c");
        assertEqual(rw.replaceWords(Arrays.asList("a", "aa", "aaa", "aaaa"), "a aa a aaaa aaa aaa aaa aaaaaa bbb baba ababa"), "a a a a a a a a bbb baba a");
        assertEqual(rw.replaceWords(Arrays.asList("catt","cat","bat","rat"), "the cattle was rattled by the battery"), "the cat was rat by the bat");
        assertEqual(rw.replaceWords(Arrays.asList("ac","ab"), "it is abnormal that this solution is accepted"), "it is ab that this solution is ac");
        assertEqual(rw.replaceWords(Arrays.asList("abc", "de"), "vwx yz"), "vwx yz");
    }

    private static void testMapSum() {
        Solutions.MapSum ms = new Solutions.MapSum();
        ms.insert("apple", 3);
        assertEqual(ms.sum("ap"), 3);
        ms.insert("app", 2);
        assertEqual(ms.sum("ap"), 5);
        ms.insert("apple", 2);
        assertEqual(ms.sum("ap"), 4);
        assertEqual(ms.sum("b"), 0);
        ms.insert("banana", 5);
        assertEqual(ms.sum("b"), 5);
    }

    private static void testWordSearchII() {
        Solutions.WordSearchII ws = new Solutions.WordSearchII();
        char[][] board = {{'o','a','a','n'},{'e','t','a','e'},{'i','h','k','r'},{'i','f','l','v'}};
        String[] words = {"oath","pea","eat","rain"};
        List<String> res = ws.findWords(board, words);
        Collections.sort(res);
        List<String> expected = Arrays.asList("eat", "oath");
        assertEqual(res, expected);

        char[][] board2 = {{'a','b'},{'c','d'}};
        String[] words2 = {"abcb"};
        assertEqual(ws.findWords(board2, words2), new ArrayList<>());
        
        char[][] board3 = {{'a'}};
        String[] words3 = {"a"};
        assertEqual(ws.findWords(board3, words3), Arrays.asList("a"));
        
        char[][] board4 = {{'a','a'}};
        String[] words4 = {"aaa"};
        assertEqual(ws.findWords(board4, words4), new ArrayList<>());

        char[][] board5 = {{'a','b','c'},{'a','e','d'},{'a','f','g'}};
        String[] words5 = {"eaabcdgfa"};
        assertEqual(ws.findWords(board5, words5), Arrays.asList("eaabcdgfa"));

        char[][] board6 = {{'a'}};
        String[] words6 = {"b"};
        assertEqual(ws.findWords(board6, words6), new ArrayList<>());
    }

    private static void testAutocompleteSystem() {
        Solutions.AutocompleteSystem ac = new Solutions.AutocompleteSystem(
            new String[]{"i love you", "island", "ironman", "i love leetcode"},
            new int[]{5, 3, 2, 2}
        );
        assertEqual(ac.input('i'), Arrays.asList("i love you", "island", "i love leetcode"));
        assertEqual(ac.input(' '), Arrays.asList("i love you", "i love leetcode"));
        assertEqual(ac.input('a'), new ArrayList<>());
        assertEqual(ac.input('#'), new ArrayList<>());
        assertEqual(ac.input('i'), Arrays.asList("i love you", "island", "i love leetcode"));
        assertEqual(ac.input(' '), Arrays.asList("i love you", "i love leetcode", "i a"));
        assertEqual(ac.input('a'), Arrays.asList("i a"));
        assertEqual(ac.input('#'), new ArrayList<>());
    }
}
