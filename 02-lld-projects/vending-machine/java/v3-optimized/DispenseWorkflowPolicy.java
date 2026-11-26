/**
 * Interview-focused workflow contracts for vending-machine dispense flow.
 */
public class DispenseWorkflowPolicy {
    private final MachineStateTransition stateTransition;
    private final PaymentCommand paymentCommand;
    private final InventoryReservationPolicy inventoryReservationPolicy;

    public DispenseWorkflowPolicy(
            MachineStateTransition stateTransition,
            PaymentCommand paymentCommand,
            InventoryReservationPolicy inventoryReservationPolicy) {
        this.stateTransition = stateTransition;
        this.paymentCommand = paymentCommand;
        this.inventoryReservationPolicy = inventoryReservationPolicy;
    }

    public boolean execute(Object machine, Object slot) {
        if (!inventoryReservationPolicy.tryReserve(slot)) {
            return false;
        }
        paymentCommand.apply(machine);
        stateTransition.move(machine, "DISPENSING");
        return true;
    }
}

interface MachineStateTransition {
    void move(Object machine, String nextState);
}

interface PaymentCommand {
    void apply(Object machine);
}

interface InventoryReservationPolicy {
    boolean tryReserve(Object slot);
}
