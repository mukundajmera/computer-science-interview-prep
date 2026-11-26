

import java.util.ArrayList;
import java.util.List;

public class LineBuffer implements TextBuffer {
    private final List<String> lines;

    public LineBuffer() {
        this.lines = new ArrayList<>();
    }

    @Override
    public void insert(int lineNum, String text) {
        int index = lineNum - 1;
        if (index >= 0 && index <= lines.size()) {
            lines.add(index, text);
        } else {
            lines.add(text);
        }
    }

    @Override
    public void delete(int lineNum) {
        int index = lineNum - 1;
        if (index >= 0 && index < lines.size()) {
            lines.remove(index);
        }
    }

    @Override
    public void replace(int lineNum, String text) {
        int index = lineNum - 1;
        if (index >= 0 && index < lines.size()) {
            lines.set(index, text);
        }
    }

    @Override
    public List<String> getAll() {
        return new ArrayList<>(lines);
    }
}
