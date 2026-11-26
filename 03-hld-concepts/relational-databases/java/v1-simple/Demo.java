package v1_simple;

import java.util.List;

public class Demo {
    public static void main(String[] args) {
        System.out.println("B+ Tree Index Demo");

        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(4);

        System.out.println("Inserting keys 1 to 20...");
        for (int i = 1; i <= 20; i++) {
            tree.insert(i, "Value_" + i);
        }

        System.out.println("Searching for key 10: " + tree.search(10));
        System.out.println("Searching for key 25: " + tree.search(25));

        System.out.println("Range scan from 5 to 15:");
        List<BPlusTreeIndex.Entry<Integer, String>> results = tree.rangeScan(5, 15);
        for (BPlusTreeIndex.Entry<Integer, String> entry : results) {
            System.out.println("  " + entry.key + " -> " + entry.value);
        }
    }
}
