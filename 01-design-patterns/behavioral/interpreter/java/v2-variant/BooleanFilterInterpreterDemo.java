package interpreter.v2;

import java.util.*;

/**
 * v2-variant: Boolean Filtering Rule AST Interpreter.
 * Evaluates composite boolean criteria against data records (e.g., query filters, rules engines)
 * using terminal field comparisons (Equals, GreaterThan, Contains) and non-terminal logical combinators (And, Or, Not).
 */
public class BooleanFilterInterpreterDemo {

    public interface FilterExpression {
        boolean interpret(Map<String, Object> record);
    }

    public static class EqualsExpression implements FilterExpression {
        private final String field;
        private final Object expected;

        public EqualsExpression(String field, Object expected) {
            this.field = Objects.requireNonNull(field);
            this.expected = expected;
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            if (record == null) return false;
            Object val = record.get(field);
            return Objects.equals(val, expected);
        }
    }

    public static class GreaterThanExpression implements FilterExpression {
        private final String field;
        private final double threshold;

        public GreaterThanExpression(String field, double threshold) {
            this.field = Objects.requireNonNull(field);
            this.threshold = threshold;
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            if (record == null || !record.containsKey(field)) return false;
            Object val = record.get(field);
            if (val instanceof Number) {
                return ((Number) val).doubleValue() > threshold;
            }
            return false;
        }
    }

    public static class ContainsExpression implements FilterExpression {
        private final String field;
        private final String substring;

        public ContainsExpression(String field, String substring) {
            this.field = Objects.requireNonNull(field);
            this.substring = Objects.requireNonNull(substring);
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            if (record == null || !record.containsKey(field)) return false;
            Object val = record.get(field);
            return val != null && val.toString().contains(substring);
        }
    }

    public static class AndExpression implements FilterExpression {
        private final FilterExpression left;
        private final FilterExpression right;

        public AndExpression(FilterExpression left, FilterExpression right) {
            this.left = Objects.requireNonNull(left);
            this.right = Objects.requireNonNull(right);
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            return left.interpret(record) && right.interpret(record);
        }
    }

    public static class OrExpression implements FilterExpression {
        private final FilterExpression left;
        private final FilterExpression right;

        public OrExpression(FilterExpression left, FilterExpression right) {
            this.left = Objects.requireNonNull(left);
            this.right = Objects.requireNonNull(right);
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            return left.interpret(record) || right.interpret(record);
        }
    }

    public static class NotExpression implements FilterExpression {
        private final FilterExpression expression;

        public NotExpression(FilterExpression expression) {
            this.expression = Objects.requireNonNull(expression);
        }

        @Override
        public boolean interpret(Map<String, Object> record) {
            return !expression.interpret(record);
        }
    }

    public static List<Map<String, Object>> filter(List<Map<String, Object>> records, FilterExpression rule) {
        List<Map<String, Object>> matches = new ArrayList<>();
        for (Map<String, Object> r : records) {
            if (rule.interpret(r)) {
                matches.add(r);
            }
        }
        return matches;
    }

    public static void main(String[] args) {
        Map<String, Object> u1 = Map.of("role", "admin", "age", 35, "email", "admin@corp.io");
        Map<String, Object> u2 = Map.of("role", "developer", "age", 25, "email", "dev@external.com");
        Map<String, Object> u3 = Map.of("role", "admin", "age", 22, "email", "intern@corp.io");

        List<Map<String, Object>> users = List.of(u1, u2, u3);

        // Rule: role == 'admin' AND age > 30
        FilterExpression seniorAdmin = new AndExpression(
                new EqualsExpression("role", "admin"),
                new GreaterThanExpression("age", 30.0)
        );

        List<Map<String, Object>> result = filter(users, seniorAdmin);
        System.out.println("Senior admins count: " + result.size());
    }
}
