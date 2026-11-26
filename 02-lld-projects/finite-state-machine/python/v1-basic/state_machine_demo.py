import sys
import os

# Ensure absolute path import so it correctly runs from python/v1-basic context
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from builder import StateMachineBuilder

class OrderContext:
    def __init__(self, order_id: str, amount: float):
        self.order_id = order_id
        self.amount = amount
        self.is_paid = False

def print_created(ctx: OrderContext):
    print(f"Order {ctx.order_id} created.")

def print_leaving_created(ctx: OrderContext):
    print("Leaving CREATED state.")

def process_checkout(ctx: OrderContext):
    print(f"Processing checkout for order {ctx.order_id}")
    
def check_amount(ctx: OrderContext) -> bool:
    return ctx.amount > 0

def process_payment(ctx: OrderContext):
    ctx.is_paid = True
    print(f"Payment received for order {ctx.order_id}")

def global_listener(from_state: str, to_state: str, event: str):
    print(f"Transitioned from {from_state} to {to_state} on {event}")

def main():
    builder = StateMachineBuilder[OrderContext]()
    
    builder.with_initial_state("CREATED") \
           .with_state("PAYMENT_PENDING", False) \
           .with_state("COMPLETED", True) \
           .with_state("CANCELLED", True)
           
    builder.with_entry_action("CREATED", print_created)
    builder.with_exit_action("CREATED", print_leaving_created)
    
    builder.with_transition() \
           .from_state("CREATED").to_state("PAYMENT_PENDING").on_event("CHECKOUT") \
           .with_action(process_checkout) \
           .create()
           
    builder.with_transition() \
           .from_state("PAYMENT_PENDING").to_state("COMPLETED").on_event("PAY") \
           .with_guard(check_amount) \
           .with_action(process_payment) \
           .create()
           
    builder.with_transition() \
           .from_state("CREATED").to_state("CANCELLED").on_event("CANCEL") \
           .create()
           
    builder.with_transition() \
           .from_state("PAYMENT_PENDING").to_state("CANCELLED").on_event("CANCEL") \
           .create()
           
    builder.with_global_listener(global_listener)
    
    state_machine = builder.build()
    
    order1 = OrderContext("ORD-001", 150.0)
    state_machine.start(order1)
    
    print(f"Current State: {state_machine.current_state}")
    state_machine.fire("CHECKOUT", order1)
    print(f"Current State: {state_machine.current_state}")
    state_machine.fire("PAY", order1)
    print(f"Current State: {state_machine.current_state}")
    
    print(f"Is Terminal: {state_machine.is_terminal}")
    
    fired = state_machine.fire("CANCEL", order1)
    print(f"Fired after terminal? {fired}")

if __name__ == "__main__":
    main()
