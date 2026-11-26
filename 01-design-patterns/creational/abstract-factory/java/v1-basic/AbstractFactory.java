/**
 * Abstract Factory Pattern - V1 Basic
 * 
 * Creates families of related objects without specifying concrete classes.
 * Example: Cross-platform UI components.
 */

// Abstract Products
interface Button {
    void render();

    void onClick();
}

interface Checkbox {
    void render();

    boolean isChecked();

    void toggle();
}

interface TextField {
    void render();

    String getValue();

    void setValue(String value);
}

// Windows Products (Family 1)
class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("[Windows Button] Rendering with Win32 API");
    }

    @Override
    public void onClick() {
        System.out.println("[Windows Button] Click handled by Win32");
    }
}

class WindowsCheckbox implements Checkbox {
    private boolean checked = false;

    @Override
    public void render() {
        String state = checked ? "[x]" : "[ ]";
        System.out.println("[Windows Checkbox] " + state + " (Win32 style)");
    }

    @Override
    public boolean isChecked() {
        return checked;
    }

    @Override
    public void toggle() {
        checked = !checked;
    }
}

class WindowsTextField implements TextField {
    private String value = "";

    @Override
    public void render() {
        System.out.println("[Windows TextField] +-------------+");
        System.out.println("                    | " + value + " |");
        System.out.println("                    +-------------+");
    }

    @Override
    public String getValue() {
        return value;
    }

    @Override
    public void setValue(String value) {
        this.value = value;
    }
}

// Mac Products (Family 2)
class MacButton implements Button {
    @Override
    public void render() {
        System.out.println("[Mac Button] Rendering with Cocoa framework");
    }

    @Override
    public void onClick() {
        System.out.println("[Mac Button] Click handled by Cocoa");
    }
}

class MacCheckbox implements Checkbox {
    private boolean checked = false;

    @Override
    public void render() {
        String state = checked ? "[v]" : "[ ]";
        System.out.println("[Mac Checkbox] " + state + " (Aqua style)");
    }

    @Override
    public boolean isChecked() {
        return checked;
    }

    @Override
    public void toggle() {
        checked = !checked;
    }
}

class MacTextField implements TextField {
    private String value = "";

    @Override
    public void render() {
        System.out.println("[Mac TextField] +-------------+");
        System.out.println("               | " + value + " |");
        System.out.println("               +-------------+");
    }

    @Override
    public String getValue() {
        return value;
    }

    @Override
    public void setValue(String value) {
        this.value = value;
    }
}

// Abstract Factory
interface GUIFactory {
    Button createButton();

    Checkbox createCheckbox();

    TextField createTextField();
}

// Concrete Factories
class WindowsFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }

    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }

    @Override
    public TextField createTextField() {
        return new WindowsTextField();
    }
}

class MacFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }

    @Override
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }

    @Override
    public TextField createTextField() {
        return new MacTextField();
    }
}

// Client class - works with any factory
class Application {
    private Button button;
    private Checkbox checkbox;
    private TextField textField;

    public Application(GUIFactory factory) {
        // Create consistent product family
        this.button = factory.createButton();
        this.checkbox = factory.createCheckbox();
        this.textField = factory.createTextField();
    }

    public void renderUI() {
        System.out.println("\n--- Rendering Application UI ---");
        button.render();
        checkbox.render();
        textField.render();
    }

    public void simulateInteraction() {
        System.out.println("\n--- Simulating User Interaction ---");
        button.onClick();
        checkbox.toggle();
        checkbox.render();
        textField.setValue("Hello!");
        textField.render();
    }
}

// Factory selector
class GUIFactoryProvider {
    public static GUIFactory getFactory(String os) {
        switch (os.toLowerCase()) {
            case "windows":
            case "win":
                return new WindowsFactory();
            case "mac":
            case "macos":
            case "darwin":
                return new MacFactory();
            default:
                throw new IllegalArgumentException("Unsupported OS: " + os);
        }
    }

    public static GUIFactory getSystemFactory() {
        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win")) {
            return new WindowsFactory();
        } else if (os.contains("mac")) {
            return new MacFactory();
        } else {
            // Default to Windows for demonstration
            return new WindowsFactory();
        }
    }
}

// Demo
class AbstractFactoryDemo {
    public static void main(String[] args) {
        System.out.println("=== Abstract Factory Pattern Demo ===");

        // Windows application
        System.out.println("\n========== WINDOWS APPLICATION ==========");
        GUIFactory windowsFactory = GUIFactoryProvider.getFactory("windows");
        Application windowsApp = new Application(windowsFactory);
        windowsApp.renderUI();
        windowsApp.simulateInteraction();

        // Mac application
        System.out.println("\n========== MAC APPLICATION ==========");
        GUIFactory macFactory = GUIFactoryProvider.getFactory("mac");
        Application macApp = new Application(macFactory);
        macApp.renderUI();
        macApp.simulateInteraction();

        // System-specific (auto-detect)
        System.out.println("\n========== SYSTEM APPLICATION ==========");
        GUIFactory systemFactory = GUIFactoryProvider.getSystemFactory();
        Application systemApp = new Application(systemFactory);
        systemApp.renderUI();
    }
}
