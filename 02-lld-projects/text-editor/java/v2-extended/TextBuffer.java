

import java.util.List;

public interface TextBuffer {
    void insert(int lineNum, String text);
    void delete(int lineNum);
    void replace(int lineNum, String text);
    List<String> getAll();
}
