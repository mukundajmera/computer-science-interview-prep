from abc import ABC, abstractmethod
from typing import List, Optional
import sys
import os

from payment_request import PaymentRequest
from payment_response import PaymentResponse, PaymentStatus
from gateway_adapters import PaymentGateway, AbstractPaymentGateway
from idempotency_store import IdempotencyStore, IdempotencyState

class RoutingStrategy(ABC):
    @abstractmethod
    def route(self, gateways: List[PaymentGateway], request: PaymentRequest) -> Optional[PaymentGateway]:
        pass

class HealthBasedRoutingStrategy(RoutingStrategy):
    def route(self, gateways: List[PaymentGateway], request: PaymentRequest) -> Optional[PaymentGateway]:
        available = []
        for g in gateways:
            if isinstance(g, AbstractPaymentGateway):
                if g.circuit_breaker.allow_request():
                    available.append(g)
            else:
                available.append(g)
                
        if not available:
            return None
            
        return sorted(available, key=lambda x: x.get_success_rate(), reverse=True)[0]

class GatewayRouter:
    def __init__(self, gateways: List[PaymentGateway], routing_strategy: RoutingStrategy, idempotency_store: IdempotencyStore):
        self.gateways = gateways
        self.routing_strategy = routing_strategy
        self.idempotency_store = idempotency_store

    def route_payment(self, request: PaymentRequest) -> PaymentResponse:
        key = request.idempotency_key
        
        if key:
            with self.idempotency_store.lock:
                state = self.idempotency_store.get_state(key)
                if state in (IdempotencyState.COMPLETED, IdempotencyState.FAILED):
                    return self.idempotency_store.get_response(key)
                elif state == IdempotencyState.IN_PROGRESS:
                    return PaymentResponse(None, PaymentStatus.CONFLICT, "Concurrent request with same idempotency key", None)
                
                # If not locked, lock it (bypassing the explicit method to keep under one lock)
                self.idempotency_store.store[key] = __import__('idempotency_store').IdempotencyRecord(IdempotencyState.IN_PROGRESS, None)

        response = None
        attempted_gateways = set()
        
        while len(attempted_gateways) < len(self.gateways):
            remaining = [g for g in self.gateways if g not in attempted_gateways]
            selected = self.routing_strategy.route(remaining, request)
            
            if not selected:
                break
                
            attempted_gateways.add(selected)
            response = selected.process_payment(request)
            
            if response.status == PaymentStatus.SUCCESS:
                break

        if not response:
            response = PaymentResponse(None, PaymentStatus.FAILED, "All gateways failed or unavailable", None)

        if key:
            final_state = IdempotencyState.COMPLETED if response.status == PaymentStatus.SUCCESS else IdempotencyState.FAILED
            self.idempotency_store.update(key, final_state, response)

        return response
