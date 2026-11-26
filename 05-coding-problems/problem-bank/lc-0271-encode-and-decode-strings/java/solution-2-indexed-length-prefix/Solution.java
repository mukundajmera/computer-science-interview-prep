import java.util.ArrayList;
import java.util.List;

class Codec {
    public String encode(List<String> strs) {
        StringBuilder builder = new StringBuilder();
        for (String value : strs) {
            builder.append(value.length()).append('#').append(value);
        }
        return builder.toString();
    }

    public List<String> decode(String s) {
        List<String> decoded = new ArrayList<>();
        int index = 0;
        while (index < s.length()) {
            int length = 0;
            while (s.charAt(index) != '#') {
                length = length * 10 + (s.charAt(index) - '0');
                index++;
            }
            index++;
            decoded.add(s.substring(index, index + length));
            index += length;
        }
        return decoded;
    }
}
