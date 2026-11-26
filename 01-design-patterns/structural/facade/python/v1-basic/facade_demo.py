"""
Facade Pattern - Python Implementation
"""

# ============ V1: Home Theater ============

class DVDPlayer:
    def on(self): print("DVD Player on")
    def play(self, movie): print(f"Playing: {movie}")
    def stop(self): print("DVD stopped")
    def off(self): print("DVD Player off")

class Projector:
    def on(self): print("Projector on")
    def widescreen(self): print("Widescreen mode")
    def off(self): print("Projector off")

class SoundSystem:
    def on(self): print("Sound on")
    def volume(self, level): print(f"Volume: {level}")
    def off(self): print("Sound off")

class Lights:
    def dim(self, level): print(f"Lights: {level}%")
    def on(self): print("Lights on")


class HomeTheaterFacade:
    """Simplified interface to home theater subsystem"""
    
    def __init__(self):
        self._dvd = DVDPlayer()
        self._projector = Projector()
        self._sound = SoundSystem()
        self._lights = Lights()
    
    def watch_movie(self, movie: str):
        print(f"=== Starting: {movie} ===")
        self._lights.dim(10)
        self._projector.on()
        self._projector.widescreen()
        self._sound.on()
        self._sound.volume(50)
        self._dvd.on()
        self._dvd.play(movie)
    
    def end_movie(self):
        print("=== Shutting down ===")
        self._dvd.stop()
        self._dvd.off()
        self._sound.off()
        self._projector.off()
        self._lights.on()


# ============ V2: E-commerce Checkout ============

class InventoryService:
    def check_stock(self, item_id): return True
    def reserve(self, item_id): print(f"Reserved: {item_id}")

class PaymentService:
    def process(self, amount, card): 
        print(f"Charged ${amount}")
        return "txn_123"

class ShippingService:
    def calculate_rate(self, address): return 5.99
    def create_shipment(self, address, item_id): return "ship_456"

class NotificationService:
    def send_email(self, email, msg): print(f"Email sent to {email}")


class CheckoutFacade:
    """Simplifies complex checkout process"""
    
    def __init__(self):
        self._inventory = InventoryService()
        self._payment = PaymentService()
        self._shipping = ShippingService()
        self._notify = NotificationService()
    
    def checkout(self, item_id: str, amount: float, card: str, 
                 address: str, email: str) -> str:
        # Complex workflow simplified
        if not self._inventory.check_stock(item_id):
            raise ValueError("Out of stock")
        
        self._inventory.reserve(item_id)
        shipping = self._shipping.calculate_rate(address)
        total = amount + shipping
        
        self._payment.process(total, card)
        ship = self._shipping.create_shipment(address, item_id)
        self._notify.send_email(email, f"Order confirmed: {ship}")
        
        return ship


if __name__ == "__main__":
    print("=== Home Theater Facade ===")
    theater = HomeTheaterFacade()
    theater.watch_movie("Inception")
    print()
    theater.end_movie()
    
    print("\n=== Checkout Facade ===")
    checkout = CheckoutFacade()
    order = checkout.checkout("item_1", 99.99, "card_xxx", "123 Main St", "user@test.com")
    print(f"Order: {order}")
