import java.util.List;

public class Demo {
    public static void main(String[] args) {
        DataPartitioner partitioner = new DataPartitioner(4);
        System.out.println(partitioner.hashPartition("user-123"));
        System.out.println(
            partitioner.rangePartition(450, List.of(
                new DataPartitioner.IntRange(0, 99),
                new DataPartitioner.IntRange(100, 499),
                new DataPartitioner.IntRange(500, 999)
            ))
        );
    }
}
