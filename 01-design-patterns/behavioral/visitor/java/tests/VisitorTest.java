import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Collections;
import java.util.List;

import visitor.v2.DocumentExportVisitorDemo.*;
import visitor.v3.CodeMetricsVisitorDemo.*;

public class VisitorTest {

    @Test
    @DisplayName("AreaCalculator visits shapes and accumulates total area correctly")
    void testAreaCalculatorVisitsAllShapes() {
        Circle circle = new Circle(5.0);
        Rectangle rectangle = new Rectangle(4.0, 6.0);
        Triangle triangle = new Triangle(3.0, 4.0);

        AreaCalculator calc = new AreaCalculator();
        circle.accept(calc);
        rectangle.accept(calc);
        triangle.accept(calc);

        double expectedArea = (Math.PI * 25.0) + (24.0) + (0.5 * 3.0 * 4.0);
        assertEquals(expectedArea, calc.getTotalArea(), 0.01);
    }

    @Test
    @DisplayName("DrawingVisitor visits all shapes without throwing exceptions")
    void testDrawingVisitorVisitsAllShapes() {
        DrawingVisitor visitor = new DrawingVisitor();
        Circle circle = new Circle(2.5);
        Rectangle rectangle = new Rectangle(5.0, 10.0);
        Triangle triangle = new Triangle(4.0, 5.0);

        assertDoesNotThrow(() -> circle.accept(visitor));
        assertDoesNotThrow(() -> rectangle.accept(visitor));
        assertDoesNotThrow(() -> triangle.accept(visitor));
    }

    @Test
    @DisplayName("Polymorphic shapes accept visitor in a collection")
    void testShapesAcceptVisitorPolymorphically() {
        List<Shape> shapes = List.of(
            new Circle(3.0),
            new Rectangle(2.0, 5.0),
            new Triangle(6.0, 2.0)
        );

        AreaCalculator calc = new AreaCalculator();
        for (Shape shape : shapes) {
            shape.accept(calc);
        }

        double expected = (Math.PI * 9.0) + 10.0 + 6.0;
        assertEquals(expected, calc.getTotalArea(), 0.01);
    }

    @Test
    @DisplayName("v2 DocumentExportVisitor formats elements to Markdown and HTML")
    void testDocumentExportVisitors() {
        List<DocumentElement> doc = List.of(
                new Heading("System Architecture", 2),
                new Paragraph("This is a modular microservice setup."),
                new CodeBlock("npm start", "bash"),
                new Hyperlink("API Docs", "https://api.docs.internal")
        );

        MarkdownExportVisitor mdVisitor = new MarkdownExportVisitor();
        HtmlExportVisitor htmlVisitor = new HtmlExportVisitor();

        for (DocumentElement elem : doc) {
            elem.accept(mdVisitor);
            elem.accept(htmlVisitor);
        }

        String md = mdVisitor.getExportedOutput();
        assertTrue(md.contains("## System Architecture"));
        assertTrue(md.contains("This is a modular microservice setup."));
        assertTrue(md.contains("```bash\nnpm start\n```"));
        assertTrue(md.contains("[API Docs](https://api.docs.internal)"));

        String html = htmlVisitor.getExportedOutput();
        assertTrue(html.contains("<h2>System Architecture</h2>"));
        assertTrue(html.contains("<p>This is a modular microservice setup.</p>"));
        assertTrue(html.contains("<code class=\"language-bash\">npm start</code>"));
        assertTrue(html.contains("<a href=\"https://api.docs.internal\">API Docs</a>"));
    }

    @Test
    @DisplayName("v3 AST Code Metrics and Security Audit visitors traverse syntax tree")
    void testAstCodeMetricsAndSecurityAudit() {
        FunctionDef fn = new FunctionDef("processUserPayload", List.of("payload"), List.of(
                new Assignment("token", "payload.getToken()"),
                new IfStatement("token == null", List.of(new CallExpression("logWarning", List.of("Missing token"))), Collections.emptyList()),
                new LoopStatement("while", List.of(new CallExpression("eval", List.of("payload.getCmd()"))))
        ));

        MetricsVisitor metrics = new MetricsVisitor();
        SecurityAuditVisitor security = new SecurityAuditVisitor();

        fn.accept(metrics);
        fn.accept(security);

        assertEquals(1, metrics.getFunctionCount());
        // Complexity: 1 (func) + 1 (if) + 1 (loop) = 3
        assertEquals(3, metrics.getCyclomaticComplexity());
        assertTrue(metrics.getStatementCount() >= 3);

        assertEquals(1, security.getSecurityAlerts().size());
        assertTrue(security.getSecurityAlerts().get(0).contains("eval"));
    }
}
