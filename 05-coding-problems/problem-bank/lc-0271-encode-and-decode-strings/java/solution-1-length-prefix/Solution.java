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
        List<String> result = new ArrayList<>();
        int index = 0;
        while (index < s.length()) {
            int marker = s.indexOf('#', index);
            int length = Integer.parseInt(s.substring(index, marker));
            int start = marker + 1;
            result.add(s.substring(start, start + length));
            index = start + length;
        }
        return result;
    }
}
