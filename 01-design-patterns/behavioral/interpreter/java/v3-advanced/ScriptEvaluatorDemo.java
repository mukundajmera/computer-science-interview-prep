package interpreter.v3;

import java.util.*;
import java.util.function.Function;

/**
 * v3-advanced: Extensible Math & DSL Script AST Interpreter.
 * Evaluates mathematical and formula expressions with dynamic variable scopes,
 * pluggable functions (min, max, abs), operator precedence/binary operations,
 * and context memoization for repeated evaluations.
 */
public class ScriptEvaluatorDemo {

    public static class ExecutionContext {
        private final Map<String, Double> variables = new HashMap<>();
        private final Map<String, Function<List<Double>, Double>> functions = new HashMap<>();
        private final Map<String, Double> memoCache = new HashMap<>();
        private int evaluationCount = 0;

        public ExecutionContext() {
            registerDefaultFunctions();
        }

        private void registerDefaultFunctions() {
            functions.put("abs", args -> {
                if (args.isEmpty()) throw new IllegalArgumentException("abs requires 1 argument");
                return Math.abs(args.get(0));
            });
            functions.put("max", args -> {
                if (args.isEmpty()) throw new IllegalArgumentException("max requires at least 1 argument");
                return args.stream().max(Double::compare).orElse(0.0);
            });
            functions.put("min", args -> {
                if (args.isEmpty()) throw new IllegalArgumentException("min requires at least 1 argument");
                return args.stream().min(Double::compare).orElse(0.0);
            });
        }

        public void setVariable(String name, double value) {
            variables.put(name, value);
            memoCache.clear(); // invalidate cache on variable change
        }

        public double getVariable(String name) {
            if (!variables.containsKey(name)) {
                throw new IllegalArgumentException("Undefined variable: " + name);
            }
            return variables.get(name);
        }

        public void registerFunction(String name, Function<List<Double>, Double> func) {
            functions.put(name, func);
        }

        public Function<List<Double>, Double> getFunction(String name) {
            if (!functions.containsKey(name)) {
                throw new IllegalArgumentException("Unknown function: " + name);
            }
            return functions.get(name);
        }

        public void incrementEvalCount() {
            evaluationCount++;
        }

        public int getEvaluationCount() {
            return evaluationCount;
        }

        public Map<String, Double> getMemoCache() {
            return memoCache;
        }
    }

    public interface ScriptExpression {
        double evaluate(ExecutionContext context);
        String toFormulaString();
    }

    public static class NumberLiteral implements ScriptExpression {
        private final double value;

        public NumberLiteral(double value) {
            this.value = value;
        }

        @Override
        public double evaluate(ExecutionContext context) {
            context.incrementEvalCount();
            return value;
        }

        @Override
        public String toFormulaString() {
            return String.valueOf(value);
        }
    }

    public static class VariableReference implements ScriptExpression {
        private final String name;

        public VariableReference(String name) {
            this.name = Objects.requireNonNull(name);
        }

        @Override
        public double evaluate(ExecutionContext context) {
            context.incrementEvalCount();
            return context.getVariable(name);
        }

        @Override
        public String toFormulaString() {
            return name;
        }
    }

    public static class BinaryOperation implements ScriptExpression {
        private final ScriptExpression left;
        private final String operator;
        private final ScriptExpression right;

        public BinaryOperation(ScriptExpression left, String operator, ScriptExpression right) {
            this.left = Objects.requireNonNull(left);
            this.operator = Objects.requireNonNull(operator);
            this.right = Objects.requireNonNull(right);
        }

        @Override
        public double evaluate(ExecutionContext context) {
            context.incrementEvalCount();
            double l = left.evaluate(context);
            double r = right.evaluate(context);

            switch (operator) {
                case "+": return l + r;
                case "-": return l - r;
                case "*": return l * r;
                case "/":
                    if (r == 0.0) throw new ArithmeticException("Division by zero");
                    return l / r;
                case "^": return Math.pow(l, r);
                default: throw new UnsupportedOperationException("Unknown operator: " + operator);
            }
        }

        @Override
        public String toFormulaString() {
            return "(" + left.toFormulaString() + " " + operator + " " + right.toFormulaString() + ")";
        }
    }

    public static class FunctionCall implements ScriptExpression {
        private final String functionName;
        private final List<ScriptExpression> arguments;

        public FunctionCall(String functionName, List<ScriptExpression> arguments) {
            this.functionName = Objects.requireNonNull(functionName);
            this.arguments = arguments != null ? new ArrayList<>(arguments) : Collections.emptyList();
        }

        @Override
        public double evaluate(ExecutionContext context) {
            context.incrementEvalCount();
            Function<List<Double>, Double> func = context.getFunction(functionName);
            List<Double> evaluatedArgs = new ArrayList<>();
            for (ScriptExpression arg : arguments) {
                evaluatedArgs.add(arg.evaluate(context));
            }
            return func.apply(evaluatedArgs);
        }

        @Override
        public String toFormulaString() {
            StringBuilder sb = new StringBuilder(functionName).append("(");
            for (int i = 0; i < arguments.size(); i++) {
                sb.append(arguments.get(i).toFormulaString());
                if (i < arguments.size() - 1) sb.append(", ");
            }
            return sb.append(")").toString();
        }
    }

    public static class MemoizedExpression implements ScriptExpression {
        private final ScriptExpression inner;
        private final String cacheKey;

        public MemoizedExpression(ScriptExpression inner) {
            this.inner = Objects.requireNonNull(inner);
            this.cacheKey = inner.toFormulaString();
        }

        @Override
        public double evaluate(ExecutionContext context) {
            if (context.getMemoCache().containsKey(cacheKey)) {
                return context.getMemoCache().get(cacheKey);
            }
            double val = inner.evaluate(context);
            context.getMemoCache().put(cacheKey, val);
            return val;
        }

        @Override
        public String toFormulaString() {
            return inner.toFormulaString();
        }
    }

    public static void main(String[] args) {
        ExecutionContext ctx = new ExecutionContext();
        ctx.setVariable("x", 10.0);
        ctx.setVariable("y", 5.0);

        // Formula: max(x * 2, y + 20)
        ScriptExpression expr = new FunctionCall("max", List.of(
                new BinaryOperation(new VariableReference("x"), "*", new NumberLiteral(2.0)),
                new BinaryOperation(new VariableReference("y"), "+", new NumberLiteral(20.0))
        ));

        System.out.println("Formula: " + expr.toFormulaString());
        System.out.println("Result: " + expr.evaluate(ctx));
    }
}
