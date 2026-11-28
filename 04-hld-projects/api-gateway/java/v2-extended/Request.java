package v2_extended;

import java.util.Map;

public class Request {
    public String path;
    public Map<String, String> headers;

    public Request(String path, Map<String, String> headers) {
        this.path = path;
        this.headers = headers;
    }
}
