import java.util.ArrayList;
import java.util.List;

class StringIterator {
    private final List<Character> chars = new ArrayList<>();
    private final List<Integer> counts = new ArrayList<>();
    private int index = 0;

    public StringIterator(String compressedString) {
        for (int i = 0; i < compressedString.length();) {
            char c = compressedString.charAt(i++);
            int count = 0;
            while (i < compressedString.length() && Character.isDigit(compressedString.charAt(i))) count = count * 10 + compressedString.charAt(i++) - '0';
            chars.add(c);
            counts.add(count);
        }
    }

    public char next() {
        if (!hasNext()) return ' ';
        char c = chars.get(index);
        counts.set(index, counts.get(index) - 1);
        if (counts.get(index) == 0) index++;
        return c;
    }

    public boolean hasNext() {
        return index < chars.size();
    }
}
