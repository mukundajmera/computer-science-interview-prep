package v2_extended;

import java.util.Map;

/** Injectable downstream service: receives the scrubbed headers. */
public interface Downstream {
    Response call(String path, Map<String, String> headers);
}
