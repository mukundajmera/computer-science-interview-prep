class CustomerOrigin:
    def __init__(self):
        self.data_store = {}
        self.fetch_count = 0

    def put(self, path: str, data: str):
        self.data_store[path] = data

    def fetch(self, path: str) -> str:
        self.fetch_count += 1
        return self.data_store.get(path)

class OriginShield:
    def __init__(self, origin: CustomerOrigin):
        self.origin = origin
        self.cache = {}
        self.in_flight_requests = {}
        self.cache_hit_count = 0
        self.fetch_count = 0

    def fetch(self, path: str) -> str:
        self.fetch_count += 1
        if path in self.cache:
            self.cache_hit_count += 1
            return self.cache[path]
            
        if path in self.in_flight_requests:
            return "COALESCED"
            
        self.in_flight_requests[path] = []
        data = self.origin.fetch(path)
        if data is not None:
            self.cache[path] = data
        del self.in_flight_requests[path]
        return data

    def simulate_concurrent_fetches(self, path: str, num_requests: int, results: list):
        self.fetch_count += num_requests
        if path in self.cache:
            self.cache_hit_count += num_requests
            results.extend([self.cache[path]] * num_requests)
            return

        # Simulating coalescing
        data = self.origin.fetch(path)
        if data is not None:
            self.cache[path] = data
        results.extend([data] * num_requests)

class EdgeNode:
    def __init__(self, shield: OriginShield):
        self.shield = shield
        self.cache = {}
        self.cache_hit_count = 0

    def fetch(self, path: str) -> str:
        if path in self.cache:
            self.cache_hit_count += 1
            return self.cache[path]
            
        data = self.shield.fetch(path)
        if data is not None and data != "COALESCED":
            self.cache[path] = data
        return data
        
    def fetch_batch(self, path: str, count: int, results: list):
        if path in self.cache:
            self.cache_hit_count += count
            results.extend([self.cache[path]] * count)
            return
            
        self.shield.simulate_concurrent_fetches(path, count, results)
        if results and results[0] is not None:
            self.cache[path] = results[0]

    def purge(self, path: str):
        if path in self.cache:
            del self.cache[path]
