/**
 * Command Pattern - V3 Advanced: Transactional Macro Commands
 */

import java.util.*;

interface MacroAction {
    void execute();
    void undo();
}

class TextDocument {
    private final List<String> lines = new ArrayList<>();

    public String getContent() {
        return String.join("\n", lines);
    }

    public int appendLine(String line) {
        lines.add(line);
        return lines.size() - 1;
    }

    public String removeLine(int index) {
        return lines.remove(index);
    }

    public void replace(String oldText, String newText) {
        for (int i = 0; i < lines.size(); i++) {
            lines.set(i, lines.get(i).replace(oldText, newText));
        }
    }

    public void replaceAllContent(String content) {
        lines.clear();
        if (!content.isEmpty()) {
            lines.addAll(Arrays.asList(content.split("\\n", -1)));
        }
    }
}

class AppendLineCommand implements MacroAction {
    private final TextDocument document;
    private final String line;
    private int index = -1;

    AppendLineCommand(TextDocument document, String line) {
        this.document = document;
        this.line = line;
    }

    @Override
    public void execute() {
        index = document.appendLine(line);
    }

    @Override
    public void undo() {
        if (index >= 0) {
            document.removeLine(index);
            index = -1;
        }
    }
}

class ReplaceTextCommand implements MacroAction {
    private final TextDocument document;
    private final String oldText;
    private final String newText;
    private String before = "";

    ReplaceTextCommand(TextDocument document, String oldText, String newText) {
        this.document = document;
        this.oldText = oldText;
        this.newText = newText;
    }

    @Override
    public void execute() {
        before = document.getContent();
        document.replace(oldText, newText);
    }

    @Override
    public void undo() {
        document.replaceAllContent(before);
    }
}

class FailingCommand implements MacroAction {
    private final String message;

    FailingCommand(String message) {
        this.message = message;
    }

    @Override
    public void execute() {
        throw new IllegalStateException(message);
    }

    @Override
    public void undo() { }
}

class MacroCommand implements MacroAction {
    private final String name;
    private final List<MacroAction> commands;
    private final Deque<MacroAction> executed = new ArrayDeque<>();

    MacroCommand(String name, List<MacroAction> commands) {
        this.name = name;
        this.commands = new ArrayList<>(commands);
    }

    public String getName() {
        return name;
    }

    @Override
    public void execute() {
        executed.clear();
        try {
            for (MacroAction command : commands) {
                command.execute();
                executed.push(command);
            }
        } catch (RuntimeException error) {
            undo();
            throw error;
        }
    }

    @Override
    public void undo() {
        while (!executed.isEmpty()) {
            executed.pop().undo();
        }
    }
}

public class MacroCommandDemo {
    public static void main(String[] args) {
        TextDocument document = new TextDocument();
        MacroCommand macro = new MacroCommand(
            "publish draft",
            Arrays.asList(
                new AppendLineCommand(document, "title"),
                new AppendLineCommand(document, "body"),
                new ReplaceTextCommand(document, "body", "final body")
            )
        );

        macro.execute();
        System.out.println(document.getContent());
        macro.undo();
        System.out.println("After undo: '" + document.getContent() + "'");
    }
}
