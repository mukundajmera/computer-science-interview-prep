public class Demo {
    public static void main(String[] args) {
        long customEpoch = 1609459200000L; // Jan 1 2021
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, customEpoch, 5);
        
        long id = generator.nextId();
        System.out.println("Generated ID: " + id);
        
        IdComponents components = generator.parse(id);
        System.out.println("Parsed Components: " + components);
    }
}
