import java.util.List;
import java.util.Map;

public class Demo {
    public static void main(String[] args) throws InterruptedException {
        DnsResolver resolver = new DnsResolver(
            Map.of("api.example.com", List.of("10.0.0.1", "10.0.0.2"))
        );

        System.out.println(resolver.resolve("api.example.com", 1000));
        System.out.println(resolver.resolve("api.example.com", 1000));
        Thread.sleep(1100);
        System.out.println(resolver.resolve("api.example.com", 1000));
    }
}
