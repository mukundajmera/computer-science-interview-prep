import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<String> fullJustify(String[] words, int maxWidth) {
        List<String> lines = new ArrayList<>();
        int index = 0;
        while (index < words.length) {
            int start = index;
            int letters = words[index].length();
            index++;
            while (index < words.length && letters + words[index].length() + (index - start) <= maxWidth) {
                letters += words[index].length();
                index++;
            }
            boolean lastLine = index == words.length;
            lines.add(formatLine(words, start, index, letters, maxWidth, lastLine));
        }
        return lines;
    }

    private String formatLine(String[] words, int start, int end, int letters, int width, boolean lastLine) {
        int gaps = end - start - 1;
        StringBuilder builder = new StringBuilder();
        if (lastLine || gaps == 0) {
            for (int i = start; i < end; i++) {
                if (i > start) {
                    builder.append(' ');
                }
                builder.append(words[i]);
            }
            while (builder.length() < width) {
                builder.append(' ');
            }
            return builder.toString();
        }
        int totalSpaces = width - letters;
        int evenSpaces = totalSpaces / gaps;
        int extraSpaces = totalSpaces % gaps;
        for (int i = start; i < end; i++) {
            if (i > start) {
                int spaces = evenSpaces + (i - start <= extraSpaces ? 1 : 0);
                for (int j = 0; j < spaces; j++) {
                    builder.append(' ');
                }
            }
            builder.append(words[i]);
        }
        return builder.toString();
    }
}
