
from __future__ import annotations

import time
import threading
from dataclasses import dataclass
from typing import Dict, List, Protocol, Optional


@dataclass
class RegionPlan:
    event_id: str
    primary_region: str
    read_regions: List[str]


class RegionRouter(Protocol):
    def read_region(self, user_region: str, event_id: str) -> str:
        ...

    def write_region(self, event_id: str) -> str:
        ...


class WaitingRoomQueue(Protocol):
    def enqueue(self, user_id: str, event_id: str) -> str:
        ...
        
    def check_status(self, token_id: str) -> str:
        ...


class EventRepositoryGlobal(Protocol):
    def search(self, region: str, city: str, page: int, page_size: int) -> List[Dict[str, str]]:
        ...


class BookingOrchestrator(Protocol):
    def create(self, region: str, event_id: str, hold_id: str, payment_token: str, idempotency_key: str) -> str:
        ...

class DistributedTicketingService:
    def __init__(self, router: RegionRouter, wait_queue: WaitingRoomQueue, 
                 event_repo: EventRepositoryGlobal, orchestrator: BookingOrchestrator):
        self.router = router
        self.wait_queue = wait_queue
        self.event_repo = event_repo
        self.orchestrator = orchestrator

    def search_events_global(self, user_region: str, city: str, page: int, page_size: int) -> List[Dict[str, str]]:
        # Usually search goes to multiple read regions or a dedicated global index
        region = self.router.read_region(user_region, "*")
        return self.event_repo.search(region, city, page, page_size)

    def create_booking_global(self, event_id: str, hold_id: str, payment_token: str, idempotency_key: str) -> str:
        write_region = self.router.write_region(event_id)
        return self.orchestrator.create(write_region, event_id, hold_id, payment_token, idempotency_key)

    def region_plan(self, event_id: str) -> RegionPlan:
        primary = self.router.write_region(event_id)
        # Simplified assumption: all regions can be read regions
        return RegionPlan(event_id=event_id, primary_region=primary, read_regions=[primary, "eu-west-1", "ap-northeast-1"])
