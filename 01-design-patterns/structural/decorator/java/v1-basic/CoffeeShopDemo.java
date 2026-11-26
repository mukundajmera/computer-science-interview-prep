/**
 * Decorator Pattern - V1 Basic: Coffee Shop
 * 
 * Classic example demonstrating how to add condiments to beverages
 * without creating a class for each combination.
 */

// Component Interface
abstract class Beverage {
    protected String description = "Unknown Beverage";
    
    public String getDescription() {
        return description;
    }
    
    public abstract double cost();
}

// Concrete Components
class Espresso extends Beverage {
    public Espresso() {
        description = "Espresso";
    }
    
    @Override
    public double cost() {
        return 1.99;
    }
}

class HouseBlend extends Beverage {
    public HouseBlend() {
        description = "House Blend Coffee";
    }
    
    @Override
    public double cost() {
        return 0.89;
    }
}

class DarkRoast extends Beverage {
    public DarkRoast() {
        description = "Dark Roast";
    }
    
    @Override
    public double cost() {
        return 1.49;
    }
}

// Abstract Decorator - extends Component
abstract class CondimentDecorator extends Beverage {
    protected Beverage beverage;
    
    public CondimentDecorator(Beverage beverage) {
        this.beverage = beverage;
    }
    
    @Override
    public abstract String getDescription();
}

// Concrete Decorators
class Milk extends CondimentDecorator {
    public Milk(Beverage beverage) {
        super(beverage);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Milk";
    }
    
    @Override
    public double cost() {
        return beverage.cost() + 0.30;
    }
}

class Mocha extends CondimentDecorator {
    public Mocha(Beverage beverage) {
        super(beverage);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Mocha";
    }
    
    @Override
    public double cost() {
        return beverage.cost() + 0.50;
    }
}

class Whip extends CondimentDecorator {
    public Whip(Beverage beverage) {
        super(beverage);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Whip";
    }
    
    @Override
    public double cost() {
        return beverage.cost() + 0.40;
    }
}

class Soy extends CondimentDecorator {
    public Soy(Beverage beverage) {
        super(beverage);
    }
    
    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Soy";
    }
    
    @Override
    public double cost() {
        return beverage.cost() + 0.45;
    }
}

// Demo
public class CoffeeShopDemo {
    public static void main(String[] args) {
        // Order 1: Simple Espresso
        Beverage beverage1 = new Espresso();
        System.out.println(beverage1.getDescription() + " $" + beverage1.cost());
        
        // Order 2: Dark Roast with double Mocha and Whip
        Beverage beverage2 = new DarkRoast();
        beverage2 = new Mocha(beverage2);
        beverage2 = new Mocha(beverage2);  // Double mocha
        beverage2 = new Whip(beverage2);
        System.out.println(beverage2.getDescription() + " $" + beverage2.cost());
        
        // Order 3: House Blend with Soy, Mocha, and Whip
        Beverage beverage3 = new HouseBlend();
        beverage3 = new Soy(beverage3);
        beverage3 = new Mocha(beverage3);
        beverage3 = new Whip(beverage3);
        System.out.println(beverage3.getDescription() + " $" + beverage3.cost());
        
        // Order 4: Espresso with everything
        Beverage beverage4 = new Espresso();
        beverage4 = new Milk(beverage4);
        beverage4 = new Mocha(beverage4);
        beverage4 = new Soy(beverage4);
        beverage4 = new Whip(beverage4);
        System.out.println(beverage4.getDescription() + " $" + beverage4.cost());
    }
}
