import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Queue;
import java.util.Set;

class Solution {
    private static final char[] LETTERS = {'A', 'C', 'G', 'T'};

    public int minMutation(String startGene, String endGene, String[] bank) {
        Set<String> available = new HashSet<>();
        for (String gene : bank) {
            available.add(gene);
        }
        Queue<String> queue = new ArrayDeque<>();
        queue.add(startGene);
        int steps = 0;
        while (!queue.isEmpty()) {
            for (int size = queue.size(); size > 0; size--) {
                String gene = queue.remove();
                if (gene.equals(endGene)) {
                    return steps;
                }
                char[] chars = gene.toCharArray();
                for (int i = 0; i < chars.length; i++) {
                    char original = chars[i];
                    for (char next : LETTERS) {
                        if (next == original) {
                            continue;
                        }
                        chars[i] = next;
                        String candidate = new String(chars);
                        if (available.remove(candidate)) {
                            queue.add(candidate);
                        }
                    }
                    chars[i] = original;
                }
            }
            steps++;
        }
        return -1;
    }
}
