"""
URL Shortener - V2 Scaled

Analytics service for click event aggregation.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional
from abc import ABC, abstractmethod
from collections import defaultdict
import threading


@dataclass
class UrlAnalytics:
    """Analytics data for a URL."""
    short_code: str
    total_clicks: int
    clicks_by_date: Dict[str, int] = field(default_factory=dict)
    clicks_by_country: Dict[str, int] = field(default_factory=dict)
    top_referrers: Dict[str, int] = field(default_factory=dict)


class AnalyticsService(ABC):
    """Analytics service interface."""
    
    @abstractmethod
    def record_click(self, event) -> None:
        """Record a click event."""
        pass
    
    @abstractmethod
    def get_total_clicks(self, short_code: str) -> int:
        """Get total clicks for a URL."""
        pass
    
    @abstractmethod
    def get_daily_clicks(self, short_code: str, date: date) -> int:
        """Get daily clicks for a URL."""
        pass
    
    @abstractmethod
    def get_analytics(self, short_code: str) -> Optional[UrlAnalytics]:
        """Get detailed analytics for a URL."""
        pass


class InMemoryAnalyticsService(AnalyticsService):
    """In-memory analytics service implementation."""
    
    def __init__(self):
        self._total_clicks: Dict[str, int] = defaultdict(int)
        self._daily_clicks: Dict[str, int] = defaultdict(int)
        self._country_clicks: Dict[str, int] = defaultdict(int)
        self._referrer_clicks: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_click(self, event) -> None:
        with self._lock:
            short_code = event.short_code
            
            # Increment total
            self._total_clicks[short_code] += 1
            
            # Increment daily
            date_key = f"{short_code}:{event.timestamp.date()}"
            self._daily_clicks[date_key] += 1
            
            # Increment by country
            if event.country:
                country_key = f"{short_code}:{event.country}"
                self._country_clicks[country_key] += 1
            
            # Increment by referrer
            if event.referrer:
                referrer_key = f"{short_code}:{event.referrer}"
                self._referrer_clicks[referrer_key] += 1
    
    def get_total_clicks(self, short_code: str) -> int:
        return self._total_clicks.get(short_code, 0)
    
    def get_daily_clicks(self, short_code: str, date: date) -> int:
        key = f"{short_code}:{date}"
        return self._daily_clicks.get(key, 0)
    
    def get_analytics(self, short_code: str) -> Optional[UrlAnalytics]:
        total = self.get_total_clicks(short_code)
        
        # Aggregate daily clicks
        by_date = {}
        prefix = f"{short_code}:"
        for key, count in self._daily_clicks.items():
            if key.startswith(prefix):
                date_str = key[len(prefix):]
                by_date[date_str] = count
        
        # Aggregate country clicks
        by_country = {}
        for key, count in self._country_clicks.items():
            if key.startswith(prefix):
                country = key[len(prefix):]
                by_country[country] = count
        
        # Aggregate referrer clicks
        by_referrer = {}
        for key, count in self._referrer_clicks.items():
            if key.startswith(prefix):
                referrer = key[len(prefix):]
                by_referrer[referrer] = count
        
        return UrlAnalytics(
            short_code=short_code,
            total_clicks=total,
            clicks_by_date=by_date,
            clicks_by_country=by_country,
            top_referrers=by_referrer
        )


class ClickEventProcessor(threading.Thread):
    """Background worker that processes click events from queue."""
    
    def __init__(self, message_queue, analytics_service: AnalyticsService,
                 url_repository):
        super().__init__(daemon=True)
        self._message_queue = message_queue
        self._analytics_service = analytics_service
        self._url_repository = url_repository
        self._running = True
    
    def run(self):
        while self._running:
            try:
                events = self._message_queue.drain()
                
                for event in events:
                    try:
                        # Update analytics
                        self._analytics_service.record_click(event)
                        
                        # Update click count in database
                        self._url_repository.increment_click_count(event.short_code)
                        
                    except Exception as e:
                        print(f"Error processing click event: {e}")
                
                # Sleep between batches
                import time
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Event processor error: {e}")
    
    def stop(self):
        self._running = False
