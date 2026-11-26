import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import interpreter.v2.BooleanFilterInterpreterDemo;
import interpreter.v2.BooleanFilterInterpreterDemo.*;
import interpreter.v3.ScriptEvaluatorDemo;
import interpreter.v3.ScriptEvaluatorDemo.*;

public class InterpreterTest {

    @Test
    @DisplayName("Individual expression nodes evaluate arithmetic correctly")
    void testIndividualExpressions() {
        Expression num5 = new NumberExpression(5);
        Expression num3 = new NumberExpression(3);

        assertEquals(5, num5.interpret());
        assertEquals(3, num3.interpret());

        Expression add = new AddExpression(num5, num3);
        assertEquals(8, add.interpret());

        Expression sub = new SubtractExpression(num5, num3);
        assertEquals(2, sub.interpret());

        Expression mul = new MultiplyExpression(num5, num3);
        assertEquals(15, mul.interpret());
    }

    @Test
    @DisplayName("ExpressionParser correctly parses and evaluates postfix expressions")
    void testExpressionParserEvaluation() {
        ExpressionParser parser = new ExpressionParser();

        assertEquals(7, parser.parse("3 4 +").interpret());
        assertEquals(5, parser.parse("10 5 -").interpret());
        assertEquals(42, parser.parse("6 7 *").interpret());
        assertEquals(35, parser.parse("3 4 + 5 *").interpret());
        assertEquals(50, parser.parse("10 2 3 + *").interpret());
    }

    @Test
    @DisplayName("ExpressionParser throws IllegalArgumentException on invalid operator")
    void testParserThrowsOnInvalidOperator() {
        ExpressionParser parser = new ExpressionParser();
        assertThrows(IllegalArgumentException.class, () -> parser.parse("3 4 /"));
    }

    @Test
    @DisplayName("v2 Boolean filter interpreter evaluates record criteria")
    void testBooleanFilterInterpreter() {
        Map<String, Object> r1 = Map.of("role", "admin", "age", 35, "email", "alice@corp.com");
        Map<String, Object> r2 = Map.of("role", "developer", "age", 28, "email", "bob@contractor.org");
        Map<String, Object> r3 = Map.of("role", "admin", "age", 22, "email", "carol@corp.com");
        List<Map<String, Object>> records = List.of(r1, r2, r3);

        // Filter: role == 'admin' AND age > 30
        FilterExpression seniorAdmin = new AndExpression(
                new EqualsExpression("role", "admin"),
                new GreaterThanExpression("age", 30.0)
        );

        List<Map<String, Object>> res = BooleanFilterInterpreterDemo.filter(records, seniorAdmin);
        assertEquals(1, res.size());
        assertEquals("alice@corp.com", res.get(0).get("email"));

        // Filter: email contains '@corp.com' AND NOT (role == 'developer')
        FilterExpression corpNonDev = new AndExpression(
                new ContainsExpression("email", "@corp.com"),
                new NotExpression(new EqualsExpression("role", "developer"))
        );
        assertEquals(2, BooleanFilterInterpreterDemo.filter(records, corpNonDev).size());
    }

    @Test
    @DisplayName("v3 Script evaluator evaluates AST formulas with variables and memoization")
    void testScriptEvaluatorAstAndMemoization() {
        ExecutionContext ctx = new ExecutionContext();
        ctx.setVariable("x", 10.0);
        ctx.setVariable("y", 4.0);

        // max(x * 2, y + 20) -> max(20, 24) = 24.0
        ScriptExpression formula = new FunctionCall("max", List.of(
                new BinaryOperation(new VariableReference("x"), "*", new NumberLiteral(2.0)),
                new BinaryOperation(new VariableReference("y"), "+", new NumberLiteral(20.0))
        ));

        assertEquals(24.0, formula.evaluate(ctx), 0.001);

        // Memoized expression
        MemoizedExpression memo = new MemoizedExpression(formula);
        int countBefore = ctx.getEvaluationCount();
        double v1 = memo.evaluate(ctx);
        int countAfterFirst = ctx.getEvaluationCount();
        assertTrue(countAfterFirst > countBefore);

        double v2 = memo.evaluate(ctx);
        assertEquals(24.0, v1, 0.001);
        assertEquals(24.0, v2, 0.001);
        // Second call used memoCache, no additional node evaluations
        assertEquals(countAfterFirst, ctx.getEvaluationCount());

        // Division by zero throws
        ScriptExpression divZero = new BinaryOperation(new NumberLiteral(10.0), "/", new NumberLiteral(0.0));
        assertThrows(ArithmeticException.class, () -> divZero.evaluate(ctx));
    }
}
