/**
 * Interpreter Pattern - Math Expression Evaluator
 */

import java.util.*;

// Abstract Expression
interface Expression {
    int interpret();
}

// Terminal Expression
class NumberExpression implements Expression {
    private int number;
    
    public NumberExpression(int number) {
        this.number = number;
    }
    
    @Override
    public int interpret() {
        return number;
    }
}

// Non-terminal Expressions
class AddExpression implements Expression {
    private Expression left, right;
    
    public AddExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }
    
    @Override
    public int interpret() {
        return left.interpret() + right.interpret();
    }
}

class SubtractExpression implements Expression {
    private Expression left, right;
    
    public SubtractExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }
    
    @Override
    public int interpret() {
        return left.interpret() - right.interpret();
    }
}

class MultiplyExpression implements Expression {
    private Expression left, right;
    
    public MultiplyExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }
    
    @Override
    public int interpret() {
        return left.interpret() * right.interpret();
    }
}

// Parser (Client)
class ExpressionParser {
    public Expression parse(String expression) {
        Stack<Expression> stack = new Stack<>();
        String[] tokens = expression.split(" ");
        
        for (String token : tokens) {
            if (isOperator(token)) {
                Expression right = stack.pop();
                Expression left = stack.pop();
                stack.push(createOperation(token, left, right));
            } else {
                stack.push(new NumberExpression(Integer.parseInt(token)));
            }
        }
        return stack.pop();
    }
    
    private boolean isOperator(String token) {
        return token.equals("+") || token.equals("-") || token.equals("*");
    }
    
    private Expression createOperation(String op, Expression left, Expression right) {
        switch (op) {
            case "+": return new AddExpression(left, right);
            case "-": return new SubtractExpression(left, right);
            case "*": return new MultiplyExpression(left, right);
            default: throw new IllegalArgumentException("Unknown operator: " + op);
        }
    }
}

public class InterpreterDemo {
    public static void main(String[] args) {
        ExpressionParser parser = new ExpressionParser();
        
        // Postfix notation: "3 4 +" means 3 + 4
        String[] expressions = {
            "3 4 +",           // 3 + 4 = 7
            "10 5 -",          // 10 - 5 = 5
            "6 7 *",           // 6 * 7 = 42
            "3 4 + 5 *",       // (3 + 4) * 5 = 35
            "10 2 3 + *"       // 10 * (2 + 3) = 50
        };
        
        System.out.println("=== Expression Interpreter ===");
        for (String expr : expressions) {
            Expression parsed = parser.parse(expr);
            System.out.printf("'%s' = %d%n", expr, parsed.interpret());
        }
    }
}
