import threading

class ReplicatedPartition:
    def __init__(self, id, leader_id, followers):
        self.id = id
        self.leader_id = leader_id
        self.followers = followers
        self.isr = set([leader_id] + followers)
        self.log = []
        self.high_watermark = 0
        self.lock = threading.Lock()
        
    def append(self, message, acks="all", min_insync_replicas=2):
        with self.lock:
            if len(self.isr) < min_insync_replicas:
                raise Exception("NotEnoughReplicas")
            
            offset = len(self.log)
            self.log.append(message)
            
            if acks == "all":
                # Wait for all ISR to acknowledge
                self.high_watermark += 1
                
            return offset
            
    def fail_node(self, node_id):
        with self.lock:
            if node_id in self.isr:
                self.isr.remove(node_id)
                if node_id == self.leader_id:
                    self.elect_leader()
                    
    def elect_leader(self):
        if self.isr:
            self.leader_id = list(self.isr)[0]
        else:
            self.leader_id = None
