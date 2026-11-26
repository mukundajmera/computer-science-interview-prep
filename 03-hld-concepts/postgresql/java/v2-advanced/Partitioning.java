public class Partitioning {
    public static String getPartition(String dateStr) {
        return "part_" + dateStr.substring(0, 7).replace("-", "_");
    }
}
