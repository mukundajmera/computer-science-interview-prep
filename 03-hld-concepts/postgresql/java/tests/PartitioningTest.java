public class PartitioningTest {
    public static void main(String[] args) {
        String res = Partitioning.getPartition("2023-10-15");
        assert "part_2023_10".equals(res);
        System.out.println("PartitioningTest passed");
    }
}
