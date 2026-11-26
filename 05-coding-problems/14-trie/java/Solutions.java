import java.util.*;

public class Solutions {

    static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        boolean isWord = false;
        String word = null; // Used for WordSearchII
    }

    public static class Trie {
        TrieNode root = new TrieNode();

        public void insert(String word) {
            TrieNode node = root;
            for (char c : word.toCharArray()) {
                node.children.putIfAbsent(c, new TrieNode());
                node = node.children.get(c);
            }
            node.isWord = true;
        }

        public boolean search(String word) {
            TrieNode node = root;
            for (char c : word.toCharArray()) {
                if (!node.children.containsKey(c)) return false;
                node = node.children.get(c);
            }
            return node.isWord;
        }

        public boolean startsWith(String prefix) {
            TrieNode node = root;
            for (char c : prefix.toCharArray()) {
                if (!node.children.containsKey(c)) return false;
                node = node.children.get(c);
            }
            return true;
        }
    }

    public static class WordDictionary {
        TrieNode root = new TrieNode();

        public void addWord(String word) {
            TrieNode node = root;
            for (char c : word.toCharArray()) {
                node.children.putIfAbsent(c, new TrieNode());
                node = node.children.get(c);
            }
            node.isWord = true;
        }

        public boolean search(String word) {
            return dfs(0, root, word);
        }

        private boolean dfs(int index, TrieNode node, String word) {
            if (index == word.length()) return node.isWord;
            char c = word.charAt(index);
            if (c != '.') {
                if (!node.children.containsKey(c)) return false;
                return dfs(index + 1, node.children.get(c), word);
            } else {
                for (TrieNode child : node.children.values()) {
                    if (dfs(index + 1, child, word)) return true;
                }
                return false;
            }
        }
    }

    public static class ReplaceWords {
        public String replaceWords(List<String> dictionary, String sentence) {
            TrieNode root = new TrieNode();
            for (String word : dictionary) {
                TrieNode node = root;
                for (char c : word.toCharArray()) {
                    node.children.putIfAbsent(c, new TrieNode());
                    node = node.children.get(c);
                }
                node.isWord = true;
            }

            StringBuilder res = new StringBuilder();
            String[] words = sentence.split(" ");
            for (int i = 0; i < words.length; i++) {
                String word = words[i];
                TrieNode node = root;
                StringBuilder prefix = new StringBuilder();
                boolean found = false;
                for (char c : word.toCharArray()) {
                    if (!node.children.containsKey(c)) break;
                    node = node.children.get(c);
                    prefix.append(c);
                    if (node.isWord) {
                        res.append(prefix);
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    res.append(word);
                }
                if (i != words.length - 1) res.append(" ");
            }
            return res.toString();
        }
    }

    public static class MapSum {
        static class MapSumNode {
            Map<Character, MapSumNode> children = new HashMap<>();
            int sum = 0;
        }
        
        MapSumNode root = new MapSumNode();
        Map<String, Integer> map = new HashMap<>();

        public void insert(String key, int val) {
            int delta = val - map.getOrDefault(key, 0);
            map.put(key, val);
            MapSumNode node = root;
            node.sum += delta;
            for (char c : key.toCharArray()) {
                node.children.putIfAbsent(c, new MapSumNode());
                node = node.children.get(c);
                node.sum += delta;
            }
        }

        public int sum(String prefix) {
            MapSumNode node = root;
            for (char c : prefix.toCharArray()) {
                if (!node.children.containsKey(c)) return 0;
                node = node.children.get(c);
            }
            return node.sum;
        }
    }

    public static class WordSearchII {
        public List<String> findWords(char[][] board, String[] words) {
            TrieNode root = new TrieNode();
            for (String word : words) {
                TrieNode node = root;
                for (char c : word.toCharArray()) {
                    node.children.putIfAbsent(c, new TrieNode());
                    node = node.children.get(c);
                }
                node.isWord = true;
                node.word = word;
            }

            List<String> res = new ArrayList<>();
            for (int r = 0; r < board.length; r++) {
                for (int c = 0; c < board[0].length; c++) {
                    dfs(board, r, c, root, res);
                }
            }
            return res;
        }

        private void dfs(char[][] board, int r, int c, TrieNode node, List<String> res) {
            if (r < 0 || r >= board.length || c < 0 || c >= board[0].length) return;
            char ch = board[r][c];
            if (ch == '#' || !node.children.containsKey(ch)) return;

            TrieNode nextNode = node.children.get(ch);
            if (nextNode.isWord) {
                res.add(nextNode.word);
                nextNode.isWord = false;
            }

            board[r][c] = '#';
            dfs(board, r + 1, c, nextNode, res);
            dfs(board, r - 1, c, nextNode, res);
            dfs(board, r, c + 1, nextNode, res);
            dfs(board, r, c - 1, nextNode, res);
            board[r][c] = ch;
        }
    }

    public static class AutocompleteSystem {
        static class AutocompleteNode {
            Map<Character, AutocompleteNode> children = new HashMap<>();
            Map<String, Integer> counts = new HashMap<>();
        }

        AutocompleteNode root = new AutocompleteNode();
        Map<String, Integer> sentenceCounts = new HashMap<>();
        String currentPrefix = "";
        AutocompleteNode currentNode = root;

        public AutocompleteSystem(String[] sentences, int[] times) {
            for (int i = 0; i < sentences.length; i++) {
                addSentence(sentences[i], times[i]);
            }
        }

        private void addSentence(String sentence, int count) {
            sentenceCounts.put(sentence, sentenceCounts.getOrDefault(sentence, 0) + count);
            AutocompleteNode node = root;
            for (char c : sentence.toCharArray()) {
                node.children.putIfAbsent(c, new AutocompleteNode());
                node = node.children.get(c);
                node.counts.put(sentence, node.counts.getOrDefault(sentence, 0) + count);
            }
        }

        public List<String> input(char c) {
            if (c == '#') {
                addSentence(currentPrefix, 1);
                currentPrefix = "";
                currentNode = root;
                return new ArrayList<>();
            }

            currentPrefix += c;
            if (currentNode != null) {
                currentNode = currentNode.children.getOrDefault(c, null);
            }

            if (currentNode == null) return new ArrayList<>();

            List<String> candidates = new ArrayList<>(currentNode.counts.keySet());
            candidates.sort((a, b) -> {
                int countA = sentenceCounts.get(a);
                int countB = sentenceCounts.get(b);
                if (countA != countB) return countB - countA;
                return a.compareTo(b);
            });

            return candidates.subList(0, Math.min(3, candidates.size()));
        }
    }
}
