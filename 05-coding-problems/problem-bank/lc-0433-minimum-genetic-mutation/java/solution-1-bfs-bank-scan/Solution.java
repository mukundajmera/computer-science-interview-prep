import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Queue;
import java.util.Set;

class Solution {
    public int minMutation(String startGene, String endGene, String[] bank) {
        Set<String> unused = new HashSet<>();
        for (String gene : bank) {
            unused.add(gene);
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
                Set<String> nextLayer = new HashSet<>();
                for (String candidate : unused) {
                    if (differsByOne(gene, candidate)) {
                        queue.add(candidate);
                        nextLayer.add(candidate);
                    }
                }
                unused.removeAll(nextLayer);
            }
            steps++;
        }
        return -1;
    }

    private boolean differsByOne(String a, String b) {
        int diff = 0;
        for (int i = 0; i < a.length(); i++) {
            if (a.charAt(i) != b.charAt(i) && ++diff > 1) {
                return false;
            }
        }
        return diff == 1;
    }
}
