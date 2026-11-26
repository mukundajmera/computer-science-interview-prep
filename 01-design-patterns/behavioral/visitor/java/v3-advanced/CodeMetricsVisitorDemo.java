package visitor.v3;

import java.util.*;

/**
 * v3-advanced: AST Static Analysis and Code Metrics Visitor.
 * Traverses an Abstract Syntax Tree (FunctionDef, IfStatement, LoopStatement, Assignment, CallExpression)
 * to compute cyclomatic complexity, statement metrics, and security audit violations.
 */
public class CodeMetricsVisitorDemo {

    public interface AstVisitor {
        void visit(FunctionDef node);
        void visit(IfStatement node);
        void visit(LoopStatement node);
        void visit(Assignment node);
        void visit(CallExpression node);
    }

    public interface AstNode {
        void accept(AstVisitor visitor);
    }

    public static class FunctionDef implements AstNode {
        private final String name;
        private final List<String> parameters;
        private final List<AstNode> body;

        public FunctionDef(String name, List<String> parameters, List<AstNode> body) {
            this.name = Objects.requireNonNull(name);
            this.parameters = parameters != null ? new ArrayList<>(parameters) : Collections.emptyList();
            this.body = body != null ? new ArrayList<>(body) : Collections.emptyList();
        }

        public String getName() {
            return name;
        }

        public List<String> getParameters() {
            return Collections.unmodifiableList(parameters);
        }

        public List<AstNode> getBody() {
            return Collections.unmodifiableList(body);
        }

        @Override
        public void accept(AstVisitor visitor) {
            visitor.visit(this);
            for (AstNode stmt : body) {
                stmt.accept(visitor);
            }
        }
    }

    public static class IfStatement implements AstNode {
        private final String condition;
        private final List<AstNode> thenBranch;
        private final List<AstNode> elseBranch;

        public IfStatement(String condition, List<AstNode> thenBranch, List<AstNode> elseBranch) {
            this.condition = Objects.requireNonNull(condition);
            this.thenBranch = thenBranch != null ? new ArrayList<>(thenBranch) : Collections.emptyList();
            this.elseBranch = elseBranch != null ? new ArrayList<>(elseBranch) : Collections.emptyList();
        }

        public String getCondition() {
            return condition;
        }

        public List<AstNode> getThenBranch() {
            return Collections.unmodifiableList(thenBranch);
        }

        public List<AstNode> getElseBranch() {
            return Collections.unmodifiableList(elseBranch);
        }

        @Override
        public void accept(AstVisitor visitor) {
            visitor.visit(this);
            for (AstNode node : thenBranch) {
                node.accept(visitor);
            }
            for (AstNode node : elseBranch) {
                node.accept(visitor);
            }
        }
    }

    public static class LoopStatement implements AstNode {
        private final String loopType;
        private final List<AstNode> body;

        public LoopStatement(String loopType, List<AstNode> body) {
            this.loopType = Objects.requireNonNull(loopType);
            this.body = body != null ? new ArrayList<>(body) : Collections.emptyList();
        }

        public String getLoopType() {
            return loopType;
        }

        public List<AstNode> getBody() {
            return Collections.unmodifiableList(body);
        }

        @Override
        public void accept(AstVisitor visitor) {
            visitor.visit(this);
            for (AstNode node : body) {
                node.accept(visitor);
            }
        }
    }

    public static class Assignment implements AstNode {
        private final String variable;
        private final String expression;

        public Assignment(String variable, String expression) {
            this.variable = Objects.requireNonNull(variable);
            this.expression = Objects.requireNonNull(expression);
        }

        public String getVariable() {
            return variable;
        }

        public String getExpression() {
            return expression;
        }

        @Override
        public void accept(AstVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class CallExpression implements AstNode {
        private final String callee;
        private final List<String> arguments;

        public CallExpression(String callee, List<String> arguments) {
            this.callee = Objects.requireNonNull(callee);
            this.arguments = arguments != null ? new ArrayList<>(arguments) : Collections.emptyList();
        }

        public String getCallee() {
            return callee;
        }

        public List<String> getArguments() {
            return Collections.unmodifiableList(arguments);
        }

        @Override
        public void accept(AstVisitor visitor) {
            visitor.visit(this);
        }
    }

    public static class MetricsVisitor implements AstVisitor {
        private int functionCount = 0;
        private int statementCount = 0;
        private int cyclomaticComplexity = 0;

        @Override
        public void visit(FunctionDef node) {
            functionCount++;
            cyclomaticComplexity++; // base 1 per function
        }

        @Override
        public void visit(IfStatement node) {
            statementCount++;
            cyclomaticComplexity++; // branch point
        }

        @Override
        public void visit(LoopStatement node) {
            statementCount++;
            cyclomaticComplexity++; // loop branch point
        }

        @Override
        public void visit(Assignment node) {
            statementCount++;
        }

        @Override
        public void visit(CallExpression node) {
            statementCount++;
        }

        public int getFunctionCount() {
            return functionCount;
        }

        public int getStatementCount() {
            return statementCount;
        }

        public int getCyclomaticComplexity() {
            return cyclomaticComplexity;
        }
    }

    public static class SecurityAuditVisitor implements AstVisitor {
        private static final Set<String> DANGEROUS_CALLS = Set.of("eval", "exec", "system", "popen");
        private final List<String> securityAlerts = new ArrayList<>();

        @Override
        public void visit(FunctionDef node) {}

        @Override
        public void visit(IfStatement node) {}

        @Override
        public void visit(LoopStatement node) {}

        @Override
        public void visit(Assignment node) {}

        @Override
        public void visit(CallExpression node) {
            if (DANGEROUS_CALLS.contains(node.getCallee())) {
                securityAlerts.add("CRITICAL: Insecure call to '" + node.getCallee() + "' detected with args: " + node.getArguments());
            }
        }

        public List<String> getSecurityAlerts() {
            return Collections.unmodifiableList(securityAlerts);
        }
    }

    public static void main(String[] args) {
        FunctionDef fn = new FunctionDef("processUserPayload", List.of("payload"), List.of(
                new Assignment("token", "payload.getToken()"),
                new IfStatement("token == null", List.of(new CallExpression("logWarning", List.of("Missing token"))), Collections.emptyList()),
                new LoopStatement("while", List.of(new CallExpression("eval", List.of("payload.getCmd()"))))
        ));

        MetricsVisitor metrics = new MetricsVisitor();
        SecurityAuditVisitor security = new SecurityAuditVisitor();

        fn.accept(metrics);
        fn.accept(security);

        System.out.println("Functions: " + metrics.getFunctionCount());
        System.out.println("Complexity: " + metrics.getCyclomaticComplexity());
        System.out.println("Alerts: " + security.getSecurityAlerts());
    }
}
