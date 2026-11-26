/**
 * Composite Pattern - V2 Variant: Graphics Groups.
 *
 * Shapes and groups share one Graphic interface so clients can move,
 * measure, and render individual shapes or nested groups uniformly.
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

interface Graphic {
    void move(int dx, int dy);
    double area();
    String render(String indent);
}

class Circle implements Graphic {
    private final String name;
    private int x;
    private int y;
    private final int radius;

    public Circle(String name, int x, int y, int radius) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.radius = radius;
    }

    public int getX() { return x; }
    public int getY() { return y; }

    @Override
    public void move(int dx, int dy) {
        x += dx;
        y += dy;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }

    @Override
    public String render(String indent) {
        return indent + "Circle(" + name + ") at (" + x + ", " + y + ")";
    }
}

class Rectangle implements Graphic {
    private final String name;
    private int x;
    private int y;
    private final int width;
    private final int height;

    public Rectangle(String name, int x, int y, int width, int height) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    public int getX() { return x; }
    public int getY() { return y; }

    @Override
    public void move(int dx, int dy) {
        x += dx;
        y += dy;
    }

    @Override
    public double area() {
        return width * height;
    }

    @Override
    public String render(String indent) {
        return indent + "Rectangle(" + name + ") at (" + x + ", " + y + ")";
    }
}

class GraphicGroup implements Graphic {
    private final String name;
    private final List<Graphic> children;

    public GraphicGroup(String name) {
        this.name = name;
        this.children = new ArrayList<>();
    }

    public void add(Graphic graphic) {
        children.add(graphic);
    }

    public void remove(Graphic graphic) {
        children.remove(graphic);
    }

    public List<Graphic> getChildren() {
        return Collections.unmodifiableList(children);
    }

    @Override
    public void move(int dx, int dy) {
        for (Graphic child : children) {
            child.move(dx, dy);
        }
    }

    @Override
    public double area() {
        return children.stream().mapToDouble(Graphic::area).sum();
    }

    @Override
    public String render(String indent) {
        StringBuilder builder = new StringBuilder();
        builder.append(indent).append("Group(").append(name).append(") area=");
        builder.append(String.format("%.2f", area()));
        for (Graphic child : children) {
            builder.append(System.lineSeparator()).append(child.render(indent + "  "));
        }
        return builder.toString();
    }
}

public class GraphicsDemo {
    public static void main(String[] args) {
        GraphicGroup icon = new GraphicGroup("profile-icon");
        icon.add(new Circle("avatar", 0, 0, 4));
        icon.add(new Rectangle("status-badge", 6, 6, 3, 2));

        System.out.println(icon.render(""));
        icon.move(10, 5);
        System.out.println();
        System.out.println(icon.render(""));
    }
}
