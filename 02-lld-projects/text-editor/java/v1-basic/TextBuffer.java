import java.util.List;

public interface TextBuffer {
    void insert(int lineNum, String text);
    String delete(int lineNum);
    List<String> deleteRange(int start, int end);
    String getLine(int lineNum);
    List<String> getRange(int start, int end);
    List<String> getAll();
}
