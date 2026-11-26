package v2_extended;

import java.net.URI;
import java.net.URISyntaxException;

public class UrlCanonicalizer {
    public String canonicalize(String urlStr) {
        try {
            URI uri = new URI(urlStr);
            String scheme = uri.getScheme() != null ? uri.getScheme().toLowerCase() : "";
            String host = uri.getHost() != null ? uri.getHost().toLowerCase() : "";
            String path = uri.getPath() != null ? uri.getPath() : "";
            if (path.isEmpty()) path = "/";
            
            return scheme + "://" + host + (uri.getPort() != -1 ? ":" + uri.getPort() : "") + path;
        } catch (URISyntaxException e) {
            return urlStr;
        }
    }
}
