

public class Benchmark {
    public static void main(String[] args) {
        GapBuffer gb = new GapBuffer(10);

        long startTime = System.currentTimeMillis();

        // Insert 100,000 lines
        for (int i = 0; i < 100000; i++) {
            gb.insert(i, "Line " + i);
        }

        long insertTime = System.currentTimeMillis() - startTime;
        System.out.println("Time to insert 100,000 lines: " + (insertTime / 1000.0) + " seconds");

        // Local cursor insertions
        startTime = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            gb.insert(99000 + i, "New Line " + i);
        }

        long localInsertTime = System.currentTimeMillis() - startTime;
        System.out.println("Time for 1,000 local cursor insertions: " + (localInsertTime / 1000.0) + " seconds");
    }
}
