/**
 * Composite Pattern - V3 Advanced: Menu Hierarchy.
 *
 * Menu sections can contain items or nested sections while clients keep one
 * uniform API for counting, filtering, pricing, and rendering.
 */

import java.util.ArrayList;
import java.util.List;

interface MenuComponent {
    int itemCount();
    double totalPrice();
    List<MenuItem> availableItems();
    String render(String indent);
}

class MenuItem implements MenuComponent {
    private final String name;
    private final double price;
    private final boolean vegetarian;
    private final boolean available;

    public MenuItem(String name, double price, boolean vegetarian) {
        this(name, price, vegetarian, true);
    }

    public MenuItem(String name, double price, boolean vegetarian, boolean available) {
        this.name = name;
        this.price = price;
        this.vegetarian = vegetarian;
        this.available = available;
    }

    public String getName() { return name; }

    @Override
    public int itemCount() {
        return 1;
    }

    @Override
    public double totalPrice() {
        return price;
    }

    @Override
    public List<MenuItem> availableItems() {
        List<MenuItem> items = new ArrayList<>();
        if (available) {
            items.add(this);
        }
        return items;
    }

    @Override
    public String render(String indent) {
        String marker = vegetarian ? "vegetarian" : "regular";
        String status = available ? "available" : "sold out";
        return indent + name + " - $" + String.format("%.2f", price)
            + " (" + marker + ", " + status + ")";
    }
}

class Menu implements MenuComponent {
    private final String name;
    private final List<MenuComponent> children;

    public Menu(String name) {
        this.name = name;
        this.children = new ArrayList<>();
    }

    public void add(MenuComponent component) {
        children.add(component);
    }

    public void remove(MenuComponent component) {
        children.remove(component);
    }

    @Override
    public int itemCount() {
        return children.stream().mapToInt(MenuComponent::itemCount).sum();
    }

    @Override
    public double totalPrice() {
        return children.stream().mapToDouble(MenuComponent::totalPrice).sum();
    }

    @Override
    public List<MenuItem> availableItems() {
        List<MenuItem> items = new ArrayList<>();
        for (MenuComponent child : children) {
            items.addAll(child.availableItems());
        }
        return items;
    }

    @Override
    public String render(String indent) {
        StringBuilder builder = new StringBuilder();
        builder.append(indent).append(name).append(" (").append(itemCount()).append(" items)");
        for (MenuComponent child : children) {
            builder.append(System.lineSeparator()).append(child.render(indent + "  "));
        }
        return builder.toString();
    }
}

public class MenuDemo {
    public static void main(String[] args) {
        Menu dinner = new Menu("Dinner");
        Menu mains = new Menu("Mains");
        mains.add(new MenuItem("Paneer Bowl", 12.50, true));
        mains.add(new MenuItem("Chicken Bowl", 13.75, false));
        dinner.add(mains);

        System.out.println(dinner.render(""));
        System.out.println("Available items: " + dinner.availableItems().size());
    }
}
