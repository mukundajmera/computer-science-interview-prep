import typing
from domain import PriceRecord, PriceAlertSubscription
from dispatcher import RateLimitedDispatcher
from ring_buffer import OptimizedPriceTracker

class Clock(typing.Protocol):
    def now_sec(self) -> int: ...

class PriceHistoryStore(typing.Protocol):
    def add_price_tick(self, product_id: str, merchant_id: str, record: PriceRecord) -> None: ...
    def get_current_price(self, product_id: str, merchant_id: str) -> typing.Optional[int]: ...
    def get_history(self, product_id: str, merchant_id: str) -> typing.List[PriceRecord]: ...

class OptimizedPriceHistoryStore:
    def __init__(self, retention_seconds: int, clock: Clock) -> None:
        self.retention_seconds = retention_seconds
        self.clock = clock
        self.tracker = OptimizedPriceTracker(window_size=1000)
        self.history: typing.Dict[str, typing.Dict[str, typing.List[PriceRecord]]] = {}

    def add_price_tick(self, product_id: str, merchant_id: str, record: PriceRecord) -> None:
        if self.tracker.add_tick(product_id, merchant_id, record):
            if product_id not in self.history:
                self.history[product_id] = {}
            if merchant_id not in self.history[product_id]:
                self.history[product_id][merchant_id] = []
            
            self.history[product_id][merchant_id].append(record)
        self._cleanup(product_id, merchant_id)

    def get_current_price(self, product_id: str, merchant_id: str) -> typing.Optional[int]:
        return self.tracker.get_stats(product_id, merchant_id).get('current_price')

    def get_history(self, product_id: str, merchant_id: str) -> typing.List[PriceRecord]:
        return self.history.get(product_id, {}).get(merchant_id, [])

    def _cleanup(self, product_id: str, merchant_id: str) -> None:
        cutoff_time = self.clock.now_sec() - self.retention_seconds
        records = self.history.get(product_id, {}).get(merchant_id)
        if records is not None:
            self.history[product_id][merchant_id] = [r for r in records if r.timestamp >= cutoff_time]
            
class InMemoryPriceHistoryStore(OptimizedPriceHistoryStore):
    pass

class PriceService:
    def __init__(self, history_store: PriceHistoryStore, dispatcher: RateLimitedDispatcher) -> None:
        self.history_store = history_store
        self.dispatcher = dispatcher
        self._subscriptions: typing.Dict[str, typing.List[PriceAlertSubscription]] = {}
        self._alert_state: typing.Dict[str, bool] = {}

    def subscribe(self, subscription: PriceAlertSubscription) -> None:
        if subscription.product_id not in self._subscriptions:
            self._subscriptions[subscription.product_id] = []
        self._subscriptions[subscription.product_id].append(subscription)

    def unsubscribe(self, subscription_id: str) -> None:
        for product_id in self._subscriptions:
            self._subscriptions[product_id] = [
                sub for sub in self._subscriptions[product_id]
                if sub.id != subscription_id
            ]

    def on_price_update(self, product_id: str, merchant_id: str, record: PriceRecord) -> None:
        history = self.history_store.get_history(product_id, merchant_id)
        if history:
            max_timestamp = max(r.timestamp for r in history)
            if record.timestamp < max_timestamp:
                return
        self.history_store.add_price_tick(product_id, merchant_id, record)
        self._check_alerts(product_id, merchant_id, record)

    def _check_alerts(self, product_id: str, merchant_id: str, current_record: PriceRecord) -> None:
        subs = self._subscriptions.get(product_id, [])
        for sub in subs:
            condition_met = False
            
            # Check fixed threshold
            if sub.threshold_price is not None and current_record.price_cents < sub.threshold_price:
                condition_met = True
                
            # Check percentage drop in 24h
            if not condition_met and sub.percentage_drop is not None:
                now = current_record.timestamp
                history = self.history_store.get_history(product_id, merchant_id)
                twenty_four_hours_ago = now - (24 * 60 * 60)
                old_records = [r for r in history if r.timestamp <= twenty_four_hours_ago]
                
                if old_records:
                    old_price_record = max(old_records, key=lambda r: r.timestamp)
                    old_price = old_price_record.price_cents
                    if old_price > 0:
                        drop = ((old_price - current_record.price_cents) / old_price) * 100.0
                        if drop >= sub.percentage_drop:
                            condition_met = True
                            
            alert_key = f"{sub.id}:{merchant_id}"
            previously_alerted = self._alert_state.get(alert_key, False)

            if condition_met:
                if not previously_alerted:
                    msg = f"Price alert for {product_id}: {current_record.price_cents} cents"
                    self.dispatcher.dispatch(sub.id, sub.user_id, sub.channel, msg)
                    self._alert_state[alert_key] = True
            else:
                self._alert_state[alert_key] = False
