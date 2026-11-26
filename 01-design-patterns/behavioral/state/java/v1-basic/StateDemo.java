/**
 * State Pattern - V1 Basic: Vending Machine
 */

// State Interface
interface State {
    void insertMoney(VendingMachine vm);
    void selectProduct(VendingMachine vm);
    void dispense(VendingMachine vm);
}

// Context
class VendingMachine {
    private State idleState;
    private State hasMoneyState;
    private State dispensingState;
    private State currentState;
    private double balance = 0;
    
    public VendingMachine() {
        idleState = new IdleState();
        hasMoneyState = new HasMoneyState();
        dispensingState = new DispensingState();
        currentState = idleState;
    }
    
    public void setState(State state) {
        System.out.println("State: " + state.getClass().getSimpleName());
        this.currentState = state;
    }
    
    public State getIdleState() { return idleState; }
    public State getHasMoneyState() { return hasMoneyState; }
    public State getDispensingState() { return dispensingState; }
    
    public void addBalance(double amount) { balance += amount; }
    public double getBalance() { return balance; }
    public void resetBalance() { balance = 0; }
    
    public void insertMoney(double amount) {
        addBalance(amount);
        currentState.insertMoney(this);
    }
    
    public void selectProduct() {
        currentState.selectProduct(this);
    }
    
    public void dispense() {
        currentState.dispense(this);
    }
}

// Concrete States
class IdleState implements State {
    @Override
    public void insertMoney(VendingMachine vm) {
        System.out.println("Money inserted: $" + vm.getBalance());
        vm.setState(vm.getHasMoneyState());
    }
    
    @Override
    public void selectProduct(VendingMachine vm) {
        System.out.println("Please insert money first");
    }
    
    @Override
    public void dispense(VendingMachine vm) {
        System.out.println("Please insert money and select product");
    }
}

class HasMoneyState implements State {
    @Override
    public void insertMoney(VendingMachine vm) {
        System.out.println("Total balance: $" + vm.getBalance());
    }
    
    @Override
    public void selectProduct(VendingMachine vm) {
        if (vm.getBalance() >= 1.50) {
            System.out.println("Product selected");
            vm.setState(vm.getDispensingState());
            vm.dispense();
        } else {
            System.out.println("Insufficient balance. Need $1.50, have $" + vm.getBalance());
        }
    }
    
    @Override
    public void dispense(VendingMachine vm) {
        System.out.println("Please select a product first");
    }
}

class DispensingState implements State {
    @Override
    public void insertMoney(VendingMachine vm) {
        System.out.println("Please wait, dispensing...");
    }
    
    @Override
    public void selectProduct(VendingMachine vm) {
        System.out.println("Please wait, dispensing...");
    }
    
    @Override
    public void dispense(VendingMachine vm) {
        System.out.println("🥤 Product dispensed!");
        vm.resetBalance();
        vm.setState(vm.getIdleState());
    }
}

public class StateDemo {
    public static void main(String[] args) {
        VendingMachine vm = new VendingMachine();
        
        System.out.println("=== Vending Machine ===\n");
        
        // Try without money
        vm.selectProduct();
        
        // Insert money
        System.out.println();
        vm.insertMoney(1.00);
        vm.selectProduct();  // Not enough
        
        // Add more money
        System.out.println();
        vm.insertMoney(0.50);
        vm.selectProduct();  // Now enough - dispenses
        
        // Back to idle
        System.out.println();
        vm.selectProduct();  // Need money again
    }
}
