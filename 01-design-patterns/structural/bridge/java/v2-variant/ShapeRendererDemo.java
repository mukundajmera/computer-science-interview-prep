/**
 * Bridge Pattern - V2: Shapes + Renderers
 *
 * Separates the shape abstraction hierarchy from rendering implementations.
 */

import java.util.ArrayList;
import java.util.List;

interface Renderer {
    String renderCircle(int x, int y, int radius);
    String renderRectangle(int x, int y, int width, int height);
}

class SvgRenderer implements Renderer {
    @Override
    public String renderCircle(int x, int y, int radius) {
        return "<circle cx=\"" + x + "\" cy=\"" + y + "\" r=\"" + radius + "\" />";
    }

    @Override
    public String renderRectangle(int x, int y, int width, int height) {
        return "<rect x=\"" + x + "\" y=\"" + y
            + "\" width=\"" + width + "\" height=\"" + height + "\" />";
    }
}

class RasterRenderer implements Renderer {
    @Override
    public String renderCircle(int x, int y, int radius) {
        return "Raster circle at (" + x + ", " + y + ") with radius " + radius;
    }

    @Override
    public String renderRectangle(int x, int y, int width, int height) {
        return "Raster rectangle at (" + x + ", " + y + ") sized " + width + "x" + height;
    }
}

class RecordingRenderer implements Renderer {
    private final List<String> commands = new ArrayList<>();

    @Override
    public String renderCircle(int x, int y, int radius) {
        String command = "circle:" + x + ":" + y + ":" + radius;
        commands.add(command);
        return command;
    }

    @Override
    public String renderRectangle(int x, int y, int width, int height) {
        String command = "rectangle:" + x + ":" + y + ":" + width + ":" + height;
        commands.add(command);
        return command;
    }

    public List<String> getCommands() {
        return new ArrayList<>(commands);
    }
}

abstract class Shape {
    protected Renderer renderer;

    protected Shape(Renderer renderer) {
        this.renderer = renderer;
    }

    public void setRenderer(Renderer renderer) {
        this.renderer = renderer;
    }

    public abstract String draw();
}

class Circle extends Shape {
    private final int x;
    private final int y;
    private final int radius;

    public Circle(int x, int y, int radius, Renderer renderer) {
        super(renderer);
        this.x = x;
        this.y = y;
        this.radius = radius;
    }

    @Override
    public String draw() {
        return renderer.renderCircle(x, y, radius);
    }
}

class Rectangle extends Shape {
    private final int x;
    private final int y;
    private final int width;
    private final int height;

    public Rectangle(int x, int y, int width, int height, Renderer renderer) {
        super(renderer);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    @Override
    public String draw() {
        return renderer.renderRectangle(x, y, width, height);
    }
}

public class ShapeRendererDemo {
    public static void main(String[] args) {
        Shape shape = new Circle(5, 10, 3, new SvgRenderer());
        System.out.println(shape.draw());
        shape.setRenderer(new RasterRenderer());
        System.out.println(shape.draw());
    }
}
