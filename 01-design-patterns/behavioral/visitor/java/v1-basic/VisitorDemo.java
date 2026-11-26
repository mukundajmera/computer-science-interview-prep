/**
 * Visitor Pattern - Shape Calculator
 */

import java.util.*;

// Visitor Interface
interface ShapeVisitor {
    void visit(Circle circle);
    void visit(Rectangle rectangle);
    void visit(Triangle triangle);
}

// Element Interface
interface Shape {
    void accept(ShapeVisitor visitor);
}

// Concrete Elements
class Circle implements Shape {
    public double radius;
    
    public Circle(double radius) { this.radius = radius; }
    
    @Override
    public void accept(ShapeVisitor visitor) {
        visitor.visit(this);
    }
}

class Rectangle implements Shape {
    public double width, height;
    
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public void accept(ShapeVisitor visitor) {
        visitor.visit(this);
    }
}

class Triangle implements Shape {
    public double base, height;
    
    public Triangle(double base, double height) {
        this.base = base;
        this.height = height;
    }
    
    @Override
    public void accept(ShapeVisitor visitor) {
        visitor.visit(this);
    }
}

// Concrete Visitors
class AreaCalculator implements ShapeVisitor {
    private double totalArea = 0;
    
    @Override
    public void visit(Circle c) {
        double area = Math.PI * c.radius * c.radius;
        System.out.printf("Circle area: %.2f%n", area);
        totalArea += area;
    }
    
    @Override
    public void visit(Rectangle r) {
        double area = r.width * r.height;
        System.out.printf("Rectangle area: %.2f%n", area);
        totalArea += area;
    }
    
    @Override
    public void visit(Triangle t) {
        double area = 0.5 * t.base * t.height;
        System.out.printf("Triangle area: %.2f%n", area);
        totalArea += area;
    }
    
    public double getTotalArea() { return totalArea; }
}

class DrawingVisitor implements ShapeVisitor {
    @Override
    public void visit(Circle c) {
        System.out.println("Drawing ○ Circle with radius " + c.radius);
    }
    
    @Override
    public void visit(Rectangle r) {
        System.out.println("Drawing □ Rectangle " + r.width + "x" + r.height);
    }
    
    @Override
    public void visit(Triangle t) {
        System.out.println("Drawing △ Triangle base=" + t.base);
    }
}

public class VisitorDemo {
    public static void main(String[] args) {
        List<Shape> shapes = Arrays.asList(
            new Circle(5),
            new Rectangle(4, 6),
            new Triangle(3, 4)
        );
        
        System.out.println("=== Area Calculation ===");
        AreaCalculator areaCalc = new AreaCalculator();
        for (Shape shape : shapes) {
            shape.accept(areaCalc);
        }
        System.out.printf("Total area: %.2f%n", areaCalc.getTotalArea());
        
        System.out.println("\n=== Drawing ===");
        DrawingVisitor drawer = new DrawingVisitor();
        for (Shape shape : shapes) {
            shape.accept(drawer);
        }
    }
}
