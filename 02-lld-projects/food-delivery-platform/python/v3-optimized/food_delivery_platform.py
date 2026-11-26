import threading

class FoodDeliveryPlatform:
    def __init__(self):
        self._driver_locks = {}
        self._map_lock = threading.Lock()
        
    def _assign_driver_thread_safe(self, driver_id: str) -> bool:
        with self._map_lock:
            if driver_id not in self._driver_locks:
                self._driver_locks[driver_id] = threading.Lock()
            lock = self._driver_locks[driver_id]
            
        return lock.acquire(blocking=False)
        
    def _release_driver_thread_safe(self, driver_id: str):
        with self._map_lock:
            lock = self._driver_locks.get(driver_id)
        if lock:
            try:
                lock.release()
            except RuntimeError:
                pass

    def process_order(self, order, driver_id: str, restaurant_accepts: bool, stock_available: bool) -> bool:
        state_cls = type(order.state)
        
        if not stock_available:
            return False
            
        try:
            order.transition_state(state_cls.CREATED, state_cls.ACCEPTED)
        except ValueError:
            return False
            
        if not restaurant_accepts:
            return False
            
        try:
            order.transition_state(state_cls.ACCEPTED, state_cls.PREPARING)
        except ValueError:
            return False
            
        if not self._assign_driver_thread_safe(driver_id):
            return False
            
        try:
            order.transition_state(state_cls.PREPARING, state_cls.OUT_FOR_DELIVERY)
            return True
        except ValueError:
            self._release_driver_thread_safe(driver_id)
            return False
