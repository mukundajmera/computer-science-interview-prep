import java.util.List;

public interface TopKQueryService {
    List<String> topK(String windowKey, int k);
}
