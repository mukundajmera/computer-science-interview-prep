package builder.v2;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * v2-variant: Builder Pattern with Director and Reusable Concrete Builders.
 * Demonstrates decoupling complex document assembly logic (Director)
 * from representation generation (HTML vs. Markdown Concrete Builders).
 */
public class DocumentDirectorDemo {

    public interface DocumentBuilder {
        DocumentBuilder reset();
        DocumentBuilder setTitle(String title);
        DocumentBuilder addSection(String heading, String body);
        DocumentBuilder setFooter(String footer);
        String getResult();
    }

    public static class HtmlDocumentBuilder implements DocumentBuilder {
        private String title = "";
        private final List<String[]> sections = new ArrayList<>();
        private String footer = "";

        @Override
        public HtmlDocumentBuilder reset() {
            this.title = "";
            this.sections.clear();
            this.footer = "";
            return this;
        }

        @Override
        public HtmlDocumentBuilder setTitle(String title) {
            this.title = title == null ? "" : title;
            return this;
        }

        @Override
        public HtmlDocumentBuilder addSection(String heading, String body) {
            this.sections.add(new String[]{heading == null ? "" : heading, body == null ? "" : body});
            return this;
        }

        @Override
        public HtmlDocumentBuilder setFooter(String footer) {
            this.footer = footer == null ? "" : footer;
            return this;
        }

        @Override
        public String getResult() {
            StringBuilder sb = new StringBuilder();
            sb.append("<article>\n");
            if (!title.isEmpty()) {
                sb.append("  <h1>").append(title).append("</h1>\n");
            }
            for (String[] sec : sections) {
                sb.append("  <section>\n");
                sb.append("    <h2>").append(sec[0]).append("</h2>\n");
                sb.append("    <p>").append(sec[1]).append("</p>\n");
                sb.append("  </section>\n");
            }
            if (!footer.isEmpty()) {
                sb.append("  <footer>").append(footer).append("</footer>\n");
            }
            sb.append("</article>");
            return sb.toString();
        }
    }

    public static class MarkdownDocumentBuilder implements DocumentBuilder {
        private String title = "";
        private final List<String[]> sections = new ArrayList<>();
        private String footer = "";

        @Override
        public MarkdownDocumentBuilder reset() {
            this.title = "";
            this.sections.clear();
            this.footer = "";
            return this;
        }

        @Override
        public MarkdownDocumentBuilder setTitle(String title) {
            this.title = title == null ? "" : title;
            return this;
        }

        @Override
        public MarkdownDocumentBuilder addSection(String heading, String body) {
            this.sections.add(new String[]{heading == null ? "" : heading, body == null ? "" : body});
            return this;
        }

        @Override
        public MarkdownDocumentBuilder setFooter(String footer) {
            this.footer = footer == null ? "" : footer;
            return this;
        }

        @Override
        public String getResult() {
            StringBuilder sb = new StringBuilder();
            if (!title.isEmpty()) {
                sb.append("# ").append(title).append("\n\n");
            }
            for (String[] sec : sections) {
                sb.append("## ").append(sec[0]).append("\n");
                sb.append(sec[1]).append("\n\n");
            }
            if (!footer.isEmpty()) {
                sb.append("---\n*").append(footer).append("*\n");
            }
            return sb.toString().trim();
        }
    }

    public static class DocumentDirector {
        private DocumentBuilder builder;

        public DocumentDirector(DocumentBuilder builder) {
            if (builder == null) {
                throw new IllegalArgumentException("Builder cannot be null");
            }
            this.builder = builder;
        }

        public void changeBuilder(DocumentBuilder builder) {
            if (builder == null) {
                throw new IllegalArgumentException("Builder cannot be null");
            }
            this.builder = builder;
        }

        public String constructReport(String title, List<String> findings, String signOff) {
            builder.reset();
            builder.setTitle(title);
            for (int i = 0; i < findings.size(); i++) {
                builder.addSection("Finding " + (i + 1), findings.get(i));
            }
            builder.setFooter(signOff);
            return builder.getResult();
        }

        public String constructSummary(String title, String summaryText) {
            builder.reset();
            builder.setTitle(title);
            builder.addSection("Executive Summary", summaryText);
            builder.setFooter("Confidential");
            return builder.getResult();
        }
    }

    public static void main(String[] args) {
        HtmlDocumentBuilder htmlBuilder = new HtmlDocumentBuilder();
        DocumentDirector director = new DocumentDirector(htmlBuilder);

        List<String> findings = List.of("Latencies decreased by 40%", "Cache hit ratio reached 94%");
        String htmlOutput = director.constructReport("Q3 System Audit", findings, "Approved by SRE Lead");
        System.out.println("HTML Output:\n" + htmlOutput);

        MarkdownDocumentBuilder mdBuilder = new MarkdownDocumentBuilder();
        director.changeBuilder(mdBuilder);
        String mdOutput = director.constructReport("Q3 System Audit", findings, "Approved by SRE Lead");
        System.out.println("\nMarkdown Output:\n" + mdOutput);
    }
}
