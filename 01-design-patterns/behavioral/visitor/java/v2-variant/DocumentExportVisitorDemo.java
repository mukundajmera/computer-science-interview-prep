package visitor.v2;

import java.util.*;

/**
 * v2-variant: Document Elements Multi-Format Exporter using Visitor Pattern.
 * Decouples document representation (Heading, Paragraph, CodeBlock, Hyperlink)
 * from export targets (Markdown, HTML, PlainText) using double dispatch.
 */
public class DocumentExportVisitorDemo {

    public interface DocumentVisitor {
        void visit(Heading heading);
        void visit(Paragraph paragraph);
        void visit(CodeBlock codeBlock);
        void visit(Hyperlink hyperlink);
    }

    public interface DocumentElement {
        void accept(DocumentVisitor visitor);
    }

    public static class Heading implements DocumentElement {
        private final String text;
        private final int level;

        public Heading(String text, int level) {
            this.text = Objects.requireNonNull(text);
            this.level = Math.max(1, Math.min(6, level));
        }

        public String getText() {
            return text;
        }

        public int getLevel() {
            return level;
        }

        @Override
        public void accept(DocumentVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class Paragraph implements DocumentElement {
        private final String text;

        public Paragraph(String text) {
            this.text = Objects.requireNonNull(text);
        }

        public String getText() {
            return text;
        }

        @Override
        public void accept(DocumentVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class CodeBlock implements DocumentElement {
        private final String code;
        private final String language;

        public CodeBlock(String code, String language) {
            this.code = Objects.requireNonNull(code);
            this.language = language != null ? language : "";
        }

        public String getCode() {
            return code;
        }

        public String getLanguage() {
            return language;
        }

        @Override
        public void accept(DocumentVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class Hyperlink implements DocumentElement {
        private final String label;
        private final String url;

        public Hyperlink(String label, String url) {
            this.label = Objects.requireNonNull(label);
            this.url = Objects.requireNonNull(url);
        }

        public String getLabel() {
            return label;
        }

        public String getUrl() {
            return url;
        }

        @Override
        public void accept(DocumentVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class MarkdownExportVisitor implements DocumentVisitor {
        private final StringBuilder sb = new StringBuilder();

        @Override
        public void visit(Heading heading) {
            sb.append("#".repeat(heading.getLevel())).append(" ").append(heading.getText()).append("\n\n");
        }

        @Override
        public void visit(Paragraph paragraph) {
            sb.append(paragraph.getText()).append("\n\n");
        }

        @Override
        public void visit(CodeBlock codeBlock) {
            sb.append("```").append(codeBlock.getLanguage()).append("\n")
              .append(codeBlock.getCode()).append("\n```\n\n");
        }

        @Override
        public void visit(Hyperlink hyperlink) {
            sb.append("[").append(hyperlink.getLabel()).append("](").append(hyperlink.getUrl()).append(")\n\n");
        }

        public String getExportedOutput() {
            return sb.toString().trim();
        }
    }

    public static class HtmlExportVisitor implements DocumentVisitor {
        private final StringBuilder sb = new StringBuilder();

        @Override
        public void visit(Heading heading) {
            sb.append("<h").append(heading.getLevel()).append(">")
              .append(heading.getText())
              .append("</h").append(heading.getLevel()).append(">\n");
        }

        @Override
        public void visit(Paragraph paragraph) {
            sb.append("<p>").append(paragraph.getText()).append("</p>\n");
        }

        @Override
        public void visit(CodeBlock codeBlock) {
            sb.append("<pre><code class=\"language-").append(codeBlock.getLanguage()).append("\">")
              .append(codeBlock.getCode())
              .append("</code></pre>\n");
        }

        @Override
        public void visit(Hyperlink hyperlink) {
            sb.append("<a href=\"").append(hyperlink.getUrl()).append("\">")
              .append(hyperlink.getLabel())
              .append("</a>\n");
        }

        public String getExportedOutput() {
            return sb.toString().trim();
        }
    }

    public static void main(String[] args) {
        List<DocumentElement> doc = List.of(
                new Heading("System Architecture", 1),
                new Paragraph("This is a modular microservice setup."),
                new CodeBlock("npm start", "bash"),
                new Hyperlink("API Docs", "https://api.docs.internal")
        );

        MarkdownExportVisitor mdVisitor = new MarkdownExportVisitor();
        for (DocumentElement elem : doc) {
            elem.accept(mdVisitor);
        }
        System.out.println("=== Markdown Output ===\n" + mdVisitor.getExportedOutput());
    }
}
