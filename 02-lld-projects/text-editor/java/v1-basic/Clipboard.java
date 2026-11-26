import java.util.ArrayList;
import java.util.List;

public class Clipboard {
    private List<String> content;

    public Clipboard() {
        this.content = new ArrayList<>();
    }

    public void setContent(List<String> content) {
        this.content = new ArrayList<>(content);
    }

    public List<String> getContent() {
        return new ArrayList<>(content);
    }
}
