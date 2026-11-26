import time

class PacelcSimulator:
    VALID_POLICIES = {"PC_EC", "PC_EL", "PA_EL", "PA_EC"}

    def __init__(self, policy="PC_EC"):
        if policy not in self.VALID_POLICIES:
            raise ValueError(f"Invalid policy. Must be one of {self.VALID_POLICIES}")
        self.policy = policy
        self.nodes = {1: None, 2: None, 3: None}
        self.isolated_nodes = set()
        
    def write(self, key, value):
        start_time = time.time()
        
        active_nodes = set(self.nodes.keys()) - self.isolated_nodes
        has_majority = len(active_nodes) > len(self.nodes) / 2
        
        is_partitioned = len(self.isolated_nodes) > 0

        if is_partitioned:
            if self.policy in ["PC_EC", "PC_EL"]:
                if not has_majority:
                    return {"status": "error", "message": "Consistency rejected write: Minority partition", "latency": time.time() - start_time}
            if not active_nodes:
                return {"status": "error", "message": "No active nodes", "latency": time.time() - start_time}
        else:
            if self.policy in ["PC_EC", "PA_EC"]:
                time.sleep(0.05) 
            elif self.policy in ["PC_EL", "PA_EL"]:
                pass
                
        for node in active_nodes:
            self.nodes[node] = value

        return {"status": "success", "latency": time.time() - start_time}
        
    def read(self, key):
        start_time = time.time()
        
        active_nodes = set(self.nodes.keys()) - self.isolated_nodes
        has_majority = len(active_nodes) > len(self.nodes) / 2
        
        is_partitioned = len(self.isolated_nodes) > 0
        
        if is_partitioned:
            if self.policy in ["PC_EC", "PC_EL"]:
                if not has_majority:
                    return {"status": "error", "message": "Consistency rejected read: Minority partition", "latency": time.time() - start_time, "value": None}
            if not active_nodes:
                return {"status": "error", "message": "No active nodes", "latency": time.time() - start_time, "value": None}
        else:
            if self.policy in ["PC_EC", "PA_EC"]:
                time.sleep(0.05)
                
        if not active_nodes:
            return {"status": "error", "message": "No active nodes", "latency": time.time() - start_time, "value": None}
            
        val = self.nodes[list(active_nodes)[0]]
        stale = len(set(self.nodes.values())) > 1
        
        return {"status": "success", "value": val, "latency": time.time() - start_time, "stale": stale}
        
    def injectPartition(self, isolated_nodes):
        self.isolated_nodes = set(isolated_nodes)
        
    def healPartition(self):
        self.isolated_nodes = set()
        vals = [v for v in self.nodes.values() if v is not None]
        if vals:
            val = vals[-1] 
            for n in self.nodes:
                self.nodes[n] = val

