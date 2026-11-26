
import java.util.HashMap;
import java.util.Map;

public class StateMachineDemo {

    static class OrderContext {
        private String orderId;
        private double amount;
        private boolean isPaid;

        public OrderContext(String orderId, double amount) {
            this.orderId = orderId;
            this.amount = amount;
            this.isPaid = false;
        }

        public String getOrderId() { return orderId; }
        public double getAmount() { return amount; }
        public boolean isPaid() { return isPaid; }
        public void setPaid(boolean paid) { isPaid = paid; }
    }

    public static void main(String[] args) {
        StateMachineBuilder<OrderContext, Object> builder = new StateMachineBuilder<>();

        builder.withInitialState("CREATED")
               .withState("PAYMENT_PENDING", false)
               .withState("COMPLETED", true)
               .withState("CANCELLED", true);

        builder.withEntryAction("CREATED", (ctx, payload) -> System.out.println("Order " + ctx.getOrderId() + " created."));
        builder.withExitAction("CREATED", (ctx, payload) -> System.out.println("Leaving CREATED state."));

        builder.withTransition()
               .from("CREATED").to("PAYMENT_PENDING").on("CHECKOUT")
               .withAction((ctx, payload) -> System.out.println("Processing checkout for order " + ctx.getOrderId()))
               .create();

        builder.withTransition()
               .from("PAYMENT_PENDING").to("COMPLETED").on("PAY")
               .withGuard((ctx, payload) -> ctx.getAmount() > 0)
               .withAction((ctx, payload) -> {
                   ctx.setPaid(true);
                   System.out.println("Payment received for order " + ctx.getOrderId());
               })
               .create();

        builder.withTransition()
               .from("CREATED").to("CANCELLED").on("CANCEL")
               .create();
               
        builder.withTransition()
               .from("PAYMENT_PENDING").to("CANCELLED").on("CANCEL")
               .create();

        builder.withGlobalListener((fromState, toState, event) ->
                System.out.println("Transitioned from " + fromState + " to " + toState + " on " + event));

        StateMachine<OrderContext, Object> stateMachine = builder.build();

        OrderContext order1 = new OrderContext("ORD-001", 150.0);
        stateMachine.start(order1, null);

        System.out.println("Current State: " + stateMachine.getCurrentState());
        stateMachine.fire("CHECKOUT", order1, null);
        System.out.println("Current State: " + stateMachine.getCurrentState());
        stateMachine.fire("PAY", order1, null);
        System.out.println("Current State: " + stateMachine.getCurrentState());
        
        System.out.println("Is Terminal: " + stateMachine.isTerminal());
        
        boolean fired = stateMachine.fire("CANCEL", order1, null);
        System.out.println("Fired after terminal? " + fired);
    }
}
