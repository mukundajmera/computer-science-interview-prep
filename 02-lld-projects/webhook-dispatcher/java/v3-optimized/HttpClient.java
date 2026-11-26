
import java.util.Map;

public interface HttpClient {
    DeliveryResult post(String url, String data, Map<String, String> headers);
}
