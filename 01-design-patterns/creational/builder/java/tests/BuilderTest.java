import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import builder.v1.Pizza;
import builder.v1.Computer;
import builder.v1.Pizza;
import builder.v1.Computer;
import builder.v1.Computer;
import builder.v1.Computer;
import builder.v2.DocumentDirectorDemo.*;
import builder.v3.TypeSafeBuilderDemo.*;

public class BuilderTest {

    @Test
    @DisplayName("Pizza.Builder constructs immutable Pizza with specified options")
    void testPizzaBuilderConstructsImmutablePizza() {
        Pizza pizza = new Pizza.Builder("large")
                .crust("thin")
                .sauce("bbq")
                .addTopping("mushrooms")
                .addTopping("onions")
                .extraCheese()
                .glutenFree()
                .build();

        assertEquals("large", pizza.getSize());
        assertEquals("thin", pizza.getCrust());
        assertEquals("bbq", pizza.getSauce());
        assertTrue(pizza.getToppings().contains("mushrooms"));
        assertTrue(pizza.getToppings().contains("onions"));
        assertTrue(pizza.hasExtraCheese());
        assertTrue(pizza.isGlutenFree());
    }

    @Test
    @DisplayName("Pizza.Builder enforces required size parameter")
    void testPizzaBuilderRequiresSize() {
        assertThrows(IllegalStateException.class, () -> new Pizza.Builder(null).build());
        assertThrows(IllegalStateException.class, () -> new Pizza.Builder("").build());
    }

    @Test
    @DisplayName("Computer.Builder enforces minimum RAM requirement")
    void testComputerBuilderEnforcesRamRequirement() {
        Computer computer = new Computer.Builder("Intel i7", 16)
                .storage(512)
                .gpu("RTX 4080")
                .noBluetooth()
                .noWifi()
                .build();

        assertNotNull(computer);
        assertThrows(IllegalStateException.class, () -> new Computer.Builder("Intel i3", 2).build());
    }

    @Test
    @DisplayName("v2 DocumentDirector produces both HTML and Markdown variants")
    void testDocumentDirectorVariants() {
        HtmlDocumentBuilder htmlBuilder = new HtmlDocumentBuilder();
        DocumentDirector director = new DocumentDirector(htmlBuilder);

        List<String> findings = List.of("Security audit passed", "Zero critical vulnerabilities");
        String html = director.constructReport("Security Report", findings, "Approved by Security Lead");
        assertTrue(html.contains("<article>"));
        assertTrue(html.contains("<h1>Security Report</h1>"));
        assertTrue(html.contains("<footer>Approved by Security Lead</footer>"));

        MarkdownDocumentBuilder mdBuilder = new MarkdownDocumentBuilder();
        director.changeBuilder(mdBuilder);
        String md = director.constructSummary("Quick Overview", "Production cluster healthy");
        assertTrue(md.startsWith("# Quick Overview"));
        assertTrue(md.contains("## Executive Summary"));
        assertTrue(md.contains("*Confidential*"));
    }

    @Test
    @DisplayName("v3 TypeSafeBuilder staged query construction and validation")
    void testTypeSafeStagedQueryBuilder() {
        SqlQuery query = SqlQuery.builder()
                .select("id", "name", "email")
                .from("accounts")
                .where("is_active = 1")
                .limit(10)
                .build();

        assertEquals("SELECT id, name, email FROM accounts WHERE is_active = 1 LIMIT 10", query.toSql());
        assertEquals("accounts", query.getTable());
        assertEquals(List.of("id", "name", "email"), query.getColumns());

        assertThrows(IllegalArgumentException.class, () -> SqlQuery.builder().select(""));
        assertThrows(IllegalArgumentException.class, () -> SqlQuery.builder().select("id").from(" "));
        assertThrows(IllegalArgumentException.class, () -> SqlQuery.builder().select("id").from("accounts").limit(0));
    }
}
