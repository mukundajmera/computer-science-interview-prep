import java.util.ArrayList;
import java.util.List;

public class LineBuffer implements TextBuffer {
    private final List<String> lines;

    public LineBuffer() {
        this.lines = new ArrayList<>();
    }

    @Override
    public void insert(int lineNum, String text) {
        int index = Math.max(0, lineNum - 1); // Convert to 0-indexed, handle < 1
        if (index >= lines.size()) {
            // Pad with empty lines if inserting past the end
            while (lines.size() < index) {
                lines.add("");
            }
            lines.add(text);
        } else {
            lines.add(index, text);
        }
    }

    @Override
    public String delete(int lineNum) {
        int index = lineNum - 1;
        if (index < 0 || index >= lines.size()) {
            return null; // Or throw exception
        }
        return lines.remove(index);
    }

    @Override
    public List<String> deleteRange(int start, int end) {
        int startIndex = Math.max(0, start - 1);
        int endIndex = Math.min(lines.size() - 1, end - 1);
        
        List<String> deletedLines = new ArrayList<>();
        if (startIndex > endIndex || startIndex >= lines.size()) {
            return deletedLines;
        }

        for (int i = 0; i <= endIndex - startIndex; i++) {
            deletedLines.add(lines.remove(startIndex));
        }
        return deletedLines;
    }

    @Override
    public String getLine(int lineNum) {
        int index = lineNum - 1;
        if (index < 0 || index >= lines.size()) {
            return null;
        }
        return lines.get(index);
    }

    @Override
    public List<String> getRange(int start, int end) {
        int startIndex = Math.max(0, start - 1);
        int endIndex = Math.min(lines.size() - 1, end - 1);
        
        List<String> result = new ArrayList<>();
        if (startIndex > endIndex || startIndex >= lines.size()) {
            return result;
        }

        for (int i = startIndex; i <= endIndex; i++) {
            result.add(lines.get(i));
        }
        return result;
    }

    @Override
    public List<String> getAll() {
        return new ArrayList<>(lines);
    }
}
